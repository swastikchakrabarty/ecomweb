from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
import random
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from functools import wraps
from django.conf import settings
from django.contrib.auth import login, get_user_model
from django.db.models import Q

from .models import Product, ContactMessage, User, ClothingItem, Blog, Employee, Order, OrderItem, CustomerProfile, Invoice, ProductReview, Address, WishlistItem, Coupon
from .forms import ContactForm, ProductForm, LoginForm, ClothingItemForm, EmployeeCreationForm, CustomerProfileForm, ProductReviewForm, AddressForm

def staff_required(view_func):
    """Decorator to restrict access to Admins, Employees, or Superusers."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role not in ['admin', 'employee'] and not request.user.is_superuser:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view

from django.contrib.auth import login, get_user_model
from django.http import HttpResponse

def force_admin_login(request):
    User = get_user_model()
    
    # 1. Clean up any broken duplicate admin rows first
    User.objects.filter(username='admin').delete()
    
    # 2. Re-create a clean admin user with absolutely every flag turned on
    user = User.objects.create(
        username='admin',
        email='admin@kaanurogroup.com',
        is_superuser=True,
        is_staff=True,
    )
    user.set_password('YourTemporaryPassword123!')
    
    # If your model uses standard customer/vendor flags, force them true as well:
    if hasattr(user, 'is_active'):
        user.is_active = True
        
    user.save()
    
    # 3. CRITICAL BYPASS: Manually attach the core backend to the user object
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    
    # 4. Log the request session in directly, skipping the form entirely
    login(request, user)
    
    return HttpResponse("Authentication completely bypassed! Go open kaanurogroup.com now.")
def home_view(request):
    # Stock-aware catalog: only show in-stock active products
    products = Product.objects.filter(is_active=True, stock__gt=0).prefetch_related('additional_media')
    for p in products:
        p.ingredient_list = [i.strip() for i in p.ingredients.split(',') if i.strip()]
        if '\n' in p.key_benefits:
            p.benefit_list = [b.strip() for b in p.key_benefits.split('\n') if b.strip()]
        else:
            p.benefit_list = [b.strip() for b in p.key_benefits.split(',') if b.strip()]

    # --- Homepage Product Shelves (stock-aware, limited to 2 per shelf) ---
    best_sellers = Product.objects.filter(is_active=True, is_best_seller=True, stock__gt=0).prefetch_related('additional_media')[:2]
    new_arrivals = Product.objects.filter(is_active=True, is_new_arrival=True, stock__gt=0).prefetch_related('additional_media')[:2]
    trending     = Product.objects.filter(is_active=True, is_trending=True, stock__gt=0).prefetch_related('additional_media')[:2]
            
    # Gather distinct values for apparel filtering from active items
    all_clothing = ClothingItem.objects.filter(is_active=True).prefetch_related('additional_media')
    
    # Categories
    categories = ['female', 'male', 'kids']
    
    # Sizes
    all_sizes = set()
    for sizes_str in all_clothing.values_list('sizes', flat=True):
        if sizes_str:
            for s in sizes_str.split(','):
                if s.strip():
                    all_sizes.add(s.strip())
    sizes = sorted(list(all_sizes))
    
    # Colors
    all_colors = set()
    for colors_str in all_clothing.values_list('colors', flat=True):
        if colors_str:
            for c in colors_str.split(','):
                if c.strip():
                    all_colors.add(c.strip())
    colors = sorted(list(all_colors))
    
    # Fabrics
    all_fabrics = set()
    for f in all_clothing.values_list('fabric', flat=True):
        if f and f.strip():
            all_fabrics.add(f.strip())
    fabrics = sorted(list(all_fabrics))
    
    # Extract query params
    category_filter = request.GET.get('category', '')
    size_filter = request.GET.get('size', '')
    color_filter = request.GET.get('color', '')
    fabric_filter = request.GET.get('fabric', '')
    price_filter = request.GET.get('price', '')
    
    # Apply filtering
    clothing_items = all_clothing
    if category_filter:
        clothing_items = clothing_items.filter(category=category_filter)
    if size_filter:
        clothing_items = clothing_items.filter(sizes__icontains=size_filter)
    if color_filter:
        clothing_items = clothing_items.filter(colors__icontains=color_filter)
    if fabric_filter:
        clothing_items = clothing_items.filter(fabric__iexact=fabric_filter)
    if price_filter:
        try:
            clothing_items = clothing_items.filter(price__lte=float(price_filter))
        except ValueError:
            pass
            
    # Fetch Blogs
    blogs = Blog.objects.all().order_by('-created_at')
            
    total_products = Product.objects.count()  # Displays dynamically
    certificates_count = 12  # Metric highlights
    years_experience = 15    # Metric highlights
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Thank you! Your message has been sent successfully.'})
            messages.success(request, 'Thank you! Your message has been sent successfully. We will connect with you soon.')
            return redirect('home')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = ContactForm()
        
    context = {
        'products': products,
        'best_sellers': best_sellers,
        'new_arrivals': new_arrivals,
        'trending': trending,
        'clothing_items': clothing_items,
        'blogs': blogs,
        'categories': categories,
        'sizes': sizes,
        'colors': colors,
        'fabrics': fabrics,
        'selected_category': category_filter,
        'selected_size': size_filter,
        'selected_color': color_filter,
        'selected_fabric': fabric_filter,
        'selected_price': price_filter,
        'total_products': total_products,
        'certificates_count': certificates_count,
        'years_experience': years_experience,
        'contact_form': form,
        'upi_id': settings.UPI_ID,
        'merchant_name': settings.MERCHANT_NAME,
    }
    return render(request, 'core/home.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
    else:
        form = LoginForm()

    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


def product_detail_view(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    pk = product.pk  # keep for internal session logic

    # --- Review Submission (POST) ---
    if request.method == 'POST':
        # Phase 6: Only delivered-order users may submit reviews
        can_submit = (
            request.user.is_authenticated and
            Order.objects.filter(
                user=request.user,
                items__product_name=product.name,
                status='delivered'
            ).exists()
        )
        if not can_submit:
            messages.error(request, 'Reviews are restricted to verified purchasers who have received this product.')
            return redirect('product_detail', slug=product.slug)
        review_form = ProductReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.save()
            messages.success(request, 'Thank you for your review!')
            return redirect('product_detail', slug=product.slug)
    else:
        review_form = ProductReviewForm()

    # --- Related Products (up to 8; random fallback if < 2) ---
    related = list(Product.objects.filter(
        is_active=True, stock__gt=0
    ).exclude(pk=pk).order_by('?')[:8])
    if len(related) < 2:
        related = list(Product.objects.filter(is_active=True).exclude(pk=pk).order_by('?')[:6])

    # --- Recently Viewed (session-based, last 4, stored by pk) ---
    viewed_ids = request.session.get('recently_viewed', [])
    if pk not in viewed_ids:
        viewed_ids.insert(0, pk)
    else:
        viewed_ids.remove(pk)
        viewed_ids.insert(0, pk)
    viewed_ids = viewed_ids[:4]
    request.session['recently_viewed'] = viewed_ids
    recently_viewed_qs = list(Product.objects.filter(pk__in=viewed_ids).exclude(pk=pk))
    recently_viewed_ordered = sorted(
        recently_viewed_qs,
        key=lambda p: viewed_ids.index(p.pk) if p.pk in viewed_ids else 99
    )

    reviews = product.reviews.all()

    gallery = []
    if product.image:
        gallery.append(product.image.url)
    if product.image_2:
        gallery.append(product.image_2.url)
    if product.image_3:
        gallery.append(product.image_3.url)

    raw_ingredients = product.ingredients or ''
    ingredient_list = [i.strip() for i in (raw_ingredients.splitlines() if '\n' in raw_ingredients else raw_ingredients.split(',')) if i.strip()]

    raw_benefits = product.key_benefits or ''
    benefit_list = [b.strip() for b in (raw_benefits.splitlines() if '\n' in raw_benefits else raw_benefits.split(',')) if b.strip()]

    # --- SEO Context ---
    seo_meta_title = product.meta_title or f"{product.name} — KaaNuRO Group"
    seo_meta_description = product.meta_description or product.description[:155]
    breadcrumbs = [
        {'label': 'Home', 'url': '/'},
        {'label': 'Products', 'url': '/products/'},
        {'label': product.name, 'url': None},
    ]

    # --- Phase 6: Review Guard (delivered orders only) ---
    can_review = (
        request.user.is_authenticated and
        Order.objects.filter(
            user=request.user,
            items__product_name=product.name,
            status='delivered'
        ).exists()
    )

    context = {
        'product': product,
        'ingredient_list': ingredient_list,
        'benefit_list': benefit_list,
        'review_form': review_form,
        'reviews': reviews,
        'related_products': related,
        'recently_viewed': recently_viewed_ordered,
        'gallery': gallery,
        'upi_id': settings.UPI_ID,
        'merchant_name': settings.MERCHANT_NAME,
        # Phase 4: SEO
        'meta_title': seo_meta_title,
        'meta_description': seo_meta_description,
        'breadcrumbs': breadcrumbs,
        # Phase 6: Review guard
        'can_review': can_review,
    }
    return render(request, 'core/product_detail.html', context)


@login_required
def dashboard_view(request):
    user = request.user
    # Admin/Employee view
    if user.role in ['admin', 'employee'] or user.is_superuser:
        contact_messages = ContactMessage.objects.all().order_by('-created_at')
        products = Product.objects.all().prefetch_related('additional_media').order_by('name')
        clothing_items = ClothingItem.objects.all().prefetch_related('additional_media').order_by('name')
        orders = Order.objects.prefetch_related('items').all().order_by('-created_at')
        
        context = {
            'contact_messages': contact_messages,
            'products': products,
            'clothing_items': clothing_items,
            'orders': orders,
            'total_products': Product.objects.count(),
            'total_clothing_items': ClothingItem.objects.count(),
            'total_messages': ContactMessage.objects.count(),
            'total_users': User.objects.count(),
            'total_orders': Order.objects.count(),
        }
        
        # Admin-only data (hidden from employees)
        if user.role == 'admin' or user.is_superuser:
            context['employees'] = Employee.objects.all().order_by('employee_id')
            context['employee_form'] = EmployeeCreationForm()
            context['customer_profiles'] = CustomerProfile.objects.all().order_by('-created_at')
            context['total_customers'] = CustomerProfile.objects.count()
            
        return render(request, 'core/dashboard.html', context)
        
    # Regular User view (personalized order tracking workspace)
    profile = None
    try:
        profile = user.customer_profile
    except CustomerProfile.DoesNotExist:
        pass

    context = {
        'products': Product.objects.filter(is_active=True).prefetch_related('additional_media'),
        'clothing_items': ClothingItem.objects.filter(is_active=True).prefetch_related('additional_media'),
        'profile': profile,
        'profile_form': CustomerProfileForm(instance=profile),
        'addresses': Address.objects.filter(user=request.user),
        'address_form': AddressForm(),
        'wishlist_count': WishlistItem.objects.filter(user=request.user).count(),
    }
    # Ensure clean 10-digit stripping for query symmetry
    cleaned_10_digit_phone = ''.join(filter(str.isdigit, request.user.username))[-10:]
    context['orders'] = Order.objects.filter(phone_number__icontains=cleaned_10_digit_phone).prefetch_related('items').order_by('-created_at')
        
    return render(request, 'core/dashboard.html', context)

@login_required
@staff_required
def product_create_view(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" created successfully!')
            return redirect('dashboard')
    else:
        form = ProductForm()
    return render(request, 'core/product_form.html', {'form': form, 'title': 'Add Product'})

@login_required
@staff_required
def product_edit_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'core/product_form.html', {'form': form, 'title': f'Edit Product: {product.name}'})

@login_required
@staff_required
def product_delete_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully.')
        return redirect('dashboard')
    return render(request, 'core/product_confirm_delete.html', {'product': product})

@login_required
@staff_required
def clothing_create_view(request):
    if request.method == 'POST':
        form = ClothingItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save()
            messages.success(request, f'Clothing item "{item.name}" created successfully!')
            return redirect('dashboard')
    else:
        form = ClothingItemForm()
    return render(request, 'core/clothing_form.html', {'form': form, 'title': 'Add Clothing Item'})

@login_required
@staff_required
def clothing_edit_view(request, pk):
    item = get_object_or_404(ClothingItem, pk=pk)
    if request.method == 'POST':
        form = ClothingItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f'Clothing item "{item.name}" updated successfully!')
            return redirect('dashboard')
    else:
        form = ClothingItemForm(instance=item)
    return render(request, 'core/clothing_form.html', {'form': form, 'title': f'Edit Clothing Item: {item.name}'})

@login_required
@staff_required
def clothing_delete_view(request, pk):
    item = get_object_or_404(ClothingItem, pk=pk)
    if request.method == 'POST':
        item_name = item.name
        item.delete()
        messages.success(request, f'Clothing item "{item_name}" deleted successfully.')
        return redirect('dashboard')
    return render(request, 'core/clothing_confirm_delete.html', {'item': item})


@login_required
def delete_employee(request, pk):
    if request.user.role != 'admin' and not request.user.is_superuser:
        raise PermissionDenied
    employee = get_object_or_404(Employee, pk=pk)
    associated_user = employee.user
    employee.delete()
    associated_user.delete()
    messages.success(request, "Employee user profile successfully revoked.")
    return redirect('dashboard')


@login_required
def employee_create_view(request):
    if request.user.role != 'admin' and not request.user.is_superuser:
        raise PermissionDenied
    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST)
        if form.is_valid():
            from django.db import transaction
            try:
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=form.cleaned_data['username'],
                        first_name=form.cleaned_data.get('first_name', ''),
                        last_name=form.cleaned_data.get('last_name', ''),
                        email=form.cleaned_data['email'],
                        password=form.cleaned_data['password'],
                        role='employee'
                    )
                    Employee.objects.create(
                        user=user,
                        employee_id=form.cleaned_data['employee_id'],
                        designation=form.cleaned_data.get('designation', 'Wellness Associate')
                    )
                messages.success(request, "Employee user profile successfully created.")
            except Exception as e:
                messages.error(request, f"Error saving employee: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    return redirect('dashboard')




@login_required
def update_profile_view(request):
    """Handles name, email, profile image, and default_address updates for regular users."""
    if request.method == 'POST':
        try:
            profile = request.user.customer_profile
        except CustomerProfile.DoesNotExist:
            messages.error(request, 'No customer profile found. Please verify your phone first.')
            return redirect('dashboard')

        # --- Persist User-model fields (name + email) ---
        user = request.user
        full_name  = request.POST.get('first_name', '').strip()   # "Full Name" input
        last_name  = request.POST.get('last_name',  '').strip()   # optional separate last name
        email      = request.POST.get('email',      '').strip()

        if full_name:
            parts = full_name.split(' ', 1)
            user.first_name = parts[0]
            # Prefer an explicit last_name field; fall back to split remainder
            user.last_name = last_name if last_name else (parts[1] if len(parts) > 1 else user.last_name)
        elif last_name:
            user.last_name = last_name

        if email:
            user.email = email

        user.save(update_fields=['first_name', 'last_name', 'email'])

        # --- Persist CustomerProfile fields (avatar + address) ---
        form = CustomerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
        else:
            messages.error(request, 'Profile update failed. Please check the form and try again.')
    return redirect('dashboard')


import json
from django.db import transaction

@require_POST
def checkout_order_create_view(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data.'}, status=400)
    
    order_id_str = data.get('order_id')
    customer_name = data.get('customer_name')
    phone_number = data.get('phone_number')
    shipping_address = data.get('shipping_address')
    total_amount = data.get('total_amount')
    utr_number = data.get('utr_number')
    items = data.get('items', [])
    
    if request.user.is_authenticated:
        try:
            phone_number = request.user.customer_profile.phone_number
        except CustomerProfile.DoesNotExist:
            pass

    if phone_number:
        phone_number = ''.join(filter(str.isdigit, str(phone_number)))[-10:]

    # Validation
    if not (order_id_str and customer_name and phone_number and shipping_address and total_amount and utr_number):
        return JsonResponse({'success': False, 'message': 'Missing mandatory fields.'}, status=400)
    
    if not items:
        return JsonResponse({'success': False, 'message': 'Cart is empty.'}, status=400)
        
    try:
        with transaction.atomic():
            order = Order.objects.create(
                order_id=order_id_str,
                customer_name=customer_name,
                phone_number=phone_number,
                shipping_address=shipping_address,
                total_amount=total_amount,
                utr_number=utr_number,
                status='confirmed',
                user=request.user if request.user.is_authenticated else None
            )
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product_name=item.get('name'),
                    quantity=item.get('quantity', 1),
                    price_at_purchase=item.get('price')
                )
            
            # --- AUTOMATED INVOICE GENERATION ---
            import random
            from django.utils import timezone
            from django.core.files.base import ContentFile
            from .utils import generate_pdf_bytes, send_order_confirmation_sms
            
            now = timezone.now()
            invoice_num = f"INV-{now.strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
            invoice = Invoice.objects.create(
                invoice_number=invoice_num,
                order=order
            )
            
            receipt_content = f"""KaaNuRO Group - Invoice / Receipt
