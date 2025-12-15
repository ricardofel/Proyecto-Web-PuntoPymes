import os
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.contrib.auth import get_user_model

from .models import Empleado, Contrato 
from .forms import EmpleadoForm
# Importamos modelos de Usuarios para la gestión de roles
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
# 2. CREAR EMPLEADO (MODIFICADA CON SELECCIÓN DE ROL)
# ---------------------------------------------------------
def crear_empleado_view(request):
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, request.FILES)
        
        # 1. Capturar el ID del rol seleccionado en el HTML
        rol_id = request.POST.get('rol_usuario')

        if form.is_valid():
            try:
                with transaction.atomic():
                    # A. Guardar Empleado (Dispara Signal que crea usuario base)
                    empleado = form.save()
                    
                    email = form.cleaned_data.get('email') or empleado.email
                    
                    if email:
                        User = get_user_model()
                        password_acceso = f"PuntoPymes{empleado.cedula or '2025'}"
                        
                        # B. Gestión del Usuario (Creación o Vinculación)
                        if User.objects.filter(email=email).exists():
                            user = User.objects.get(email=email)
                            
                            # Si el usuario fue creado por el Signal (sin password usable) o ya existía
                            if not user.has_usable_password():
                                user.set_password(password_acceso)
                                user.estado = True 
                                user.empleado = empleado
                                user.save()
                                messages.success(request, f"Usuario activado. Clave: {password_acceso}")
                            else:
                                if not hasattr(user, 'empleado') or not user.empleado:
                                    user.empleado = empleado
                                    user.save()
                                    messages.info(request, "Usuario existente vinculado.")
                        else:
                            # Fallback: Creación manual si el signal falló
                            user = User.objects.create_user(
                                username=email,
                                email=email,
                                password=password_acceso,
                                estado=True 
                            )
                            user.empleado = empleado
                            user.save()
                            messages.success(request, f"Usuario creado. Clave: {password_acceso}")

                        # C. ASIGNACIÓN DE ROL (Lógica Nueva)
                        # Determinamos qué rol asignar
                        rol_seleccionado = None
                        if rol_id:
                            rol_seleccionado = Rol.objects.filter(id=rol_id).first()
                        
                        # Si no seleccionó nada (o no encontró ID), usamos 'Empleado' por defecto
                        if not rol_seleccionado:
                            rol_seleccionado = Rol.objects.filter(nombre="Empleado").first()

                        if rol_seleccionado:
                            # Limpiamos roles previos (ej: el signal asigna 'Empleado' automáticamente, 
                            # si elegimos 'Admin', debemos borrar el 'Empleado' previo para evitar duplicados o conflictos)
                            UsuarioRol.objects.filter(usuario=user).delete()
                            
                            # Asignamos el nuevo rol
                            UsuarioRol.objects.create(usuario=user, rol=rol_seleccionado)
                            # print(f"Asignado rol: {rol_seleccionado.nombre}") 

                    else:
                        messages.warning(request, "Empleado creado SIN usuario (no tiene email).")

            except Exception as e:
                messages.error(request, f"Error en el proceso: {e}")
            
            return redirect('empleados:lista_empleados')
    else:
        form = EmpleadoForm()

    # 2. Obtener roles para llenar el <select> en el HTML
    roles_disponibles = Rol.objects.filter(estado=True)

    return render(request, 'empleados/crear_empleado.html', {
        'form': form,
        'roles_disponibles': roles_disponibles # <--- Importante: pasamos esto al template
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
        
        # Sincronización usando .estado (no .is_active)
        if hasattr(empleado, 'usuario') and empleado.usuario:
            empleado.usuario.estado = (nuevo_estado == 'Activo')
            empleado.usuario.save()
            
    return redirect('empleados:editar_empleado', pk=pk)