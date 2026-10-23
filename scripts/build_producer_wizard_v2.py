"""Builder for producer_wizard.js with full Harvest Lot Management, Checkboxes, Other Crops, Admin Trash, and Unlimited QR."""

import os
import shutil
import re

src_path = "backend/apps/publicview/static/publicview/js/producer_wizard.js"
with open(src_path, "r", encoding="utf-8") as f:
    js = f.read()

# 1. Update WIZARD_I18N for all three languages (en, hi, bn)
# Add keys for harvest lot management, delete producer, trash tab, and crop adder
extra_en_keys = """
      btnApproveEntity: 'Approve',
      btnDeleteProducer: 'Delete Producer Data',
      tabTrash: 'Trash',
      consoleHeading: 'Harvest Lot & Custody Ledger Console',
      btnRegisterLot: '+ Register New Harvest Lot',
      searchLotPh: 'Search lot code, crop, variety, or plot...',
      filterAllCrops: 'All Crops & Produce',
      filterAllPlots: 'All Land Parcels / Plots',
      filterAllCustody: 'All Custody States',
      statusInCustody: 'In Farm Custody',
      statusInTransit: 'In Transit (Locked)',
      statusHandoverDone: 'Handover Approved (Locked)',
      filterAllPayment: 'All Payment Statuses',
      paymentPending: 'Pending Settlement',
      paymentAdvance: 'Advance Received',
      paymentSettled: 'Fully Settled',
      sortLatest: 'Latest to Oldest',
      sortOldest: 'Oldest to Latest',
      sortQtyHigh: 'Quantity: High to Low',
      sortQtyLow: 'Quantity: Low to High',
      btnPrintQr: 'Print QR Labels',
      btnEditLot: 'Edit Harvest Lot',
      lblLockedNotice: 'Locked: Custody handover active. Immutability enforced by ledger.',
      emptyLotsTitle: 'No harvest lots recorded in custody yet',
      emptyLotsSub: 'Click the button above to register your first harvest lot and generate unique QR labels.',
      confirmDeletePrompt: 'To confirm moving this producer to Trash, type DELETE in capital letters below:',
      btnMoveToTrash: 'Move to Trash',
      btnRestoreProducer: 'Restore Producer',
      btnPurgeProducer: 'Purge Permanently',
      addOtherProduce: 'Other Produce / Fruits / Spices',
      customCropPh: 'Type fruit or crop name (e.g. Guava, Pomegranate, Turmeric)...',
      btnAddProduce: '+ Add Produce',
"""

extra_hi_keys = """
      btnApproveEntity: 'स्वीकृत करें',
      btnDeleteProducer: 'उत्पादक डेटा हटाएं',
      tabTrash: 'ट्रैश (कचरा)',
      consoleHeading: 'फसल लॉट एवं कस्टडी लेज़र कंसोल',
      btnRegisterLot: '+ नया फसल लॉट पंजीकृत करें',
      searchLotPh: 'लॉट कोड, फसल, किस्म या भूखंड खोजें...',
      filterAllCrops: 'सभी फसलें व उत्पाद',
      filterAllPlots: 'सभी भूमि / भूखंड',
      filterAllCustody: 'सभी कस्टडी स्थितियां',
      statusInCustody: 'खेत कस्टडी में',
      statusInTransit: 'पारगमन में (लॉक)',
      statusHandoverDone: 'हस्तांतरण स्वीकृत (लॉक)',
      filterAllPayment: 'सभी भुगतान स्थितियां',
      paymentPending: 'निपटान लंबित',
      paymentAdvance: 'अग्रिम प्राप्त',
      paymentSettled: 'पूर्णतः चुकता',
      sortLatest: 'नवीनतम से पुराना',
      sortOldest: 'पुराना से नवीनतम',
      sortQtyHigh: 'मात्रा: अधिक से कम',
      sortQtyLow: 'मात्रा: कम से अधिक',
      btnPrintQr: 'क्यूआर लेबल प्रिंट करें',
      btnEditLot: 'फसल लॉट संपादित करें',
      lblLockedNotice: 'लॉक: कस्टडी हस्तांतरण सक्रिय। अपरिवर्तनीय लेज़र द्वारा सुरक्षित।',
      emptyLotsTitle: 'कस्टडी में अभी कोई फसल लॉट दर्ज नहीं है',
      emptyLotsSub: 'अपना पहला फसल लॉट पंजीकृत करने और अद्वितीय क्यूआर लेबल बनाने के लिए ऊपर दिए गए बटन का उपयोग करें।',
      confirmDeletePrompt: 'इस उत्पादक को ट्रैश में स्थानांतरित करने के लिए नीचे DELETE लिखें:',
      btnMoveToTrash: 'ट्रैश में भेजें',
      btnRestoreProducer: 'उत्पादक पुनर्स्थापित करें',
      btnPurgeProducer: 'स्थायी रूप से हटाएं',
      addOtherProduce: 'अन्य उपज / फल / मसाले',
      customCropPh: 'फल या फसल का नाम लिखें (उदा. अमरूद, अनार, हल्दी)...',
      btnAddProduce: '+ फसल जोड़ें',
"""

