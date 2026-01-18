from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.paginator import Paginator
from auditoria.models import LogAuditoria
from usuarios.decorators import solo_superusuario


@login_required
@solo_superusuario
def auditoria_dashboard_view(request):
    query = request.GET.get("q", "")

    # Se usa select_related para evitar consultas N+1 al acceder al usuario
    logs_list = (
        LogAuditoria.objects
        .select_related("usuario")
        .all()
        .order_by("-fecha")
    )

    if query:
        logs_list = logs_list.filter(detalle__icontains=query)

    paginator = Paginator(logs_list, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "auditoria/dashboard.html",
        {
            "page_obj": page_obj,
            "query": query,
        },
    )
