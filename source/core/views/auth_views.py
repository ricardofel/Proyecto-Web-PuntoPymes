from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        UserModel = get_user_model()
        username = email

        # Permitir login por email o username sin mentirle al usuario
        try:
            user_obj = UserModel.objects.get(email=email)
            username = user_obj.get_username()
        except UserModel.DoesNotExist:
            # Si no existe ese email, intentará con el identificador como username
            username = email

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            return render(
                request, "core/login.html", {"error": "Email o contraseña incorrectos."}
            )

    return render(request, "core/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def dashboard_view(request):
    # Roles por grupos
    roles = list(request.user.groups.values_list("name", flat=True))
    main_role = roles[0] if roles else "EMPLOYEE"

    # Datos falsos solo para mostrar barras (no son KPIs reales)
    meses = [
        ("Jan", 80),
        ("Feb", 90),
        ("Mar", 95),
        ("Apr", 100),
        ("May", 105),
        ("Jun", 110),
    ]

    context = {
        "main_role": main_role,
        "meses": meses,
    }
    return render(request, "core/dashboard.html", context)
