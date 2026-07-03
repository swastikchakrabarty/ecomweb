from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Employee, Product, ContactMessage, ClothingItem, Blog, ProductMedia, Order, OrderItem, CustomerProfile, Invoice, ProductReview

class ProductMediaInline(admin.TabularInline):
    model = ProductMedia
    extra = 1
    fk_name = 'product'

class ProductReviewInline(admin.TabularInline):
    model = ProductReview
    extra = 0
    readonly_fields = ('created_at',)

class ClothingItemMediaInline(admin.TabularInline):
    model = ProductMedia
    extra = 1
    fk_name = 'clothing_item'

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductMediaInline, ProductReviewInline]
    list_display = ('name', 'price', 'stock', 'is_active', 'is_best_seller', 'is_new_arrival', 'is_trending')
    search_fields = ('name', 'subtitle_tagline')
    list_filter = ('is_active', 'is_best_seller', 'is_new_arrival', 'is_trending')
    list_editable = ('is_active', 'is_best_seller', 'is_new_arrival', 'is_trending')

class ClothingItemAdmin(admin.ModelAdmin):
    inlines = [ClothingItemMediaInline]
    list_display = ('name', 'category', 'price', 'is_active')
    search_fields = ('name', 'fabric')
    list_filter = ('category', 'is_active')

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Role Info', {'fields': ('role',)}),
    )
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ('order_id', 'customer_name', 'phone_number', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer_name', 'phone_number', 'utr_number', 'order_id')
    readonly_fields = ('order_id', 'created_at')

class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'user', 'created_at')
    search_fields = ('phone_number', 'user__username')

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'order', 'issued_at')
    search_fields = ('invoice_number', 'order__order_id')

admin.site.register(User, CustomUserAdmin)
admin.site.register(Employee)
admin.site.register(ContactMessage)
admin.site.register(Blog)
admin.site.register(Product, ProductAdmin)
admin.site.register(ClothingItem, ClothingItemAdmin)
admin.site.register(ProductMedia)
admin.site.register(ProductReview)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(CustomerProfile, CustomerProfileAdmin)
admin.site.register(Invoice, InvoiceAdmin)


