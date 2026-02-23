from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from applications.product.models import Category, Product
from applications.partner.models import Profile
from .models import Ticket, TicketItem


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
