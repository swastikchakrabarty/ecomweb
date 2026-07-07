import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kaanuro_project.settings')
django.setup()

from core.models import User, Employee, Product, Blog


def seed_database():
    print("Starting database seeding...")
    
    # 1. Create Admin User
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'kaanurogroup@gmail.com',
            'role': 'admin',
            'first_name': 'KaaNuRO',
            'last_name': 'Admin',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('adminpassword123')
        admin_user.save()
        print("Created Admin User (username: admin, password: adminpassword123)")
    else:
        print("Admin User already exists.")

    # 2. Create Employee User & Profile
    emp_user, created = User.objects.get_or_create(
        username='employee',
        defaults={
            'email': 'employee@kaanuro.com',
            'role': 'employee',
            'first_name': 'Rajesh',
            'last_name': 'Sharma',
            'is_staff': True
        }
    )
    if created:
        emp_user.set_password('employeepassword123')
        emp_user.save()
        
        # Create Employee profile
        Employee.objects.create(
            user=emp_user,
            employee_id='EMP001',
            designation='Senior Wellness consultant'
        )
        print("Created Employee User (username: employee, password: employeepassword123)")
    else:
        print("Employee User already exists.")

    # 3. Create Regular User
    reg_user, created = User.objects.get_or_create(
        username='user',
        defaults={
            'email': 'customer@test.com',
            'role': 'user',
            'first_name': 'Amit',
            'last_name': 'Kumar'
        }
    )
    if created:
        reg_user.set_password('userpassword123')
        reg_user.save()
        print("Created Regular User (username: user, password: userpassword123)")
    else:
        print("Regular User already exists.")

    # 4. Clean up old cardiovascular products and blogs first
    print("Cleaning up old database records...")
    Product.objects.filter(name__in=['Arjuna Heart Tea', 'Tejpatra Glow Oil', 'Sarpagandha Calming Blend']).delete()
    Blog.objects.filter(title__in=[
        'The Secrets of Arjuna Bark for Cardiovascular Longevity',
        'Natural Skin Glow: Saffron and Bay Leaf Elixirs',
        'Deep Bedtime Calming: Ayurveda\'s Sleep Herbs Decoded'
    ]).delete()

    # 5. Create Mock Products
    products_data = [
        {
            'name': 'KaanuRO Kesh Vitality Formulation',
            'subtitle_tagline': 'Herbal Hair Growth Elixir',
            'description': 'A premium Ayurvedic formulation targeting scalp nourishment, DHT-blocking botanicals, and hair follicle density to naturally restore hair vitality.',
            'total_quantity_info': '120g loose herb blend',
            'ingredients': 'Bhringraj Extract, Saw Palmetto, Amalaki, Rosemary, Neem',
            'key_benefits': 'Nourishes scalp and hair roots\nBlocks DHT naturally to reduce hair fall\nAccelerates hair follicle density',
            'directions_for_use': 'Apply 5-10ml to the scalp and massage gently. Leave on for at least 2 hours or overnight before washing. Use 3 times a week.',
            'price': 499.00,
            'is_active': True
        },
        {
            'name': 'Veda Lean Fat Loss Infusion',
            'subtitle_tagline': 'Metabolic Fire Herbal Accelerator',
            'description': 'A high-potency organic tea blend that accelerates natural thermogenesis, aids in appetite regulation, and supports an antioxidant-rich cellular cleanse.',
            'total_quantity_info': '100g loose tea',
            'ingredients': 'Green Tea Extract, Garcinia Cambogia, Guggul, Ginger, Cinnamon',
            'key_benefits': 'Accelerates natural thermogenesis\nSupports healthy appetite regulation\nPromotes cellular cleanse and digestion',
            'directions_for_use': 'Steep 1 teaspoon in boiling water for 5-7 minutes. Consume warm twice daily before meals.',
            'price': 599.00,
            'is_active': True
        },
        {
            'name': 'Nidra Deep Sleep Blend',
            'subtitle_tagline': 'Circadian Calm Herbal Infusion',
            'description': 'A soothing, non-habit-forming formulation containing traditional roots designed to ease nervous tension, lower stress metrics, and extend deep REM sleep cycles.',
            'total_quantity_info': '60 vegetable capsules',
            'ingredients': 'Sarpagandha extract, Valerian Root, Chamomile, Ashwagandha, Brahmi',
            'key_benefits': 'Promotes restful and extended REM sleep\nReduces nighttime stress and anxiety\nSupports morning clarity without grogginess',
            'directions_for_use': 'Mix 1 teaspoon with warm water or milk and consume 30 minutes before bed.',
            'price': 699.00,
            'is_active': True
        }
    ]

    for p_info in products_data:
        prod, created = Product.objects.get_or_create(
            name=p_info['name'],
            defaults=p_info
        )
        if not created:
            for key, val in p_info.items():
                setattr(prod, key, val)
            prod.save()
            print(f"Updated Product: {prod.name}")
        else:
            print(f"Created Product: {prod.name}")

    blog_data = [
        {
            'title': 'Ayurvedic Secrets for Restoring Hair Density and Scalp Vitality',
            'summary': 'Discover how traditional DHT-blocking botanicals like Bhringraj and Saw Palmetto nourish hair follicles and promote thick, healthy hair growth.',
            'content': 'Hair loss can be deeply frustrating. In this article, we dive into the Ayurvedic science of Kesh health, highlighting how natural herbs like Bhringraj, Amalaki, and Saw Palmetto block DHT receptors, revitalize the scalp, and increase follicle density from the root.',
            'author': 'Dr. Alok Sharma, Wellness Associate'
        },
        {
            'title': 'Igniting Metabolism: The Science of Natural Thermogenesis',
            'summary': 'Discover how metabolic accelerators and green tea extracts support appetite regulation, cellular cleansing, and active fat loss.',
            'content': 'Achieving a healthy metabolic rate involves more than just counting calories. We analyze how natural thermogenic herbs like Guggul, Garcinia Cambogia, and green tea catechins elevate metabolic speed, aid in appetite control, and support a comprehensive cellular detox.',
            'author': 'Pooja Verma, Beauty Consultant'
        },
        {
            'title': 'Deep Bedtime Calming: Restoring Circadian Sleep Metrics Naturally',
            'summary': 'Learn how non-habit-forming calming roots like Sarpagandha and Ashwagandha ease nervous tension and promote restorative REM sleep cycles.',
            'content': 'Quality sleep is the foundation of cognitive clarity and overall health. We explore the biological mechanisms of circadian rhythms and how traditional Ayurvedic adaptogens like Sarpagandha, Valerian root, and Ashwagandha lower cortisol levels to facilitate deep, uninterrupted REM sleep.',
            'author': 'KaaNuRO Wellness Editorial'
        }
    ]

    for b_info in blog_data:
        post, created = Blog.objects.get_or_create(
            title=b_info['title'],
            defaults=b_info
        )
        if not created:
            post.summary = b_info['summary']
            post.content = b_info['content']
            post.author = b_info['author']
            post.save()
            print(f"Updated Blog Post: {post.title}")
        else:
            print(f"Created Blog Post: {post.title}")

    print("Database seeding completed successfully!")

if __name__ == '__main__':
    seed_database()