extra_bn_keys = """
      btnApproveEntity: 'অনুমোদন করুন',
      btnDeleteProducer: 'উৎপাদক তথ্য মুছুন',
      tabTrash: 'ট্র্যাশ',
      consoleHeading: 'ফসল লট ও হেফাজত লেজার কনসোল',
      btnRegisterLot: '+ নতুন ফসল লট নিবন্ধন করুন',
      searchLotPh: 'লট কোড, ফসল বা প্লট খুঁজুন...',
      filterAllCrops: 'সকল ফসল ও উৎপাদিত দ্রব্য',
      filterAllPlots: 'সকল জমি / প্লট',
      filterAllCustody: 'সকল হেফাজত স্থিতি',
      statusInCustody: 'খামার হেফাজতে',
      statusInTransit: 'পরিবহনরত (লক)',
      statusHandoverDone: 'হস্তান্তর অনুমোদিত (লক)',
      filterAllPayment: 'সকল অর্থপ্রদান স্থিতি',
      paymentPending: 'নিষ্পত্তি বাকি',
      paymentAdvance: 'অগ্রিম গৃহীত',
      paymentSettled: 'সম্পূর্ণ পরিশোধিত',
      sortLatest: 'নতুন থেকে পুরাতন',
      sortOldest: 'পুরাতন থেকে নতুন',
      sortQtyHigh: 'পরিমাণ: বেশি থেকে কম',
      sortQtyLow: 'পরিমাণ: কম থেকে বেশি',
      btnPrintQr: 'QR লেবেল প্রিন্ট করুন',
      btnEditLot: 'ফসল লট সম্পাদনা করুন',
      lblLockedNotice: 'লক: হেফাজত হস্তান্তর সক্রিয়। অপরিবর্তনীয়।',
      emptyLotsTitle: 'হেফাজতে এখনও কোনো ফসল লট নিবন্ধিত নেই',
      emptyLotsSub: 'আপনার প্রথম ফসল লট নিবন্ধন করতে এবং অনন্য QR লেবেল তৈরি করতে উপরের বোতামটি ব্যবহার করুন।',
      confirmDeletePrompt: 'এই উৎপাদককে ট্র্যাশে সরাতে নিচে DELETE লিখুন:',
      btnMoveToTrash: 'ট্র্যাশে স্থানান্তর',
      btnRestoreProducer: 'উৎপাদক পুনরুদ্ধার',
      btnPurgeProducer: 'স্থায়ীভাবে মুছে ফেলুন',
      addOtherProduce: 'অন্যান্য ফলমূল ও মশলা',
      customCropPh: 'ফল বা ফসলের নাম লিখুন (যেমন পেয়ারা, বেদানা, হলুদ)...',
      btnAddProduce: '+ ফসল যোগ করুন',
"""

