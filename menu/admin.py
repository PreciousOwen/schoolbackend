from django.contrib import admin
from django.utils.html import format_html
from .models import Category, MenuItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'formatted_price',
        'available',
        'stock_status',
        'availability_status',
        'updated_at'
    )
    list_filter = ('category', 'available', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('available',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'description')
        }),
        ('Pricing & Availability', {
            'fields': ('price', 'available', 'stock', 'low_stock_threshold')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def formatted_price(self, obj):
        return f"TZS {obj.price * 1000:,.0f}"
    formatted_price.short_description = 'Price'
    formatted_price.admin_order_field = 'price'

    def stock_status(self, obj):
        if obj.stock <= 0:
            color = 'red'
            status = 'Out of Stock'
        elif obj.stock <= obj.low_stock_threshold:
            color = 'orange'
            status = f'Low Stock ({obj.stock})'
        else:
            color = 'green'
            status = f'In Stock ({obj.stock})'

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, status
        )
    stock_status.short_description = 'Stock Status'
    stock_status.admin_order_field = 'stock'

    def availability_status(self, obj):
        if obj.available:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Available</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Unavailable</span>'
            )
    availability_status.short_description = 'Status'
    availability_status.admin_order_field = 'available'

    actions = ['make_available', 'make_unavailable', 'mark_low_stock']

    def make_available(self, request, queryset):
        updated = queryset.update(available=True)
        self.message_user(
            request,
            f'{updated} items marked as available.'
        )
    make_available.short_description = "Mark selected items as available"

    def make_unavailable(self, request, queryset):
        updated = queryset.update(available=False)
        self.message_user(
            request,
            f'{updated} items marked as unavailable.'
        )
    make_unavailable.short_description = "Mark selected items as unavailable"

    def mark_low_stock(self, request, queryset):
        updated = queryset.update(stock=2)  # Set to low stock for testing
        self.message_user(
            request,
            f'{updated} items marked as low stock.'
        )
    mark_low_stock.short_description = "Mark selected items as low stock (for testing)"
