import os
import re

TEMPLATES_DIR = os.path.join('core', 'templates', 'core')
HOME_TEMPLATE = os.path.join(TEMPLATES_DIR, 'home.html')

if not os.path.exists(HOME_TEMPLATE):
    print(f"❌ Error: {HOME_TEMPLATE} not found.")
    exit(1)

with open(HOME_TEMPLATE, 'r', encoding='utf-8') as f:
    home_html = f.read()

cleaned_html = home_html

# The targeted sections to remove entirely from the homepage layout
sections_to_remove = ['about', 'blog', 'contact']

print("--- Starting Homepage Content Cleanup Engine ---")

for target_id in sections_to_remove:
    # 1. Try removing via standard tag block regex pattern match
    pattern = rf'(<(section|div)[^>]*id=["\']{target_id}["\'][^>]*>.*?</\2>)'
    match = re.search(pattern, cleaned_html, re.DOTALL | re.IGNORECASE)
    
    if match:
        cleaned_html = re.sub(pattern, '', cleaned_html, flags=re.DOTALL | re.IGNORECASE)
        print(f"✂ Removed section layout block: id='{target_id}'")
    else:
        # 2. Fallback: Line by line removal scan if custom structural nesting styles are wrapped around it
        lines = cleaned_html.split('\n')
        start_idx = -1
        end_idx = -1
        tag_type = "div"
        
        for idx, line in enumerate(lines):
            if f'id="{target_id}"' in line or f"id='{target_id}'" in line:
                start_idx = idx
                if '<section' in line: tag_type = "section"
            if start_idx != -1 and f'</{tag_type}>' in line:
                end_idx = idx
                break
                
        if start_idx != -1 and end_idx != -1:
            del lines[start_idx:end_idx + 1]
            cleaned_html = '\n'.join(lines)
            print(f"✂ Removed section via fallback scanner block: id='{target_id}'")
        else:
            print(f"⚠ Could not locate section element for id='{target_id}' on homepage to remove.")

# Save the final pristine cleaned home template file back out
with open(HOME_TEMPLATE, 'w', encoding='utf-8') as f:
    f.write(cleaned_html)

print("\n🚀 Homepage optimized! Old sections completely stripped.")