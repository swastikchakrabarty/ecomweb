import os
import django

# Set up the Django runtime environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecomweb.settings') # Adjust if your settings folder name is different (e.g. core.settings)
django.setup()

from core.models import Product  # Adjust to your exact app path if not 'core'

def update_catalog_data():
    print("--- Initializing Automated Product Catalog Update Engine ---")
    
    # Define exact data mappings extracted directly from the corporate inventory sheet
    product_updates = {
        "KaaNuRO Leaf - Herbal Heart Tea": {
            "ingredients": """• Arjan Chal (Terminalia arjuna) - 200 mg
• Dashmool - 250 mg
• Tulsi (Ocimum tenuiflorum) - 50 mg
• Ginger (Zingiber officinale) - 50 mg
• Mulethi (Glycyrrhiza glabra) – 50 mg
• Dalchini (Cinnamomum verum) - 50 mg
• Green Tea Leaf (Camellia sinensis) - 50 mg
• Ashwagandha (Withania somnifera) - 50 mg
• Beetroot (Beta vulgaris) - 50 mg
• Citric Acid - 50 mg
• Pipli (Piper longum) - 200 mg
• Haldi (Curcuma longa) - 20 mg
• Rock Salt - 20 mg
• Krishna Marich (Piper nigrum) - 10 mg
• Chhoti Elachi (Elettaria cardamomum) - 5 mg
• Lavng (Syzygium aromaticum) - 5 mg
• Lemon Extract (Citrus limon) - 5 mg
• Preservative - 100 mg""",
            "benefits": """1. Heart Health: Strengthens the heart and maintains balanced blood flow.
2. Blood Pressure Control: Helps keep blood pressure stable and balanced.
3. Cholesterol Balance: Reduces bad cholesterol (LDL) and increases good cholesterol (HDL).
4. Anti-inflammatory Properties: Naturally reduces inflammation, pain, and fatigue.
5. Relief from Stress and Anxiety: Captivating aroma promotes mental peace and improves sleep.
6. Boosts Digestive Health: Improves digestion and alleviates heaviness.
7. Natural Detox and Antioxidant: Flushes out toxins, filling each day with energy and freshness.
8. Citric Acid Beauty Benefits: Imparts glowing skin, clear/smooth texture, and shiny hair."""
        },
        "KaaNuRO Leaf - Natural Herbal Tea": {
            "ingredients": """• Arjun Chaal - Supports heart health.
• Tulsi - Helps boost immunity.
• Sonth (Dry Ginger) - Supports healthy digestion.
• Mulethi - Soothes throat and respiratory health.
• Dalchini - Supports metabolism.
• Chhoti Elaichi - Aids digestion and adds freshness.
• Kali Mirch - Improves nutrient absorption.
• Green Tea - Rich in natural antioxidants.
• Laung - Supports immunity and oral health.
• Pippali - Helps support digestion and respiratory wellness.
• Dashmool - Promotes overall wellness.
• Beetroot - Supports healthy blood circulation.
• Ashwagandha - Helps manage stress and boosts stamina.
• Safed Musli - Supports strength and vitality.
• Garcinia - Supports healthy weight management.""",
            "benefits": """• Heart Health Support
• Immunity Boost
• Better Digestion
• Natural Energy
• Stress Management
• Weight Management Support
• Rich in Antioxidants
• Daily Wellness Support"""
        },
        "KaaNuRO VynorA": {
            "ingredients": """Contains Powerful Herbs: Ashoka, Arjuna, Shatavari, Shankhpushpi, Musali, Mulethi, Ashwagandha, Daru Haldi, Dashmool Kwath, Aamla, Vidanga, Devdaru, Citric Acid & more...""",
            "benefits": """• Revitalizes women's overall health: Helps address weakness, fatigue, and hormonal imbalances.
• Naturally balances hormones: Helps restore natural balance in PCOD/PCOS, irregular menstruation, and mood swings.
• Strengthens the reproductive system: Supports uterine strength and proper functioning.
• Boosts immunity: Strengthens the body's immune system.
• Increases energy and stamina: Provides nourishment by alleviating stress and weakness.
• Supports healthy skin and a natural glow: Promotes facial glow through internal hormonal balance."""
        },
        "KaaNuRO Herbal SeaBerry Juice": {
            "ingredients": """Premium Himalayan Seabuckthorn Extract | Superfood Nutrition (Contains Vitamin C, Vitamin E, Omega 3-6-7-9, Amino Acids, Minerals, and Powerful Antioxidants)""",
            "benefits": """• Skin Glow & Anti-Aging: Natural facial glow, reduces wrinkles, dark spots, and repairs dry skin.
• Digestion & Gastric Relief: Relief from acidity, gas, bloating, and strengthens digestion.
• Blood Circulation Boost: Improves oxygen supply, reduces fatigue and muscle stiffness.
• Liver Detox & Body Cleansing: Flushes out body toxins and strengthens liver function.
• Hair Health Benefits: Promotes strong, shiny hair and controls hair fall.
• Eye Health Support: Vitamin A and antioxidants support vision and reduce eye fatigue.
• Women's Health Support: Promotes hormonal balance and overall wellness.
• High Vitamin C: Strong protection against viral and bacterial infections.
• Heart Health Support: Lowers bad cholesterol and maintains balanced blood pressure.
• Diabetes Management Support: Helps control blood sugar levels and reduces insulin resistance."""
        },
        "APTOFIT SYRUP": {
            "ingredients": """• Pineapple Extract
• Mango Extract
• Watermelon Extract
• Pomegranate Extract
• Pear Extract
• Apple Extract
• Propanediol
• Glycerin
• Xanthan Gum
• Preservatives
• Citric Acid
• Natural Flavour
• Purified Water""",
            "benefits": """✓ Stimulates Natural Appetite & Daily Food Intake
✓ Supports Healthy Weight Gain
✓ Enhances Nutrient Absorption
✓ Improves Natural Energy Levels
✓ Supports Healthy Digestion
✓ Rich in Fruit-Based Nutrients
✓ Helps Reduce Weakness & Fatigue
✓ Promotes Overall Growth & Wellness"""
        },
        "Melatonin Drops": {
            "ingredients": """• Melatonin
• Purified Water
• Natural Banana Flavour
• Glycerin
• Preservatives
• Food Grade Stabilizers""",
            "benefits": """✓ Supports Natural Sleep Cycle
✓ Helps You Fall Asleep Faster
✓ Promotes Deep & Restful Sleep
✓ Helps Reduce Night-Time Restlessness
✓ Supports Relaxation Before Bedtime
✓ Helps Improve Sleep Quality
✓ May Help Reduce Stress & Anxiety
✓ Supports Healthy Sleep-Wake Rhythm
✓ Pleasant Banana Flavour (Non-Habit Forming)"""
        }
    }

    for name_query, data in product_updates.items():
        # Match products dynamically via a case-insensitive name filter look
        db_product = Product.objects.filter(name__icontains=name_query).first()
        
        if db_product:
            db_product.ingredients = data['ingredients']
            db_product.benefits = data['benefits']
            db_product.save()
            print(f"✔ Successfully saved database items for: {db_product.name}")
        else:
            # Fallback if names differ slightly - list similar records
            print(f"⚠ Match skipped: Could not locate product containing '{name_query}' in DB.")

    print("\n🚀 Database optimization script completed safely!")

if __name__ == "__main__":
    update_catalog_data()
