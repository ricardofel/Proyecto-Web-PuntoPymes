# core/views/auth_views.py
from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    login,
    logout,
    get_user_model,
    update_session_auth_hash,
)
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_login_failed
from django.contrib.auth.forms import PasswordChangeForm

User = get_user_model()


def login_view(request):
    # Si el usuario ya está autenticado, redirigir al dashboard.
    if request.user.is_authenticated:
        return redirect("dashboard")

    # Se reutiliza para repoblar el campo email ante errores de autenticación.
    email_inicial = ""

    if request.method == "POST":
        email_inicial = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")

        # authenticate usa el parámetro "username" incluso si internamente trabajas con email.
        user = authenticate(request, username=email_inicial, password=password)

        if user is not None:
            # Respetar la bandera de negocio `estado` (si existe).
            if not getattr(user, "estado", True):
                messages.error(
                    request,
                    "Tu usuario está inactivo. Contacta con el administrador.",
                )
            else:
                login(request, user)
                return redirect("dashboard")
        else:
            # Emitir signal para registrar intentos fallidos (si hay listeners configurados).
            user_login_failed.send(
                sender=User,
                credentials={"username": email_inicial},
                request=request,
            )
            messages.error(request, "Correo o contraseña incorrectos.")

    context = {
        "email": email_inicial,
    }
    return render(request, "usuarios/login.html", context)


def logout_view(request):
    """
    Cierra sesión y redirige a la pantalla de login.
    """
    logout(request)
    messages.success(request, "Has cerrado sesión correctamente.")
    return redirect("login")


@login_required
def dashboard_view(request):
    """
    Vista simple de dashboard (placeholder).
    """
    return render(request, "core/dashboard.html")


@login_required
def password_change_view(request):
    """
    Permite al usuario cambiar su contraseña dentro del sistema.

    - Solicita contraseña actual, nueva y confirmación.
    - Mantiene la sesión activa después del cambio.
    """
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            # Mantener la sesión activa tras actualizar el hash de contraseña.
            update_session_auth_hash(request, user)
            messages.success(request, "Tu contraseña se ha actualizado correctamente.")
            return redirect("dashboard")
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, "usuarios/password_change.html", {"form": form})
