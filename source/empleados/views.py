import os
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.contrib.auth import get_user_model

from .models import Empleado, Contrato 
from .forms import EmpleadoForm
from usuarios.models import Rol, UsuarioRol 

# ---------------------------------------------------------
# 1. LISTA EMPLEADOS
# ---------------------------------------------------------
def lista_empleados_view(request):
    empleados = Empleado.objects.all().order_by('-id')
    busqueda = request.GET.get('q')
    if busqueda:
        empleados = empleados.filter(
            Q(nombres__icontains=busqueda) | 
            Q(apellidos__icontains=busqueda) |
            Q(cedula__icontains=busqueda)
        )
    return render(request, 'empleados/lista_empleados.html', {'empleados': empleados})

# ---------------------------------------------------------
# 2. CREAR EMPLEADO
# ---------------------------------------------------------
def crear_empleado_view(request):
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, request.FILES)
        
        # 1. Capturamos el Rol elegido en el HTML
        rol_id = request.POST.get('rol_usuario')

        if form.is_valid():
            try:
                with transaction.atomic():
                    # A. Guardar Empleado
                    empleado = form.save()
                    
                    email = form.cleaned_data.get('email') or empleado.email
                    
                    if email:
                        User = get_user_model()
                        # Generamos la clave: PuntoPymes + Cédula (o 2025 si no hay cédula)
                        password_acceso = f"PuntoPymes{empleado.cedula or '2025'}"
                        
                        user = None
                        
                        # B. Gestión del Usuario (Crear o Vincular)
                        if User.objects.filter(email=email).exists():
                            # CASO 1: El usuario YA EXISTE
                            user = User.objects.get(email=email)
                            
                            # Forzamos el cambio de contraseña para que coincida con la nueva
                            user.set_password(password_acceso)
                            
                            user.estado = True 
                            user.empleado = empleado
                            user.save()
                            
                            # Mensaje con la clave (Actualizado)
                            messages.success(request, f"Usuario vinculado y actualizado. Clave: {password_acceso}")
                        else:
                            # CASO 2: Usuario NUEVO
                            user = User.objects.create_user(
                                username=email,
                                email=email,
                                password=password_acceso,
                                estado=True 
                            )
                            user.empleado = empleado
                            user.save()
                            
                            # Mensaje con la clave (Nuevo)
                            messages.success(request, f"Usuario creado. Clave: {password_acceso}")

                        # C. ASIGNACIÓN DE ROL
                        rol_seleccionado = None
                        if rol_id:
                            rol_seleccionado = Rol.objects.filter(id=rol_id).first()
                        
                        # Fallback: Si no hay rol, 'Empleado' por defecto
                        if not rol_seleccionado:
                            rol_seleccionado = Rol.objects.filter(nombre="Empleado").first()

                        if rol_seleccionado:
                            # Borramos roles previos para evitar duplicados/mezclas
                            UsuarioRol.objects.filter(usuario=user).delete()
                            
                            # Creamos la relación nueva
                            UsuarioRol.objects.create(usuario=user, rol=rol_seleccionado)

                    else:
                        messages.warning(request, "Empleado creado SIN usuario (falta email).")

            except Exception as e:
                messages.error(request, f"Error en el proceso: {e}")
            
            return redirect('empleados:lista_empleados')
    else:
        form = EmpleadoForm()

    # Enviamos roles activos al template
    roles_disponibles = Rol.objects.filter(estado=True)

    return render(request, 'empleados/crear_empleado.html', {
        'form': form,
        'roles_disponibles': roles_disponibles
    })

# ---------------------------------------------------------
# 3. EDICIÓN
# ---------------------------------------------------------
def editar_empleado_view(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, request.FILES, instance=empleado)
        if form.is_valid():
            form.save()
            return redirect('empleados:lista_empleados')
    else:
        form = EmpleadoForm(instance=empleado)
    return render(request, 'empleados/editar_empleado.html', {'form': form, 'empleado': empleado})

# ---------------------------------------------------------
# 4. CONTRATOS
# ---------------------------------------------------------
def lista_contratos_view(request, empleado_id):
    empleado = get_object_or_404(Empleado, pk=empleado_id)
    contratos = Contrato.objects.filter(empleado=empleado).order_by('-fecha_inicio')
    return render(request, 'empleados/lista_contratos.html', {'empleado': empleado, 'contratos': contratos})

# ---------------------------------------------------------
# 5. FOTO
# ---------------------------------------------------------
@require_POST
def actualizar_foto_view(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if 'foto' in request.FILES:
        if empleado.foto and os.path.isfile(empleado.foto.path):
            try: os.remove(empleado.foto.path)
            except: pass
        empleado.foto = request.FILES['foto']
        empleado.save()
    return redirect('empleados:editar_empleado', pk=pk)

# ---------------------------------------------------------
# 6. ESTADO
# ---------------------------------------------------------
@require_POST
def cambiar_estado_empleado_view(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    nuevo_estado = request.POST.get('nuevo_estado')
    if nuevo_estado in ['Activo', 'Inactivo', 'Licencia', 'Suspendido']:
        empleado.estado = nuevo_estado
        empleado.save()
        
        if hasattr(empleado, 'usuario') and empleado.usuario:
            empleado.usuario.estado = (nuevo_estado == 'Activo')
            empleado.usuario.save()
            
    return redirect('empleados:editar_empleado', pk=pk)