from django.shortcuts import render

def login_view(request):
    return render(request, "usuarios/login.html")

def home_view(request):
    return render(request, "usuarios/home.html")

def form_view(request):
    return render(request, "usuarios/form.html")