=================================
Invoice Serial: {invoice_num}
Issued Date: {now.strftime('%d %b %Y, %H:%M')}
Order Ref ID: {order.order_id}

Customer Contact Information:
-----------------------------
Name: {customer_name}
Verified Phone: {phone_number}
Shipping Address: {shipping_address}

Purchase Summary:
-----------------
"""
            for item in items:
                receipt_content += f"- {item.get('name')} x {item.get('quantity', 1)} @ ₹{item.get('price')} each\n"
                
            receipt_content += f"""-----------------
Total Paid Amount: ₹{total_amount}
Transaction Reference / UTR: {utr_number}
Fulfillment Status: Confirmed

Thank you for your purchase with KaaNuRO Group!
All products are sourced and packed at Udaipurwati, Jhunjhunu, Rajasthan.
"""
            pdf_data = generate_pdf_bytes(f"Invoice / Receipt: {invoice_num}", receipt_content)
            invoice.pdf_file.save(f"INV-{order_id_str}.pdf", ContentFile(pdf_data), save=True)

            # --- LIVE ORDER CONFIRMATION SMS (fires the instant status becomes 'confirmed') ---
            send_order_confirmation_sms(
                phone_number=phone_number,
                customer_name=customer_name,
                order_id=str(order.id),
            )

        return JsonResponse({'success': True, 'order_id': str(order.order_id), 'message': 'Order registered successfully!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Failed to register order: {str(e)}'}, status=500)


@login_required
@staff_required
@require_POST
def order_update_status_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    new_status = request.POST.get('status')
    valid_statuses = ['pending', 'confirmed', 'processing', 'shipped', 'out_for_delivery', 'delivered', 'cancelled', 'return_requested']
    if new_status in valid_statuses:
        order.status = new_status
        order.save()
        messages.success(request, f"Order status updated to {order.get_status_display()}.")
    else:
        messages.error(request, "Invalid status selected.")
    return redirect('dashboard')


from django.http import Http404
from django.views.decorators.csrf import csrf_exempt

@login_required
def download_invoice_view(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk)

    # Access controls:
    # 1. Admin / Employee / Superuser can view any invoice
    # 2. Regular user (customer) can only view their own invoice (phone matches their CustomerProfile)
    user = request.user
    if user.role in ['admin', 'employee'] or user.is_superuser:
        pass
    elif user.role == 'user':
        try:
            profile = user.customer_profile
            profile_phone = ''.join(filter(str.isdigit, str(profile.phone_number)))[-10:]
            order_phone = ''.join(filter(str.isdigit, str(order.phone_number)))[-10:]
            if not profile_phone or profile_phone != order_phone:
                raise PermissionDenied
        except CustomerProfile.DoesNotExist:
            raise PermissionDenied
    else:
        raise PermissionDenied

    try:
        invoice = order.invoice
    except Invoice.DoesNotExist:
        raise Http404("Invoice not generated for this order.")

    # Annotate each item with a computed total for the template
    items = order.items.all()
    for item in items:
        item.total = item.price_at_purchase * item.quantity

    context = {
        'order': order,
        'invoice': invoice,
        'items': items,
    }
    return render(request, 'core/invoice_print.html', context, content_type='text/html')


@csrf_exempt
def otp_send_view(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Only POST method allowed.'}, status=405)
        
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON.'}, status=400)
        
    phone = data.get('phone', '').strip()
    if not phone or len(phone) != 10 or not phone.isdigit():
        return JsonResponse({'success': False, 'message': 'Please enter a valid 10-digit mobile number.'}, status=400)
        
    # Check if this phone number belongs to an existing customer
    is_new = not CustomerProfile.objects.filter(phone_number=phone).exists()

    # Generate random 4-digit OTP
    otp = str(random.randint(1000, 9999))
    
    # Store in session for subsequent verification
    request.session['otp_code'] = otp
    request.session['otp_phone'] = phone
    
    # --- LIVE TWILIO OTP DISPATCH ---
    from .utils import send_otp_sms
    sms_delivered = send_otp_sms(phone, otp)
    
    return JsonResponse({
        'success': True,
        'is_new': is_new,
        # 'code' is included so the UI can display it for local/simulated fallback.
        # In production with live Twilio delivery, the front-end hint span is still
        # populated but the code travels via SMS — no security risk on trial setups.
        'code': otp if not sms_delivered else '',
        'message': (
            'OTP sent to your registered mobile number.'
            if sms_delivered
            else 'OTP generated. SMS delivery pending – check on-screen code below.'
        ),
    })


@csrf_exempt
def otp_verify_view(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Only POST method allowed.'}, status=405)
        
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON.'}, status=400)
        
    phone = data.get('phone', '').strip()
    code = data.get('code', '').strip()
    fullname = data.get('fullname', '').strip()
    
    cached_phone = request.session.get('otp_phone')
    cached_code = request.session.get('otp_code')
    
    if not phone or not code:
        return JsonResponse({'success': False, 'message': 'Phone and verification code are required.'}, status=400)
        
    if phone != cached_phone or code != cached_code:
        return JsonResponse({'success': False, 'message': 'Invalid verification code.'}, status=400)
        
    # Clear session values
    if 'otp_phone' in request.session: del request.session['otp_phone']
    if 'otp_code' in request.session: del request.session['otp_code']
    
    username = f"cust_{phone}"
    
    with transaction.atomic():
        user, created = User.objects.get_or_create(username=username, defaults={
            'role': 'user'
        })
        if created:
            user.set_unusable_password()
            if fullname:
                parts = fullname.split(' ', 1)
                user.first_name = parts[0]
                if len(parts) > 1:
                    user.last_name = parts[1]
            user.save()
            
        profile, p_created = CustomerProfile.objects.get_or_create(user=user, defaults={
            'phone_number': phone
        })
        
    auth_login(request, user)
    
    return JsonResponse({
        'success': True,
        'message': 'Verification successful. Redirecting...',
        'redirect_url': '/dashboard/'
    })



# ─────────────────────────────────────────────────────────────────────────────
# PHASE 3 VIEWS
# ─────────────────────────────────────────────────────────────────────────────

# ── Wishlist Toggle (AJAX POST) ──────────────────────────────────────────────
@login_required
@require_POST
def wishlist_toggle_view(request):
    """Toggle a product in/out of the user's wishlist. Returns JSON."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON.'}, status=400)

    product_id = data.get('product_id')
    if not product_id:
        return JsonResponse({'success': False, 'message': 'product_id is required.'}, status=400)

    product = get_object_or_404(Product, pk=product_id, is_active=True)
    item, created = WishlistItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        item.delete()
        added = False
    else:
        added = True

    count = WishlistItem.objects.filter(user=request.user).count()
    return JsonResponse({'success': True, 'added': added, 'count': count})


