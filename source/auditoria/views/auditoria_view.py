from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.paginator import Paginator
from auditoria.models import LogAuditoria

# Reutilizamos tu decorador de seguridad
from usuarios.decorators import solo_superusuario 

@login_required
@solo_superusuario # <--- SOLO TÚ PUEDES VER ESTO
def auditoria_dashboard_view(request):
    # Filtros simples (Búsqueda)
    query = request.GET.get('q', '')
    logs_list = LogAuditoria.objects.all().order_by('-fecha')
    
    if query:
        logs_list = logs_list.filter(detalle__icontains=query)

    # Paginación (Mostrar 20 por página)
    paginator = Paginator(logs_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "auditoria/dashboard.html", {
        "page_obj": page_obj,
        "query": query
    })