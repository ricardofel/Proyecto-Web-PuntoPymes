# core/views/auth_views.py
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

User = get_user_model()


def login_view(request):
    # Si ya está logueado, lo mandamos al dashboard
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")

        # OJO: aunque usamos email, el parámetro se llama username
        user = authenticate(request, username=email, password=password)

        if user is not None:
            # Por si acaso, respetamos el estado del usuario
            if not getattr(user, "estado", True):
                messages.error(
                    request,
                    "Tu usuario está inactivo. Contacta con el administrador.",
                )
            else:
                login(request, user)
                return redirect("dashboard")
        else:
            messages.error(request, "Correo o contraseña incorrectos.")

    return render(request, "usuarios/login.html", {})


def logout_view(request):
    logout(request)
    messages.success(request, "Has cerrado sesión correctamente.")
    return redirect("login")


@login_required
def dashboard_view(request):
    # De momento lo dejamos sencillo; tú ya tienes algo aquí
    return render(request, "core/dashboard.html")