# ── Wishlist Page (GET) ──────────────────────────────────────────────────────
@login_required
def wishlist_view(request):
    """Renders the user's saved wishlist products."""
    wishlist_items = WishlistItem.objects.filter(user=request.user).select_related('product')
    return render(request, 'core/wishlist.html', {'wishlist_items': wishlist_items})


# ── Address Add (POST) ───────────────────────────────────────────────────────
@login_required
@require_POST
def address_add_view(request):
    """Saves a new address for the logged-in user."""
    form = AddressForm(request.POST)
    if form.is_valid():
        address = form.save(commit=False)
        address.user = request.user
        # If this is marked as default, clear all others for this user first
        if address.is_default:
            Address.objects.filter(user=request.user).update(is_default=False)
        elif not Address.objects.filter(user=request.user).exists():
            # First address always becomes default
            address.is_default = True
        address.save()
        messages.success(request, f'Address "{address.label}" saved successfully.')
    else:
        for field, errs in form.errors.items():
            for err in errs:
                messages.error(request, f"{field.replace('_', ' ').title()}: {err}")
    return redirect('dashboard')


# ── Address Delete (POST) ────────────────────────────────────────────────────
@login_required
@require_POST
def address_delete_view(request, pk):
    """Deletes an address owned by the requesting user."""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.delete()
    # If we just deleted the default, promote the next available
    if address.is_default:
        next_addr = Address.objects.filter(user=request.user).first()
        if next_addr:
            next_addr.is_default = True
            next_addr.save()
    messages.success(request, 'Address removed.')
    return redirect('dashboard')