# Replace in WIZARD_I18N.en
js = js.replace(
    "btnApproveEntity: 'Approve & Issue Sovereign Code + 50 QR',",
    extra_en_keys.strip()
)

# Replace in WIZARD_I18N.hi
js = js.replace(
    "btnApproveEntity: 'स्वीकृत करें एवं आधिकारिक कोड + 50 QR जारी करें',",
    extra_hi_keys.strip()
)

# Replace in WIZARD_I18N.bn
js = js.replace(
    "btnApproveEntity: 'অনুমোদন করুন এবং কোড + ৫০টি QR জারি করুন',",
    extra_bn_keys.strip()
)

# Clean any 50 QR mentions from descriptions
js = js.replace("and your initial 50-QR label batch will be allocated upon administrative approval.", "and QR label issuance will be enabled upon administrative approval. Unlimited QR labels can be generated for your harvest lots.")
js = js.replace("और 50 क्यूआर लेबल आवंटित किए जाएंगे।", "आवंटित किए जाएंगे एवं प्रत्येक फसल लॉट के लिए असीमित क्यूआर कोड उत्पन्न किए जा सकते हैं।")
js = js.replace("এবং প্রাথমিক ৫০টি QR লেবেল বরাদ্দ করা হবে।", "হবে এবং ফসলের লটের জন্য সীমাহীন QR তৈরি করা যাবে।")

