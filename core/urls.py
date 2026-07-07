from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/products/add/', views.product_create_view, name='product_create'),
    path('dashboard/products/<int:pk>/edit/', views.product_edit_view, name='product_edit'),
    path('dashboard/products/<int:pk>/delete/', views.product_delete_view, name='product_delete'),

    path('dashboard/employees/add/', views.employee_create_view, name='employee_create'),
    path('dashboard/employees/<int:pk>/delete/', views.delete_employee, name='employee_delete'),
    path('api/orders/create/', views.checkout_order_create_view, name='checkout_order_create'),
    path('dashboard/orders/<int:pk>/status/', views.order_update_status_view, name='order_update_status'),
    path('api/otp/send/', views.otp_send_view, name='otp_send'),
    path('api/otp/verify/', views.otp_verify_view, name='otp_verify'),
    path('orders/<int:order_pk>/invoice/', views.download_invoice_view, name='download_invoice'),
    path('dashboard/profile/update/', views.update_profile_view, name='update_profile'),

    # ── Phase 6: Product Catalog (must be before slug route) ──────────────────
    path('products/', views.product_catalog_view, name='product_catalog'),

    # ── Phase 4: SEO slug-based product detail ────────────────────────────────
    path('products/<slug:slug>/', views.product_detail_view, name='product_detail'),

    # ── Phase 3: Wishlist ─────────────────────────────────────────────────────
    path('api/wishlist/toggle/', views.toggle_wishlist_view, name='wishlist_toggle'),
    path('wishlist/', views.wishlist_view, name='wishlist_view'),

    # ── Phase 3: Address Management ───────────────────────────────────────────
    path('dashboard/addresses/add/', views.address_add_view, name='address_add'),
    path('dashboard/addresses/<int:pk>/delete/', views.address_delete_view, name='address_delete'),
    path('dashboard/addresses/<int:pk>/default/', views.address_set_default_view, name='address_set_default'),

    # ── Phase 3: Order Actions ────────────────────────────────────────────────
    path('orders/<int:pk>/action/', views.order_cancel_return_view, name='order_cancel_return'),

    # ── Phase 3: Coupon Engine ────────────────────────────────────────────────
    path('api/coupons/validate/', views.coupon_validate_view, name='coupon_validate'),

    # ── Phase 4: SEO Infrastructure ───────────────────────────────────────────
    path('sitemap.xml', views.sitemap_view, name='sitemap'),
    path('robots.txt', views.robots_txt_view, name='robots_txt'),

    # ── Phase 4: Blog Engine ──────────────────────────────────────────────────
    path('blog/', views.blog_list_view, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail_view, name='blog_detail'),

    # ── Legal Documents ───────────────────────────────────────────────────────
    path('legal/<slug:doc_type>/', views.legal_document_view, name='legal_document'),
]
