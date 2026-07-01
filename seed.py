import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kaanuro_project.settings')
django.setup()

from core.models import User, Employee, Product, ClothingItem, Blog

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

    # 4. Create Mock Products
    products_data = [
        {
            'name': 'Arjuna Heart Tea',
            'subtitle_tagline': 'Herbal Heart Infusion',
            'description': 'A revitalizing organic tea blend containing Arjuna bark extract and wild rosehip to support muscle tone, clean circulation, and arterial resilience.',
            'total_quantity_info': '120g loose tea',
            'ingredients': 'Arjuna Bark, Rosehip, Hibiscus Petals, Cardamom, Ginger',
            'key_benefits': 'Supports cardiovascular health\nImproves circulation efficiency\nRich in heart-protective antioxidants',
            'directions_for_use': 'Boil 1 teaspoon in 200ml water for 5 minutes. Strain and consume warm once daily in the morning.',
            'price': 499.00,
            'is_active': True
        },
        {
            'name': 'Tejpatra Glow Oil',
            'subtitle_tagline': 'Natural Skin Radiance',
            'description': 'An ancient cold-pressed formulation using bay leaves, saffron, and sweet almond oil to deeply cleanse and naturally brighten the skin barrier.',
            'total_quantity_info': '50ml dropper bottle',
            'ingredients': 'Tejpatra (Bay Leaf) Extract, Kashmiri Saffron, Sweet Almond Oil, Vetiver Root',
            'key_benefits': 'Enhances skin brightness\nRestores skin moisture barrier\nDefends against free radical damage',
            'directions_for_use': 'Apply 3-4 drops onto clean face and neck. Massage gently in circular upward strokes before bedtime.',
            'price': 599.00,
            'is_active': True
        },
        {
            'name': 'Sarpagandha Calming Blend',
            'subtitle_tagline': 'Sleep & Mind Balance',
            'description': 'A soothing bedtime formula combining Sarpagandha and Ashwagandha to ease nervous tension, lower stress hormones, and induce deep, restful sleep.',
            'total_quantity_info': '60 vegetable capsules',
            'ingredients': 'Sarpagandha extract, Ashwagandha root, Brahmi extract, Shankhpushpi',
            'key_benefits': 'Reduces anxiety and stress\nPromotes restful sleep cycles\nSupports cognitive calmness',
            'directions_for_use': 'Take 1 capsule with warm water or milk 30 minutes before sleep, or as directed by a healthcare associate.',
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

    # 5. Create Mock Clothing Items
    clothing_data = [
        {
            'name': 'Organic Cotton Female Kurti',
            'category': 'female',
            'price': 1499.00,
            'fabric': '100% Organic Cotton',
            'colors': 'Cream, Sage Green, Soft Gold',
            'sizes': 'S, M, L, XL',
            'is_active': True
        },
        {
            'name': 'Handwoven Linen Male Shirt',
            'category': 'male',
            'price': 1899.00,
            'fabric': 'Handwoven Linen',
            'colors': 'Beige, Herbal Green, White',
            'sizes': 'M, L, XL, XXL',
            'is_active': True
        },
        {
            'name': 'Soft Herbal Kids Romper',
            'category': 'kids',
            'price': 899.00,
            'fabric': 'Organic Bamboo Cotton',
            'colors': 'Cream, Soft Gold, Pale Pink',
            'sizes': '6-12M, 12-18M, 2T',
            'is_active': True
        }
    ]

    for c_info in clothing_data:
        item, created = ClothingItem.objects.get_or_create(
            name=c_info['name'],
            defaults=c_info
        )
        if created:
            print(f"Created Clothing Item: {item.name}")
        else:
            print(f"Clothing Item already exists: {item.name}")

    blog_data = [
        {
            'title': 'The Secrets of Arjuna Bark for Cardiovascular Longevity',
            'summary': 'Arjuna has been a cardiotonic cornerstone for centuries. Learn how Arjuna bark extract supports muscle tone, clean circulation, and arterial resilience.',
            'content': 'Arjuna (Terminalia arjuna) has been a cornerstone of cardiotonic therapy in Rajasthan and ancient India for centuries. In this post, we discuss the scientific mechanisms through which Arjuna bark extract supports muscle tone, clean circulation, and arterial resilience, protecting your heart first.',
            'author': 'Dr. Alok Sharma, Wellness Associate'
        },
        {
            'title': 'Natural Skin Glow: Saffron and Bay Leaf Elixirs',
            'summary': 'Discover how natural bay leaf and saffron extracts brighten the skin barrier and defend against aging.',
            'content': 'External radiance is a reflection of internal purity. Traditional cold-pressed oils incorporating Tejpatra (Bay Leaf) extract and Kashmiri Saffron work to naturally brighten the skin barrier. Discover how these organic elements defend against premature aging and bring out your natural glow.',
            'author': 'Pooja Verma, Beauty Consultant'
        },
        {
            'title': 'Deep Bedtime Calming: Ayurveda\'s Sleep Herbs Decoded',
            'summary': 'Ease nervous tension and induce restorative sleep using traditional Ayurvedic roots like Sarpagandha and Ashwagandha.',
            'content': 'In our modern, busy life, stress hormones can build up and lead to restless sleep. Ayurveda offers powerful root extracts like Sarpagandha and Ashwagandha to ease nervous tension, promote neural calming, and induce deep, restorative sleep. Learn how to incorporate them safely.',
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