# 2. Expand CROPS_LIST with prominent Indian fruits & horticultural crops
expanded_crops = """  const CROPS_LIST = [
    { id: 'Tomato', icon: 'sprout', labels: { en: 'Tomato', hi: 'टमाटर', bn: 'টমেটো', as: 'বিলাহী', gu: 'ટામેટા', kn: 'ಟೊಮೆಟೊ', ml: 'തക്കാളി', mr: 'टोमॅटो', or: 'ଟମାଟୋ', pa: 'ਟਮਾਟਰ', ta: 'தக்காளி', te: 'టమాటా' } },
    { id: 'Potato', icon: 'sprout', labels: { en: 'Potato', hi: 'आलू', bn: 'আলু', as: 'আলু', gu: 'બટાકા', kn: 'ಆಲೂಗಡ್ಡೆ', ml: 'ഉരുളക്കിഴങ്ങ്', mr: 'बटाटा', or: 'ଆଳୁ', pa: 'ਆਲੂ', ta: 'உருளைக்கிழங்கு', te: 'బంగాళாదుంప' } },
    { id: 'Onion', icon: 'sprout', labels: { en: 'Onion', hi: 'प्याज', bn: 'পেঁয়াজ', as: 'পিঁয়াজ', gu: 'ડુંગળી', kn: 'ಈರುಳ್ಳಿ', ml: 'ഉള്ളി', mr: 'कांदा', or: 'ପିଆଜ', pa: 'ਪਿਆਜ਼', ta: 'வெங்காயம்', te: 'ఉల్లిপాయ' } },
    { id: 'Chilli', icon: 'sprout', labels: { en: 'Green Chilli', hi: 'हरी मिर्च', bn: 'কাঁচা লঙ্কা', as: 'কেঁচা জলকীয়া', gu: 'લીલા મરચાં', kn: 'ಹಸಿರು ಮೆಣಸಿನಕಾಯಿ', ml: 'പച്ചമുളക്', mr: 'हिरवी मिरची', or: 'କଞ୍ଚା ଲଙ୍କା', pa: 'ਹਰੀ ਮਿਰਚ', ta: 'பச்சை மிளகாய்', te: 'పచ్చిమిర్చి' } },
    { id: 'Cabbage', icon: 'sprout', labels: { en: 'Cabbage', hi: 'पत्तागोभी', bn: 'বাঁধাকপি', as: 'বন্ধাকবি', gu: 'કોબીજ', kn: 'ಎಲೆಕೋಸು', ml: 'കാബേജ്', mr: 'कोबी', or: 'ବନ୍ଧାକୋବି', pa: 'ਬੰਦਗੋਭੀ', ta: 'முட்டைக்கோஸ்', te: 'క్యాబేజీ' } },
    { id: 'Cauliflower', icon: 'sprout', labels: { en: 'Cauliflower', hi: 'फूलगोभी', bn: 'ফুলকপি', as: 'ফুলকবি', gu: 'ફ્લાવર', kn: 'ಹೂಕೋಸು', ml: 'കോളിഫ്ലവർ', mr: 'फ्लॉवर', or: 'ଫୁଲକୋବି', pa: 'ਫੁੱਲਗੋਭੀ', ta: 'காலிஃபிளவர்', te: 'కాలీఫ్లవర్' } },
    { id: 'Carrot', icon: 'sprout', labels: { en: 'Carrot', hi: 'गाजर', bn: 'গাজর', as: 'গাজৰ', gu: 'ગાજર', kn: 'ಕ್ಯಾರೆಟ್', ml: 'ക്യാരറ്റ്', mr: 'गाजर', or: 'ଗାଜର', pa: 'ਗਾਜਰ', ta: 'கேரட்', te: 'క్యారెట్' } },
    { id: 'Brinjal', icon: 'sprout', labels: { en: 'Brinjal', hi: 'बैंगन', bn: 'বেগুন', as: 'বেঙেনা', gu: 'રીંગણ', kn: 'ಬದನೆಕಾಯಿ', ml: 'വഴുതനങ്ങ', mr: 'वांगी', or: 'ବାଇଗଣ', pa: 'ਬੈਂਗਣ', ta: 'கத்திரிக்காய்', te: 'వంకాయ' } },
    { id: 'Rice', icon: 'wheat', labels: { en: 'Paddy / Rice', hi: 'धान / चावल', bn: 'ধান / চাল', as: 'ধান / চাউল', gu: 'ડાંગર / ચોખા', kn: 'ಭತ್ತ / ಅಕ್ಕಿ', ml: 'നെല്ല് / അരി', mr: 'भात / तांदूळ', or: 'ଧାନ / ଚାଉଳ', pa: 'ਝੋਨਾ / ਚਾਵਲ', ta: 'நெல் / அரிசி', te: 'వరి / బియ్యం' } },
    { id: 'Wheat', icon: 'wheat', labels: { en: 'Wheat', hi: 'गेहूं', bn: 'গম', as: 'ঘেঁহু', gu: 'ઘઉં', kn: 'ಗೋಧಿ', ml: 'ഗോതമ്പ്', mr: 'गहू', or: 'ଗହମ', pa: 'ਕਣਕ', ta: 'கோதுமை', te: 'గోధుమలు' } },
    { id: 'Mustard', icon: 'sprout', labels: { en: 'Mustard', hi: 'सरसों', bn: 'সর্ষে', as: 'সঁৰিয়হ', gu: 'રાઈ / সরસવ', kn: 'ಸಾಸಿವೆ', ml: 'കടുക്', mr: 'मोहरी', or: 'ସୋରିଷ', pa: 'ਸਰ੍ਹੋਂ', ta: 'கடுகு', te: 'ఆవాలు' } },
    { id: 'Banana', icon: 'sprout', labels: { en: 'Banana', hi: 'केला', bn: 'কলা', as: 'কল', gu: 'કેળા', kn: 'ಬಾಳೆಹಣ್ಣು', ml: 'വാഴപ്പഴം', mr: 'केळी', or: 'କଦଳୀ', pa: 'ਕੇਲਾ', ta: 'வாழைப்பழம்', te: 'అరటి' } },
    { id: 'Mango', icon: 'sprout', labels: { en: 'Mango', hi: 'आम', bn: 'আম', as: 'আম', gu: 'કેરી', kn: 'ಮಾವಿನಹಣ್ಣು', ml: 'മാമ്പഴം', mr: 'आंबा', or: 'ଆମ୍ବ', pa: 'ਅੰਬ', ta: 'மாம்பழம்', te: 'మామిడి' } },
    { id: 'Apple', icon: 'sprout', labels: { en: 'Apple', hi: 'सेब', bn: 'আপেল', as: 'আপেল', gu: 'સફરજન', kn: 'ಸೇಬು', ml: 'ആപ്പിൾ', mr: 'सफरचंद', or: 'ସେଓ', pa: 'ਸੇਬ', ta: 'ஆப்பிள்', te: 'ఆపిల్' } },
    { id: 'Guava', icon: 'sprout', labels: { en: 'Guava', hi: 'अमरूद', bn: 'পেয়ারা', as: 'মধুৰিআম', gu: 'જામફળ', kn: 'ಸೀಬೆಹಣ್ಣು', ml: 'പേരയ്ക്ക', mr: 'पेरू', or: 'ପିଜୁଳି', pa: 'ਅਮਰੂਦ', ta: 'கொய்யா', te: 'జామకాయ' } },
    { id: 'Pomegranate', icon: 'sprout', labels: { en: 'Pomegranate', hi: 'अनार', bn: 'বেদানা / ডালিম', as: 'ডালিম', gu: 'દાડમ', kn: 'ದಾಳಿಂಬೆ', ml: 'മാതളനാരങ്ങ', mr: 'डाळिंब', or: 'ଡାଳିମ୍ବ', pa: 'ਅਨਾਰ', ta: 'மாதுளை', te: 'దానిమ్మ' } },
    { id: 'Papaya', icon: 'sprout', labels: { en: 'Papaya', hi: 'पपीता', bn: 'পেঁপে', as: 'অমিতা', gu: 'પપૈયું', kn: 'ಪಪ್ಪಾಯಿ', ml: 'പപ്പായ', mr: 'पपई', or: 'ଅମୃତଭଣ୍ଡା', pa: 'ਪਪੀਤਾ', ta: 'பப்பாளி', te: 'బొప్పాయి' } },
    { id: 'Ginger', icon: 'sprout', labels: { en: 'Ginger', hi: 'अदरक', bn: 'আদা', as: 'আদা', gu: 'આદુ', kn: 'ಶುಂಠಿ', ml: 'ഇഞ്ചി', mr: 'आले', or: 'ଅଦା', pa: 'ਅਦਰਕ', ta: 'இஞ்சி', te: 'అల్లం' } },
    { id: 'Garlic', icon: 'sprout', labels: { en: 'Garlic', hi: 'लहसुन', bn: 'রসুন', as: 'নহৰু', gu: 'લસણ', kn: 'ಬೆಳ್ಳುಳ್ಳಿ', ml: 'വെളുത്തുള്ളി', mr: 'लसूण', or: 'ରସୁଣ', pa: 'ਲਸਣ', ta: 'பூண்டு', te: 'వెల్లుల్లి' } },
    { id: 'Turmeric', icon: 'sprout', labels: { en: 'Turmeric', hi: 'हल्दी', bn: 'হলুদ', as: 'হালধি', gu: 'હળદર', kn: 'ಅರಿಶಿನ', ml: 'മഞ്ഞൾ', mr: 'हळद', or: 'ହଳଦୀ', pa: 'ਹਲਦੀ', ta: 'மஞ்சள்', te: 'పసుపు' } },
    { id: 'GreenPeas', icon: 'sprout', labels: { en: 'Green Peas', hi: 'हरी मटर', bn: 'মটরশুঁটি', as: 'মটৰ', gu: 'વટાણા', kn: 'ಬಟಾಣಿ', ml: 'പട്ടாണി', mr: 'मटार', or: 'ମଟର', pa: 'ਮਟਰ', ta: 'பட்டாணி', te: 'బఠానీ' } }
  ];"""

