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
from django.db.models import Q

# ──────────────────────────────────────────────────────────────────────────────
# Promotional category definitions
# ──────────────────────────────────────────────────────────────────────────────
categories = [
    'hair-growth',
    'sleep-optimization',
    'fat-loss-support',
]

category_details = {
    'hair-growth': {
        'display': 'Hair Growth',
        'subtitle': 'Premium Kesh Vitality Formulation',
        'description': 'A premium Ayurvedic formulation targeting scalp nourishment, DHT-blocking botanicals, and hair follicle density to naturally restore hair vitality.',
        'ingredients': 'Bhringraj Extract, Saw Palmetto, Amalaki, Rosemary, Neem',
        'key_benefits': 'Nourishes scalp and hair roots\nBlocks DHT naturally to reduce hair fall\nAccelerates hair follicle density',
        'directions': 'Apply 5-10ml to the scalp and massage gently. Leave on for at least 2 hours or overnight before washing. Use 3 times a week.'
    },
    'sleep-optimization': {
        'display': 'Sleep Optimization',
        'subtitle': 'Circadian Calm Herbal Infusion',
        'description': 'A soothing, non-habit-forming formulation containing traditional roots designed to ease nervous tension, lower stress metrics, and extend deep REM sleep cycles.',
        'ingredients': 'Sarpagandha extract, Valerian Root, Chamomile, Ashwagandha, Brahmi',
        'key_benefits': 'Promotes restful and extended REM sleep\nReduces nighttime stress and anxiety\nSupports morning clarity without grogginess',
        'directions': 'Mix 1 teaspoon with warm water or milk and consume 30 minutes before bed.'
    },
    'fat-loss-support': {
        'display': 'Fat Loss Support',
        'subtitle': 'Metabolic Fire Herbal Accelerator',
        'description': 'A high-potency organic tea blend that accelerates natural thermogenesis, aids in appetite regulation, and supports an antioxidant-rich cellular cleanse.',
        'ingredients': 'Green Tea Extract, Garcinia Cambogia, Guggul, Ginger, Cinnamon',
        'key_benefits': 'Accelerates natural thermogenesis\nSupports healthy appetite regulation\nPromotes cellular cleanse and digestion',
        'directions': 'Steep 1 teaspoon in boiling water for 5-7 minutes. Consume warm twice daily before meals.'
    }
}

# Each entry maps to a boolean flag field on the Product model
demo_shelves = [
    {'flag': 'is_best_seller', 'prefix': 'Best Seller'},
    {'flag': 'is_new_arrival', 'prefix': 'New Arrival'},
    {'flag': 'is_trending',    'prefix': 'Trending Item'},
]

# Delete old demo products first
print("Cleaning up old demo products...")
Product.objects.filter(
    Q(name__contains="Wellness Teas") |
    Q(name__contains="Heart Care") |
    Q(name__contains="Skin Beauty") |
    Q(name__contains="Organic Apparel")
).delete()

created_count = 0
updated_count = 0

for cat in categories:
    details = category_details[cat]
    cat_display = details['display']

    for shelf in demo_shelves:
        for i in range(1, 6):
            product_name = f"{shelf['prefix']} - {cat_display} #{i}"

            # ── get_or_create is idempotent on product name ──────────────────
            product, created = Product.objects.get_or_create(
                name=product_name,
                defaults={
                    # Correct field name: subtitle_tagline (not category)
                    'subtitle_tagline': details['subtitle'],

                    'price': 499.00 + (i * 50),
                    'stock': 50,
                    'is_active': True,

                    'description': f"{details['description']} (Batch #{i})",

                    # Correct field name: ingredients ✅
                    'ingredients': details['ingredients'],

                    # Correct field name: key_benefits (NOT 'benefits')
                    'key_benefits': details['key_benefits'],

                    # Correct field name: directions_for_use (NOT 'usage_instructions')
                    'directions_for_use': details['directions'],
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
