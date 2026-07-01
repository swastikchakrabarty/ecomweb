from django.db import migrations
from django.contrib.auth import get_user_model

def create_superuser(apps, schema_editor):
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@kaanurogroup.com',
            password='YourTemporaryPassword123!'
        )

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0009_customerprofile_default_address_and_more'),
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]