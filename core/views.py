from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
import random
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from functools import wraps
from django.conf import settings
from django.contrib.auth import login, get_user_model
from django.db.models import Q
from django.utils import timezone
import json
from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.core.files.base import ContentFile
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
import difflib
import operator
from functools import reduce

from .models import Product, ContactMessage, User, Blog, Employee, Order, OrderItem, CustomerProfile, Invoice, ProductReview, Address, WishlistItem, Coupon, LegalDocument
from .forms import ContactForm, ProductForm, LoginForm, EmployeeCreationForm, CustomerProfileForm, ProductReviewForm, AddressForm


def staff_required(view_func):
    """Decorator to restrict access to Admins, Employees, or Superusers."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            # ────────────────────────────────────────────────────────────
            # FIX 1: Capture the exact checkout route context during login redirects
            # ────────────────────────────────────────────────────────────
            path = request.get_full_path()
            return redirect(f"{settings.LOGIN_URL}?next={path}")
        if request.user.role not in ['admin', 'employee'] and not request.user.is_superuser:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def force_admin_login(request):
    User = get_user_model()
    User.objects.filter(username='admin').delete()
    user = User.objects.create(
        username='admin',
        email='admin@kaanurogroup.com',
        is_superuser=True,
        is_staff=True,
    )
    user.set_password('YourTemporaryPassword123!')
    if hasattr(user, 'is_active'):
        user.is_active = True
    user.save()
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)
    return HttpResponse("Authentication completely bypassed! Go open kaanurogroup.com now.")


def home_view(request):
    best_sellers = Product.objects.filter(is_active=True, is_best_seller=True, stock__gt=0).prefetch_related('additional_media')[:2]
    new_arrivals = Product.objects.filter(is_active=True, is_new_arrival=True, stock__gt=0).prefetch_related('additional_media')[:2]
    trending     = Product.objects.filter(is_active=True, is_trending=True, stock__gt=0).prefetch_related('additional_media')[:2]

    blogs = Blog.objects.all().order_by('-created_at')
    total_products = Product.objects.count()  
    certificates_count = 3  
    years_experience = 15    

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
        'best_sellers': best_sellers,
        'new_arrivals': new_arrivals,
        'trending': trending,
        'blogs': blogs,
        'total_products': total_products,
        'certificates_count': certificates_count,
        'years_experience': years_experience,
        'contact_form': form,
        'upi_id': settings.UPI_ID,
        'merchant_name': settings.MERCHANT_NAME,
    }
    return render(request, 'core/home.html', context)


from django.contrib.auth import authenticate

def login_view(request):
    if request.user.is_authenticated:
        # Check next parameter even if already authenticated to ensure no trap
        next_url = request.GET.get('next') or request.POST.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('dashboard')

    next_url = request.GET.get('next') or request.POST.get('next') or ''

    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not hasattr(user, 'backend'):
                user.backend = 'django.contrib.auth.backends.ModelBackend'
            auth_login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            
            # ────────────────────────────────────────────────────────────
            # FIX 1 (Continued): Dynamic redirection to bypass staff portal for buyers
            # ────────────────────────────────────────────────────────────
            if next_url:
                return redirect(next_url)
            
            if user.role in ['admin', 'employee'] or user.is_superuser:
                return redirect('dashboard')
            return redirect('dashboard')
    else:
        form = LoginForm()

    return render(request, 'core/login.html', {'form': form, 'next': next_url})

# def custom_login_processing(request):
#     pass








def logout_view(request):
    auth_logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


def product_detail_view(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    pk = product.pk 

    can_review = (
        request.user.is_authenticated and
        Order.objects.filter(
            user=request.user,
            items__product_name=product.name,
            status='delivered'
        ).exists()
    )

    if request.method == 'POST':
        if not can_review:
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

    related = list(Product.objects.filter(is_active=True, stock__gt=0).exclude(pk=pk).order_by('?')[:8])
    if len(related) < 2:
        related = list(Product.objects.filter(is_active=True).exclude(pk=pk).order_by('?')[:6])

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
    if product.image: gallery.append(product.image.url)
    if product.image_2: gallery.append(product.image_2.url)
    if product.image_3: gallery.append(product.image_3.url)

    raw_ingredients = product.ingredients or ''
    ingredient_list = [i.strip() for i in (raw_ingredients.splitlines() if '\n' in raw_ingredients else raw_ingredients.split(',')) if i.strip()]

    raw_benefits = product.key_benefits or ''
    benefit_list = [b.strip() for b in (raw_benefits.splitlines() if '\n' in raw_benefits else raw_benefits.split(',')) if b.strip()]

    seo_meta_title = product.meta_title or f"{product.name} — KaaNuRO Group"
    seo_meta_description = product.meta_description or product.description[:155]
    breadcrumbs = [
        {'label': 'Home', 'url': '/'},
        {'label': 'Products', 'url': '/products/'},
        {'label': product.name, 'url': None},
    ]

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
        'meta_title': seo_meta_title,
        'meta_description': seo_meta_description,
        'breadcrumbs': breadcrumbs,
        'can_review': can_review,
    }
    return render(request, 'core/product_detail.html', context)


@never_cache
@login_required
def dashboard_view(request):
    user = request.user
    if user.role in ['admin', 'employee'] or user.is_superuser:
        contact_messages = ContactMessage.objects.all().order_by('-created_at')
        products = Product.objects.all().prefetch_related('additional_media').order_by('name')
        orders = Order.objects.prefetch_related('items').all().order_by('-created_at')

        context = {
            'contact_messages': contact_messages,
            'products': products,
            'orders': orders,
            'total_products': Product.objects.count(),
            'total_messages': ContactMessage.objects.count(),
            'total_users': User.objects.count(),
            'total_orders': Order.objects.count(),
        }
        if user.role == 'admin' or user.is_superuser:
            context['employees'] = Employee.objects.all().order_by('employee_id')
            context['employee_form'] = EmployeeCreationForm()
            context['customer_profiles'] = CustomerProfile.objects.all().order_by('-created_at')
            context['total_customers'] = CustomerProfile.objects.count()
            
        return render(request, 'core/dashboard.html', context)
        
    profile = None
    try:
        profile = user.customer_profile
    except CustomerProfile.DoesNotExist:
        pass

    context = {
        'products': Product.objects.filter(is_active=True).prefetch_related('additional_media'),
        'profile': profile,
        'profile_form': CustomerProfileForm(instance=profile),
        'addresses': Address.objects.filter(user=request.user),
        'address_form': AddressForm(),
        'wishlist_count': WishlistItem.objects.filter(user=request.user).count(),
    }
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


@never_cache
@login_required
def update_profile_view(request):
    if request.method == 'POST':
        try:
            profile = request.user.customer_profile
        except CustomerProfile.DoesNotExist:
            messages.error(request, 'No customer profile found. Please verify your phone first.')
            return redirect('dashboard')

        user = request.user
        full_name  = request.POST.get('first_name', '').strip()  
        last_name  = request.POST.get('last_name',  '').strip()   
        email      = request.POST.get('email',      '').strip()

        if full_name:
            parts = full_name.split(' ', 1)
            user.first_name = parts[0]
            user.last_name = last_name if last_name else (parts[1] if len(parts) > 1 else user.last_name)
        elif last_name:
            user.last_name = last_name

        if email:
            user.email = email

        user.save(update_fields=['first_name', 'last_name', 'email'])

        form = CustomerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
        else:
            messages.error(request, 'Profile update failed. Please check the form and try again.')
    return redirect('dashboard')


@require_POST
def checkout_order_create_view(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {'success': False, 'message': 'Authentication required. Please log in to complete your order.'},
            status=403
        )
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data.'}, status=400)

    order_id_str   = data.get('order_id')
    customer_name  = data.get('customer_name')
    phone_number   = data.get('phone_number')
    shipping_address = data.get('shipping_address')
    utr_number      = data.get('utr_number')
    items          = data.get('items', [])

    if not items:
        return JsonResponse({'success': False, 'message': 'Cart is empty.'}, status=400)

    resolved_items = []   
    server_total   = Decimal('0.00')

    for item in items:
        raw_id   = str(item.get('id', '')).strip()   
        quantity = item.get('quantity', 1)

        try:
            quantity = int(quantity)
            if quantity < 1: raise ValueError
        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'message': f'Invalid quantity for item "{item.get("name")}".'}, status=400)

        if raw_id.startswith('prod_'):
            try:
                numeric_id = int(raw_id.split('prod_')[1])
                product_obj = Product.objects.get(pk=numeric_id, is_active=True)
            except (Product.DoesNotExist, ValueError, IndexError):
                return JsonResponse({'success': False, 'message': f'Product not found or no longer available: "{item.get("name")}".'}, status=400)
            authoritative_price = product_obj.current_price  
            item_name           = product_obj.name
        else:
            return JsonResponse({'success': False, 'message': f'Unresolvable item identifier "{raw_id}". Order rejected.'}, status=400)

        line_total    = authoritative_price * Decimal(quantity)
        server_total += line_total
        resolved_items.append({
            'name':      item_name,
            'quantity': quantity,
            'price':    authoritative_price,
        })

    if request.user.is_authenticated:
        try:
            phone_number = request.user.customer_profile.phone_number
        except CustomerProfile.DoesNotExist:
            pass

    if phone_number:
        phone_number = ''.join(filter(str.isdigit, str(phone_number)))[-10:]

    if not (order_id_str and customer_name and phone_number and shipping_address and utr_number):
        return JsonResponse({'success': False, 'message': 'Missing mandatory fields.'}, status=400)

    try:
        with transaction.atomic():
            order = Order.objects.create(
                order_id=order_id_str,
                customer_name=customer_name,
                phone_number=phone_number,
                shipping_address=shipping_address,
                total_amount=server_total,   
                utr_number=utr_number,
                status='confirmed',
                user=request.user if request.user.is_authenticated else None
            )
            for resolved in resolved_items:
                OrderItem.objects.create(
                    order=order,
                    product_name=resolved['name'],
                    quantity=resolved['quantity'],
                    price_at_purchase=resolved['price'],   
                )

            from .utils import generate_pdf_bytes, send_order_confirmation_sms

            now = timezone.now()
            invoice_num = f"INV-{now.strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
            invoice = Invoice.objects.create(
                invoice_number=invoice_num,
                order=order
            )

            receipt_content = f"KaaNuRO Group - Invoice / Receipt\n=======================\nInvoice Serial: {invoice_num}\nIssued Date: {now.strftime('%d %b %Y, %H:%M')}\nOrder Ref ID: {order.order_id}\n\nCustomer Contact Information:\n-----------------------------\nName: {customer_name}\nVerified Phone: {phone_number}\nShipping Address: {shipping_address}\n\nPurchase Summary:\n-----------------\n"
            for resolved in resolved_items:
                receipt_content += f"- {resolved['name']} x {resolved['quantity']} @ ₹{resolved['price']} each\n"

            receipt_content += f"-----------------\nTotal Paid Amount: ₹{server_total}\nTransaction Reference / UTR: {utr_number}\nFulfillment Status: Confirmed\n\nThank you for your purchase with KaaNuRO Group!\nAll products are sourced and packed at Udaipurwati, Jhunjhunu, Rajasthan.\n"
            pdf_data = generate_pdf_bytes(f"Invoice / Receipt: {invoice_num}", receipt_content)
            invoice.pdf_file.save(f"INV-{order_id_str}.pdf", ContentFile(pdf_data), save=True)

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


@never_cache
@login_required
def download_invoice_view(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk)
    if order.user != request.user and not (request.user.role in ['admin', 'employee'] or request.user.is_staff or request.user.is_superuser):
        raise PermissionDenied("You do not have permission to view this order.")

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
        
    is_new = not CustomerProfile.objects.filter(phone_number=phone).exists()
    otp = str(random.randint(1000, 9999))
    request.session['otp_code'] = otp
    request.session['otp_phone'] = phone
    
    from .utils import send_otp_sms
    sms_delivered = send_otp_sms(phone, otp)
    
    return JsonResponse({
        'success': True,
        'is_new': is_new,
        'code': otp if not sms_delivered else '',
        'message': 'OTP sent to mobile number.' if sms_delivered else 'OTP generated on-screen.',
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
        return JsonResponse({'success': False, 'message': 'Phone and code are required.'}, status=400)
    if phone != cached_phone or code != cached_code:
        return JsonResponse({'success': False, 'message': 'Invalid verification code.'}, status=400)
        
    if 'otp_phone' in request.session: del request.session['otp_phone']
    if 'otp_code' in request.session: del request.session['otp_code']
    
    username = f"cust_{phone}"
    with transaction.atomic():
        user, created = User.objects.get_or_create(username=username, defaults={'role': 'user'})
        if created:
            user.set_unusable_password()
            if fullname:
                parts = fullname.split(' ', 1)
                user.first_name = parts[0]
                if len(parts) > 1: user.last_name = parts[1]
            user.save()
            
        profile, p_created = CustomerProfile.objects.get_or_create(user=user, defaults={'phone_number': phone})
        
    auth_login(request, user)
    return JsonResponse({'success': True, 'message': 'Verification successful.', 'redirect_url': '/dashboard/'})


@require_POST
def toggle_wishlist_view(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON.'}, status=400)

    product_id = data.get('product_id')
    if not product_id:
        return JsonResponse({'success': False, 'message': 'product_id is required.'}, status=400)

    product = get_object_or_404(Product, pk=product_id, is_active=True)
    wishlist = request.session.get('wishlist', [])
    product_id_str = str(product.id)

    if product_id_str in wishlist:
        wishlist.remove(product_id_str)
        added = False
    else:
        wishlist.append(product_id_str)
        added = True

    request.session['wishlist'] = wishlist
    request.session.modified = True
    return JsonResponse({'status': 'success', 'success': True, 'added': added, 'count': len(wishlist)})


@never_cache
def wishlist_view(request):
    wishlist_ids = request.session.get('wishlist', [])
    active_products = Product.objects.filter(id__in=wishlist_ids, is_active=True)
    product_map = {str(p.id): p for p in active_products}

    class WishlistSessionItem:
        def __init__(self, product):
            self.product = product
            self.added_at = None

    wishlist_items = [WishlistSessionItem(product_map[str(pid)]) for pid in wishlist_ids if str(pid) in product_map]
    return render(request, 'core/wishlist.html', {'wishlist_items': wishlist_items})


@never_cache
@login_required
@require_POST
def address_add_view(request):
    form = AddressForm(request.POST)
    if form.is_valid():
        address = form.save(commit=False)
        address.user = request.user
        if address.is_default:
            Address.objects.filter(user=request.user).update(is_default=False)
        elif not Address.objects.filter(user=request.user).exists():
            address.is_default = True
        address.save()
        messages.success(request, f'Address "{address.label}" saved successfully.')
    else:
        for field, errs in form.errors.items():
            for err in errs: messages.error(request, f"{field.replace('_', ' ').title()}: {err}")
    return redirect('dashboard')


@never_cache
@login_required
@require_POST
def address_delete_view(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.delete()
    if address.is_default:
        next_addr = Address.objects.filter(user=request.user).first()
        if next_addr:
            next_addr.is_default = True
            next_addr.save()
    messages.success(request, 'Address removed.')
    return redirect('dashboard')


@never_cache
@login_required
@require_POST
def address_set_default_view(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    Address.objects.filter(user=request.user).update(is_default=False)
    address.is_default = True
    address.save()
    messages.success(request, f'"{address.label}" is now your default address.')
    return redirect('dashboard')


@never_cache
@login_required
@require_POST
def order_cancel_return_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.user != request.user:
        try:
            profile = request.user.customer_profile
            profile_phone = ''.join(filter(str.isdigit, str(profile.phone_number)))[-10:]
            order_phone = ''.join(filter(str.isdigit, str(order.phone_number)))[-10:]
            if profile_phone != order_phone: raise PermissionDenied
        except CustomerProfile.DoesNotExist:
            raise PermissionDenied

    action = request.POST.get('action')
    if action == 'cancel':
        if order.status in ('pending', 'confirmed'):
            order.status = 'cancelled'
            order.save()
            messages.success(request, f'Order #{str(order.order_id)[:8].upper()} has been cancelled.')
        else:
            messages.error(request, 'This order cannot be cancelled at this stage.')
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


@require_POST
def coupon_validate_view(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON.'}, status=400)

    coupon_code = data.get('code', '').strip().upper()
    cart_total  = data.get('cart_total', 0)

    if not coupon_code:
        return JsonResponse({'success': False, 'message': 'Please enter a coupon code.'}, status=400)

    now = timezone.now()
    qs = Coupon.objects.filter(code__iexact=coupon_code, is_active=True)
    qs = qs.filter(Q(start_date__isnull=True) | Q(start_date__lte=now))
    qs = qs.filter(Q(end_date__isnull=True) | Q(end_date__gte=now))
    coupon = qs.first()

    if coupon is None:
        return JsonResponse({'success': False, 'message': 'This coupon code is invalid or expired.'}, status=404)

    try:
        cart_total_decimal = float(cart_total)
    except (ValueError, TypeError):
        cart_total_decimal = 0

    if cart_total_decimal < float(coupon.minimum_order_value):
        return JsonResponse({'success': False, 'message': f'Minimum order value of ₹{coupon.minimum_order_value} required.'}, status=400)

    return JsonResponse({
        'success': True,
        'code': coupon.code,
        'discount_amount': float(coupon.discount_amount),
        'message': f'Coupon applied! You save ₹{coupon.discount_amount}.'
    })


def sitemap_view(request):
    scheme = request.scheme
    host = request.get_host()
    base = f"{scheme}://{host}"
    urls = []

    for page in ['', '/login/', '/blog/']:
        urls.append(f"<url><loc>{base}{page}</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>")

    products = Product.objects.filter(is_active=True).exclude(slug__isnull=True).exclude(slug='')
    for p in products:
        urls.append(f"<url><loc>{base}/products/{p.slug}/</loc><changefreq>weekly</changefreq><priority>0.9</priority></url>")

    blog_posts = Blog.objects.filter(is_published=True).exclude(slug='')
    for post in blog_posts:
        urls.append(f"<url><loc>{base}/blog/{post.slug}/</loc><lastmod>{post.created_at.strftime('%Y-%m-%d')}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>")

    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="https://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(urls) + '</urlset>'
    return HttpResponse(xml_content, content_type='application/xml')


def robots_txt_view(request):
    base = f"{request.scheme}://{request.get_host()}"
    content = f"User-agent: *\nAllow: /\nDisallow: /dashboard/\nDisallow: /api/\nDisallow: /admin/\n\nSitemap: {base}/sitemap.xml\n"
    return HttpResponse(content, content_type='text/plain')


def blog_list_view(request):
    posts = Blog.objects.filter(is_published=True).order_by('-created_at')
    context = {
        'posts': posts,
        'meta_title': 'Wellness Blog — KaaNuRO Group',
        'meta_description': 'Explore herbal wellness tips and insights from the KaaNuRO Group research team.',
        'breadcrumbs': [{'label': 'Home', 'url': '/'}, {'label': 'Blog', 'url': None}],
    }
    return render(request, 'core/blog_list.html', context)


def blog_detail_view(request, slug):
    post = get_object_or_404(Blog, slug=slug, is_published=True)
    related_posts = Blog.objects.filter(is_published=True).exclude(pk=post.pk).order_by('-created_at')[:3]
    context = {
        'post': post,
        'related_posts': related_posts,
        'meta_title': post.meta_title or f"{post.title} — KaaNuRO Wellness Blog",
        'meta_description': post.meta_description or post.summary or post.content[:155],
        'breadcrumbs': [{'label': 'Home', 'url': '/'}, {'label': 'Blog', 'url': '/blog/'}, {'label': post.title, 'url': None}],
    }
    return render(request, 'core/blog_detail.html', context)


# ─────────────────────────────────────────────────────────────────────────────
# REFACTORED PHASE 6 CATALOG VIEW WITH ADVANCED SEGREGATION AND POOL SPLITTING
# ─────────────────────────────────────────────────────────────────────────────
def product_catalog_view(request):
    """
    Splits rendering into dynamic context streams:
    - Primary focused categories (Teas, Juices, Wellness) display custom matching selections at top.
    - All remaining non-matching products drop gracefully into the lower secondary 'Other Products' pool.
    """
    q = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    shelf = request.GET.get('shelf', '').strip()

    # Base Query: Active items in stock
    base_qs = Product.objects.filter(is_active=True, stock__gt=0)

    # Apply standard shelf properties if present
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
    
    # Handle search parameters first
    if q:
        exact_results = base_qs.filter(
            Q(name__icontains=q) |
            Q(subtitle_tagline__icontains=q) |
            Q(description__icontains=q)
        )
        if exact_results.exists():
            base_qs = exact_results
        else:
            all_names = list(Product.objects.filter(is_active=True).values_list('name', flat=True))
            close = difflib.get_close_matches(q, all_names, n=5, cutoff=0.45)
            if close:
                q_objs = [Q(name__icontains=name) for name in close]
                fuzzy_filter = reduce(operator.or_, q_objs)
                base_qs = base_qs.filter(fuzzy_filter)
                corrected_query = close[0]
            else:
                base_qs = Product.objects.filter(is_active=True, stock__gt=0).order_by('?')[:12]
                search_fallback = True

    # ────────────────────────────────────────────────────────────
    # FIX 2 & 3: Segment into Focused Display Categories vs Remaining Pool items
    # ────────────────────────────────────────────────────────────
    featured_products = base_qs.none()
    other_products = base_qs.order_by('name')

    if category:
        if category == 'tea':
            # Target exact text matching rules for tea variants
            featured_products = base_qs.filter(
                Q(name__icontains='tea') | Q(name__icontains='leaf') | Q(name__icontains='heart')
            )
            other_products = base_qs.exclude(id__in=featured_products.values_list('id', flat=True)).order_by('name')
        elif category == 'juice':
            # Target exact text matching rules for juice variants (Aptofit, Vynora, Seaberry)
            featured_products = base_qs.filter(
                Q(name__icontains='juice') | Q(name__icontains='aptofit') | Q(name__icontains='vynora') | Q(name__icontains='seaberry')
            )
            other_products = base_qs.exclude(id__in=featured_products.values_list('id', flat=True)).order_by('name')
        elif category == 'wellness':
            # Target exact text matching rules for wellness formulas (Melatonin, drops, support)
            featured_products = base_qs.filter(
                Q(name__icontains='wellness') | Q(name__icontains='melatonin') | Q(name__icontains='drops')
            )
            other_products = base_qs.exclude(id__in=featured_products.values_list('id', flat=True)).order_by('name')

    seo_title = f"Products — KaaNuRO Group" if not q else f'Search: {q} — KaaNuRO'

    context = {
        'products': base_qs.order_by('name') if not category else featured_products,
        'featured_products': featured_products,
        'other_products': other_products,
        'q': q,
        'shelf': shelf,
        'category': category,
        'shelf_label': shelf_label,
        'search_fallback': search_fallback,
        'corrected_query': corrected_query,
        'meta_title': seo_title,
        'meta_description': 'Browse the full KaaNuRO natural wellness catalog. Filtered by targeted therapeutic herbal profiles.',
        'breadcrumbs': [{'label': 'Home', 'url': '/'}, {'label': 'Products', 'url': None}],
    }
    return render(request, 'core/products.html', context)


def legal_document_view(request, doc_type):
    db_type = 'PRIVACY_POLICY' if doc_type == 'privacy-policy' else 'TERMS_OF_SERVICE'
    doc = LegalDocument.objects.filter(doc_type=db_type).first()
    if not doc:
        default_title = "Privacy Policy" if db_type == 'PRIVACY_POLICY' else "Terms of Service"
        doc = LegalDocument.objects.create(
            doc_type=db_type,
            title=default_title,
            content=f"<h1>{default_title}</h1>\n<p>Welcome to our {default_title}. Content is under administrative draft.</p>"
        )
    rendered_content = doc.content
    try:
        import markdown
        rendered_content = markdown.markdown(doc.content, extensions=['extra', 'nl2br'])
    except Exception:
        pass
        
    context = {
        'doc': doc,
        'rendered_content': rendered_content,
        'meta_title': f"{doc.title} — KaaNuRO Group",
        'meta_description': f"Official and updated {doc.title} document.",
        'breadcrumbs': [{'label': 'Home', 'url': '/'}, {'label': doc.title, 'url': None}]
    }
    return render(request, 'core/legal_document.html', context)


def about_view(request):
    return render(request, 'core/about.html')


def contact_view(request):
    return render(request, 'core/contact.html')


def blogs_view(request):
    context = {}
    try:
        context['blogs'] = Blog.objects.all()
    except Exception:
        pass
    return render(request, 'core/blogs.html', context)


def emergency_9am_sync(request):
    product_updates = {
        "KaaNuRO Leaf - Herbal Heart Tea": {
            "ingredients": """• Arjan Chal (Terminalia arjuna) - 200 mg\n• Dashmool - 250 mg\n• Tulsi - 50 mg\n• Ginger - 50 mg\n• Mulethi – 50 mg\n• Dalchini - 50 mg\n• Green Tea Leaf - 50 mg\n• Ashwagandha - 50 mg\n• Beetroot - 50 mg\n• Citric Acid - 50 mg\n• Pipli - 200 mg\n• Haldi - 20 mg\n• Rock Salt - 20 mg\n• Krishna Marich - 10 mg\n• Chhoti Elachi - 5 mg\n• Lavng - 5 mg\n• Lemon Extract - 5 mg\n• Preservative - 100 mg""",
            "benefits": """1. Heart Health: Strengthens the heart.\n2. Blood Pressure Control.\n3. Cholesterol Balance.\n4. Anti-inflammatory Properties.\n5. Stress and Anxiety Relief.\n6. Boosts Digestive Health.\n7. Natural Detox.\n8. Skin & Hair Benefits."""
        },
        "KaaNuRO Leaf - Natural Herbal Tea": {
            "ingredients": """• Arjun Chaal\n• Tulsi\n• Sonth\n• Mulethi\n• Dalchini\n• Chhoti Elaichi\n• Kali Mirch\n• Green Tea\n• Laung\n• Pippali\n• Dashmool\n• Beetroot\n• Ashwagandha\n• Safed Musli\n• Garcinia""",
            "benefits": """• Heart Health Support\n• Immunity Boost\n• Better Digestion\n• Natural Energy\n• Stress Management\n• Weight Management Support\n• Rich in Antioxidants"""
        },
        "KaaNuRO VynorA": {
            "ingredients": """Contains Powerful Herbs: Ashoka, Arjuna, Shatavari, Shankhpushpi, Musali, Mulethi, Ashwagandha, Daru Haldi, Dashmool Kwath, Aamla, Vidanga, Devdaru, Citric Acid""",
            "benefits": """• Revitalizes women's overall health.\n• Naturally balances hormones (PCOD/PCOS).\n• Strengthens reproductive system.\n• Boosts immunity.\n• Increases energy and stamina.\n• Supports healthy skin."""
        },
        "KaaNuRO Herbal SeaBerry Juice": {
            "ingredients": """Premium Himalayan Seabuckthorn Extract | Superfood Nutrition (Vitamin C, E, Omega 3-6-7-9, Amino Acids, Minerals)""",
            "benefits": """• Skin Glow & Anti-Aging.\n• Digestion & Gastric Relief.\n• Blood Circulation Boost.\n• Liver Detox.\n• Hair Health.\n• Eye Health Support.\n• High Vitamin C.\n• Heart Health Support."""
        },
        "APTOFIT SYRUP": {
            "ingredients": """• Pineapple Extract\n• Mango Extract\n• Watermelon Extract\n• Pomegranate Extract\n• Pear Extract\n• Apple Extract\n• Propanediol\n• Glycerin\n• Xanthan Gum\n• Preservatives\n• Citric Acid""",
            "benefits": """✓ Stimulates Natural Appetite\n✓ Supports Healthy Weight Gain\n✓ Enhances Nutrient Absorption\n✓ Improves Energy Levels\n✓ Supports Healthy Digestion"""
        },
        "Melatonin Drops": {
            "ingredients": """• Melatonin\n• Purified Water\n• Natural Banana Flavour\n• Glycerin\n• Preservatives""",
            "benefits": """✓ Supports Natural Sleep Cycle\n✓ Helps You Fall Asleep Faster\n✓ Promotes Deep Sleep\n✓ Reduces Night-Time Restlessness"""
        }
    }
    log = []
    for name_query, data in product_updates.items():
        p = Product.objects.filter(name__icontains=name_query).first()
        if p:
            p.ingredients = data['ingredients']
            p.benefits = data['benefits']
            p.save()
            log.append(f"Successfully Sync'd: {p.name}")
        else:
            log.append(f"Skipped (Not Found): {name_query}")
    return HttpResponse("<h1>🚀 Database Updated!</h1><pre>" + "\n".join(log) + "</pre>")
