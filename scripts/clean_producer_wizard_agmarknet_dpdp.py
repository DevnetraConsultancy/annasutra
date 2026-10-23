"""
Update producer_wizard.js to:
1. Eradicate Agmarknet (certNone)
2. Remove DPDP references from Step 2 photoHint, Step 2 aadhaarNotice, Admin queue subheader,
   while preserving DPDP in Step 5 (entity statutory consent) and landing page.
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
wizard_path = os.path.join(BASE_DIR, 'backend', 'apps', 'publicview', 'static', 'publicview', 'js', 'producer_wizard.js')

with open(wizard_path, 'r', encoding='utf-8') as f:
    c = f.read()

# EN
c = c.replace("photoHint: 'Clear passport or farm portrait. EXIF metadata automatically scrubbed for DPDP compliance.'",
              "photoHint: 'Clear passport or farm portrait. EXIF metadata automatically scrubbed for citizen privacy.'")
c = c.replace("certNone: 'Standard Commercial Cultivation (Agmarknet)'",
              "certNone: 'Standard Commercial Cultivation'")
c = c.replace("aadhaarNotice: 'Under DPDP & UIDAI regulations, full Aadhaar is never collected or stored.'",
              "aadhaarNotice: 'Under statutory UIDAI regulations, full Aadhaar is never collected or stored.'")
c = c.replace("adminQueueSub: 'Inspect submitted KYC, farm plot boundaries, and DPDP consent to approve entities and issue sovereign codes.'",
              "adminQueueSub: 'Inspect submitted KYC, farm plot boundaries, and statutory consent to approve entities and issue sovereign codes.'")

# HI
c = c.replace("photoHint: 'स्पष्ट पासपोर्ट या खेत की तस्वीर। डीपीडीपी अनुपालन हेतु EXIF मेटाडेटा स्वतः हटाया जाता है।'",
              "photoHint: 'स्पष्ट पासपोर्ट या खेत की तस्वीर। गोपनीयता सुरक्षा हेतु EXIF मेटाडेटा स्वतः हटाया जाता है।'")
c = c.replace("certNone: 'मानक व्यावसायिक खेती (एगमार्कनेट)'",
              "certNone: 'मानक व्यावसायिक खेती'")
c = c.replace("aadhaarNotice: 'डीपीडीपी नियमों के तहत पूर्ण आधार नंबर कभी संग्रहीत नहीं किया जाता है।'",
              "aadhaarNotice: 'वैधानिक यूआईडीएआई नियमों के तहत पूर्ण आधार नंबर कभी संग्रहीत नहीं किया जाता है।'")

# BN
c = c.replace("photoHint: 'স্পষ্ট পাসপোর্ট বা খামারের ছবি। ডিপিডিপি সম্মতির জন্য EXIF মেটাডাটা স্বয়ংক্রিয়ভাবে মুছে ফেলা হয়।'",
              "photoHint: 'স্পষ্ট পাসপোর্ট বা খামারের ছবি। গোপনীয়তা রক্ষার জন্য EXIF মেটাডাটা স্বয়ংক্রিয়ভাবে মুছে ফেলা হয়।'")
c = c.replace("certNone: 'মানক বাণিজ্যিক চাষ (অ্যাগমার্কনেট)'",
              "certNone: 'মানক বাণিজ্যিক চাষ'")
c = c.replace("aadhaarNotice: 'ডিপিডিপি বিধিমালার আওতায় সম্পূর্ণ ১২-অঙ্কের আধার কখনো চাওয়া বা সংরক্ষণ করা হয় না।'",
              "aadhaarNotice: 'বিধিবদ্ধ ইউআইডিএআই বিধিমালার আওতায় সম্পূর্ণ ১২-অঙ্কের আধার কখনো চাওয়া বা সংরক্ষণ করা হয় না।'")

with open(wizard_path, 'w', encoding='utf-8') as f:
    f.write(c)

print("producer_wizard.js Agmarknet & DPDP hints cleaned successfully.")
