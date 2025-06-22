from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .models import Product, WarehouseOrder, Category
from .forms import WarehouseOrderForm, WarehouseOrderItemFormSet
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Product, WarehouseOrder, WarehouseOrderItem


from .models import WarehouseOrder, WarehouseOrderItem, Product

class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'warehouse/product_list.html'
    context_object_name = 'products'
    queryset = Product.objects.filter(is_active=True).order_by('category__name', 'name')



class OrderCreateView(LoginRequiredMixin, CreateView):
    model = WarehouseOrder
    form_class = WarehouseOrderForm
    template_name = 'warehouse/create_order.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = WarehouseOrderItemFormSet(self.request.POST or None, prefix='items')

        else:
            context['formset'] = WarehouseOrderItemFormSet(prefix='items')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']

        if formset.is_valid():
            form.instance.created_by = self.request.user
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return redirect('warehouse:order_detail', pk=self.object.pk)
        else:
            return self.render_to_response(self.get_context_data(form=form))




class OrderDetailView(LoginRequiredMixin, DetailView):
    model = WarehouseOrder
    template_name = 'warehouse/order_detail.html'
    context_object_name = 'order'




class WarehouseOrderCreateView(LoginRequiredMixin, View):
    def get(self, request):
        products = Product.objects.filter(is_active=True)
        return render(request, 'warehouse/create_order.html', {'products': products})

    def post(self, request):
        notes = request.POST.get('notes', '')
        product_ids = request.POST.getlist('product_id')
        quantities = request.POST.getlist('quantity')

        if not product_ids or not quantities:
            return render(request, 'warehouse/create_order.html', {
                'products': Product.objects.filter(is_active=True),
                'error': 'Debes seleccionar al menos un producto y cantidad.'
            })

        order = WarehouseOrder.objects.create(created_by=request.user, notes=notes)

        for pid, qty in zip(product_ids, quantities):
            try:
                product = Product.objects.get(pk=pid)
                quantity = int(qty)
                if quantity > 0:
                    WarehouseOrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity_requested=quantity
                    )
            except (Product.DoesNotExist, ValueError):
                continue

        return redirect('warehouse:order_list') # O redirigir a lista de pedidos

class WarehouseOrderListView(ListView):
    model = WarehouseOrder
    template_name = 'warehouse/order_list.html'
    context_object_name = 'orders'
    ordering = ['-created_at']