old_crops_pattern = re.search(r"  const CROPS_LIST = \[[\s\S]*?\n  \];", js)
if old_crops_pattern:
    js = js[:old_crops_pattern.start()] + expanded_crops + js[old_crops_pattern.end():]

print("CROPS_LIST expanded to 21 common commodities")

# 3. Step 3 Markup: Replace plain chips with real checkboxes + custom produce adder
old_step3_crops = """        <div class="form-group">
          <label class="form-label">${escapeHtml(t.commodities)} <span class="req">*</span></label>
          <div class="crop-chips-grid">
            ${CROPS_LIST.map(c => {
              const isSelected = selectedCrops.includes(c.id);
              return `
                <div class="crop-chip-item ${isSelected ? 'selected' : ''}" onclick="toggleCropSelection('${c.id}', this)">
                  <span>${getIcon(c.icon, 15, isSelected ? '#047857' : '#64748b')}</span>
                  <span>${escapeHtml(getCropLabel(c.id))}</span>
                </div>
              `;
            }).join('')}
          </div>
        </div>"""

new_step3_crops = """        <div class="form-group">
          <label class="form-label">${escapeHtml(t.commodities)} <span class="req">*</span></label>
          <div class="crop-checkbox-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(170px, 1fr)); gap: 10px; margin-top: 8px;">
            ${CROPS_LIST.map(c => {
              const isSelected = selectedCrops.includes(c.id);
              return `
                <label class="crop-checkbox-card ${isSelected ? 'selected' : ''}" id="card_crop_${c.id}" style="display: flex; align-items: center; gap: 9px; padding: 10px 12px; background: ${isSelected ? '#ecfdf5' : '#ffffff'}; border: 1.5px solid ${isSelected ? '#047857' : '#e2e8f0'}; border-radius: 8px; cursor: pointer; transition: all 0.15s ease-in-out; user-select: none;">
                  <input type="checkbox" id="chk_crop_${c.id}" value="${c.id}" ${isSelected ? 'checked' : ''} onchange="toggleCropCheckbox('${c.id}', this.checked)" style="width: 17px; height: 17px; accent-color: #047857; cursor: pointer;" />
                  <span style="display: inline-flex; align-items: center; justify-content: center; width: 22px; height: 22px; background: ${isSelected ? '#d1fae5' : '#f8fafc'}; border-radius: 6px;">${getIcon(c.icon, 14, isSelected ? '#047857' : '#64748b')}</span>
                  <span style="font-size: 13px; font-weight: ${isSelected ? '700' : '600'}; color: ${isSelected ? '#065f46' : '#334155'};">${escapeHtml(getCropLabel(c.id))}</span>
                </label>
              `;
            }).join('')}
          </div>

          <!-- Other Produce / Custom Fruits / Spices Adder -->
          <div style="margin-top: 16px; background: #f8fafc; border: 1.5px dashed #cbd5e1; border-radius: 10px; padding: 14px;">
            <label style="display: block; font-size: 12.5px; font-weight: 700; color: #0b3d2e; margin-bottom: 6px;">
              <span>${getIcon('sprout', 15, '#047857')}</span> ${escapeHtml(t.addOtherProduce || 'Other Produce / Fruits / Spices (If unlisted above)')}
            </label>
            <div style="display: flex; gap: 8px;">
              <input type="text" id="inp_custom_crop" class="form-input" style="flex: 1;" placeholder="${escapeHtml(t.customCropPh || 'Type fruit or crop name (e.g. Guava, Pomegranate, Turmeric)...')}" onkeydown="if(event.key==='Enter'){event.preventDefault();addCustomCrop();}" />
              <button type="button" class="btn-wizard-action btn-wizard-draft" style="padding: 8px 16px; white-space: nowrap;" onclick="addCustomCrop()">
                ${escapeHtml(t.btnAddProduce || '+ Add Produce')}
              </button>
            </div>
            <div id="customCropsTagsContainer" style="margin-top: 10px; display: flex; flex-wrap: wrap; gap: 8px;">
              ${(selectedCrops.filter(id => !CROPS_LIST.some(c => c.id === id))).map(customName => `
                <span class="custom-crop-pill" style="display: inline-flex; align-items: center; gap: 6px; background: #ecfdf5; border: 1.5px solid #047857; color: #065f46; font-size: 12.5px; font-weight: 700; padding: 4px 10px; border-radius: 20px;">
                  <span>${getIcon('sprout', 13, '#047857')}</span>
                  <span>${escapeHtml(customName)}</span>
                  <button type="button" onclick="removeCustomCrop('${escapeHtml(customName)}')" style="background: transparent; border: none; cursor: pointer; color: #dc2626; font-size: 14px; font-weight: 900; line-height: 1; padding: 0 0 0 4px;" title="Remove">&times;</button>
                </span>
              `).join('')}
            </div>
          </div>
        </div>"""

