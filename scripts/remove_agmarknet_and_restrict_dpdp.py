"""
Script to eradicate Agmarknet completely and restrict DPDP visibility to only:
1. Home page (landing.html)
2. Step 5 Entity Consent (producer_wizard.js)
"""
import re
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def clean_landing_html():
    path = os.path.join(BASE_DIR, 'backend', 'apps', 'publicview', 'templates', 'publicview', 'landing.html')
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Agmarknet Grade A home stat
    content = content.replace('id="statGradeALabel">Agmarknet Grade A</div>', 'id="statGradeALabel">Certified Grade A Quality</div>')
    
    # 2. SVG animation text
    content = content.replace('GRADE: AGMARKNET A+', 'GRADE: CERTIFIED A+')
    content = content.replace('<text x="0" y="-3" font-size="4.5" font-weight="900" fill="#fef08a" text-anchor="middle">AGMARKNET</text>',
                              '<text x="0" y="-3" font-size="4.5" font-weight="900" fill="#fef08a" text-anchor="middle">CERTIFIED</text>')
    content = content.replace('Agmarknet Grade-A Stamp Seal', 'Certified Grade-A Quality Stamp')

    # 3. Flow step 2 description
    content = content.replace('Mandi collection, weight verification, Agmarknet grading.',
                              'Mandi collection, digital weight verification, quality assaying.')
    
    # 4. Trust pillar
    content = content.replace('Both dispatching and receiving operators must digitally sign off on net weights and Agmarknet grades.',
                              'Both dispatching and receiving operators must digitally sign off on net weights and certified quality grades.')
    content = content.replace('id="trust3Pill3">Agmarknet Verification</span>',
                              'id="trust3Pill3">Quality Assaying Verification</span>')
    content = content.replace('id="trustRibbonAgmark">Agmarknet Quality Grading</span>',
                              'id="trustRibbonAgmark">Certified Quality Grading</span>')
    
    # 5. Footer & portal role
    content = content.replace('id="footerLinkAgmarknet">Agmarknet Standards & APMC</span>',
                              'id="footerLinkAgmarknet">Agricultural Quality Standards</span>')
    content = content.replace('Verify gross weights on digital weighbridges, assign Agmarknet grades, and settle e-NAM auctions.',
                              'Verify gross weights on digital weighbridges, assign certified quality grades, and settle auctions.')
    content = content.replace('id="portalPill2B">Agmarknet Grade</span>',
                              'id="portalPill2B">Certified Grade</span>')
    
    # 6. Agmarknet in help section & ticker
    content = content.replace('authenticated farm origin, harvest date, and Agmarknet grade.',
                              'authenticated farm origin, harvest date, and certified quality grade.')
    content = content.replace('Agmarknet Grade A certified', 'Certified Grade A quality inspected')
    content = content.replace('Agmarknet Grade A', 'Certified Grade A')
    content = content.replace('Issue Agmarknet Crate QR Labels', 'Issue Certified Crate QR Labels')
    content = content.replace('label: \'Agmarknet Quality Grading\'', 'label: \'Quality Assaying & Grading\'')
    content = content.replace('Conduct physical examination and issue Agmarknet Grade A, B, or C quality certificate.',
                              'Conduct physical examination and issue Grade A, B, or C quality certificate.')

    # 7. Gov Modal agmarknet -> quality
    content = content.replace("title: 'Agmarknet Standards & APMC Assaying Framework'",
                              "title: 'National Agricultural Quality Assaying Framework'")
    content = content.replace('<strong>Agmarknet Quality & Grading Assaying:</strong> AnnaSutra strictly adheres to the Agricultural Produce (Grading and Marking) Act and standard APMC mandi assaying protocols.',
                              '<strong>National Quality & Grading Assaying:</strong> AnnaSutra strictly adheres to standardized agricultural assaying and grading protocols.')
    content = content.replace('https://agmarknet.gov.in/', '#')
    content = content.replace('Visit Agmarknet National Portal', 'Standard Quality Assaying Guidelines')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Cleaned landing.html")

