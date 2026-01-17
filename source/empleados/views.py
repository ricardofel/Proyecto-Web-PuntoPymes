import os

# --- 1. Imports de Django ---
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404

# --- 2. Imports del Core (Mixins y Lógica Global) ---
from core.mixins import FiltradoEmpresaMixin
from core.storage import private_storage

# --- 3. Imports de Usuarios (Decoradores y Roles) ---
from usuarios.decorators import solo_superusuario_o_admin_rrhh
from usuarios.models import Rol, UsuarioRol

# --- 4. Imports Locales (Empleados) ---
from .models import Empleado, Contrato
from .forms import EmpleadoForm, ContratoForm

# =========================================================
# 1. LISTA DE EMPLEADOS (Protegida y Filtrada)
# =========================================================
@method_decorator(solo_superusuario_o_admin_rrhh, name='dispatch')
class ListaEmpleadosView(FiltradoEmpresaMixin, ListView):
    model = Empleado
    template_name = 'empleados/lista_empleados.html'
    context_object_name = 'empleados'
    paginate_by = 10 

    def get_queryset(self):
        qs = super().get_queryset()
        busqueda = self.request.GET.get('q')
        if busqueda:
            qs = qs.filter(
                Q(nombres__icontains=busqueda) | 
                Q(apellidos__icontains=busqueda) |
                Q(cedula__icontains=busqueda)
            )
        return qs.order_by('-id')

# =========================================================
# 2. CREAR EMPLEADO (¡Aquí aseguramos la Empresa!)
# =========================================================
@login_required
def crear_empleado_view(request):
    # A. RECUPERAR EMPRESA SELECCIONADA GLOBALMENTE
    empresa_actual = getattr(request, 'empresa_actual', None)
    empresa_id = empresa_actual.id if empresa_actual else None

    if request.method == 'POST':
        # Pasamos el ID al form para validar (managers/unidades correctos)
        form = EmpleadoForm(request.POST, request.FILES, empresa_id=empresa_id)
        rol_id = request.POST.get('rol_usuario')

        if form.is_valid():
            try:
                with transaction.atomic():
                    # --- PASO CRÍTICO: ASIGNACIÓN FORZOSA ---
                    # 1. Preparamos el objeto pero NO lo guardamos en DB todavía
                    empleado = form.save(commit=False)
                    
                    # 2. Le inyectamos la empresa seleccionada en el menú lateral
                    if empresa_actual:
                        empleado.empresa = empresa_actual
                    
                    # 3. Ahora sí, guardamos en la base de datos
                    empleado.save()
                    # ----------------------------------------
                    
                    # Lógica de Usuario de Sistema (Login)
                    email = form.cleaned_data.get('email') or empleado.email
                    
                    if email:
                        User = get_user_model()
                        password_acceso = f"Talent{empleado.cedula[-4:] if empleado.cedula else '2025'}"
                        
                        user = None
                        if User.objects.filter(email=email).exists():
                            user = User.objects.get(email=email)
                            user.estado = True 
                            if hasattr(user, 'empleado'): user.empleado = empleado
                            user.save()
                            messages.success(request, "Usuario vinculado existente.")
                        else:
                            user = User.objects.create_user(
                                username=email, email=email, password=password_acceso, estado=True 
                            )
                            if hasattr(user, 'empleado'): user.empleado = empleado
                            user.save()
                            messages.success(request, f"Usuario creado. Clave: {password_acceso}")

                        # Asignar Rol
                        if user:
                            rol_obj = None
                            if rol_id: rol_obj = Rol.objects.filter(id=rol_id).first()
                            if not rol_obj: rol_obj = Rol.objects.filter(nombre="Empleado").first()

                            if rol_obj:
                                UsuarioRol.objects.filter(usuario=user).delete()
                                UsuarioRol.objects.create(usuario=user, rol=rol_obj)
                    else:
                        messages.warning(request, "Empleado creado SIN acceso al sistema (falta email).")

                return redirect('empleados:lista_empleados')

            except Exception as e:
                messages.error(request, f"Error al guardar: {e}")
        else:
             messages.error(request, "Error en el formulario. Verifique los campos.")
    else:
        # Al cargar la página vacía, pasamos el ID para filtrar los combos (Manager/Unidad)
        form = EmpleadoForm(empresa_id=empresa_id)

    roles_disponibles = Rol.objects.filter(estado=True)

    return render(request, 'empleados/crear_empleado.html', {
        'form': form,
        'roles_disponibles': roles_disponibles
    })

