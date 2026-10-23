"""
Integrate Dual-Tab Producer Console and 4-Chart Harvest Lot Analytics Dashboard into producer_wizard.js.
"""
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
wizard_path = os.path.join(BASE_DIR, 'backend', 'apps', 'publicview', 'static', 'publicview', 'js', 'producer_wizard.js')

with open(wizard_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add i18n entries for tabs and analytics
i18n_en_add = """      tabHarvestLedger: 'Harvest Lots & Custody Ledger',
      tabAnalytics: 'Analytics & Farm Insights',
      periodAllLots: 'All Recorded Lots',
      periodLast30: 'Last 30 Days',
      periodLast90: 'Last 90 Days',
      periodSeason: 'Current Season (Rabi 2026-27)',
      statGrossValuation: 'Gross Crop Valuation',
      statRealizedRevenue: 'Realized Revenue (Bank)',
      statGradeARate: 'Grade A Quality Ratio',
      statAvgPrice: 'Average Realized Price',
      statActiveOnFarm: 'Active Farm Custody',
      chartCropShare: 'Crop Volume & Valuation Share',
      chartYieldTimeline: 'Harvest Yield Cadence Timeline',
      chartCustodyPipeline: 'Custody & Logistics Pipeline Flow',
      chartPaymentHealth: 'Commercial Payment & Settlement Health',
      btnToggleWeight: 'By Weight (kg)',
      btnToggleValue: 'By Value (₹)',
      noAnalyticsLots: 'No harvest lots recorded yet. Register your first lot to generate yield analytics!',"""

i18n_hi_add = """      tabHarvestLedger: 'फसल लॉट एवं कस्टडी लेज़र',
      tabAnalytics: 'एनालिटिक्स एवं कृषि अंतर्दृष्टि',
      periodAllLots: 'सभी दर्ज लॉट',
      periodLast30: 'पिछले 30 दिन',
      periodLast90: 'पिछले 90 दिन',
      periodSeason: 'वर्तमान सीज़न (रबी 2026-27)',
      statGrossValuation: 'कुल फसल मूल्यांकन',
      statRealizedRevenue: 'प्राप्त भुगतान (बैंक)',
      statGradeARate: 'ग्रेड ए गुणवत्ता दर',
      statAvgPrice: 'औसत प्राप्त मूल्य',
      statActiveOnFarm: 'खेत में सक्रिय कस्टडी',
      chartCropShare: 'फसल मात्रा एवं मूल्य हिस्सेदारी',
      chartYieldTimeline: 'फसल कटाई समयरेखा',
      chartCustodyPipeline: 'कस्टडी एवं लॉजिस्टिक्स पाइपलाइन',
      chartPaymentHealth: 'भुगतान एवं वाणिज्यिक स्थिति',
      btnToggleWeight: 'मात्रा अनुसार (किलो)',
      btnToggleValue: 'मूल्य अनुसार (₹)',
      noAnalyticsLots: 'अभी तक कोई फसल लॉट दर्ज नहीं है। एनालिटिक्स देखने के लिए नया लॉट जोड़ें!',"""

i18n_bn_add = """      tabHarvestLedger: 'ফসল লট ও হেফাজত লেজার',
      tabAnalytics: 'বিশ্লেষণ ও খামার অন্তর্দৃষ্টি',
      periodAllLots: 'সকল রেকর্ডকৃত লট',
      periodLast30: 'বিগত ৩০ দিন',
      periodLast90: 'বিগত ৯০ দিন',
      periodSeason: 'বর্তমান মরশুম (রবি ২০২৬-২৭)',
      statGrossValuation: 'মোট ফসল মূল্যায়ন',
      statRealizedRevenue: 'প্রাপ্ত অর্থ (ব্যাঙ্ক)',
      statGradeARate: 'গ্রেড এ গুণমান অনুপাত',
      statAvgPrice: 'গড় বিক্রয় মূল্য',
      statActiveOnFarm: 'খামারে সক্রিয় হেফাজত',
      chartCropShare: 'ফসল উৎপাদন ও মূল্য অনুপাত',
      chartHarvestTimeline: 'ফসল কাটার সময়রেখা',
      chartCustodyPipeline: 'হেফাজত ও লজিস্টিকস পাইপলাইন',
      chartPaymentHealth: 'পেমেন্ট ও বাণিজ্যিক স্থিতি',
      btnToggleWeight: 'ওজন অনুযায়ী (কেজি)',
      btnToggleValue: 'মূল্য অনুযায়ী (₹)',
      noAnalyticsLots: 'এখনও কোনো ফসল লট নিবন্ধিত হয়নি। অ্যানালিটিক্স দেখতে নতুন লট যোগ করুন!',"""

# Inject i18n
code = code.replace("consoleHeading: 'Harvest Lot & Custody Ledger Console',",
                    f"consoleHeading: 'Harvest Lot & Custody Ledger Console',\n{i18n_en_add}")
code = code.replace("consoleHeading: 'फसल लॉट एवं कस्टडी लेज़र कंसोल',",
                    f"consoleHeading: 'फसल लॉट एवं कस्टडी लेज़र कंसोल',\n{i18n_hi_add}")
code = code.replace("consoleHeading: 'ফসল লট ও হেফাজত লেজার কনসোল',",
                    f"consoleHeading: 'ফসল লট ও হেফাজত লেজার কনসোল',\n{i18n_bn_add}")

print("i18n keys injected.")
with open(wizard_path, 'w', encoding='utf-8') as f:
    f.write(code)
