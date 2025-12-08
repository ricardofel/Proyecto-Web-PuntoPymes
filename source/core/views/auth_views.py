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
    # Si ya está logueado, lo mandamos al dashboard
    if request.user.is_authenticated:
        return redirect("dashboard")  # o "core:dashboard" si lo tienes con namespace

    email_inicial = ""  # para rellenar el campo si hay error

    if request.method == "POST":
        email_inicial = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")

        # Aunque usamos email, el parámetro se llama username
        user = authenticate(request, username=email_inicial, password=password)

        if user is not None:
            # Respetamos el estado del usuario (tu bandera de negocio)
            if not getattr(user, "estado", True):
                messages.error(
                    request,
                    "Tu usuario está inactivo. Contacta con el administrador.",
                )
            else:
                login(request, user)
                return redirect("dashboard")  # o "core:dashboard"
        else:
            # 👇 Disparamos el signal para que tu logger lo capture
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
    logout(request)
    messages.success(request, "Has cerrado sesión correctamente.")
    return redirect("login")  # asegúrate que tu URL de login se llame "login"


@login_required
def dashboard_view(request):
    # De momento lo dejamos sencillo; tú ya tienes algo aquí
    return render(request, "core/dashboard.html")


@login_required
def password_change_view(request):
    """
    Permite al usuario cambiar su contraseña dentro del sistema.
    - Pide contraseña actual, nueva y confirmación.
    - Mantiene la sesión activa después del cambio.
    """
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()  # guarda la nueva contraseña hasheada
            update_session_auth_hash(request, user)  # 👈 mantiene la sesión activa
            messages.success(request, "Tu contraseña se ha actualizado correctamente.")
            return redirect("dashboard")  # o "core:dashboard" si usas namespace
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, "usuarios/password_change.html", {"form": form})
