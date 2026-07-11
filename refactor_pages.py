import os
import re

# --- AUTO DETECT DJANGO APP STRUCTURE ---
def find_django_files():
    possible_files = ['views.py', 'urls.py', 'models.py']
    for root, dirs, files in os.walk('.'):
        # Ignore virtual environments or hidden directories
        if any(x in root for x in ['venv', '.git', 'env', '__pycache__']):
            continue
        if all(f in files for f in possible_files):
            return root
    return None

APP_DIR = find_django_files()

if not APP_DIR:
    print("❌ Error: Could not automatically locate your Django app folder.")
    print("Please open this script and manually set APP_DIR = 'your_app_name'")
    exit(1)

print(f"📦 Detected Django application directory: {APP_DIR}")

# Define actual verified paths
TEMPLATES_DIR = None
for root, dirs, files in os.walk('.'):
    if 'templates' in dirs and not any(x in root for x in ['venv', '.git', 'env']):
        TEMPLATES_DIR = os.path.join(root, 'templates')
        break

if not TEMPLATES_DIR:
    TEMPLATES_DIR = os.path.join(APP_DIR, 'templates')
    os.makedirs(TEMPLATES_DIR, exist_ok=True)

URLS_FILE = os.path.join(APP_DIR, 'urls.py')
VIEWS_FILE = os.path.join(APP_DIR, 'views.py')

# Search for home.html anywhere in the templates directory
HOME_TEMPLATE = None
NAVBAR_TEMPLATE = None

for root, dirs, files in os.walk(TEMPLATES_DIR):
    if 'home.html' in files:
        HOME_TEMPLATE = os.path.join(root, 'home.html')
    if 'navbar.html' in files:
        NAVBAR_TEMPLATE = os.path.join(root, 'navbar.html')
    elif 'header.html' in files:
        NAVBAR_TEMPLATE = os.path.join(root, 'header.html')

if not HOME_TEMPLATE:
    # Fallback default location if not found
    HOME_TEMPLATE = os.path.join(TEMPLATES_DIR, 'home.html')

def create_template_from_section(section_id, filename, title):
    if not os.path.exists(HOME_TEMPLATE):
        section_html = ""
    else:
        with open(HOME_TEMPLATE, 'r') as f:
            content = f.read()
        pattern = rf'(<section[^>]*id=["\']{section_id}["\'][^>]*>.*? </section>)'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        section_html = match.group(1) if match else ""
    
    if section_html:
        new_template_content = f"""{{% extends 'base.html' %}}
{{% load static %}}

{{% block title %}}{title}{{% endblock %}}

{{% block content %}}
{section_html}
{{% endblock %}}"""
        print(f"✔ Extracted section '{section_id}' from home.html")
    else:
        new_template_content = f"""{{% extends 'base.html' %}}
{{% block content %}}
<div class="container mx-auto py-12 text-center" style="min-height: 60vh; display: flex; flex-direction: column; justify-content: center; align-items: center;">
    <h1 class="text-3xl font-bold mb-4">{title}</h1>
    <p class="text-gray-600">Welcome to the dedicated {title} page.</p>
</div>
{{% endblock %}}"""
        print(f"✔ Created clean page layout: {filename}")
        
    out_path = os.path.join(TEMPLATES_DIR, filename)
    with open(out_path, 'w') as out_f:
        out_f.write(new_template_content)

# Run extraction
print("\n--- Processing Templates ---")
create_template_from_section('about', 'about.html', 'About Us')
create_template_from_section('contact', 'contact.html', 'Contact Us')
create_template_from_section('blogs', 'blogs.html', 'Blogs')

# Update views.py
print("\n--- Updating views.py ---")
with open(VIEWS_FILE, 'r') as f:
    views_content = f.read()

new_views = """

def about_view(request):
    return render(request, 'about.html')

def contact_view(request):
    return render(request, 'contact.html')

def blogs_view(request):
    context = {}
    try:
        from .models import Blog
        context['blogs'] = Blog.objects.all()
    except Exception:
        pass
    return render(request, 'blogs.html', context)
"""

if 'about_view' not in views_content:
    with open(VIEWS_FILE, 'a') as f:
        f.write(new_views)
    print("✔ Appended view handlers safely.")

# Update urls.py
print("\n--- Updating urls.py ---")
with open(URLS_FILE, 'r') as f:
    urls_content = f.read()

new_urls = """
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('blogs/', views.blogs_view, name='blogs'),
"""

if "path('about/'" not in urls_content and 'path("about/"' not in urls_content:
    modified_urls = re.sub(r'(urlpatterns\s*=\s*\[.*?)(\s*\])', rf'\1{new_urls}\2', urls_content, flags=re.DOTALL)
    with open(URLS_FILE, 'w') as f:
        f.write(modified_urls)
    print("✔ Appended URL paths safely inside urlpatterns array.")

# Update Navbar if found
if NAVBAR_TEMPLATE and os.path.exists(NAVBAR_TEMPLATE):
    print("\n--- Updating Navbar Links ---")
    with open(NAVBAR_TEMPLATE, 'r') as f:
        nav_content = f.read()
    
    nav_content = nav_content.replace('href="#about"', 'href="{% url \'about\' %}"')
    nav_content = nav_content.replace('href="#contact"', 'href="{% url \'contact\' %}"')
    nav_content = nav_content.replace('href="#blogs"', 'href="{% url \'blogs\' %}"')
    
    with open(NAVBAR_TEMPLATE, 'w') as f:
        f.write(nav_content)
    print("✔ Navigation layouts updated safely.")

print("\n🚀 Refactor Complete! Ready to push.")