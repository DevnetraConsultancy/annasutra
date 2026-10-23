"""
Clean all remaining Agmarknet references across regional languages and HTML templates.
"""
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 1. Update landing.html
landing_path = os.path.join(BASE_DIR, 'backend', 'apps', 'publicview', 'templates', 'publicview', 'landing.html')
with open(landing_path, 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace("footerLinkAgmarknet: \"Agmarknet Standards & APMC\",", "footerLinkAgmarknet: \"Agricultural Quality Standards\",")
c = c.replace("trustRibbonAgmark: \"Agmarknet Quality Grading\",", "trustRibbonAgmark: \"Certified Quality Grading\",")
c = c.replace("inspect Agmarknet quality grade, and dispatch to Wholesaler.", "inspect quality grade, and dispatch to Wholesaler.")
c = c.replace("openGovModal('agmarknet')", "openGovModal('quality')")
c = c.replace("agmarknet: {", "quality: {")
c = c.replace("// 5. Agmarknet Grade-A verification stamp bounces down", "// 5. Certified Grade-A verification stamp bounces down")

with open(landing_path, 'w', encoding='utf-8') as f:
    f.write(c)

# 2. Update lot_summary.html and lot_not_found.html
for fname in ['lot_summary.html', 'lot_not_found.html']:
    p = os.path.join(BASE_DIR, 'backend', 'apps', 'publicview', 'templates', 'publicview', fname)
    if not os.path.exists(p):
        continue
    with open(p, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace("openGovModal('agmarknet')", "openGovModal('quality')")
    content = content.replace("agmarknet: {", "quality: {")
    with open(p, 'w', encoding='utf-8') as f:
        f.write(content)

# 3. Update all regional strings in annasutra_i18n.js
for rel in [
    os.path.join('backend', 'apps', 'publicview', 'static', 'publicview', 'js', 'annasutra_i18n.js'),
    os.path.join('static', 'publicview', 'js', 'annasutra_i18n.js')
]:
    p = os.path.join(BASE_DIR, rel)
    if not os.path.exists(p):
        continue
    with open(p, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace all occurrences of Agmarknet in remaining regional languages
    content = re.sub(r'["\']footerLinkAgmarknet["\']:\s*["\'][^"\']*["\']', '"footerLinkAgmarknet": "Agricultural Quality Standards"', content)
    content = re.sub(r'["\']statGradeALabel["\']:\s*["\'][^"\']*["\']', '"statGradeALabel": "Certified Grade A"', content)
    content = re.sub(r'["\']flowStep2Desc["\']:\s*["\'][^"\']*["\']', '"flowStep2Desc": "Mandi collection, weight verification, quality assaying."', content)
    content = re.sub(r'["\']trustRibbonAgmark["\']:\s*["\'][^"\']*["\']', '"trustRibbonAgmark": "Certified Quality Grading"', content)
    
    with open(p, 'w', encoding='utf-8') as f:
        f.write(content)

# 4. Sync producer_wizard.js to static/ and staticfiles/
import shutil
src_wiz = os.path.join(BASE_DIR, 'backend', 'apps', 'publicview', 'static', 'publicview', 'js', 'producer_wizard.js')
dst_wiz = os.path.join(BASE_DIR, 'static', 'publicview', 'js', 'producer_wizard.js')
shutil.copyfile(src_wiz, dst_wiz)
print("Deep eradication of Agmarknet completed successfully.")
