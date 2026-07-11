import os
import re

TEMPLATES_DIR = os.path.join('core', 'templates', 'core')
HOME_TEMPLATE = os.path.join(TEMPLATES_DIR, 'home.html')

if not os.path.exists(HOME_TEMPLATE):
    print(f"❌ Error: {HOME_TEMPLATE} not found. Run from project root.")
    exit(1)

with open(HOME_TEMPLATE, 'r', encoding='utf-8') as f:
    home_html = f.read()

def extract_by_id_clean(target_id, filename, title):
    # Matches any tag string starting with id="target" or id='target' until its closing context block safely
    pattern = rf'(<(section|div)[^>]*id=["\']{target_id}["\'][^>]*>.*?</\2>)'
    match = re.search(pattern, home_html, re.DOTALL | re.IGNORECASE)
    
    if match:
        extracted_content = match.group(1)
        print(f"✔ Isolated exact inner layouts for: {target_id}")
    else:
        # Fallback raw line splitting if custom attributes wrap the markup block
        lines = home_html.split('\n')
        captured = []
        inside = False
        tag_type = "div"
        
        for line in lines:
            if f'id="{target_id}"' in line or f"id='{target_id}'" in line:
                inside = True
                if '<section' in line: tag_type = "section"
            if inside:
                captured.append(line)
                if f'</{tag_type}>' in line and len(captured) > 1:
                    inside = False
                    break
        
        if captured:
            extracted_content = '\n'.join(captured)
            print(f"✔ Extracted target content via line-scan layer for: {target_id}")
        else:
            print(f"⚠ Could not isolate block for '{target_id}'. Creating empty grid container.")
            extracted_content = f'<div class="container mx-auto py-24 text-center"><h1 class="text-3xl font-bold">{title}</h1></div>'

    page_markup = f"""{{% extends 'core/base.html' %}}
{{% load static %}}

{{% block title %}}{title}{{% endblock %}}

{{% block content %}}
{extracted_content}
{{% endblock %}}"""

    out_path = os.path.join(TEMPLATES_DIR, filename)
    with open(out_path, 'w', encoding='utf-8') as out_f:
        out_f.write(page_markup)
    print(f"🎉 File updated: {out_path}\n")

print("--- Running Native String Parsing Extraction Engine ---")
extract_by_id_clean('about', 'about.html', 'About Us')
extract_by_id_clean('blog', 'blogs.html', 'Blogs')
extract_by_id_clean('contact', 'contact.html', 'Contact Us')

print("🚀 Complete! No external pip installations needed.")