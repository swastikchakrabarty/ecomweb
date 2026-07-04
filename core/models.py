from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify

# --- USER ROLES & CUSTOM USER MODEL ---
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('employee', 'Employee'),
        ('user', 'Regular User'),
    )
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='user')
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

# --- EMPLOYEE PROFILE MODEL ---
class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'employee'})
    employee_id = models.CharField(max_length=20, unique=True, verbose_name="Employee ID")
    designation = models.CharField(max_length=100, default="Wellness Associate")
    joined_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.employee_id}"

# --- PRODUCT INVENTORY MODEL ---
class Product(models.Model):
    name = models.CharField(max_length=255)
    subtitle_tagline = models.CharField(max_length=500, blank=True, help_text="e.g., Herbal Heart Tea")
    description = models.TextField(help_text="Detailed product overview")
    total_quantity_info = models.CharField(max_length=100, blank=True, help_text="e.g., 1,220 mg per pouch")
    ingredients = models.TextField(help_text="Comma-separated or newline list of ingredients with dosages")
    key_benefits = models.TextField(help_text="Bullet-pointed core health benefits")
    directions_for_use = models.TextField(blank=True, help_text="Preparation and timing guidelines")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Retail Price (INR)")
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_2 = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Gallery Image 2")
    image_3 = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Gallery Image 3")
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock Quantity", help_text="Set to 0 to auto-hide from catalog")
    is_active = models.BooleanField(default=True)
    is_best_seller = models.BooleanField(default=False, verbose_name="Best Seller", help_text="Feature on homepage Best Sellers shelf")
    is_new_arrival = models.BooleanField(default=False, verbose_name="New Arrival", help_text="Feature on homepage New Arrivals shelf")
    is_trending = models.BooleanField(default=False, verbose_name="Trending", help_text="Feature on homepage Trending shelf")

    # ── Phase 4: SEO Fields ───────────────────────────────────────────────────
    slug = models.SlugField(max_length=280, unique=False, blank=True, null=True, help_text="Auto-generated from product name. Used in SEO-friendly URLs.")
    meta_title = models.CharField(max_length=150, blank=True, null=True, help_text="Custom SEO title (max 150 chars). Falls back to product name.")
    meta_description = models.TextField(blank=True, null=True, help_text="Custom meta description for search engines. Falls back to product description.")

    @property
    def media_list_json(self):
        import json
        media_items = []
        if self.image:
            media_items.append({'type': 'image', 'url': self.image.url})
        for m in self.additional_media.all():
            if m.media_type == 'image' and m.file:
                media_items.append({'type': 'image', 'url': m.file.url})
            elif m.media_type == 'video':
                url = m.file.url if m.file else m.embed_url
                if url:
                    media_items.append({'type': 'video', 'url': url})
        return json.dumps(media_items)

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        # Post-save: resolve slug collision by suffixing pk
        if self.slug and Product.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            self.slug = f"{slugify(self.name)}-{self.pk}"
            Product.objects.filter(pk=self.pk).update(slug=self.slug)

    def __str__(self):
        return self.name

# --- CONTACT FORM SUBMISSIONS ---
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} ({self.email}) at {self.created_at}"


# --- CLOTHING ITEM MODEL ---
class ClothingItem(models.Model):
    CATEGORY_CHOICES = (
        ('female', 'Female'),
        ('male', 'Male'),
        ('kids', 'Kids'),
    )
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    fabric = models.CharField(max_length=100)
    colors = models.CharField(max_length=255, help_text="Comma-separated colors")
    sizes = models.CharField(max_length=255, help_text="Comma-separated sizes")
    image = models.ImageField(upload_to='clothing/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    @property
    def media_list_json(self):
        import json
        media_items = []
        if self.image:
            media_items.append({
                'type': 'image',
                'url': self.image.url
            })
        for m in self.additional_media.all():
            if m.media_type == 'image' and m.file:
                media_items.append({
                    'type': 'image',
                    'url': m.file.url
                })
            elif m.media_type == 'video':
                url = m.file.url if m.file else m.embed_url
                if url:
                    media_items.append({
                        'type': 'video',
                        'url': url
                    })
        return json.dumps(media_items)

    def __str__(self):
        return self.name


# --- BLOG POST MODEL ---
class Blog(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=False, blank=True, help_text="Auto-generated from title. Used in SEO-friendly URLs.")
    summary = models.TextField(blank=True, default="")
    content = models.TextField()
    image = models.ImageField(upload_to='blogs/', blank=True, null=True)
    featured_image = models.ImageField(upload_to='blog/', blank=True, null=True, verbose_name="Featured Image")
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=100, default="KaaNuRO Group")
    # ── Phase 4: SEO & Publishing Fields ────────────────────────────────────
    meta_title = models.CharField(max_length=150, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    is_published = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            base_slug = slugify(self.title)
            candidate = base_slug
            counter = 1
            while Blog.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base_slug}-{counter}"
                counter += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# --- MULTI-IMAGES / MULTI-VIDEOS RELATIONSHIPS ---
