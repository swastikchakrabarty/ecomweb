from django.db import migrations
from django.contrib.auth import get_user_model

def recreate_admin(apps, schema_editor):
    User = get_user_model()
    # Delete old admin user if present to ensure clean state
    User.objects.filter(username='admin').delete()
    
    # Create fresh superuser with correct credentials
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@kaanurogroup.com',
        password='KaanuroAdmin2026!'
    )
    # Ensure role is set to 'admin' as required by custom user model view restrictions
    admin_user.role = 'admin'
    admin_user.save()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_legaldocument'),
    ]

    operations = [
        migrations.RunPython(recreate_admin),
    ]
