from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .models import Product, WarehouseOrder, Category
from .forms import WarehouseOrderForm, WarehouseOrderItemFormSet


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