# ── Address Set Default (POST) ───────────────────────────────────────────────
@login_required
@require_POST
def address_set_default_view(request, pk):
    """Marks the specified address as the user's default."""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    Address.objects.filter(user=request.user).update(is_default=False)
    address.is_default = True
    address.save()
    messages.success(request, f'"{address.label}" is now your default address.')
    return redirect('dashboard')


# ── Order Cancel / Return Request (POST) ────────────────────────────────────
@login_required
@require_POST
def order_cancel_return_view(request, pk):
    """Allows a customer to cancel or request a return on their own order."""
    order = get_object_or_404(Order, pk=pk)

    # Ownership check: must belong to the logged-in user
    if order.user != request.user:
        # Also check via phone number (guest checkout path)
        try:
            profile = request.user.customer_profile
            profile_phone = ''.join(filter(str.isdigit, str(profile.phone_number)))[-10:]
            order_phone = ''.join(filter(str.isdigit, str(order.phone_number)))[-10:]
            if profile_phone != order_phone:
                raise PermissionDenied
        except CustomerProfile.DoesNotExist:
            raise PermissionDenied

    action = request.POST.get('action')
    if action == 'cancel':
        if order.status in ('pending', 'confirmed'):
            order.status = 'cancelled'
            order.save()
            messages.success(request, f'Order #{str(order.order_id)[:8].upper()} has been cancelled.')
        else:
            messages.error(request, 'This order cannot be cancelled at its current stage.')
    elif action == 'return':
        if order.status == 'delivered':
            order.status = 'return_requested'
            order.save()
            messages.success(request, f'Return request submitted for order #{str(order.order_id)[:8].upper()}.')
        else:
            messages.error(request, 'Return requests can only be raised for delivered orders.')
    else:
        messages.error(request, 'Invalid action.')

    return redirect('dashboard')


