
from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, Customer, Order, OrderItem, StorePaymentSettings
from .models import (
    Category,
    Product,
    Customer,
    Order,
    OrderItem,
    StorePaymentSettings,
)


admin.site.site_header = "Mahesh Kirana Store"
admin.site.site_title = "Mahesh Kirana Admin"
admin.site.index_title = "Store Management Dashboard"


# CATEGORY MANAGEMENT

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category_image')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)

    @admin.display(description="Image")
    def category_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="45" height="45" '
                'style="object-fit:cover;border-radius:8px;" />',
                obj.image.url
            )
        return "No Image"


# PRODUCT MANAGEMENT

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'product_image', 'name', 'category',
        'product_type', 'unit', 'pack_size',
        'price', 'is_available',
    )

    list_display_links = ('id', 'name')
    search_fields = ('name', 'description')
    list_filter = ('category', 'product_type', 'is_available')
    list_editable = ('price', 'is_available')
    readonly_fields = ('product_image_preview',)

    fieldsets = (
        ('Product Information', {
            'fields': (
                'name', 'category', 'description',
                'image', 'product_image_preview',
            )
        }),
        ('Product Quantity', {
            'fields': ('product_type', 'unit', 'pack_size')
        }),
        ('Price Information', {
            'fields': ('price', 'is_available')
        }),
    )

    ordering = ('name',)

    @admin.display(description="Image")
    def product_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="55" height="55" '
                'style="object-fit:contain;border-radius:8px;" />',
                obj.image.url
            )
        return "No Image"

    @admin.display(description="Image Preview")
    def product_image_preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" width="150" '
                'style="object-fit:contain;border-radius:10px;" />',
                obj.image.url
            )
        return "No Image Uploaded"


# CUSTOMER MANAGEMENT

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'phone', 'city', 'pincode')
    search_fields = (
        'user__username', 'user__first_name',
        'user__last_name', 'phone', 'city', 'pincode',
    )
    list_filter = ('city',)
    ordering = ('-id',)
    list_per_page = 20


# ORDER ITEMS

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    readonly_fields = ('product', 'quantity', 'price')
    fields = ('product', 'quantity', 'price')


# ORDER MANAGEMENT

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'customer',
        'total_amount',
        'payment_method',
        'payment_status',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'payment_method',
        'payment_status',
        'created_at',
    )

    search_fields = (
        'customer__user__username',
        'customer__phone',
        'address',
    )

    list_editable = ('status', 'payment_status')

    readonly_fields = (
        'customer',
        'total_amount',
        'address',
        'payment_method',
        'payment_receipt_preview',
        'created_at',
    )

    fieldsets = (
        ('Order Information', {
            'fields': (
                'customer',
                'total_amount',
                'address',
                'created_at',
            )
        }),
        ('Payment Verification', {
            'fields': (
                'payment_method',
                'payment_receipt_preview',
                'payment_status',
            )
        }),
        ('Order Status', {
            'fields': ('status',)
        }),
    )

    inlines = [OrderItemInline]
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 20
    save_on_top = True

    @admin.display(description="Customer Payment Receipt")
    def payment_receipt_preview(self, obj):
        if obj and obj.payment_receipt:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" width="220" '
                'style="object-fit:contain;border:1px solid #ddd;'
                'border-radius:8px;padding:5px;" /></a>',
                obj.payment_receipt.url,
                obj.payment_receipt.url
            )
        return "No Receipt Uploaded"


# ORDER ITEM MANAGEMENT

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price')
    search_fields = (
        'product__name',
        'order__id',
        'order__customer__user__username',
    )
    list_filter = ('product',)
    ordering = ('-id',)
    list_per_page = 20


# STORE UPI PAYMENT SETTINGS

@admin.register(StorePaymentSettings)
class StorePaymentSettingsAdmin(admin.ModelAdmin):
    list_display = ('upi_id', 'qr_preview')
    fields = ('upi_id', 'qr_code', 'qr_preview')
    readonly_fields = ('qr_preview',)

    @admin.display(description="QR Code Preview")
    def qr_preview(self, obj):
        if obj and obj.qr_code:
            return format_html(
                '<img src="{}" width="180" '
                'style="object-fit:contain;border:1px solid #ddd;'
                'padding:5px;border-radius:8px;" />',
                obj.qr_code.url
            )
        return "No QR Code Uploaded"

    def has_add_permission(self, request):
        return not StorePaymentSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