if old_step3_crops in js:
    js = js.replace(old_step3_crops, new_step3_crops)
    print("Step 3 Crop checkboxes & custom adder integrated")

# Add handlers for checkboxes and custom crop adder
crop_helpers = """
  window.toggleCropCheckbox = function (cropId, isChecked) {
    if (!wizardState.selectedCrops) wizardState.selectedCrops = [];
    const idx = wizardState.selectedCrops.indexOf(cropId);
    if (isChecked && idx === -1) {
      wizardState.selectedCrops.push(cropId);
    } else if (!isChecked && idx > -1) {
      wizardState.selectedCrops.splice(idx, 1);
    }
    const card = document.getElementById('card_crop_' + cropId);
    if (card) {
      if (isChecked) {
        card.classList.add('selected');
        card.style.background = '#ecfdf5';
        card.style.borderColor = '#047857';
      } else {
        card.classList.remove('selected');
        card.style.background = '#ffffff';
        card.style.borderColor = '#e2e8f0';
      }
    }
  };

  window.addCustomCrop = function () {
    const inp = document.getElementById('inp_custom_crop');
    if (!inp) return;
    const name = inp.value.trim();
    if (!name) return;
    if (!wizardState.selectedCrops) wizardState.selectedCrops = [];
    if (!wizardState.selectedCrops.includes(name)) {
      wizardState.selectedCrops.push(name);
    }
    inp.value = '';
    const container = document.getElementById('customCropsTagsContainer');
    if (container) {
      const customList = wizardState.selectedCrops.filter(id => !CROPS_LIST.some(c => c.id === id));
      container.innerHTML = customList.map(customName => `
        <span class="custom-crop-pill" style="display: inline-flex; align-items: center; gap: 6px; background: #ecfdf5; border: 1.5px solid #047857; color: #065f46; font-size: 12.5px; font-weight: 700; padding: 4px 10px; border-radius: 20px;">
          <span>${getIcon('sprout', 13, '#047857')}</span>
          <span>${escapeHtml(customName)}</span>
          <button type="button" onclick="removeCustomCrop('${escapeHtml(customName)}')" style="background: transparent; border: none; cursor: pointer; color: #dc2626; font-size: 14px; font-weight: 900; line-height: 1; padding: 0 0 0 4px;" title="Remove">&times;</button>
        </span>
      `).join('');
    }
  };

  window.removeCustomCrop = function (cropName) {
    if (!wizardState.selectedCrops) return;
    const idx = wizardState.selectedCrops.indexOf(cropName);
    if (idx > -1) {
      wizardState.selectedCrops.splice(idx, 1);
    }
    const container = document.getElementById('customCropsTagsContainer');
    if (container) {
      const customList = wizardState.selectedCrops.filter(id => !CROPS_LIST.some(c => c.id === id));
      container.innerHTML = customList.map(customName => `
        <span class="custom-crop-pill" style="display: inline-flex; align-items: center; gap: 6px; background: #ecfdf5; border: 1.5px solid #047857; color: #065f46; font-size: 12.5px; font-weight: 700; padding: 4px 10px; border-radius: 20px;">
          <span>${getIcon('sprout', 13, '#047857')}</span>
          <span>${escapeHtml(customName)}</span>
          <button type="button" onclick="removeCustomCrop('${escapeHtml(customName)}')" style="background: transparent; border: none; cursor: pointer; color: #dc2626; font-size: 14px; font-weight: 900; line-height: 1; padding: 0 0 0 4px;" title="Remove">&times;</button>
        </span>
      `).join('');
    }
  };
"""

js += crop_helpers

with open(src_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(js)

print("producer_wizard.js updated with crop helpers")