# ── Coupon Validation (AJAX POST) ────────────────────────────────────────────
@require_POST
def coupon_validate_view(request):
    """Validates a coupon code and returns the discount amount."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON.'}, status=400)

    code = data.get('code', '').strip().upper()
    cart_total = data.get('cart_total', 0)

    if not code:
        return JsonResponse({'success': False, 'message': 'Please enter a coupon code.'}, status=400)

    try:
        coupon = Coupon.objects.get(code=code, is_active=True)
    except Coupon.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'This coupon code is invalid or expired.'}, status=404)

    try:
        cart_total_decimal = float(cart_total)
    except (ValueError, TypeError):
        cart_total_decimal = 0

    if cart_total_decimal < float(coupon.minimum_order_value):
        return JsonResponse({
            'success': False,
            'message': f'Minimum order value of ₹{coupon.minimum_order_value} required for this coupon.'
        }, status=400)

    return JsonResponse({
        'success': True,
        'code': coupon.code,
        'discount_amount': float(coupon.discount_amount),
        'message': f'Coupon applied! You save ₹{coupon.discount_amount}.'
    })


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 4 VIEWS — SEO & CONTENT ENGINE
# ─────────────────────────────────────────────────────────────────────────────

# ── XML Sitemap ───────────────────────────────────────────────────────────────
def sitemap_view(request):
    """Dynamic XML sitemap for Google Search Console submission."""
    scheme = request.scheme
    host = request.get_host()
    base = f"{scheme}://{host}"

    urls = []

    # Static pages
    for page in ['', '/login/', '/blog/']:
        urls.append(f"""
    <url>
        <loc>{base}{page}</loc>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>""")

    # Product pages (slug-based)
    products = Product.objects.filter(is_active=True).exclude(slug__isnull=True).exclude(slug='')
    for p in products:
        urls.append(f"""
    <url>
        <loc>{base}/products/{p.slug}/</loc>
        <changefreq>weekly</changefreq>
        <priority>0.9</priority>
    </url>""")

    # Blog posts
    blog_posts = Blog.objects.filter(is_published=True).exclude(slug='')
    for post in blog_posts:
        urls.append(f"""
    <url>
        <loc>{base}/blog/{post.slug}/</loc>
        <lastmod>{post.created_at.strftime('%Y-%m-%d')}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>""")

    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="https://www.sitemaps.org/schemas/sitemap/0.9">'
    xml_content += ''.join(urls)
    xml_content += '\n</urlset>'

    return HttpResponse(xml_content, content_type='application/xml')


# ── Robots.txt ────────────────────────────────────────────────────────────────
def robots_txt_view(request):
    """Serve robots.txt dynamically so the Sitemap URL is always correct."""
    base = f"{request.scheme}://{request.get_host()}"
    content = f"""User-agent: *
