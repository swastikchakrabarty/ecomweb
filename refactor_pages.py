import os
import re

# Verified structure settings
TEMPLATES_DIR = os.path.join('core', 'templates', 'core')
HOME_TEMPLATE = os.path.join(TEMPLATES_DIR, 'home.html')
FOOTER_TEMPLATE = os.path.join(TEMPLATES_DIR, 'base.html') # Check if quicklinks live here or in a separate footer.html

def extract_and_build_page(section_id, filename, title):
    if not os.path.exists(HOME_TEMPLATE):
        print(f"❌ Error: {HOME_TEMPLATE} not found.")
        return
    
    with open(HOME_TEMPLATE, 'r', encoding='utf-8') as f:
        home_content = f.read()
    
    # Isolate target section by searching for the opening tag up to its closing tag pair matching the ID
    # This captures the exact original HTML styling, Tailwind rules, and structural blocks
    pattern = rf'(<section[^>]*id=["\']{section_id}["\'][^>]*>.*? </section>)'
    match = re.search(pattern, home_content, re.DOTALL | re.IGNORECASE)
    
    if match:
        section_html = match.group(1)
        print(f"✔ Successfully extracted the original layout data for ID: {section_id}")
    else:
        # Fallback to general container scan if standard <section> wrapper variants are used
        pattern_fallback = rf'(<div[^>]*id=["\']{section_id}["\'][^>]*>.*?</div>)'
        match_fallback = re.search(pattern_fallback, home_content, re.DOTALL | re.IGNORECASE)
        if match_fallback:
            section_html = match_fallback.group(1)
            print(f"✔ Successfully extracted layout via fallback for ID: {section_id}")
        else:
            print(f"⚠ Could not isolate content section for ID: {section_id}. Creating default wrapper.")
            section_html = f'<div class="container mx-auto py-12 text-center"><h1 class="text-3xl font-bold">{title}</h1></div>'

    # Package structure matching core/base.html inheritance
    page_code = f"""{{% extends 'core/base.html' %}}
{{% load static %}}

{{% block title %}}{title}{{% endblock %}}

{{% block content %}}
{section_html}
{{% endblock %}}"""

    out_path = os.path.join(TEMPLATES_DIR, filename)
    with open(out_path, 'w', encoding='utf-8') as out_f:
        out_f.write(page_code)
    print(f"🎉 Fully built template file written: {out_path}")

print("--- Starting Full Content Extraction Engine ---")
extract_and_build_page('about', 'about.html', 'About Us')
extract_and_build_page('contact', 'contact.html', 'Contact Us')
extract_and_build_page('blog', 'blogs.html', 'Blogs') # Matches your exact #blog ID observed in screencast

# Update Quick Links inside base / footer templates if present
for target_file in [FOOTER_TEMPLATE, os.path.join(TEMPLATES_DIR, 'footer.html')]:
    if os.path.exists(target_file):
        print(f"\n--- Cleaning Quick Links layout in: {target_file} ---")
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Swapping out layout bindings to call active Django paths
        updated = content.replace('href="#about"', 'href="{% url \'about\' %}"')
        updated = updated.replace('href="{% url \'home\' %}#about"', 'href="{% url \'about\' %}"')
        
        updated = updated.replace('href="#blog"', 'href="{% url \'blogs\' %}"')
        updated = updated.replace('href="{% url \'home\' %}#blog"', 'href="{% url \'blogs\' %}"')
        
        updated = updated.replace('href="#contact"', 'href="{% url \'contact\' %}"')
        updated = updated.replace('href="{% url \'home\' %}#contact"', 'href="{% url \'contact\' %}"')
        
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(updated)
        print("✔ Quick Links paths safely updated to new standalone endpoints.")

print("\n🚀 Layout extraction and link optimization successfully finalized!")