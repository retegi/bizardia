from django.contrib import admin
from .models import Category, Product, WarehouseOrder, WarehouseOrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'stock_level', 'min_stock', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name',)
    list_editable = ('stock_level', 'min_stock', 'is_active')


class WarehouseOrderItemInline(admin.TabularInline):
    model = WarehouseOrderItem
    extra = 0
    readonly_fields = ('subtotal',)


@admin.register(WarehouseOrder)
class WarehouseOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_by', 'created_at', 'status', 'total_items')
    list_filter = ('status', 'created_at')
    search_fields = ('created_by__username',)
    inlines = [WarehouseOrderItemInline]
    readonly_fields = ('created_at',)


@admin.register(WarehouseOrderItem)
class WarehouseOrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity_requested', 'unit_price', 'subtotal')
    list_filter = ('product',)
    search_fields = ('product__name', 'order__id')
