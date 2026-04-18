from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'price', 'quantity']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'total_amount', 'status', 'is_paid', 'created_at']
    list_filter = ['status', 'is_paid', 'created_at']
    list_editable = ['status']
    search_fields = ['full_name', 'email']
    inlines = [OrderItemInline]
