from django.shortcuts import render

# Esta es la vista que carga tu panel con pestañas
def organizacion_view(request):
    # Fíjate que la ruta coincida con la carpeta que creamos antes
    return render(request, 'core/organizacion/panel_organizacion.html')