# =========================================================
# 3. EDITAR EMPLEADO
# =========================================================
@login_required
def editar_empleado_view(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    
    # Al editar, respetamos la empresa ORIGINAL del empleado
    empresa_id = empleado.empresa.id if empleado.empresa else None
    
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, request.FILES, instance=empleado, empresa_id=empresa_id)
        if form.is_valid():
            form.save()
            messages.success(request, "Empleado actualizado.")
            return redirect('empleados:lista_empleados')
    else:
        form = EmpleadoForm(instance=empleado, empresa_id=empresa_id)

    roles_disponibles = Rol.objects.filter(estado=True)
    
    # Buscamos el rol actual para marcarlo en el HTML
    rol_actual_id = None
    usuario_asociado = get_user_model().objects.filter(email=empleado.email).first()
    if usuario_asociado:
        ur = UsuarioRol.objects.filter(usuario=usuario_asociado).first()
        if ur: rol_actual_id = ur.rol.id

    return render(request, 'empleados/editar_empleado.html', {
        'form': form, 
        'empleado': empleado,
        'roles_disponibles': roles_disponibles,
        'rol_actual_id': rol_actual_id,
        'es_edicion': True
    })

# =========================================================
# 4. OTRAS VISTAS (Contratos, Fotos, Estado)
# =========================================================
@login_required
def lista_contratos_view(request, empleado_id):
    empleado = get_object_or_404(Empleado, pk=empleado_id)
    contratos = Contrato.objects.filter(empleado=empleado).order_by('-fecha_inicio')
    return render(request, 'empleados/lista_contratos.html', {'empleado': empleado, 'contratos': contratos})

@require_POST
@login_required
def actualizar_foto_view(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if 'foto' in request.FILES:
        if empleado.foto and os.path.isfile(empleado.foto.path):
            try: os.remove(empleado.foto.path)
            except: pass
        empleado.foto = request.FILES['foto']
        empleado.save()
        messages.success(request, "Foto actualizada.")
    return redirect('empleados:editar_empleado', pk=pk)

@require_POST
@login_required
def cambiar_estado_empleado_view(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    nuevo_estado = request.POST.get('nuevo_estado')
    if nuevo_estado in ['Activo', 'Inactivo', 'Licencia', 'Suspendido']:
        empleado.estado = nuevo_estado
        empleado.save()
        
        # Bloquear acceso si se inactiva
        User = get_user_model()
        u = User.objects.filter(email=empleado.email).first()
        if u:
            u.estado = (nuevo_estado == 'Activo')
            u.save()
            
        messages.success(request, f"Estado cambiado a {nuevo_estado}")
    return redirect('empleados:editar_empleado', pk=pk)


def crear_contrato_view(request, empleado_id):
    empleado = get_object_or_404(Empleado, pk=empleado_id)
    
    if request.method == 'POST':
        form = ContratoForm(request.POST, request.FILES) # <--- IMPORTANTE: request.FILES
        if form.is_valid():
            contrato = form.save(commit=False)
            contrato.empleado = empleado # Asignamos el empleado AQUÍ
            contrato.save() # Al guardar, se ejecuta upload_to usando contrato.empleado.id
            messages.success(request, "Contrato registrado correctamente.")
            return redirect('empleados:lista_contratos', empleado_id=empleado.id)
    else:
        form = ContratoForm()
    
    return render(request, 'empleados/crear_contrato.html', {
        'form': form, 
        'empleado': empleado
    })

@login_required
def servir_contrato_privado(request, filepath):
    # 1. Limpieza de seguridad: Quitamos barras al inicio o final
    filepath = filepath.strip('/')
    
    # 2. FIX DE DOBLE RUTA: 
    # A veces la BD guarda "contratos/archivo.pdf" y a veces solo "archivo.pdf".
    # Si la ruta que nos llega YA empieza con 'contratos/', la usamos tal cual.
    # Si NO empieza con 'contratos/', se lo agregamos (por si acaso).
    
    # En tu caso, la BD YA TIENE "contratos/...", así que confiamos en filepath.
    ruta_final = filepath

    # Debug (opcional, lo verás en la consola negra donde corre el server)
    print(f"--- INTENTANDO ABRIR: {ruta_final} ---")

    # 3. Verificar existencia
    if not private_storage.exists(ruta_final):
        # Intento de rescate: Probamos agregando 'contratos/' si falló el anterior
        if private_storage.exists(f'contratos/{ruta_final}'):
             ruta_final = f'contratos/{ruta_final}'
        else:
             raise Http404(f"El documento no se encuentra en: {ruta_final}")
        
    # 4. Servir archivo
    archivo = private_storage.open(ruta_final)
    return FileResponse(archivo)