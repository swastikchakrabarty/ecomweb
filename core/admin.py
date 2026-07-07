"""
KaaNuRO Group — Django Admin Control Dashboard
Phase 5: Polished, scannable, and operationally efficient admin grid views.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import (
    User, Employee,
    Product, ProductMedia, ProductReview,
    ContactMessage,
    Blog,
    Order, OrderItem,
    CustomerProfile, Invoice,
    Address, WishlistItem, Coupon,
    LegalDocument,
)


# ─────────────────────────────────────────────────────────────────────────────
# INLINE DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────

class ProductMediaInline(admin.TabularInline):
    model = ProductMedia
    extra = 1
    fk_name = 'product'
    fields = ('media_type', 'file', 'embed_url')



class ProductReviewInline(admin.TabularInline):
    model = ProductReview
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('user_name', 'rating', 'comment', 'created_at')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'price_at_purchase', 'quantity')
    fields = ('product_name', 'quantity', 'price_at_purchase')


# ─────────────────────────────────────────────────────────────────────────────
# USER & EMPLOYEE
# ─────────────────────────────────────────────────────────────────────────────

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('KaaNuRO Role', {'fields': ('role',)}),
    )
    list_display = ('username', 'email', 'get_full_name', 'role', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'designation', 'joined_date')
    search_fields = ('user__username', 'employee_id', 'designation')
    ordering = ('-joined_date',)


# ─────────────────────────────────────────────────────────────────────────────
# PRODUCT CONTROL PORTAL
# ─────────────────────────────────────────────────────────────────────────────

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductMediaInline, ProductReviewInline]

    # Phase 5: Enhanced grid columns
    list_display = (
        'name', 'price', 'discount_percentage', 'current_price_display', 'stock', 'stock_status_badge',
        'is_best_seller', 'is_new_arrival', 'is_trending', 'is_active', 'slug',
    )
    list_editable = ('price', 'discount_percentage', 'stock', 'is_best_seller', 'is_new_arrival', 'is_trending', 'is_active')
    list_filter = ('is_active', 'is_best_seller', 'is_new_arrival', 'is_trending')
    search_fields = ('name', 'description', 'slug', 'subtitle_tagline')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)

    fieldsets = (
        ('Core Identity', {
            'fields': ('name', 'slug', 'subtitle_tagline', 'description', 'total_quantity_info')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'discount_percentage', 'stock', 'is_active')
        }),
        ('Homepage Shelves', {
            'fields': ('is_best_seller', 'is_new_arrival', 'is_trending'),
            'description': 'Control which promotional shelves this product appears on.'
        }),
        ('Media', {
            'fields': ('image', 'image_2', 'image_3'),
        }),
        ('Product Details', {
            'fields': ('ingredients', 'key_benefits', 'directions_for_use'),
            'classes': ('collapse',),
        }),
        ('SEO & Metadata', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Stock Status')
    def stock_status_badge(self, obj):
        if obj.stock == 0:
            return mark_safe(
                '<span style="color:#dc2626;font-weight:bold;font-size:11px;">● Out of Stock</span>'
            )
        elif obj.stock <= 10:
            return format_html(
                '<span style="color:#d97706;font-weight:bold;font-size:11px;">● Low ({})</span>',
                obj.stock
            )
        return format_html(
            '<span style="color:#16a34a;font-weight:bold;font-size:11px;">● In Stock ({})</span>',
            obj.stock
        )

    @admin.display(description='Active Price (₹)')
    def current_price_display(self, obj):
        if obj.discount_percentage > 0:
            return format_html(
                '<span style="color:#16a34a;font-weight:bold;">₹{}</span> '
                '<span style="color:#dc2626;font-size:10px;text-decoration:line-through;">₹{}</span>',
                obj.current_price, obj.price
            )
        return format_html('<span style="color:#6b7280;">₹{}</span>', obj.price)


@admin.register(ProductMedia)
class ProductMediaAdmin(admin.ModelAdmin):
    list_display = ('media_type', 'product')
    list_filter = ('media_type',)


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user_name', 'rating', 'rating_stars', 'created_at')
    list_filter = ('rating',)
    search_fields = ('user_name', 'comment', 'product__name')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    @admin.display(description='Stars')
    def rating_stars(self, obj):
        filled = '★' * obj.rating
        empty = '☆' * (5 - obj.rating)
        return format_html(
            '<span style="color:#D4AF37;font-size:14px;">{}</span>'
            '<span style="color:#d1d5db;font-size:14px;">{}</span>',
            filled, empty
        )



# ─────────────────────────────────────────────────────────────────────────────
# ORDER TRACKING & OPERATIONS
# ─────────────────────────────────────────────────────────────────────────────

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]

    list_display = (
        'short_order_id', 'user', 'customer_name', 'phone_number',
        'total_amount', 'status_badge', 'status', 'utr_number', 'created_at',
    )
    list_editable = ('status',)
    list_filter = ('status', 'created_at')
    search_fields = (
        'customer_name', 'phone_number', 'utr_number',
        'shipping_address', 'user__username',
    )
    readonly_fields = ('order_id', 'created_at')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Order Identity', {
            'fields': ('order_id', 'user', 'created_at')
        }),
        ('Customer', {
            'fields': ('customer_name', 'phone_number', 'shipping_address')
        }),
        ('Financial', {
            'fields': ('total_amount', 'utr_number')
        }),
        ('Fulfilment', {
            'fields': ('status',)
        }),
    )

    @admin.display(description='Order ID')
    def short_order_id(self, obj):
        return str(obj.order_id)[:8].upper()

    @admin.display(description='Status')
    def status_badge(self, obj):
        colour_map = {
            'pending':          ('#d97706', '#fffbeb'),
            'confirmed':        ('#4f46e5', '#eef2ff'),
            'processing':       ('#2563eb', '#eff6ff'),
            'shipped':          ('#0891b2', '#ecfeff'),
            'out_for_delivery': ('#16a34a', '#f0fdf4'),
            'delivered':        ('#15803d', '#dcfce7'),
            'cancelled':        ('#dc2626', '#fef2f2'),
            'return_requested': ('#ea580c', '#fff7ed'),
        }
        colour, bg = colour_map.get(obj.status, ('#6b7280', '#f9fafb'))
        label = obj.get_status_display()
        return format_html(
            '<span style="background:{};color:{};padding:2px 8px;border-radius:999px;'
            'font-size:10px;font-weight:700;white-space:nowrap;">{}</span>',
            bg, colour, label
        )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'quantity', 'price_at_purchase')
    search_fields = ('product_name', 'order__customer_name')


# ─────────────────────────────────────────────────────────────────────────────
# CUSTOMER DATA PORTALS
# ─────────────────────────────────────────────────────────────────────────────

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'wallet_balance', 'created_at')
    search_fields = ('phone_number', 'user__username', 'user__email')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'label', 'city', 'state', 'postal_code', 'phone_number', 'is_default')
    list_filter = ('state', 'is_default')
    search_fields = ('user__username', 'city', 'state', 'address_line_1', 'phone_number')
    list_editable = ('is_default',)


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'product__name')
    readonly_fields = ('added_at',)


# ─────────────────────────────────────────────────────────────────────────────
# COUPON ENGINE
# ─────────────────────────────────────────────────────────────────────────────

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_amount', 'minimum_order_value', 'is_active', 'created_at')
    list_editable = ('discount_amount', 'minimum_order_value', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('code',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


# ─────────────────────────────────────────────────────────────────────────────
# BLOG ENGINE
# ─────────────────────────────────────────────────────────────────────────────

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'slug', 'is_published', 'created_at')
    list_editable = ('is_published',)
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'content', 'summary', 'author')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'author', 'summary', 'content')
        }),
        ('Media', {
            'fields': ('image', 'featured_image'),
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',),
        }),
        ('Publishing', {
            'fields': ('is_published', 'created_at'),
        }),
    )


# ─────────────────────────────────────────────────────────────────────────────
# SUPPORTING MODELS
# ─────────────────────────────────────────────────────────────────────────────

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at')
    search_fields = ('name', 'email', 'phone', 'message')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'order', 'issued_at')
    search_fields = ('invoice_number', 'order__customer_name')
    readonly_fields = ('issued_at',)
    ordering = ('-issued_at',)


@admin.register(LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'doc_type', 'last_updated')
    list_filter = ('doc_type',)
    search_fields = ('title', 'content')

