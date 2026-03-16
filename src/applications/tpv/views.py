from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from applications.product.models import Category, Product
from applications.partner.models import Profile
from .models import Ticket, TicketItem, Payment


def tpv_view(request):
    partner = Profile.objects.first()  # luego será seleccionable
    ticket, created = Ticket.objects.get_or_create(
        partner=partner,
        is_closed=False
    )

    categories = Category.objects.prefetch_related('products').all()

    return render(request, 'tpv/tpv.html', {
        'categories': categories,
        'ticket': ticket,
    })


@require_POST
def add_item(request):
    product_id = request.POST.get('product_id')
    ticket_id = request.POST.get('ticket_id')

    ticket = get_object_or_404(Ticket, id=ticket_id, is_closed=False)
    product = get_object_or_404(Product, id=product_id, is_active=True)

    item, created = TicketItem.objects.get_or_create(
        ticket=ticket,
        product=product,
        defaults={'price': product.price}
    )

    if not created:
        item.quantity += 1
        item.save()

    ticket.calculate_total()

    return JsonResponse({
        'success': True,
        'total': str(ticket.total),
        'item': {
            'id': product.id,
            'name': product.name,
            'quantity': item.quantity,
            'price': str(item.price),
            'subtotal': str(item.get_total()),
        }
    })


from django.views.decorators.http import require_POST

@require_POST
def clear_ticket(request):
    ticket_id = request.POST.get("ticket_id")
    ticket = get_object_or_404(Ticket, id=ticket_id, is_closed=False)

    ticket.items.all().delete()
    ticket.total = 0
    ticket.save()

    return JsonResponse({"success": True})

@require_POST
def update_quantity(request):
    ticket_id = request.POST.get("ticket_id")
    product_id = request.POST.get("product_id")
    action = request.POST.get("action")  # plus | minus

    ticket = get_object_or_404(Ticket, id=ticket_id, is_closed=False)
    item = get_object_or_404(TicketItem, ticket=ticket, product_id=product_id)

    if action == "plus":
        item.quantity += 1
        item.save()
    elif action == "minus":
        item.quantity -= 1
        if item.quantity <= 0:
            item.delete()
            ticket.calculate_total()
            return JsonResponse({
                "success": True,
                "removed": True,
                "quantity": 0,
                "subtotal": "0.00",
                "total": str(ticket.total),
            })
        item.save()

    ticket.calculate_total()

    return JsonResponse({
        "success": True,
        "removed": False,
        "quantity": item.quantity,
        "subtotal": str(item.get_total()),
        "total": str(ticket.total),
    })


@require_POST
def finalize_ticket(request):
    """
    Cierra el ticket, asigna (o confirma) el partner y crea el Payment.
    Devuelve la URL del ticket para imprimir.
    """
    ticket_id = request.POST.get("ticket_id")
    partner_number = request.POST.get("partner_number")
    payment_method = request.POST.get("payment_method")

    if not payment_method:
        return JsonResponse(
            {"success": False, "error": "Ordainketa-metodoa beharrezkoa da."},
            status=400,
        )

    ticket = get_object_or_404(Ticket, id=ticket_id, is_closed=False)

    if not ticket.items.exists():
        return JsonResponse(
            {"success": False, "error": "Ezin da tiketa hutsik itxi."},
            status=400,
        )

    # Si no hay partner en el ticket, lo buscamos por número introducido
    if ticket.partner is None:
        if not partner_number:
            return JsonResponse(
                {"success": False, "error": "Bazkide zenbakia beharrezkoa da."},
                status=400,
            )
        try:
            partner = Profile.objects.get(partner_number=partner_number)
        except Profile.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Ez da bazkide hori aurkitu."},
                status=404,
            )
        ticket.partner = partner

    ticket.calculate_total()
    ticket.is_closed = True
    ticket.closed_at = timezone.now()
    ticket.save()

    Payment.objects.update_or_create(
        ticket=ticket,
        defaults={
            "method": payment_method,
            "amount": ticket.total,
        },
    )

    pdf_url = reverse("tpv:ticket_pdf", args=[ticket.id])
    return JsonResponse({"success": True, "pdf_url": pdf_url})


def ticket_pdf_view(request, pk):
    """
    Vista imprimible del ticket. El navegador podrá imprimir/guardar como PDF.
    """
    ticket = get_object_or_404(
        Ticket.objects.select_related("partner").prefetch_related("items__product"),
        pk=pk,
    )
    return render(request, "tpv/ticket_pdf.html", {"ticket": ticket})


@login_required
def my_ticket_list(request):
    """
    Lista de tickets del partner asociado al usuario logueado.
    """
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        tickets = Ticket.objects.none()
    else:
        tickets = (
            Ticket.objects.filter(partner=profile, is_closed=True)
            .order_by("-created_at")
        )

    return render(request, "tpv/my_ticket_list.html", {"tickets": tickets})


@login_required
def my_ticket_detail(request, pk):
    """
    Detalle de un ticket del usuario logueado.
    """
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return HttpResponse(status=404)

    ticket = get_object_or_404(
        Ticket.objects.select_related("partner", "payment").prefetch_related(
            "items__product"
        ),
        pk=pk,
        partner=profile,
    )

    return render(request, "tpv/ticket_detail.html", {"ticket": ticket})