def clean_lot_summary_and_not_found():
    for fname in ['lot_summary.html', 'lot_not_found.html']:
        path = os.path.join(BASE_DIR, 'backend', 'apps', 'publicview', 'templates', 'publicview', fname)
        if not os.path.exists(path):
            continue
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Agmarknet removals
        content = content.replace('Agmarknet Standards & APMC', 'Agricultural Quality Standards')
        content = content.replace('Agmarknet Standards & APMC Assaying Framework', 'National Quality Assaying Standards Framework')
        content = content.replace('assign Agmarknet grades', 'assign certified quality grades')
        content = content.replace('Agmarknet grade', 'quality grade')
        content = content.replace('Agmarknet Quality & Grading Assaying', 'Quality & Grading Assaying')
        content = content.replace('https://agmarknet.gov.in/', '#')
        content = content.replace('Visit Agmarknet National Portal', 'Quality Standards Protocol')
        content = content.replace('অ্যাগমার্কনেট মানদণ্ড ও এপিএমসি', 'কৃষি গুণমান মানদণ্ড ও এপিএমসি')
        content = content.replace('एगमार्कनेट मानक एवं एपीएमसी', 'कृषि गुणवत्ता मानक एवं एपीएमसी')

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Cleaned {fname}")

def clean_i18n_files():
    for rel_path in [
        os.path.join('backend', 'apps', 'publicview', 'static', 'publicview', 'js', 'annasutra_i18n.js'),
        os.path.join('static', 'publicview', 'js', 'annasutra_i18n.js')
    ]:
        path = os.path.join(BASE_DIR, rel_path)
        if not os.path.exists(path):
            continue
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Agmarknet replacements
        content = content.replace('Agmarknet Grade A', 'Certified Grade A')
        content = content.replace('Agmarknet grading', 'quality grading')
        content = content.replace('Agmarknet Verification', 'Quality Verification')
        content = content.replace('Agmarknet Quality Grading', 'Certified Quality Grading')
        content = content.replace('Agmarknet Standards & APMC', 'Agricultural Quality Standards')
        content = content.replace('Agmarknet Grade', 'Quality Grade')
        content = content.replace('assign Agmarknet grades', 'assign quality grades')

        # Regional agmarknet terms
        content = content.replace('অ্যাগমার্কনেট গ্রেড এ', 'প্রমাণিত গ্রেড এ')
        content = content.replace('অ্যাগমার্কনেট গুণমান গ্রেডিং', 'গুণমান গ্রেডিং')
        content = content.replace('অ্যাগমার্কনেট মানদণ্ড ও এপিএমসি', 'কৃষি গুণমান মানদণ্ড ও এপিএমসি')
        content = content.replace('এগમાર્કનેટ ગ્રેડ A', 'પ્રમાણિત ગ્રેડ A')
        content = content.replace('એગમાર્કનેટ ગ્રેડિંગ', 'ગુણવત્તા ગ્રેડિંગ')
        content = content.replace('એગમાર્કનેટ ધોરણો અને APMC', 'કૃષિ ગુણવત્તા ધોરણો અને APMC')
        content = content.replace('एगमार्कनेट मानक एवं एपीएमसी', 'कृषि गुणवत्ता मानक एवं एपीएमसी')
        content = content.replace('एगमार्कनेट ग्रेड ए', 'प्रमाणित ग्रेड ए')
        content = content.replace('एगमार्कनेट ग्रेडिंग', 'गुणवत्ता ग्रेडिंग')

        # Also sanitize DPDP outside home & entity consent:
        # role description for Admin
        content = re.sub(r'audit DPDP-encrypted documents', 'audit encrypted KYC documents', content)
        content = re.sub(r'DPDP-एनक्रिप्टेड कागदपत्रे', 'एनक्रिप्टेड कागदपत्रे', content)
        content = re.sub(r'DPDP-এনক্রিপ্টেড নথি', 'এনক্রিপ্টেড নথি', content)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Cleaned {rel_path}")

clean_landing_html()
clean_lot_summary_and_not_found()
clean_i18n_files()
print("Agmarknet and DPDP cleanup script executed successfully.")
