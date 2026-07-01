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
    path('dashboard/clothing/add/', views.clothing_create_view, name='clothing_create'),
    path('dashboard/clothing/<int:pk>/edit/', views.clothing_edit_view, name='clothing_edit'),
    path('dashboard/clothing/<int:pk>/delete/', views.clothing_delete_view, name='clothing_delete'),
    path('dashboard/employees/add/', views.employee_create_view, name='employee_create'),
    path('dashboard/employees/<int:pk>/delete/', views.delete_employee, name='employee_delete'),
    path('api/orders/create/', views.checkout_order_create_view, name='checkout_order_create'),
    path('dashboard/orders/<int:pk>/status/', views.order_update_status_view, name='order_update_status'),
    path('api/otp/send/', views.otp_send_view, name='otp_send'),
    path('api/otp/verify/', views.otp_verify_view, name='otp_verify'),
    path('orders/<int:order_pk>/invoice/', views.download_invoice_view, name='download_invoice'),
    path('dashboard/profile/update/', views.update_profile_view, name='update_profile'),
]