class ProductMedia(models.Model):
    MEDIA_TYPE_CHOICES = (
        ('image', 'Image Upload'),
        ('video', 'Video Upload/Embed Link'),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='additional_media', null=True, blank=True)
    clothing_item = models.ForeignKey(ClothingItem, on_delete=models.CASCADE, related_name='additional_media', null=True, blank=True)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, default='image')
    file = models.FileField(upload_to='product_gallery/', help_text="Upload product photo or MP4 video snippet")
    embed_url = models.URLField(blank=True, null=True, help_text="Optional YouTube/Vimeo video streaming URL code link")

    def __str__(self):
        return f"Media asset for {self.product.name if self.product else self.clothing_item.name}"


import uuid

class Order(models.Model):
    ORDER_STATUS_CHOICES = (
        ('pending',           'Payment Awaiting Verification'),
        ('confirmed',         'Confirmed'),
        ('processing',        'Processing & Packing'),
        ('shipped',           'Dispatched'),
        ('out_for_delivery',  'Out for Delivery'),
        ('delivered',         'Delivered'),
        ('cancelled',         'Cancelled'),
        ('return_requested',  'Return Requested'),
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    customer_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    shipping_address = models.TextField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    utr_number = models.CharField(max_length=50, verbose_name="UPI Reference / UTR Number")
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.order_id} - {self.customer_name} ({self.get_status_display()})"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=255, help_text="Saves historical point-of-sale snapshot string")
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)


# --- SECURE SENSITIVE CUSTOMER PROFILE LOGS ---
class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    phone_number = models.CharField(max_length=15, unique=True, verbose_name="Verified Phone")
    shipping_address = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='customer_avatars/', blank=True, null=True, verbose_name="Profile Avatar")
    default_address = models.TextField(blank=True, null=True, verbose_name="Default Shipping Address")
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Wallet Balance (INR)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Customer profile: {self.phone_number}"


# --- AUTOMATED INVOICE ARCHITECTURE ---
class Invoice(models.Model):
    invoice_number = models.CharField(max_length=100, unique=True, verbose_name="Invoice Serial")
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='invoice')
    issued_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='invoices/', blank=True, null=True, help_text="Generated receipt document copy")

    def __str__(self):
        return f"Receipt {self.invoice_number} for Order {self.order.order_id}"


# --- PRODUCT REVIEWS ---
class ProductReview(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user_name = models.CharField(max_length=100, verbose_name="Reviewer Name")
    rating = models.IntegerField(default=5, choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user_name} — {self.rating}★ on {self.product.name}"


# ── PHASE 3 ADDITIONS ────────────────────────────────────────────────────────

# --- SAVED ADDRESSES ---
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    label = models.CharField(max_length=50, default='Home', help_text="e.g. Home, Work, Other")
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=15)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Saved Addresses'
        ordering = ['-is_default', 'id']

    def __str__(self):
        return f"{self.label} — {self.address_line_1}, {self.city} ({self.user.username})"


# --- WISHLIST ---
class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.username} → {self.product.name}"


# --- COUPON ENGINE ---
class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Coupon Code")
    discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name="Flat Discount (INR)",
        help_text="Fixed rupee discount applied to the cart total."
    )
    minimum_order_value = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        verbose_name="Minimum Order Value",
        help_text="Minimum cart total required for this coupon to apply."
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"{self.code} — ₹{self.discount_amount} off [{status}]"
