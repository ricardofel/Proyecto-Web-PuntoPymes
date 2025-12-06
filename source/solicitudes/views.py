from django.shortcuts import render

def lista_solicitudes_view(request):
    # Por ahora solo carga el template vacío
    return render(request, 'solicitudes/lista_solicitudes.html', {})