"""Update landing.html to wipe all fake batches and sanitize ticker events."""

with open("backend/apps/publicview/templates/publicview/landing.html", "r", encoding="utf-8") as f:
    landing = f.read()

import re

# 1. Replace all batches: [ ... ] inside roleDefinitions with batches: []
# Pattern matches batches:\s*\[[\s\S]*?\]
landing = re.sub(r"batches:\s*\[[\s\S]*?\]", "batches: []", landing)

# 2. Sanitize line 2233
landing = landing.replace(
    "[00:14:02 IST] Mandi APMC Azadpur attested 1,200 Kg Alphonso Mango (Lot #LOT-VERIFIED-01) • Hash: 0x9e8a...3f12 • Custody transferred to Aggregator",
    "[00:14:02 IST] Digital weighbridge gross weight attested • Cryptographic hash chained • e-NAM settlement confirmed"
)

# 3. Sanitize tickerEvents
landing = landing.replace(
    '"Mandi APMC Azadpur attested 1,200 Kg Alphonso Mango (Lot #LOT-VERIFIED-01) • Hash: 0x9e8a...3f12 • Custody to Aggregator",',
    '"Digital weighbridge gross weight attested • Cryptographic hash chained • e-NAM settlement confirmed",'
)
landing = landing.replace(
    '"Bardhaman Organic FPO registered 750 Kg Hybrid Tomato (Lot #LOT-VERIFIED-02) • Plot B-4 Geofence • Hash: 0x3d41...b891",',
    '"Farmer producer harvest registered • GPS geofence verified • Immutable genesis ledger hash chained",'
)
landing = landing.replace(
    '"मंडी एपीएमसी आजादपुर ने 1,200 किग्रा अल्फांसो आम प्रमाणित किया (लॉट #LOT-VERIFIED-01) • हैश: 0x9e8a...3f12 • संग्रहकर्ता को कस्टडी",',
    '"डिजिटल वेज-ब्रिज सकल भार सत्यापित • क्रिप्टोग्राफिक हैश शृंखलाबद्ध • ई-नाम निपटान प्रमाणित",'
)
landing = landing.replace(
    '"बर्धमान ऑर्गेनिक एफपीओ ने 750 किग्रा हाइब्रिड टमाटर पंजीकृत किया (लॉट #LOT-VERIFIED-02) • प्लॉट बी-4 • हैश: 0x3d41...b891",',
    '"किसान उत्पादक फसल पंजीकृत • जीपीएस जियोफेंस सत्यापित • अपरिवर्तनीय जेनेसिस लेज़र हैश",'
)
landing = landing.replace(
    '"মণ্ডি এপিএমসি আজাদপুর ১,২০০ কেজি আলফানসো আম প্রত্যয়িত করেছে (লট #LOT-VERIFIED-01) • হ্যাশ: 0x9e8a...3f12 • সংগ্রহকারীর নিকট হেফাজত",',
    '"ডিজিটাল ওয়েজ-ব্রিজ ওজন যাচাই সম্পন্ন • ক্রিপ্টোগ্রাফিক হ্যাশ শৃঙ্খলিত • ই-নাম নিষ্পত্তি প্রত্যয়িত",'
)
landing = landing.replace(
    '"বর্ধমান অর্গানিক এফপিও ৭৫০ কেজি হাইব্রিড টমেটো নিবন্ধন করেছে (লট #LOT-VERIFIED-02) • প্লট বি-৪ • হ্যাশ: 0x3d41...b891",',
    '"কৃষক উৎপাদক ফসল নিবন্ধিত • জিপিএস জিওফেন্স যাচাইকৃত • অপরিবর্তনীয় জেনেসিস লেজার হ্যাশ",'
)

with open("backend/apps/publicview/templates/publicview/landing.html", "w", encoding="utf-8", newline="\n") as f:
    f.write(landing)

print("landing.html cleaned of all mock batches and fake ticker items")
