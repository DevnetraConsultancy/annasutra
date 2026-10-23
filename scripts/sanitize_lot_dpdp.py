"""
Sanitize DPDP from lot_summary.html and lot_not_found.html.
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

for fname in ['lot_summary.html', 'lot_not_found.html']:
    p = os.path.join(BASE_DIR, 'backend', 'apps', 'publicview', 'templates', 'publicview', fname)
    if not os.path.exists(p):
        continue
    with open(p, 'r', encoding='utf-8') as f:
        c = f.read()

    c = c.replace('DPDP Act 2023 Policy & Notice', 'Privacy Policy & Citizen Protection')
    c = c.replace('DPDP Act 2023 Compliance', 'Data Privacy & Protection')
    c = c.replace('Digital Personal Data Protection Notice', 'Privacy & Security Notice')
    c = c.replace('DPDP Act 2023 protected food security', 'cryptographically protected food security')
    c = c.replace('audit DPDP encrypted credentials', 'audit encrypted credentials')
    c = c.replace('डीपीडीपी अधिनियम 2023 नीति एवं नोटिस', 'गोपनीयता नीति एवं नागरिक सुरक्षा')
    c = c.replace('डीपीडीपी अधिनियम 2023 अनुपालन', 'डेटा गोपनीयता एवं संरक्षण')
    c = c.replace('ডিপিডিপি আইন ২০২৩ নীতি ও বিজ্ঞপ্তি', 'গোপনীয়তা নীতি ও নাগরিক সুরক্ষা')
    c = c.replace('ডিপিডিপি আইন ২০২৩ সম্মতি', 'তথ্য গোপনীয়তা ও সুরক্ষা')
    c = c.replace('Grievance Redressal Officer (DPDP Act 2023)', 'Grievance Redressal Officer (Privacy Protection)')

    with open(p, 'w', encoding='utf-8') as f:
        f.write(c)
    print(f"Sanitized DPDP in {fname}")
