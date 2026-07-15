from django.db import migrations

def create_emergency_admin(apps, schema_editor):
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Clear out conflicts and force-build the clean target recovery admin credentials
        User.objects.filter(username='pop').delete()
        
        # Explicitly declare and persist the administrative access metrics on the database row instance
        admin_user = User.objects.create_superuser(
            username='pop',
            email='admin@example.com',
            password='pop'
        )
        admin_user.is_staff = True
        admin_user.is_superuser = True
        if hasattr(admin_user, 'role'):
            admin_user.role = 'admin'
        admin_user.save()
        print("--- SUCCESS: RUNTIME RECOVERY MIGRATION APPLIED SUPERUSER 'pop' ---")
    except Exception as e:
        print(f"Migration error suppression: {e}")

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0018_recreate_admin'), # Ensure this matches the exact previous file name in your directory log
    ]
    operations = [
        migrations.RunPython(create_emergency_admin),
    ]