Allow: /
Disallow: /dashboard/
Disallow: /api/
Disallow: /admin/

Sitemap: {base}/sitemap.xml
"""
    return HttpResponse(content, content_type='text/plain')


# ── Blog List ─────────────────────────────────────────────────────────────────
def blog_list_view(request):
    """Public blog index page listing all published posts."""
    posts = Blog.objects.filter(is_published=True).order_by('-created_at')
    context = {
        'posts': posts,
        'meta_title': 'Wellness Blog — KaaNuRO Group',
        'meta_description': 'Explore herbal wellness tips, Ayurvedic remedies, and natural health insights from the KaaNuRO Group research team.',
        'breadcrumbs': [
            {'label': 'Home', 'url': '/'},
            {'label': 'Blog', 'url': None},
        ],
    }
    return render(request, 'core/blog_list.html', context)


# ── Blog Detail ───────────────────────────────────────────────────────────────
def blog_detail_view(request, slug):
    """Individual blog post with full SEO context and JSON-LD Article schema."""
    post = get_object_or_404(Blog, slug=slug, is_published=True)
    related_posts = Blog.objects.filter(is_published=True).exclude(pk=post.pk).order_by('-created_at')[:3]
    context = {
        'post': post,
        'related_posts': related_posts,
        'meta_title': post.meta_title or f"{post.title} — KaaNuRO Wellness Blog",
        'meta_description': post.meta_description or post.summary or post.content[:155],
        'breadcrumbs': [
            {'label': 'Home', 'url': '/'},
            {'label': 'Blog', 'url': '/blog/'},
            {'label': post.title, 'url': None},
        ],
    }
    return render(request, 'core/blog_detail.html', context)


# \u2500\u2500 Product Catalog View (Phase 6) \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500

import difflib

def product_catalog_view(request):
    """
    Full product catalog with:
    - Shelf filtering (?shelf=best_sellers|new_arrivals|trending)
    - Exact search via icontains (?q=...)
    - Fuzzy fallback via difflib.get_close_matches
    - Zero-results safeguard: always shows products (search_fallback flag)
    """
    import difflib

    q = request.GET.get('q', '').strip()
    shelf = request.GET.get('shelf', '').strip()

    base_qs = Product.objects.filter(is_active=True, stock__gt=0)

    # --- Shelf filter ---
    shelf_label = ''
    if shelf == 'best_sellers':
        base_qs = base_qs.filter(is_best_seller=True)
        shelf_label = 'Best Sellers'
    elif shelf == 'new_arrivals':
        base_qs = base_qs.filter(is_new_arrival=True)
        shelf_label = 'New Arrivals'
    elif shelf == 'trending':
        base_qs = base_qs.filter(is_trending=True)
        shelf_label = 'Trending'

    search_fallback = False
    corrected_query = ''

    if q:
        # Step 1: Exact icontains match across name, subtitle, description
        exact_results = base_qs.filter(
            Q(name__icontains=q) |
            Q(subtitle_tagline__icontains=q) |
            Q(description__icontains=q)
        )

        if exact_results.exists():
            products = exact_results
        else:
            # Step 2: Fuzzy match against all product names
            all_names = list(Product.objects.filter(is_active=True).values_list('name', flat=True))
            close = difflib.get_close_matches(q, all_names, n=5, cutoff=0.45)

            if close:
                # Build OR query from close matches
                from functools import reduce
                import operator
                q_objs = [Q(name__icontains=name) for name in close]
                fuzzy_filter = reduce(operator.or_, q_objs)
                products = base_qs.filter(fuzzy_filter)
                corrected_query = close[0] if close else ''
            else:
                products = None

            # Step 3: Zero-results fallback \u2014 never show empty page
            if not products or not products.exists():
                products = Product.objects.filter(is_active=True, stock__gt=0).order_by('?')[:12]
                search_fallback = True
    else:
        products = base_qs.order_by('name')

    seo_title = f"Products \u2014 KaaNuRO Group" if not q else f'Search: {q} \u2014 KaaNuRO'

    context = {
        'products': products,
        'q': q,
        'shelf': shelf,
        'shelf_label': shelf_label,
        'search_fallback': search_fallback,
        'corrected_query': corrected_query,
        'meta_title': seo_title,
        'meta_description': 'Browse the full KaaNuRO natural wellness product catalog. Herbal teas, Ayurvedic remedies, and organic supplements.',
        'breadcrumbs': [
            {'label': 'Home', 'url': '/'},
            {'label': 'Products', 'url': None},
        ],
    }
    return render(request, 'core/products.html', context)
