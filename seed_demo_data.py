"""
seed_demo_data.py — KaaNuRO Demo Product Seeder
================================================
Run once from the project root to populate the database with demo products
across all three homepage promotional shelves (Best Sellers, New Arrivals, Trending).

Usage:
    # From inside the project directory:
    ./venv/bin/python3 seed_demo_data.py

This script is idempotent: re-running it will not create duplicate records.
It is safe to delete after initial data seeding is complete.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kaanuro_project.settings')
django.setup()

from core.models import Product

# ──────────────────────────────────────────────────────────────────────────────
# Promotional category prefixes mapped to the four catalog families
# NOTE: The Product model has no 'category' database column. Category identity
# is encoded in the product name and description for frontend filtering.
# ──────────────────────────────────────────────────────────────────────────────
categories = [
    'wellness-teas',
    'heart-care',
    'skin-beauty',
    'organic-apparel',
]

# Each entry maps to a boolean flag field on the Product model
demo_shelves = [
    {'flag': 'is_best_seller', 'prefix': 'Best Seller'},
    {'flag': 'is_new_arrival', 'prefix': 'New Arrival'},
    {'flag': 'is_trending',    'prefix': 'Trending Item'},
]

created_count = 0
updated_count = 0

for cat in categories:
    cat_display = cat.replace('-', ' ').title()

    for shelf in demo_shelves:
        for i in range(1, 6):
            product_name = f"{shelf['prefix']} - {cat_display} #{i}"

            # ── get_or_create is idempotent on product name ──────────────────
            product, created = Product.objects.get_or_create(
                name=product_name,
                defaults={
                    # Correct field name: subtitle_tagline (not category)
                    'subtitle_tagline': f"Premium {cat_display} formulation",

                    'price': 499.00 + (i * 50),
                    'stock': 50,
                    'is_active': True,

                    'description': (
                        f"A premium therapeutic formulation from the {cat_display} range, "
                        f"crafted for maximum organic efficacy and daily wellness support."
                    ),

                    # Correct field name: ingredients ✅
                    'ingredients': (
                        "100% Certified Organic Botanicals, "
                        "Cold-Pressed herbal extracts, "
                        "Pure essential trace elements."
                    ),

                    # Correct field name: key_benefits (NOT 'benefits')
                    'key_benefits': (
                        "Enhances metabolic balance\n"
                        "Targets cellular rejuvenation\n"
                        "Promotes long-term vitality and longevity"
                    ),

                    # Correct field name: directions_for_use (NOT 'usage_instructions')
                    'directions_for_use': (
                        "Apply or consume twice daily with warm water. "
                        "Follow the routine consistently for 30 days for optimal results."
                    ),
                }
            )

            # ── Always set the shelf flag, even on existing products ─────────
            setattr(product, shelf['flag'], True)
            product.save(update_fields=[shelf['flag']])

            if created:
                created_count += 1
                print(f"  ✅ Created : {product_name}")
            else:
                updated_count += 1
                print(f"  🔄 Updated : {product_name}  (flag → {shelf['flag']} = True)")

print()
print("─" * 60)
print(f"Seeding complete.")
print(f"  Products created : {created_count}")
print(f"  Products updated : {updated_count}")
print(f"  Total processed  : {created_count + updated_count}")
print()
print("Next step: verify homepage shelves are visible at http://127.0.0.1:8000/")
print("─" * 60)
