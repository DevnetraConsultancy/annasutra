/**
 * AnnaSutra Producer Registration Wizard & Admin Verification Console
 * Full 5-stage onboarding, Leaflet polygon mapping, encrypted identity, statutory DPDP consent,
 * Verified Producer Console, and Administrative Verification Portal.
 */

(function () {
  'use strict';
  function getIcon(name, size, color, stroke) {
    if (window.renderUniformIcon) return window.renderUniformIcon(name, size, color, stroke);
    return '';
  }

  const WIZARD_I18N = {
    en: {
      roleProducer: 'Producer',
      roleAdmin: 'Admin Verifier',
      workspaceTitleProducer: 'Producer Registration & Operational Console',
      workspaceTitleAdmin: 'Administrative Verification & QR Issuance Portal',
      stepTab1: '1. Basic Info',
      stepTab2: '2. Farm Plots',
      stepTab3: '3. Cultivation',
      stepTab4: '4. Identity & Bank',
      stepTab5: '5. Consent & Review',
      step1Title: 'Basic Producer & Farm Details',
      step1Desc: 'Enter your legal identity, farm enterprise name, and village jurisdiction.',
      step2Title: 'Farm Plots & Land Boundaries',
      step2Desc: 'Map your agricultural cultivation plots with satellite coordinates and calculate exact acreage.',
      step3Title: 'Cultivation & Farming Profile',
      step3Desc: 'Specify your farming institution type, primary crops harvested, and irrigation infrastructure.',
      step4Title: 'Encrypted Identity & Financial Settlement',
      step4Desc: 'Provide PAN, voluntary Aadhaar last-4 digits, and bank account for automated custody settlements. AES-256-GCM protected.',
      step5Title: 'Review & Statutory DPDP Consent',
      step5Desc: 'Verify all declared parameters and provide purpose-limited digital consent under the DPDP Act 2023.',
      firstName: 'First Name',
      firstNamePh: 'Enter first name',
      lastName: 'Last Name',
      lastNamePh: 'Enter last name',
      orgName: 'Farm / Enterprise Name',
      orgNamePh: 'Enter farm or FPO name',
      gender: 'Gender',
      genderSelect: '-- Select --',
      genderMale: 'Male',
      genderFemale: 'Female',
      genderOther: 'Other',
      state: 'State / UT',
      stateSelect: '-- Select State --',
      district: 'District',
      districtPh: 'Enter district name',
      village: 'Village / Town',
      villagePh: 'Enter village or town',
      pincode: 'Postal PIN Code (6 digits)',
      pincodePh: '6-digit PIN code',
      address: 'Street Address / Plot Location',
      addressPh: 'House/Plot No, Landmark, Gram Panchayat',
      photoLabel: 'Verified Farmer Photograph',
      photoHint: 'Clear passport or farm portrait. EXIF metadata automatically scrubbed for citizen privacy.',
      photoUploadBtn: 'Upload Farm Photo',
      photoScrubbed: 'Pixel Scrubbed & EXIF Cleared',
      plotMapInstructions: 'Click on the map to place polygon corner points, or use your device GPS location.',
      btnDrawPolygon: 'Draw Plot Polygon',
      btnClearPoints: 'Clear Points',
      btnUseGps: 'Use My Current GPS',
      estAreaLabel: 'Estimated Area',
      acresUnit: 'Acres',
      plotNameLabel: 'Plot Name / Survey Reference',
      plotNamePh: 'Enter plot name or Khasra/Dag number',
      plotAreaLabel: 'Cultivable Area (Acres)',
      plotAreaPh: '0.00',
      btnAddPlot: '+ Add Plot to Registry',
      registeredPlotsTitle: 'Registered Farm Plots',
      totalLabel: 'Total',
      noPlotsYet: 'No plots added yet. Draw a polygon on the map or enter plot details above and click "+ Add Plot to Registry".',
      btnRemove: 'Remove',
      farmType: 'Cultivator Category',
      farmTypeInd: 'Individual / Marginal Farmer',
      farmTypeFpo: 'Farmer Producer Organisation (FPO / FPC)',
      farmTypeShg: 'Self-Help Group (SHG) Collective',
      farmTypeCoop: 'Registered Agricultural Co-operative',
      irrigation: 'Primary Irrigation Source',
      irrRain: 'Rainfed / Monsoon Dependent',
      irrCanal: 'Canal & River Lift Irrigation',
      irrBore: 'Submersible Borewell / Tube-well',
      irrDrip: 'Micro-Drip & Sprinkler System',
      commodities: 'Primary Agricultural Crops (Select all that apply)',
      certifications: 'Quality / Organic Certifications',
      certNone: 'Standard Commercial Cultivation',
      certNpop: 'NPOP Certified Organic (India Organic)',
      certPgs: 'PGS-India Green / Organic',
      certGap: 'INDGAP (Good Agricultural Practices)',
      kycVaultNotice: 'Zero-Plaintext Vault: PAN, Bank Account, and IFSC are encrypted with AES-256-GCM using your Entity ID as Additional Authenticated Data (AAD).',
      panLabel: 'Permanent Account Number (PAN)',
      panPh: '10-character PAN',
      maskedPreview: 'Masked Preview',
      aadhaarLabel: 'Voluntary Aadhaar (Last 4 Digits Only)',
      aadhaarPh: '4 digits only',
      aadhaarNotice: 'Under statutory UIDAI regulations, full Aadhaar is never collected or stored.',
      bankName: 'Bank Name',
      bankNamePh: 'Enter bank name',
      ifsc: 'Bank IFSC Code',
      ifscPh: '11-character IFSC',
      accountNo: 'Bank Account Number',
      accountNoPh: 'Enter account number',
      confirmAccountNo: 'Re-enter Account Number',
      confirmAccountNoPh: 'Confirm account number',
      upi: 'UPI ID (Optional)',
      upiPh: 'name@bank',
      docTitle: 'Supporting Land / Identity Document (Khatian, Parcha, or Passbook)',
      docSub: 'Upload JPEG, PNG, or PDF (Max 5MB). SHA-256 checksummed for tamper-evidence.',
      docLand: 'Land Record / Khatian / Patta',
      docFpo: 'FPO / Co-op Registration Certificate',
      docOrg: 'Organic / Quality Certificate',
      docBtnUpload: 'Select & Upload Document',
      docUploadedBadge: 'Uploaded & SHA-256 Verified',
      sumApplicant: 'Applicant Name',
      sumEnterprise: 'Farm / Enterprise',
      sumJurisdiction: 'Jurisdiction',
      sumLand: 'Mapped Landholding',
      sumCrops: 'Selected Commodities',
      sumIdentity: 'Identity & Settlement',
      notEntered: 'Not entered',
      noneSelected: 'None selected',
      plotsWord: 'Plots',
      encryptedWord: 'Encrypted',
      consentHeader: 'DPDP Act 2023 Statutory Declarations',
      consent1: 'I grant purpose-limited consent under DPDP Act 2023 for my farm location and crop harvest data to be processed strictly for supply-chain traceability and trade integrity.',
      consent2: 'I voluntarily declare the last 4 digits of my Aadhaar for local identity attestation on the AnnaSutra platform. I acknowledge full Aadhaar is never requested.',
      consent3: 'I certify that all declared crop, plot acreage, and yield information accurately represent genuine agricultural production.',
      btnSaveDraft: 'Save Draft',
      btnNext: 'Next Step',
      btnPrev: 'Previous',
      btnSubmit: 'Submit Application for Verification',
      submitting: 'Submitting Application...',
      saving: 'Saving Draft...',
      underReviewTitle: 'Application Submitted — Under Verification Review',
      underReviewSub: 'Your producer profile has been securely recorded. An official sequential code and QR label issuance will be enabled upon administrative approval. Unlimited QR labels can be generated for your harvest lots.',
      lblMappedLand: 'Verified Land Mapped',
      lblMaskedPan: 'Masked PAN Identity',
      lblSettlementBank: 'Settlement Bank',
      lblSubmissionDate: 'Submission Date',
      lblEntityRefToken: 'Entity Reference Token',
      verifiedNodeBadge: 'VERIFIED PRODUCER NODE',
      lblSovereignCode: 'Permanent Sovereign Code',
      statActiveBatches: 'Active Harvest Batches',
      statActiveBatchesSub: 'Recorded in Custody Ledger',
      statQrAvail: 'Remaining QR Crate Serials',
      statQrAvailSub: 'Allocated (13-Char Crockford Base32)',
      statPlotsVerified: 'Verified Farm Plots',
      statPlotsVerifiedSub: 'Geofenced & Encrypted',
      btnDownloadQrPdf: 'Download Printable A4 Sticker Sheet (PDF)',
      loadingRegistry: 'Loading verified entity registry...',
      adminQueueTitle: 'Entity Verification Review Queue',
      adminQueueSub: 'Inspect submitted KYC, farm plot boundaries, and statutory consent to approve entities and issue sovereign codes.',
      filterAll: 'All Applications',
      filterSubmitted: 'Pending Review',
      filterVerified: 'Verified',
      filterDraft: 'Drafts',
      filterChanges: 'Needs Changes',
      filterRejected: 'Rejected',
      thApplicant: 'Applicant & Enterprise',
      thRolePhone: 'Role & Mobile',
      thLocation: 'Location',
      thPlots: 'Mapped Land',
      thStatus: 'Verification Status',
      thActions: 'Administrative Action',
      btnInspect: 'Inspect & Decide',
      btnApproveNow: 'Approve',
      btnIssueMoreQr: '+20 QR Labels',
      noApplicationsFound: 'No entity registrations found for the selected filter.',
      inspectorTitle: 'Application Verification Inspector',
      btnCloseInspector: 'Close Inspector',
      lblKycVault: 'Encrypted KYC & Settlement Vault',
      btnRevealPan: 'Reveal PAN (Audit Logged)',
      btnRevealBank: 'Reveal Account (Audit Logged)',
      lblReviewNotes: 'Administrative Review Notes / Reason',
      reviewNotesPh: 'Enter verification notes or reason for rejection / changes...',
      btnApproveEntity: 'Approve',
      btnDeleteProducer: 'Delete Producer Data',
      tabTrash: 'Trash',
      consoleHeading: 'Harvest Lot & Custody Ledger Console',
      tabHarvestLedger: 'Harvest Lots & Custody Ledger',
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
      noAnalyticsLots: 'No harvest lots recorded yet. Register your first lot to generate yield analytics!',
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
      btnRequestChanges: 'Request Changes',
      btnRejectEntity: 'Reject Application'
    },
    hi: {
      roleProducer: 'उत्पादक',
      roleAdmin: 'प्रशासक सत्यापनकर्ता',
      workspaceTitleProducer: 'उत्पादक पंजीकरण एवं संचालन कंसोल',
      workspaceTitleAdmin: 'प्रशासनिक सत्यापन एवं क्यूआर आवंटन पोर्टल',
      stepTab1: '1. मूल विवरण',
      stepTab2: '2. खेत भूखंड',
      stepTab3: '3. फसल प्रोफाइल',
      stepTab4: '4. पहचान व बैंक',
      stepTab5: '5. सहमति व जमा',
      step1Title: 'उत्पादक एवं कृषि का बुनियादी विवरण',
      step1Desc: 'अपना कानूनी नाम, कृषि उद्यम का नाम और ग्राम पंचायत अधिकार क्षेत्र दर्ज करें।',
      step2Title: 'खेत के भूखंड एवं भूमि सीमांकन',
      step2Desc: 'सैटेलाइट निर्देशांक के साथ अपने कृषि भूखंडों का नक्शा बनाएं और सटीक रकबा (एकड़) निकालें।',
      step3Title: 'खेती एवं फसल प्रोफाइल',
      step3Desc: 'अपनी कृषि संस्था का प्रकार, उगाई जाने वाली मुख्य फसलें और सिंचाई व्यवस्था बताएं।',
      step4Title: 'एन्क्रिप्टेड पहचान एवं बैंक खाता विवरण',
      step4Desc: 'व्यापार भुगतान के लिए पैन, स्वैच्छिक आधार के अंतिम 4 अंक और बैंक खाता दर्ज करें। AES-256-GCM द्वारा सुरक्षित।',
      step5Title: 'समीक्षा एवं वैधानिक डीपीडीपी सहमति',
      step5Desc: 'सभी दर्ज विवरणों की पुष्टि करें और DPDP अधिनियम 2023 के तहत डिजिटल सहमति प्रदान करें।',
      firstName: 'पहला नाम',
      firstNamePh: 'पहला नाम दर्ज करें',
      lastName: 'अंतिम नाम',
      lastNamePh: 'अंतिम नाम दर्ज करें',
      orgName: 'खेत / कृषि उद्यम का नाम',
      orgNamePh: 'खेत या एफपीओ का नाम दर्ज करें',
      gender: 'लिंग',
      genderSelect: '-- चुनें --',
      genderMale: 'पुरुष',
      genderFemale: 'महिला',
      genderOther: 'अन्य',
      state: 'राज्य / केंद्र शासित प्रदेश',
      stateSelect: '-- राज्य चुनें --',
      district: 'जिला',
      districtPh: 'जिले का नाम दर्ज करें',
      village: 'गांव / कस्बा',
      villagePh: 'गांव या कस्बे का नाम दर्ज करें',
      pincode: 'पिन कोड (6 अंक)',
      pincodePh: '6-अंकीय पिन कोड',
      address: 'सड़क का पता / खेत का स्थान',
      addressPh: 'मकान/प्लॉट नंबर, ग्राम पंचायत',
      photoLabel: 'सत्यापित किसान की तस्वीर',
      photoHint: 'स्पष्ट पासपोर्ट या खेत की तस्वीर। गोपनीयता सुरक्षा हेतु EXIF मेटाडेटा स्वतः हटाया जाता है।',
      photoUploadBtn: 'तस्वीर अपलोड करें',
      photoScrubbed: 'पिक्सेल एवं मेटाडेटा साफ़',
      plotMapInstructions: 'भूखंड की सीमा बनाने के लिए नक्शे पर क्लिक करें, या अपने वर्तमान जीपीएस स्थान का उपयोग करें।',
      btnDrawPolygon: 'भूखंड सीमा बनाएं',
      btnClearPoints: 'बिंदु साफ़ करें',
      btnUseGps: 'मेरा वर्तमान जीपीएस उपयोग करें',
      estAreaLabel: 'अनुमानित क्षेत्रफल',
      acresUnit: 'एकड़',
      plotNameLabel: 'भूखंड का नाम / खसरा संख्या',
      plotNamePh: 'भूखंड का नाम या खसरा/दाग संख्या दर्ज करें',
      plotAreaLabel: 'कृषि योग्य क्षेत्रफल (एकड़)',
      plotAreaPh: '0.00',
      btnAddPlot: '+ रजिस्ट्री में भूखंड जोड़ें',
      registeredPlotsTitle: 'पंजीकृत खेत भूखंड',
      totalLabel: 'कुल',
      noPlotsYet: 'अभी तक कोई भूखंड नहीं जोड़ा गया है। ऊपर नक्शे पर भूखंड बनाएं और "+ रजिस्ट्री में भूखंड जोड़ें" पर क्लिक करें।',
      btnRemove: 'हटाएं',
      farmType: 'किसान श्रेणी',
      farmTypeInd: 'व्यक्तिगत / सीमांत किसान',
      farmTypeFpo: 'किसान उत्पादक संगठन (FPO / FPC)',
      farmTypeShg: 'स्वयं सहायता समूह (SHG)',
      farmTypeCoop: 'पंजीकृत कृषि सहकारी समिति',
      irrigation: 'मुख्य सिंचाई स्रोत',
      irrRain: 'वर्षा आधारित / मानसून',
      irrCanal: 'नहर एवं नदी लिफ्ट सिंचाई',
      irrBore: 'बोरवेल / ट्यूबवेल',
      irrDrip: 'माइक्रो-ड्रिप एवं स्प्रिंकलर प्रणाली',
      commodities: 'उगाई जाने वाली मुख्य फसलें (सभी लागू चुनें)',
      certifications: 'गुणवत्ता / जैविक प्रमाणन',
      certNone: 'मानक व्यावसायिक खेती',
      certNpop: 'एनपीओपी प्रमाणित जैविक (इंडिया ऑर्गेनिक)',
      certPgs: 'पीजीएस-इंडिया ग्रीन / जैविक',
      certGap: 'उत्तम कृषि पद्धतियां (INDGAP)',
      kycVaultNotice: 'शून्य-प्लेनटेक्स्ट वॉल्ट: पैन, बैंक खाता और आईएफएससी को AES-256-GCM द्वारा एन्क्रिप्ट किया जाता है।',
      panLabel: 'पैन नंबर (PAN)',
      panPh: '10-अक्षरों का पैन नंबर',
      maskedPreview: 'मास्क्ड पूर्वावलोकन',
      aadhaarLabel: 'स्वैच्छिक आधार (केवल अंतिम 4 अंक)',
      aadhaarPh: 'केवल अंतिम 4 अंक',
      aadhaarNotice: 'वैधानिक यूआईडीएआई नियमों के तहत पूर्ण आधार नंबर कभी संग्रहीत नहीं किया जाता है।',
      bankName: 'बैंक का नाम',
      bankNamePh: 'बैंक का नाम दर्ज करें',
      ifsc: 'आईएफएससी कोड (IFSC)',
      ifscPh: '11-अक्षरों का IFSC कोड',
      accountNo: 'बैंक खाता संख्या',
      accountNoPh: 'खाता संख्या दर्ज करें',
      confirmAccountNo: 'खाता संख्या पुनः दर्ज करें',
      confirmAccountNoPh: 'खाता संख्या की पुष्टि करें',
      upi: 'यूपीआई आईडी (वैकल्पिक)',
      upiPh: 'name@bank',
      docTitle: 'सहायक भूमि / पहचान दस्तावेज़ (खतियान, पर्चा, या पासबुक)',
      docSub: 'JPEG, PNG या PDF अपलोड करें (अधिकतम 5MB)। SHA-256 द्वारा सत्यापित।',
      docLand: 'भूमि रिकॉर्ड / खतियान / पट्टा',
      docFpo: 'एफपीओ / सहकारी पंजीकरण प्रमाणपत्र',
      docOrg: 'जैविक / गुणवत्ता प्रमाणपत्र',
      docBtnUpload: 'दस्तावेज़ चुनें और अपलोड करें',
      docUploadedBadge: 'अपलोड एवं SHA-256 सत्यापित',
      sumApplicant: 'आवेदक का नाम',
      sumEnterprise: 'खेत / कृषि उद्यम',
      sumJurisdiction: 'अधिकार क्षेत्र',
      sumLand: 'सीमांकित भूमि',
      sumCrops: 'चयनित फसलें',
      sumIdentity: 'पहचान एवं बैंक निपटान',
      notEntered: 'दर्ज नहीं',
      noneSelected: 'कोई चयन नहीं',
      plotsWord: 'भूखंड',
      encryptedWord: 'एन्क्रिप्टेड',
      consentHeader: 'डीपीडीपी अधिनियम 2023 वैधानिक घोषणाएं',
      consent1: 'मैं DPDP अधिनियम 2023 के तहत अपनी कृषि और भूखंड डेटा को आपूर्ति-श्रृंखला ट्रेसबिलिटी के लिए संसाधित करने की सहमति देता हूँ।',
      consent2: 'मैं पहचान सत्यापन के लिए स्वेच्छा से अपने आधार के केवल अंतिम 4 अंक प्रदान कर रहा हूँ।',
      consent3: 'मैं प्रमाणित करता हूँ कि दर्ज की गई सभी फसल और रकबा जानकारी पूर्णतः सत्य और वास्तविक है।',
      btnSaveDraft: 'ड्राफ्ट सहेजें',
      btnNext: 'अगला चरण',
      btnPrev: 'पिछला चरण',
      btnSubmit: 'सत्यापन हेतु आवेदन जमा करें',
      submitting: 'आवेदन जमा हो रहा है...',
      saving: 'सहेजा जा रहा है...',
      underReviewTitle: 'आवेदन जमा हो गया — सत्यापन समीक्षाधीन है',
      underReviewSub: 'आपका उत्पादक प्रोफ़ाइल सुरक्षित रूप से दर्ज कर लिया गया है। प्रशासनिक स्वीकृति मिलने पर आधिकारिक कोड आवंटित किए जाएंगे एवं प्रत्येक फसल लॉट के लिए असीमित क्यूआर कोड उत्पन्न किए जा सकते हैं।',
      lblMappedLand: 'सत्यापित भूमि रकबा',
      lblMaskedPan: 'मास्क्ड पैन पहचान',
      lblSettlementBank: 'निपटान बैंक खाता',
      lblSubmissionDate: 'जमा करने की तिथि',
      lblEntityRefToken: 'इकाई संदर्भ टोकन',
      verifiedNodeBadge: 'सत्यापित उत्पादक नोड',
      lblSovereignCode: 'स्थायी आधिकारिक कोड',
      statActiveBatches: 'सक्रिय फसल बैच',
      statActiveBatchesSub: 'कस्टडी लेज़र में दर्ज',
      statQrAvail: 'उपलब्ध क्यूआर क्रेट लेबल',
      statQrAvailSub: 'आवंटित (13-अक्षर क्रॉकफोर्ड Base32)',
      statPlotsVerified: 'सत्यापित खेत भूखंड',
      statPlotsVerifiedSub: 'जियोफेंस्ड एवं एन्क्रिप्टेड',
      btnDownloadQrPdf: 'प्रिंट करने योग्य A4 क्यूआर स्टिकर शीट डाउनलोड करें (PDF)',
      loadingRegistry: 'सत्यापित इकाई रजिस्ट्री लोड हो रही है...',
      adminQueueTitle: 'इकाई सत्यापन समीक्षा कतार',
      adminQueueSub: 'सत्यापन प्रदान करने के लिए जमा किए गए क्रेडेंशियल, भूखंड सीमा और कानूनी सहमति की समीक्षा करें।',
      filterAll: 'सभी आवेदन',
      filterSubmitted: 'समीक्षाधीन (लंबित)',
      filterVerified: 'सत्यापित',
      filterDraft: 'ड्राफ्ट',
      filterChanges: 'सुधार अपेक्षित',
      filterRejected: 'अस्वीकृत',
      thApplicant: 'आवेदक एवं उद्यम',
      thRolePhone: 'भूमिका एवं मोबाइल',
      thLocation: 'स्थान',
      thPlots: 'भूमि रकबा',
      thStatus: 'सत्यापन स्थिति',
      thActions: 'प्रशासनिक कार्रवाई',
      btnInspect: 'जांचें और निर्णय लें',
      btnApproveNow: 'स्वीकृत करें',
      btnIssueMoreQr: '+20 QR लेबल',
      noApplicationsFound: 'चयनित फ़िल्टर के लिए कोई पंजीकरण आवेदन नहीं मिला।',
      inspectorTitle: 'आवेदन सत्यापन निरीक्षक',
      btnCloseInspector: 'निरीक्षक बंद करें',
      lblKycVault: 'एन्क्रिप्टेड पहचान एवं बैंक वॉल्ट',
      btnRevealPan: 'पैन देखें (ऑडिट लॉग)',
      btnRevealBank: 'खाता संख्या देखें (ऑडिट लॉग)',
      lblReviewNotes: 'प्रशासनिक समीक्षा टिप्पणी / कारण',
      reviewNotesPh: 'सत्यापन टिप्पणी या अस्वीकृति/सुधार का कारण दर्ज करें...',
      btnApproveEntity: 'स्वीकृत करें',
      btnDeleteProducer: 'उत्पादक डेटा हटाएं',
      tabTrash: 'ट्रैश (कचरा)',
      consoleHeading: 'फसल लॉट एवं कस्टडी लेज़र कंसोल',
      tabHarvestLedger: 'फसल लॉट एवं कस्टडी लेज़र',
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
      noAnalyticsLots: 'अभी तक कोई फसल लॉट दर्ज नहीं है। एनालिटिक्स देखने के लिए नया लॉट जोड़ें!',
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
      btnRequestChanges: 'सुधार का अनुरोध करें',
      btnRejectEntity: 'आवेदन अस्वीकृत करें'
    },
    bn: {
      roleProducer: 'উৎপাদক',
      roleAdmin: 'প্রশাসনিক যাচাইকারী',
      workspaceTitleProducer: 'উৎপাদক নিবন্ধন ও পরিচালন কনসোল',
      workspaceTitleAdmin: 'প্রশাসনিক যাচাইকরণ ও কিউআর বরাদ্দ পোর্টাল',
      stepTab1: '১. প্রাথমিক তথ্য',
      stepTab2: '২. জমির প্লট',
      stepTab3: '৩. ফসল প্রোফাইল',
      stepTab4: '৪. পরিচয় ও ব্যাঙ্ক',
      stepTab5: '৫. সম্মতি ও জমা',
      step1Title: 'উৎপাদক ও খামারের প্রাথমিক বিবরণ',
      step1Desc: 'আপনার আইনি পরিচয়, খামারের নাম এবং গ্রাম পঞ্চায়েতের এলাকা নির্বাচন করুন।',
      step2Title: 'খামারের প্লট ও জমির সীমানা',
      step2Desc: 'স্যাটেলাইট স্থানাঙ্ক দিয়ে আপনার জমির প্লট ম্যাপ করুন এবং মোট একর হিসাব করুন।',
      step3Title: 'কৃষি ও ফসলের প্রোফাইল',
      step3Desc: 'আপনার কৃষক শ্রেণি, প্রধান উৎপাদিত ফসল এবং সেচ ব্যবস্থা নির্বাচন করুন।',
      step4Title: 'এনক্রিপ্ট করা পরিচয় ও ব্যাঙ্ক অ্যাকাউন্ট',
      step4Desc: 'লেনদেনের জন্য প্যান, স্বেচ্ছায় আধার শেষ ৪ সংখ্যা এবং ব্যাঙ্ক বিবরণ দিন। AES-256-GCM দ্বারা সুরক্ষিত।',
      step5Title: 'পর্যালোচনা ও বিধিবদ্ধ ডিপিডিপি সম্মতি',
      step5Desc: 'সকল তথ্য যাচাই করুন এবং DPDP আইন ২০২৩ অনুযায়ী ডিজিটাল সম্মতি প্রদান করুন।',
      firstName: 'নামের প্রথম অংশ',
      firstNamePh: 'নামের প্রথম অংশ লিখুন',
      lastName: 'পদবি',
      lastNamePh: 'পদবি লিখুন',
      orgName: 'খামার বা সংস্থার নাম',
      orgNamePh: 'খামার বা এফপিও-এর নাম লিখুন',
      gender: 'লিঙ্গ',
      genderSelect: '-- নির্বাচন করুন --',
      genderMale: 'পুরুষ',
      genderFemale: 'মহিলা',
      genderOther: 'অন্যান্য',
      state: 'রাজ্য / কেন্দ্রশাসিত অঞ্চল',
      stateSelect: '-- রাজ্য নির্বাচন করুন --',
      district: 'জেলা',
      districtPh: 'জেলার নাম লিখুন',
      village: 'গ্রাম / শহর',
      villagePh: 'গ্রাম বা শহরের নাম লিখুন',
      pincode: 'পিন কোড (৬ অঙ্ক)',
      pincodePh: '৬-অঙ্কের পিন কোড',
      address: 'ঠিকানা / খামারের অবস্থান',
      addressPh: 'বাড়ি/প্লট নম্বর, গ্রাম পঞ্চায়েত',
      photoLabel: 'কৃষকের ছবি',
      photoHint: 'স্পষ্ট পাসপোর্ট বা খামারের ছবি। গোপনীয়তা রক্ষার জন্য EXIF মেটাডাটা স্বয়ংক্রিয়ভাবে মুছে ফেলা হয়।',
      photoUploadBtn: 'ছবি আপলোড করুন',
      photoScrubbed: 'মেটাডাটা ও এক্সিফ মুক্ত',
      plotMapInstructions: 'প্লটের সীমানা আঁকতে মানচিত্রে ক্লিক করুন, অথবা আপনার বর্তমান জিপিএস অবস্থান ব্যবহার করুন।',
      btnDrawPolygon: 'প্লট সীমানা আঁকুন',
      btnClearPoints: 'বিন্দু মুছুন',
      btnUseGps: 'আমার বর্তমান জিপিএস ব্যবহার করুন',
      estAreaLabel: 'আনুমানিক ক্ষেত্রফল',
      acresUnit: 'একর',
      plotNameLabel: 'প্লটের নাম / দাগ নম্বর',
      plotNamePh: 'প্লটের নাম বা খতিয়ান/দাগ নম্বর লিখুন',
      plotAreaLabel: 'চাষযোগ্য এলাকা (একর)',
      plotAreaPh: '0.00',
      btnAddPlot: '+ রেজিস্ট্রিতে প্লট যুক্ত করুন',
      registeredPlotsTitle: 'নিবন্ধিত খামার প্লট',
      totalLabel: 'মোট',
      noPlotsYet: 'এখনও কোনো প্লট যোগ করা হয়নি। মানচিত্রে পলিগন আঁকুন এবং "+ রেজিস্ট্রিতে প্লট যুক্ত করুন" ক্লিক করুন।',
      btnRemove: 'মুছুন',
      farmType: 'কৃষক বিভাগ',
      farmTypeInd: 'ব্যক্তিগত / প্রান্তিক কৃষক',
      farmTypeFpo: 'কৃষক উৎপাদক সংস্থা (FPO / FPC)',
      farmTypeShg: 'স্বনির্ভর গোষ্ঠী (SHG)',
      farmTypeCoop: 'নিবন্ধিত কৃষি সমবায় সমিতি',
      irrigation: 'প্রধান সেচ ব্যবস্থা',
      irrRain: 'বৃষ্টিনির্ভর / বর্ষা',
      irrCanal: 'খাল ও নদী লিফট সেচ',
      irrBore: 'সাবমার্সিবল বোরওয়েল / টিউবওয়েল',
      irrDrip: 'মাইক্রো-ড্রিপ ও স্প্রিংকলার সেচ',
      commodities: 'প্রধান উৎপাদিত ফসল (প্রযোজ্য সবগুলি নির্বাচন করুন)',
      certifications: 'জৈব বা মান শংসাপত্র',
      certNone: 'মানক বাণিজ্যিক চাষ',
      certNpop: 'এনপিওপি প্রত্যয়িত জৈব (ইন্ডিয়া অর্গানিক)',
      certPgs: 'পিজিএস-ইন্ডিয়া গ্রিন / জৈব',
      certGap: 'উত্তম কৃষি পদ্ধতি (INDGAP)',
      kycVaultNotice: 'জিরো-প্লেইনটেক্সট ভল্ট: প্যান, ব্যাঙ্ক অ্যাকাউন্ট এবং আইএফএসসি AES-256-GCM দ্বারা এনক্রিপ্ট করা হয়।',
      panLabel: 'প্যান নম্বর (PAN)',
      panPh: '১০-অক্ষরের প্যান নম্বর',
      maskedPreview: 'মাস্কড প্রিভিউ',
      aadhaarLabel: 'স্বেচ্ছামূলক আধার (শুধুমাত্র শেষ ৪টি অঙ্ক)',
      aadhaarPh: 'শুধুমাত্র শেষ ৪টি অঙ্ক',
      aadhaarNotice: 'বিধিবদ্ধ ইউআইডিএআই বিধিমালার আওতায় সম্পূর্ণ ১২-অঙ্কের আধার কখনো চাওয়া বা সংরক্ষণ করা হয় না।',
      bankName: 'ব্যাঙ্কের নাম',
      bankNamePh: 'ব্যাঙ্কের নাম লিখুন',
      ifsc: 'আইএফএসসি কোড (IFSC)',
      ifscPh: '১১-অক্ষরের IFSC কোড',
      accountNo: 'ব্যাঙ্ক অ্যাকাউন্ট নম্বর',
      accountNoPh: 'অ্যাকাউন্ট নম্বর লিখুন',
      confirmAccountNo: 'অ্যাকাউন্ট নম্বর পুনরায় লিখুন',
      confirmAccountNoPh: 'অ্যাকাউন্ট নম্বর নিশ্চিত করুন',
      upi: 'ইউপিআই আইডি (ঐচ্ছিক)',
      upiPh: 'name@bank',
      docTitle: 'সহায়ক জমি / পরিচয় নথি (খতিয়ান, পর্চা বা পাসবুক)',
      docSub: 'JPEG, PNG বা PDF আপলোড করুন (সর্বোচ্চ 5MB)। SHA-256 দ্বারা যাচাইকৃত।',
      docLand: 'জমির রেকর্ড / খতিয়ান / পাট্টা',
      docFpo: 'এফপিও / সমবায় নিবন্ধন শংসাপত্র',
      docOrg: 'জৈব / গুণমান শংসাপত্র',
      docBtnUpload: 'নথি নির্বাচন ও আপলোড করুন',
      docUploadedBadge: 'আপলোড ও SHA-256 যাচাইকৃত',
      sumApplicant: 'আবেদনকারীর নাম',
      sumEnterprise: 'খামার / সংস্থা',
      sumJurisdiction: 'এলাকা',
      sumLand: 'ম্যাপ করা জমি',
      sumCrops: 'নির্বাচিত ফসল',
      sumIdentity: 'পরিচয় ও ব্যাঙ্ক নিষ্পত্তি',
      notEntered: 'দেওয়া হয়নি',
      noneSelected: 'নির্বাচিত নয়',
      plotsWord: 'প্লট',
      encryptedWord: 'এনক্রিপ্টেড',
      consentHeader: 'ডিপিডিপি আইন ২০২৩ বিধিবদ্ধ ঘোষণা',
      consent1: 'আমি DPDP আইন ২০২৩ অনুযায়ী কৃষি ট্রেসেবিলিটি এবং হেফাজতের জন্য আমার খামারের তথ্য প্রক্রিয়াকরণে সম্মতি দিচ্ছি।',
      consent2: 'আমি পরিচয় প্রমাণের জন্য স্বেচ্ছায় আমার আধারের শেষ ৪টি সংখ্যা দিচ্ছি। সম্পূর্ণ আধার চাওয়া হয়নি।',
      consent3: 'আমি প্রত্যয়ন করছি যে ঘোষিত সকল ফসল ও জমির পরিমাণ সম্পূর্ণ বাস্তব এবং সঠিক।',
      btnSaveDraft: 'খসড়া সংরক্ষণ করুন',
      btnNext: 'পরবর্তী ধাপ',
      btnPrev: 'পূর্ববর্তী ধাপ',
      btnSubmit: 'যাচাইকরণের জন্য জমা দিন',
      submitting: 'আবেদন জমা করা হচ্ছে...',
      saving: 'সংরক্ষণ চলছে...',
      underReviewTitle: 'আবেদন জমা হয়েছে — প্রশাসনিক পর্যালোচনা চলছে',
      underReviewSub: 'আপনার উৎপাদক প্রোফাইল নথিভুক্ত হয়েছে। অনুমোদনের পর সরকারি কোড এবং প্রাথমিক ৫০টি কিউআর লেবেল প্রদান করা হবে।',
      lblMappedLand: 'যাচাইকৃত জমির পরিমাণ',
      lblMaskedPan: 'মাস্কড প্যান পরিচয়',
      lblSettlementBank: 'ব্যাঙ্ক অ্যাকাউন্ট',
      lblSubmissionDate: 'জমা দেওয়ার তারিখ',
      lblEntityRefToken: 'এনটিটি রেফারেন্স টোকেন',
      verifiedNodeBadge: 'যাচাইকৃত উৎপাদক নোড',
      lblSovereignCode: 'স্থায়ী সরকারি কোড',
      statActiveBatches: 'সক্রিয় ফসল ব্যাচ',
      statActiveBatchesSub: 'হেফাজত লেজারে নথিভুক্ত',
      statQrAvail: 'উপলব্ধ কিউআর ক্রেট লেবেল',
      statQrAvailSub: 'বরাদ্দকৃত (১৩-অক্ষর ক্রকফোর্ড Base32)',
      statPlotsVerified: 'যাচাইকৃত খামার প্লট',
      statPlotsVerifiedSub: 'জিওফেন্সড ও এনক্রিপ্টেড',
      btnDownloadQrPdf: 'প্রিন্টযোগ্য A4 কিউআর স্টিকার শিট ডাউনলোড করুন (PDF)',
      loadingRegistry: 'যাচাইকৃত এনটিটি রেজিস্ট্রি লোড হচ্ছে...',
      adminQueueTitle: 'এনটিটি যাচাইকরণ পর্যালোচনা তালিকা',
      adminQueueSub: 'উৎপাদক ও সংস্থাগুলিকে অনুমোদন করতে এবং ৫০টি কিউআর লেবেল জারি করতে কেওয়াইসি, প্লট ও সম্মতি পরীক্ষা করুন।',
      filterAll: 'সকল আবেদন',
      filterSubmitted: 'পর্যালোচনাধীন',
      filterVerified: 'যাচাইকৃত',
      filterDraft: 'খসড়া',
      filterChanges: 'সংশোধন প্রয়োজন',
      filterRejected: 'বাতিল',
      thApplicant: 'আবেদনকারী ও সংস্থা',
      thRolePhone: 'ভূমিকা ও মোবাইল',
      thLocation: 'অবস্থান',
      thPlots: 'জমির পরিমাণ',
      thStatus: 'যাচাইকরণ স্থিতি',
      thActions: 'প্রশাসনিক পদক্ষেপ',
      btnInspect: 'পরীক্ষা ও সিদ্ধান্ত',
      btnApproveNow: 'অনুমোদন করুন',
      btnIssueMoreQr: '+২০টি QR লেবেল',
      noApplicationsFound: 'নির্বাচিত ফিল্টারের জন্য কোনো আবেদন পাওয়া যায়নি।',
      inspectorTitle: 'আবেদন যাচাইকরণ পরিদর্শক',
      btnCloseInspector: 'পরিদর্শক বন্ধ করুন',
      lblKycVault: 'এনক্রিপ্টেড কেওয়াইসি ও ব্যাঙ্ক ভল্ট',
      btnRevealPan: 'প্যান দেখুন (অডিট লগ)',
      btnRevealBank: 'অ্যাকাউন্ট দেখুন (অডিট লগ)',
      lblReviewNotes: 'প্রশাসনিক মন্তব্য / কারণ',
      reviewNotesPh: 'যাচাইকরণ মন্তব্য বা বাতিলের কারণ লিখুন...',
      btnApproveEntity: 'অনুমোদন করুন',
      btnDeleteProducer: 'উৎপাদক তথ্য মুছুন',
      tabTrash: 'ট্র্যাশ',
      consoleHeading: 'ফসল লট ও হেফাজত লেজার কনসোল',
      tabHarvestLedger: 'ফসল লট ও হেফাজত লেজার',
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
      noAnalyticsLots: 'এখনও কোনো ফসল লট নিবন্ধিত হয়নি। অ্যানালিটিক্স দেখতে নতুন লট যোগ করুন!',
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
      btnRequestChanges: 'সংশোধনের অনুরোধ করুন',
      btnRejectEntity: 'আবেদন বাতিল করুন'
    }
  };

  const STATES_LIST = [
    { id: 'West Bengal', en: 'West Bengal', hi: 'पश्चिम बंगाल', bn: 'পশ্চিমবঙ্গ' },
    { id: 'Maharashtra', en: 'Maharashtra', hi: 'महाराष्ट्र', bn: 'মহারাষ্ট্র' },
    { id: 'Punjab', en: 'Punjab', hi: 'पंजाब', bn: 'পাঞ্জাব' },
    { id: 'Uttar Pradesh', en: 'Uttar Pradesh', hi: 'उत्तर प्रदेश', bn: 'উত্তরপ্রদেশ' },
    { id: 'Madhya Pradesh', en: 'Madhya Pradesh', hi: 'मध्य प्रदेश', bn: 'মধ্যপ্রদেশ' },
    { id: 'Karnataka', en: 'Karnataka', hi: 'कर्नाटक', bn: 'কর্ণাটক' },
    { id: 'Gujarat', en: 'Gujarat', hi: 'गुजरात', bn: 'গুজরাট' },
    { id: 'Bihar', en: 'Bihar', hi: 'बिहार', bn: 'বিহার' },
    { id: 'Odisha', en: 'Odisha', hi: 'ओडिशा', bn: 'ওড়িশা' },
    { id: 'Tamil Nadu', en: 'Tamil Nadu', hi: 'तमिलनाडु', bn: 'তামিলনাড়ু' },
    { id: 'Andhra Pradesh', en: 'Andhra Pradesh', hi: 'आंध्र प्रदेश', bn: 'অন্ধ্রপ্রদেশ' },
    { id: 'Telangana', en: 'Telangana', hi: 'तेलंगाना', bn: 'তেলেঙ্গানা' },
    { id: 'Assam', en: 'Assam', hi: 'असम', bn: 'আসাম' },
    { id: 'Rajasthan', en: 'Rajasthan', hi: 'राजस्थान', bn: 'রাজস্থান' },
    { id: 'Haryana', en: 'Haryana', hi: 'हरियाणा', bn: 'হরিয়ানা' },
    { id: 'Kerala', en: 'Kerala', hi: 'केरल', bn: 'কেরালা' }
  ];

  const CROPS_LIST = [
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
  ];

  let wizardState = {
    currentStep: 1,
    profile: null,
    sensitive: null,
    plots: [],
    selectedCrops: [],
    leafletMap: null,
    polygonLayer: null,
    drawnPoints: [],
    leafletAvailable: false,
    adminFilterStatus: 'ALL',
    adminEntities: [],
    adminInspectedEntity: null
  };

  function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function getLang() {
    return (typeof currentLang !== 'undefined' ? currentLang : (localStorage.getItem('annasutra_lang') || 'en'));
  }

  function getI18n() {
    const l = getLang();
    const base = WIZARD_I18N[l] || WIZARD_I18N.en;
    const extra = (window.EXTRA_I18N && window.EXTRA_I18N[l]) ? window.EXTRA_I18N[l] : {};
    const merged = Object.assign({}, WIZARD_I18N.en, base, extra);
    // Clean any legacy arrow symbols from btnPrev/btnNext
    if (merged.btnPrev) merged.btnPrev = String(merged.btnPrev).replace(/\u2190/g, '').trim();
    if (merged.btnNext) merged.btnNext = String(merged.btnNext).replace(/\u2192|&rarr;/g, '').trim();
    return merged;
  }

  function getCropLabel(cropId) {
    const l = getLang();
    const found = CROPS_LIST.find(c => c.id === cropId);
    if (!found) return cropId;
    return found.labels[l] || found.labels.en || cropId;
  }

  function getStateLabel(stateId) {
    if (!stateId) return '';
    const l = getLang();
    const found = STATES_LIST.find(s => s.id === stateId);
    if (!found) return stateId;
    return found[l] || found.en || stateId;
  }

  function getAuthHeader() {
    const token = localStorage.getItem('annasutra_access_token');
    const phone = localStorage.getItem('annasutra_phone') || '';
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = 'Bearer ' + token;
    if (phone) headers['X-Entity-Phone'] = phone;
    return headers;
  }

  function formatPhoneTag(rawPhone) {
    const savedPhone = rawPhone || localStorage.getItem('annasutra_phone') || (wizardState.profile && wizardState.profile.phone_e164) || '';
    const digits = String(savedPhone).replace(/\D/g, '');
    return digits.length >= 4 ? 'X' + digits.slice(-4) : 'X0000';
  }

  function formatEntityUserBadge(role, phone, lang) {
    const l = lang || getLang();
    const roleMap = {
      en: { PRODUCER: 'Producer', AGGREGATOR: 'Aggregator', WHOLESALER: 'Wholesaler', DISTRIBUTOR: 'Distributor', RETAILER: 'Retailer', ADMIN: 'Admin' },
      hi: { PRODUCER: 'उत्पादक', AGGREGATOR: 'संग्रहकर्ता', WHOLESALER: 'थोक व्यापारी', DISTRIBUTOR: 'वितरक', RETAILER: 'खुदरा विक्रेता', ADMIN: 'प्रशासक' },
      bn: { PRODUCER: 'উৎপাদক', AGGREGATOR: 'সংগ্রহকারী', WHOLESALER: 'পাইকারি বিক্রেতা', DISTRIBUTOR: 'পরিবেশক', RETAILER: 'খুচরা বিক্রেতা', ADMIN: 'প্রশাসক' }
    };
    const rCode = String(role || 'PRODUCER').toUpperCase();
    const dict = (window.EXTRA_I18N && window.EXTRA_I18N[l]) || {};
    const i18nMap = {
      PRODUCER: dict.tabProducerLabel,
      AGGREGATOR: dict.tabAggregatorLabel,
      WHOLESALER: dict.tabWholesalerLabel,
      DISTRIBUTOR: dict.tabDistributorLabel,
      RETAILER: dict.tabRetailerLabel,
      ADMIN: dict.portalRoleTitleAdmin
    };
    const rLabel = (roleMap[l] && roleMap[l][rCode]) || i18nMap[rCode] || (roleMap.en[rCode] || rCode);
    const tag = formatPhoneTag(phone);
    return `${rLabel} (${tag})`;
  }
  window.formatEntityUserBadge = formatEntityUserBadge;

  function updateRegisteredHeaderBanner(profile) {
    const t = getI18n();
    const p = profile || wizardState.profile || {};
    const activeRole = (typeof currentRole !== 'undefined' && currentRole) ? currentRole : (p.role || 'PRODUCER');
    const fullName = (p.full_name || [p.first_name, p.last_name].filter(Boolean).join(' ')).trim();
    const orgName = (p.organisation_name || '').trim();

    let registeredDisplay = '';
    if (orgName) {
      registeredDisplay = orgName;
    } else if (fullName) {
      registeredDisplay = fullName;
    } else {
      registeredDisplay = formatEntityUserBadge(activeRole, p.phone_e164, getLang());
    }

    const confinedEl = document.getElementById('confinedBadgeText');
    if (confinedEl) confinedEl.textContent = registeredDisplay;

    const titleEl = document.getElementById('workspaceTitle');
    if (titleEl && (activeRole === 'ADMIN' || activeRole === 'PRODUCER')) {
      titleEl.textContent = activeRole === 'ADMIN'
        ? t.workspaceTitleAdmin
        : t.workspaceTitleProducer;
    }

    const subEl = document.getElementById('workspaceSubtitle');
    if (subEl) {
      const locParts = [p.village_town, p.district, getStateLabel(p.state)].filter(Boolean).join(', ');
      subEl.textContent = locParts ? `${registeredDisplay} • ${locParts}` : registeredDisplay;
    }

    const activeUserEl = document.getElementById('activeUserName');
    if (activeUserEl) {
      activeUserEl.textContent = formatEntityUserBadge(activeRole, p.phone_e164, getLang());
    }
  }
  window.updateRegisteredHeaderBanner = updateRegisteredHeaderBanner;

  window.addEventListener('annasutra_lang_change', function () {
    const ws = document.getElementById('confinedWorkspace') || document.getElementById('entityWorkspace');
    if (ws && ws.style.display !== 'none') {
      if (typeof currentRole !== 'undefined' && (currentRole === 'PRODUCER' || currentRole === 'ADMIN')) {
        const contentArea = document.getElementById('workspaceDynamicContent');
        if (contentArea) {
          updateRegisteredHeaderBanner(wizardState.profile);
          if (currentRole === 'ADMIN') {
            renderAdminConsoleUI(contentArea);
          } else if (wizardState.profile && wizardState.profile.status === 'SUBMITTED') {
            renderUnderReviewCard(contentArea);
          } else if (wizardState.profile && wizardState.profile.status === 'VERIFIED') {
            renderVerifiedOperationalConsole(contentArea);
          } else {
            renderWizardInterface(contentArea);
          }
        }
      }
    }
  });

  window.openProducerOperationalDashboard = function (initialTab) {
    wizardState.forceConsoleView = true;
    const contentArea = document.getElementById('workspaceDynamicContent');
    if (contentArea) {
      renderVerifiedOperationalConsole(contentArea);
      if (initialTab) {
        setTimeout(() => window.switchProducerConsoleTab(initialTab), 60);
      }
    }
  };

  window.openProducerRegistrationWizard = function () {
    wizardState.forceConsoleView = false;
    const contentArea = document.getElementById('workspaceDynamicContent');
    if (contentArea) {
      renderWizardInterface(contentArea);
    }
  };

  window.renderCurrentWorkspace = async function () {
    const container = document.getElementById('confinedWorkspace');
    if (!container) return;

    const toolsGrid = document.getElementById('workspaceTools');
    const batchesList = document.getElementById('workspaceBatchesList');
    if (toolsGrid) toolsGrid.style.display = 'none';
    if (batchesList && batchesList.parentNode) batchesList.parentNode.style.display = 'none';

    let contentArea = document.getElementById('workspaceDynamicContent');
    if (!contentArea) {
      contentArea = document.createElement('div');
      contentArea.id = 'workspaceDynamicContent';
      contentArea.style.minHeight = '350px';
      container.appendChild(contentArea);
    }
    contentArea.style.display = 'block';

    if (typeof currentRole !== 'undefined' && currentRole !== 'PRODUCER' && currentRole !== 'ADMIN') {
      await renderDownstreamCustodyConsole(contentArea, currentRole);
      return;
    }

    const t = getI18n();

    // SWR STEP 1: Check for cached profile in localStorage for 0ms INSTANT HYDRATION!
    let hasRenderedCached = false;
    let cachedProfile = null;
    try {
      cachedProfile = JSON.parse(localStorage.getItem('annasutra_cached_profile'));
    } catch (e) {}

    if (cachedProfile && currentRole === 'PRODUCER') {
      wizardState.profile = cachedProfile;
      if (cachedProfile.role_details && cachedProfile.role_details.commodities) {
        wizardState.selectedCrops = cachedProfile.role_details.commodities;
      }
      try {
        const cachedPlots = JSON.parse(localStorage.getItem('annasutra_cached_plots') || '[]');
        if (Array.isArray(cachedPlots)) wizardState.plots = cachedPlots;
      } catch (e) {}
      try {
        const cachedLots = JSON.parse(localStorage.getItem('annasutra_cached_lots') || '[]');
        if (Array.isArray(cachedLots)) window._producerLots = cachedLots;
      } catch (e) {}

      updateRegisteredHeaderBanner(wizardState.profile);

      if (cachedProfile.status === 'VERIFIED' || wizardState.forceConsoleView) {
        renderVerifiedOperationalConsole(contentArea);
        updateLotMetrics();
        applyLotFilters();
        hasRenderedCached = true;
      } else if (cachedProfile.status === 'SUBMITTED') {
        renderUnderReviewCard(contentArea);
        hasRenderedCached = true;
      }
    }

    // Only show loading spinner if we didn't have cached data to render immediately
    if (!hasRenderedCached) {
      contentArea.innerHTML = `
        <div style="text-align: center; padding: 48px 16px;">
          <div style="width: 36px; height: 36px; border: 3px solid #cbd5e1; border-top-color: #0b3d2e; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 16px;"></div>
          <p style="color: #64748b; font-size: 14px; font-weight: 600;">${escapeHtml(t.loadingRegistry)}</p>
        </div>
      `;
    }

    if (typeof currentRole !== 'undefined' && currentRole === 'ADMIN') {
      updateRegisteredHeaderBanner({ organisation_name: t.workspaceTitleAdmin });
      await loadAdminQueueAndRender(contentArea);
      return;
    }

    // SWR STEP 2: Parallel Background Revalidation (No waterfall, no blocking)
    try {
      const [profileRes, lotsRes, plotsRes] = await Promise.all([
        fetch('/api/v1/me/profile', { headers: getAuthHeader() }),
        fetch('/api/v1/lots/', { headers: getAuthHeader() }),
        fetch('/api/v1/me/plots', { headers: getAuthHeader() })
      ]);

      if (profileRes.status === 401 || profileRes.status === 403) {
        localStorage.removeItem('annasutra_cached_profile');
        localStorage.removeItem('annasutra_cached_lots');
        localStorage.removeItem('annasutra_cached_plots');
        wizardState.profile = { status: 'DRAFT', role: 'PRODUCER', version: 1 };
        updateRegisteredHeaderBanner(wizardState.profile);
        renderWizardInterface(contentArea);
        return;
      }

      const data = await profileRes.json();
      wizardState.profile = data.profile || data;
      if (wizardState.profile.farmer_uid) {
        localStorage.setItem('annasutra_farmer_uid', wizardState.profile.farmer_uid);
      }
      try {
        localStorage.setItem('annasutra_cached_profile', JSON.stringify(wizardState.profile));
      } catch (e) {}

      if (wizardState.profile.role_details && wizardState.profile.role_details.commodities) {
        wizardState.selectedCrops = wizardState.profile.role_details.commodities;
      }

      if (plotsRes && plotsRes.ok) {
        const pData = await plotsRes.json();
        wizardState.plots = pData.plots || [];
        try {
          localStorage.setItem('annasutra_cached_plots', JSON.stringify(wizardState.plots));
        } catch (e) {}
      }

      if (lotsRes && lotsRes.ok) {
        const lData = await lotsRes.json();
        window._producerLots = lData.items || [];
        try {
          localStorage.setItem('annasutra_cached_lots', JSON.stringify(window._producerLots));
        } catch (e) {}
      }

      updateRegisteredHeaderBanner(wizardState.profile);

      const pStatus = wizardState.profile.status;
      if (pStatus === 'VERIFIED' || wizardState.forceConsoleView || (window._producerLots && window._producerLots.length > 0)) {
        if (!hasRenderedCached) {
          renderVerifiedOperationalConsole(contentArea);
        }
        updateLotMetrics();
        applyLotFilters();
        if (document.getElementById('consoleTabContentAnalytics')?.style.display !== 'none') {
          renderProducerAnalytics();
        }
      } else if (pStatus === 'SUBMITTED') {
        renderUnderReviewCard(contentArea);
      } else {
        renderWizardInterface(contentArea);
      }
    } catch (err) {
      if (!hasRenderedCached) {
        updateRegisteredHeaderBanner(wizardState.profile);
        renderWizardInterface(contentArea);
      }
    }
  };

  window.renderWorkspaceBatches = function (def) {
    const list = document.getElementById('workspaceBatchesList');
    if (!list || !def || !def.batches) return;
    if (def.batches.length === 0) {
      list.innerHTML = '';
      return;
    }
    list.innerHTML = def.batches.map(b => `
      <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; border-bottom: 1px solid #f1f5f9;">
        <span style="font-family: monospace; font-weight: 800; color: #0b3d2e;">${escapeHtml(b.code)}</span>
        <span style="font-size: 13px; color: #334155;">${escapeHtml(b.desc)}</span>
        <span style="font-size: 11.5px; font-weight: 700; color: #15803d; background: #ecfdf5; border: 1px solid #a7f3d0; padding: 3px 9px; border-radius: 20px;">${escapeHtml(b.status)}</span>
      </div>
    `).join('');
  };

  /* --------------------------------------------------------------------------
     ADMIN VERIFICATION PORTAL CONSOLE
     -------------------------------------------------------------------------- */
  async function loadAdminQueueAndRender(container) {
    try {
      const statusParam = wizardState.adminFilterStatus || 'ALL';
      const res = await fetch(`/api/v1/admin/reviews?status=${encodeURIComponent(statusParam)}`, {
        headers: getAuthHeader()
      });
      if (res.ok) {
        const data = await res.json();
        wizardState.adminEntities = data.results || [];
      } else {
        wizardState.adminEntities = [];
      }
    } catch (e) {
      wizardState.adminEntities = [];
    }
    renderAdminConsoleUI(container);
  }

  window.filterAdminQueue = async function (statusFilter) {
    wizardState.adminFilterStatus = statusFilter;
    wizardState.adminInspectedEntity = null;
    const contentArea = document.getElementById('workspaceDynamicContent');
    if (contentArea) {
      await loadAdminQueueAndRender(contentArea);
    }
  };

function renderAdminConsoleUI(container) {
    const t = getI18n();
    const activeFilter = wizardState.adminFilterStatus || 'ALL';
    const items = wizardState.adminEntities || [];
    const inspected = wizardState.adminInspectedEntity;

    const filters = [
      { key: 'ALL', label: t.filterAll },
      { key: 'SUBMITTED', label: t.filterSubmitted },
      { key: 'VERIFIED', label: t.filterVerified },
      { key: 'DRAFT', label: t.filterDraft },
      { key: 'NEEDS_CHANGES', label: t.filterChanges },
      { key: 'REJECTED', label: t.filterRejected },
      { key: 'TRASH', label: t.tabTrash || 'Trash' }
    ];

    container.innerHTML = `
      <div style="background: #ffffff; border-radius: 16px; border: 1.5px solid #cbd5e1; padding: 24px; margin: 12px 0;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 14px; margin-bottom: 18px; border-bottom: 1px solid #e2e8f0; padding-bottom: 14px;">
          <div>
            <h3 style="margin: 0 0 4px; font-size: 20px; color: #0b3d2e; display: flex; align-items: center; gap: 8px;">
              <span>${getIcon('shield', 20, '#047857')}</span>
              <span>${escapeHtml(t.adminQueueTitle)}</span>
            </h3>
            <p style="margin: 0; font-size: 13px; color: #64748b;">${escapeHtml(t.adminQueueSub)}</p>
          </div>
          <div style="display: flex; gap: 6px; flex-wrap: wrap;">
            ${filters.map(f => `
              <button type="button" onclick="filterAdminQueue('${f.key}')" style="padding: 7px 13px; border-radius: 8px; font-size: 12px; font-weight: 700; cursor: pointer; border: 1px solid ${activeFilter === f.key ? '#0b3d2e' : '#cbd5e1'}; background: ${activeFilter === f.key ? '#0b3d2e' : '#f8fafc'}; color: ${activeFilter === f.key ? '#ffffff' : '#334155'};">
                ${escapeHtml(f.label)}
              </button>
            `).join('')}
          </div>
        </div>

        ${inspected ? renderAdminEntityInspector(inspected, t) : ''}

        <div style="overflow-x: auto;">
          <table class="batch-table" style="width: 100%; border-collapse: collapse;">
            <thead>
              <tr style="background: #f8fafc; border-bottom: 2px solid #e2e8f0;">
                <th style="padding: 10px 12px; text-align: left; font-size: 12px; color: #475569;">${escapeHtml(t.thApplicant)}</th>
                <th style="padding: 10px 12px; text-align: left; font-size: 12px; color: #475569;">${escapeHtml(t.thRolePhone)}</th>
                <th style="padding: 10px 12px; text-align: left; font-size: 12px; color: #475569;">${escapeHtml(t.thLocation)}</th>
                <th style="padding: 10px 12px; text-align: left; font-size: 12px; color: #475569;">${escapeHtml(t.thPlots)}</th>
                <th style="padding: 10px 12px; text-align: left; font-size: 12px; color: #475569;">${escapeHtml(t.thStatus)}</th>
                <th style="padding: 10px 12px; text-align: right; font-size: 12px; color: #475569;">${escapeHtml(t.thActions)}</th>
              </tr>
            </thead>
            <tbody>
              ${items.length === 0 ? `
                <tr>
                  <td colspan="6" style="padding: 32px; text-align: center; color: #64748b; font-size: 13.5px;">
                    ${escapeHtml(t.noApplicationsFound)}
                  </td>
                </tr>
              ` : items.map(item => {
                const statusColors = {
                  VERIFIED: { bg: '#ecfdf5', text: '#065f46', border: '#86efac' },
                  SUBMITTED: { bg: '#fffbeb', text: '#92400e', border: '#fde68a' },
                  DRAFT: { bg: '#f1f5f9', text: '#475569', border: '#cbd5e1' },
                  NEEDS_CHANGES: { bg: '#fff7ed', text: '#9a3412', border: '#fed7aa' },
                  REJECTED: { bg: '#fef2f2', text: '#991b1b', border: '#fecaca' },
                  TRASH: { bg: '#fef2f2', text: '#b91c1c', border: '#fca5a5' }
                };
                const sc = statusColors[item.status] || statusColors.DRAFT;
                return `
                  <tr style="border-bottom: 1px solid #f1f5f9;">
                    <td style="padding: 12px;">
                      <strong style="color: #0f172a; font-size: 13.5px; display: block;">${escapeHtml(item.organisation_name || item.full_name || t.notEntered)}</strong>
                      <span style="font-size: 12px; color: #64748b;">${escapeHtml(item.full_name || '')}</span>
                    </td>
                    <td style="padding: 12px;">
                      <span style="font-weight: 700; font-size: 12px; color: #0b3d2e; display: block;">${escapeHtml(item.role)}</span>
                      <span style="font-family: monospace; font-size: 12px; color: #475569;">${escapeHtml(item.phone_e164)}</span>
                    </td>
                    <td style="padding: 12px; font-size: 12.5px; color: #334155;">
                      ${escapeHtml([item.district, getStateLabel(item.state)].filter(Boolean).join(', ') || t.notEntered)}
                    </td>
                    <td style="padding: 12px; font-size: 12.5px; color: #334155;">
                      ${escapeHtml(String(item.total_land_acres || 0))} ${escapeHtml(t.acresUnit)} (${item.plot_count || 0} ${escapeHtml(t.plotsWord)})
                    </td>
                    <td style="padding: 12px;">
                      <span style="display: inline-block; background: ${sc.bg}; color: ${sc.text}; border: 1px solid ${sc.border}; padding: 3px 9px; border-radius: 20px; font-size: 11px; font-weight: 800;">
                        ${escapeHtml(item.status)}
                      </span>
                      ${item.entity_code ? `<div style="font-family: monospace; font-size: 11.5px; font-weight: 800; color: #0b3d2e; margin-top: 4px;">${escapeHtml(item.entity_code)}</div>` : ''}
                    </td>
                    <td style="padding: 12px; text-align: right; white-space: nowrap;">
                      <button type="button" class="btn-wizard-action btn-wizard-draft" style="padding: 6px 12px; font-size: 11.5px; margin-right: 6px;" onclick="inspectAdminEntity('${item.entity_id}')">
                        ${escapeHtml(t.btnInspect)}
                      </button>
                      ${item.status !== 'VERIFIED' ? `
                        <button type="button" class="btn-wizard-action btn-wizard-submit" style="padding: 6px 12px; font-size: 11.5px;" onclick="submitAdminDecision('${item.entity_id}', 'APPROVED')">
                          ${escapeHtml(t.btnApproveNow)}
                        </button>
                      ` : `
                        <button type="button" class="btn-wizard-action btn-wizard-next" style="padding: 6px 12px; font-size: 11.5px;" onclick="issueAdditionalAdminQr('${item.entity_id}')">
                          ${escapeHtml(t.btnIssueMoreQr)}
                        </button>
                      `}
                    </td>
                  </tr>
                `;
              }).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  }

  function renderAdminEntityInspector(ent, t) {
    const sens = ent.sensitive || {};
    const crops = (ent.role_details && ent.role_details.commodities) ? ent.role_details.commodities.map(getCropLabel).join(', ') : t.noneSelected;
    return `
      <div style="background: #f8fafc; border: 1.5px solid #86efac; border-radius: 12px; padding: 18px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #e2e8f0; padding-bottom: 10px;">
          <div>
            <strong style="font-size: 16px; color: #0b3d2e;">${escapeHtml(t.inspectorTitle)}: ${escapeHtml(ent.organisation_name || (ent.first_name + ' ' + ent.last_name))}</strong>
            <span style="margin-left: 10px; font-family: monospace; font-size: 12px; color: #047857; font-weight: 800;">${escapeHtml(ent.entity_code || ent.status)}</span>
          </div>
          <button type="button" class="btn-wizard-action btn-wizard-prev" style="padding: 5px 12px; font-size: 12px;" onclick="closeAdminInspector()">
            ${escapeHtml(t.btnCloseInspector)}
          </button>
        </div>

        <div class="submitted-details-grid" style="margin-top: 10px; margin-bottom: 14px;">
          <div class="detail-item-box">
            <div class="detail-item-label">${escapeHtml(t.sumApplicant)}</div>
            <div class="detail-item-value">${escapeHtml(ent.first_name || '')} ${escapeHtml(ent.last_name || '')} (${escapeHtml(ent.phone_e164 || '')})</div>
          </div>
          <div class="detail-item-box">
            <div class="detail-item-label">${escapeHtml(t.sumJurisdiction)}</div>
            <div class="detail-item-value">${escapeHtml([ent.address_line1, ent.village_town, ent.district, getStateLabel(ent.state), ent.pincode].filter(Boolean).join(', '))}</div>
          </div>
          <div class="detail-item-box">
            <div class="detail-item-label">${escapeHtml(t.sumLand)} & ${escapeHtml(t.sumCrops)}</div>
            <div class="detail-item-value">${escapeHtml(String(ent.total_land_acres || 0))} ${escapeHtml(t.acresUnit)} (${(ent.plots || []).length} ${escapeHtml(t.plotsWord)}) • ${escapeHtml(crops)}</div>
          </div>
          <div class="detail-item-box">
            <div class="detail-item-label">${escapeHtml(t.lblKycVault)}</div>
            <div class="detail-item-value" id="adminRevealedKycBox">
              PAN: ${escapeHtml(sens.pan_masked || t.notEntered)} | Bank: ${escapeHtml(sens.bank_name || '')} (${escapeHtml(sens.account_no_masked || t.notEntered)}) | IFSC: ${escapeHtml(sens.ifsc || '')}
            </div>
            <div style="margin-top: 6px; display: flex; gap: 6px; flex-wrap: wrap;">
              <button type="button" style="font-size: 11px; padding: 3px 8px; border-radius: 6px; border: 1px solid #cbd5e1; background: #fff; cursor: pointer;" onclick="revealAdminField('${ent.entity_id}', 'pan')">${escapeHtml(t.btnRevealPan)}</button>
              <button type="button" style="font-size: 11px; padding: 3px 8px; border-radius: 6px; border: 1px solid #cbd5e1; background: #fff; cursor: pointer;" onclick="revealAdminField('${ent.entity_id}', 'account_no')">${escapeHtml(t.btnRevealBank)}</button>
            </div>
          </div>
        </div>

        <div style="margin-bottom: 12px;">
          <label class="form-label" style="font-size: 12px;">${escapeHtml(t.lblReviewNotes)}</label>
          <input type="text" class="form-input" id="inp_admin_review_notes" placeholder="${escapeHtml(t.reviewNotesPh)}" />
        </div>

        <div style="display: flex; gap: 10px; flex-wrap: wrap; align-items: center;">
          ${ent.status === 'TRASH' ? `
            <div style="width: 100%; background: #fee2e2; border: 1px solid #f87171; border-radius: 8px; padding: 10px 14px; color: #991b1b; font-size: 13px; font-weight: 700; margin-bottom: 8px;">
              <span>${getIcon('alert', 16, '#dc2626')}</span> <span>This producer is currently in Admin Trash.</span>
            </div>
            <button type="button" class="btn-wizard-action btn-wizard-submit" onclick="restoreAdminProducer('${ent.entity_id}')">
              <span>${getIcon('check', 14, '#ffffff')}</span> <span>${escapeHtml(t.btnRestoreProducer || 'Restore Producer')}</span>
            </button>
            <button type="button" class="btn-wizard-action" style="color: #ffffff; background: #991b1b; border: 1.5px solid #7f1d1d; font-weight: 700;" onclick="openDeleteProducerModal('${ent.entity_id}', '${escapeHtml(ent.organisation_name || ent.full_name)}', true)">
              <span>${getIcon('trash', 14, '#ffffff')}</span> <span>${escapeHtml(t.btnPurgeProducer || 'Purge Permanently')}</span>
            </button>
          ` : `
            <button type="button" class="btn-wizard-action btn-wizard-submit" onclick="submitAdminDecision('${ent.entity_id}', 'APPROVED')">
              <span>${getIcon('check', 14, '#ffffff', 2.8)}</span> <span>${escapeHtml(t.btnApproveEntity)}</span>
            </button>
            <button type="button" class="btn-wizard-action btn-wizard-draft" onclick="submitAdminDecision('${ent.entity_id}', 'NEEDS_CHANGES')">
              ${escapeHtml(t.btnRequestChanges)}
            </button>
            <button type="button" class="btn-wizard-action btn-wizard-prev" style="color: #dc2626; border-color: #fca5a5;" onclick="submitAdminDecision('${ent.entity_id}', 'REJECTED')">
              ${escapeHtml(t.btnRejectEntity)}
            </button>
            <button type="button" class="btn-wizard-action" style="color: #ffffff; background: #dc2626; border: 1.5px solid #b91c1c; font-weight: 700; display: inline-flex; align-items: center; gap: 6px;" onclick="openDeleteProducerModal('${ent.entity_id}', '${escapeHtml(ent.organisation_name || ent.full_name)}', false)">
              <span>${getIcon('trash', 14, '#ffffff')}</span> <span>${escapeHtml(t.btnDeleteProducer || 'Delete Producer Data')}</span>
            </button>
          `}
        </div>
      </div>
    `;
  }

  window.inspectAdminEntity = async function (entityId) {
    try {
      const res = await fetch(`/api/v1/admin/entities/${entityId}`, { headers: getAuthHeader() });
      if (res.ok) {
        wizardState.adminInspectedEntity = await res.json();
        const contentArea = document.getElementById('workspaceDynamicContent');
        if (contentArea) renderAdminConsoleUI(contentArea);
      }
    } catch (e) {
      showToast('Failed to load entity details.', 'error');
    }
  };

  window.closeAdminInspector = function () {
    wizardState.adminInspectedEntity = null;
    const contentArea = document.getElementById('workspaceDynamicContent');
    if (contentArea) renderAdminConsoleUI(contentArea);
  };

  window.revealAdminField = async function (entityId, fieldName) {
    try {
      const res = await fetch(`/api/v1/admin/entities/${entityId}/reveal`, {
        method: 'POST',
        headers: getAuthHeader(),
        body: JSON.stringify({
          field: fieldName,
          reason: 'Administrative KYC verification prior to sovereign entity code approval'
        })
      });
      const data = await res.json();
      if (res.ok && data.plaintext) {
        const box = document.getElementById('adminRevealedKycBox');
        if (box) {
          box.innerHTML += ` <strong style="color:#047857; font-family:monospace;">[${escapeHtml(fieldName.toUpperCase())}: ${escapeHtml(data.plaintext)}]</strong>`;
        }
      } else {
        showToast(data.detail || 'Unable to reveal field.', 'warning');
      }
    } catch (e) {
      showToast('Network error revealing field.', 'error');
    }
  };

  window.submitAdminDecision = async function (entityId, decision) {
    const notesInp = document.getElementById('inp_admin_review_notes');
    const reason = (notesInp && notesInp.value.trim()) || (decision === 'APPROVED' ? 'Verified by Administrator via Web Portal' : 'Verification update required');

    try {
      const res = await fetch(`/api/v1/admin/entities/${entityId}/decision`, {
        method: 'POST',
        headers: getAuthHeader(),
        body: JSON.stringify({
          decision: decision,
          reason: reason
        })
      });
      const data = await res.json();
      if (res.ok) {
        if (decision === 'APPROVED') {
          showToast(`${data.entity_code || 'Entity'} verified! Unlimited QR printing enabled.`, 'success');
        } else {
          showToast(`Decision recorded: ${decision}`, 'info');
        }
        wizardState.adminInspectedEntity = null;
        const contentArea = document.getElementById('workspaceDynamicContent');
        if (contentArea) await loadAdminQueueAndRender(contentArea);
      } else {
        showToast(data.detail || 'Decision action failed.', 'error');
      }
    } catch (e) {
      showToast('Network error submitting decision.', 'error');
    }
  };

  window.issueAdditionalAdminQr = async function (entityId) {
    try {
      const res = await fetch(`/api/v1/admin/entities/${entityId}/qr-blocks`, {
        method: 'POST',
        headers: getAuthHeader(),
        body: JSON.stringify({ count: 20 })
      });
      const data = await res.json();
      if (res.ok) {
        showToast(`Issued ${data.count} new Crockford Base32 QR serials.`, 'success');
      } else {
        showToast(data.detail || 'Could not issue QR block.', 'error');
      }
    } catch (e) {
      showToast('Network error issuing QR block.', 'error');
    }
  };

  /* --------------------------------------------------------------------------
     UNDER REVIEW SCREEN
     -------------------------------------------------------------------------- */
  function renderUnderReviewCard(container) {
    const t = getI18n();
    const p = wizardState.profile || {};
    const sens = wizardState.sensitive || {};
    const farmerUid = p.farmer_uid || localStorage.getItem('annasutra_farmer_uid') || p.entity_code || 'PENDING';

    container.innerHTML = `
      <div class="status-review-card">
        <div style="display: flex; justify-content: center; gap: 10px; flex-wrap: wrap; margin-bottom: 12px;">
          <div class="status-badge-submitted" style="margin-bottom: 0;">
            <span>${getIcon('clock', 16, '#f59e0b')}</span> <span>${escapeHtml(t.underReviewTitle)}</span>
          </div>
          <button type="button" class="btn-wizard-action btn-wizard-submit" style="padding: 8px 18px; font-size: 13px; font-weight: 800;" onclick="window.openProducerOperationalDashboard('ledger')">
            <span>Open Farmer Dashboard, Create Batch &amp; Live Map &rarr;</span>
          </button>
        </div>
        <h3 style="font-size: 22px; color: #0f172a; margin: 0 0 8px;">${escapeHtml(p.organisation_name || [p.first_name, p.last_name].filter(Boolean).join(' '))}</h3>
        <div style="margin-bottom: 10px; font-family: monospace; font-size: 14px; font-weight: 800; color: #047857; background: #ecfdf5; border: 1px solid #86efac; display: inline-block; padding: 5px 14px; border-radius: 20px;">
          Unique Farmer ID: ${escapeHtml(farmerUid)}
        </div>
        <p style="color: #64748b; font-size: 14px; max-width: 620px; margin: 0 auto; line-height: 1.5;">${escapeHtml(t.underReviewSub)}</p>

        <div class="submitted-details-grid">
          <div class="detail-item-box">
            <div class="detail-item-label">${escapeHtml(t.firstName)} &amp; ${escapeHtml(t.lastName)}</div>
            <div class="detail-item-value">${escapeHtml(p.first_name || '')} ${escapeHtml(p.last_name || '')}</div>
          </div>
          <div class="detail-item-box">
            <div class="detail-item-label">${escapeHtml(t.district)} &amp; ${escapeHtml(t.state)}</div>
            <div class="detail-item-value">${escapeHtml(p.district || '')}, ${escapeHtml(getStateLabel(p.state))} (${escapeHtml(p.pincode || '')})</div>
          </div>
          <div class="detail-item-box">
            <div class="detail-item-label">${escapeHtml(t.lblMappedLand)}</div>
            <div class="detail-item-value">${escapeHtml(String(p.total_land_acres || 0))} ${escapeHtml(t.acresUnit)} (${wizardState.plots.length} ${escapeHtml(t.plotsWord)})</div>
          </div>
          <div class="detail-item-box">
            <div class="detail-item-label">${escapeHtml(t.lblMaskedPan)}</div>
            <div class="detail-item-value">${escapeHtml(sens.pan_masked || (sens.aadhaar_last4 ? '•••• ' + sens.aadhaar_last4 : t.encryptedWord))}</div>
          </div>
          <div class="detail-item-box">
            <div class="detail-item-label">${escapeHtml(t.lblSettlementBank)}</div>
            <div class="detail-item-value">${escapeHtml(sens.bank_name || '')} (${escapeHtml(sens.bank_account_masked || '••••')})</div>
          </div>
          <div class="detail-item-box">
            <div class="detail-item-label">${escapeHtml(t.lblSubmissionDate)}</div>
            <div class="detail-item-value">${p.submitted_at ? new Date(p.submitted_at).toLocaleDateString() : new Date().toLocaleDateString()}</div>
          </div>
        </div>

        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px; margin-top: 20px; display: inline-flex; align-items: center; gap: 10px; font-size: 12.5px; color: #475569;">
          <span>${getIcon('lock', 16, '#047857')}</span>
          <span>${escapeHtml(t.lblEntityRefToken)}: <strong style="font-family: monospace; color: #0b3d2e;">${escapeHtml(p.entity_id || 'PENDING')}</strong></span>
        </div>
      </div>
    `;
  }

  /* --------------------------------------------------------------------------
     PRODUCT CATEGORY CATALOG (MENTOR'S 10 OFFICIAL 2-LETTER CODES)
     -------------------------------------------------------------------------- */
  const PRODUCT_CATEGORY_OPTIONS = [
    { code: 'FG', name: 'Food grains & cereals (FG)', defaultCrop: 'paddy_rice' },
    { code: 'PU', name: 'Pulses (PU)', defaultCrop: 'pulses' },
    { code: 'OI', name: 'Oilseeds (OI)', defaultCrop: 'mustard' },
    { code: 'FR', name: 'Fruits (FR)', defaultCrop: 'mango' },
    { code: 'VG', name: 'Vegetables (VG)', defaultCrop: 'potato' },
    { code: 'SP', name: 'Spices (SP)', defaultCrop: 'turmeric' },
    { code: 'CC', name: 'Commercial Crops (CC)', defaultCrop: 'jute' },
    { code: 'LS', name: 'Livestock (LS)', defaultCrop: 'livestock' },
    { code: 'SC', name: 'Special Crops (SC)', defaultCrop: 'tea' },
    { code: 'OT', name: 'Others (OT)', defaultCrop: 'other' }
  ];

  window.computeLiveMentorBatchIdPreview = function (catCode) {
    const p = wizardState.profile || {};
    const phoneDigits = String(p.phone_e164 || localStorage.getItem('annasutra_phone') || '919876543210').replace(/\D/g, '') || '919876543210';
    const d = new Date();
    const pad2 = n => String(n).padStart(2, '0');
    const ts = `${d.getFullYear()}${pad2(d.getDate())}${pad2(d.getHours())}${pad2(d.getMinutes())}${pad2(d.getSeconds())}`;
    const cCode = (catCode || 'VG').toUpperCase();
    const seq = String(((window._producerLots || []).length || 0) + 1).padStart(4, '0');
    return `${ts}${phoneDigits}${cCode}${seq}`;
  };

  window.updateInlineBatchIdPreview = function () {
    const catEl = document.getElementById('inline_lot_cat_code');
    const previewEl = document.getElementById('liveBatchIdPreviewCode');
    if (previewEl) {
      previewEl.textContent = window.computeLiveMentorBatchIdPreview(catEl ? catEl.value : 'VG');
    }
  };

  /* --------------------------------------------------------------------------
     VERIFIED PRODUCER CONSOLE: 4-TAB COMMAND CENTER & LIVE MOVEMENT MAP
     -------------------------------------------------------------------------- */
  window._producerLots = [];
  window._producerPlots = [];
  window._lotFilterState = {
    search: '',
    crop: 'ALL',
    plot: 'ALL',
    custody: 'ALL',
    payment: 'ALL',
    sort: '-created_at'
  };

  async function renderVerifiedOperationalConsole(container) {
    const t = getI18n();
    const p = wizardState.profile || {};
    const eCode = p.entity_code || '';
    const farmerUid = p.farmer_uid || localStorage.getItem('annasutra_farmer_uid') || window.computeLiveMentorBatchIdPreview('').slice(0, 22);
    const orgDisplayName = p.organisation_name || [p.first_name, p.last_name].filter(Boolean).join(' ') || 'Farmer Producer Node';

    // Permanently hide the 6 legacy tool cards and dummy batches list
    const toolsGrid = document.getElementById('workspaceTools');
    const batchesList = document.getElementById('workspaceBatchesList');
    if (toolsGrid) toolsGrid.style.display = 'none';
    if (batchesList && batchesList.parentNode) batchesList.parentNode.style.display = 'none';

    const plots = wizardState.plots || [];
    const registeredCrops = wizardState.selectedCrops || [];
    const nowIso = new Date().toISOString().slice(0, 16);

    container.innerHTML = `
      <div style="background: #ffffff; border-radius: 16px; border: 1.5px solid #10b981; padding: 24px; margin: 12px 0; box-shadow: 0 4px 16px rgba(16, 185, 129, 0.08);">
        <!-- Top Entity Header Bar -->
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #e2e8f0; padding-bottom: 14px; margin-bottom: 20px; flex-wrap: wrap; gap: 12px;">
          <div>
            <div style="display: inline-flex; align-items: center; gap: 6px; background: #ecfdf5; border: 1px solid #86efac; color: #065f46; font-size: 12px; font-weight: 800; padding: 4px 10px; border-radius: 20px; margin-bottom: 6px;">
              <span>${getIcon('check', 14, '#15803d', 2.8)}</span> <span>${escapeHtml(t.verifiedNodeBadge || 'VERIFIED PRODUCER NODE')}</span>
            </div>
            <h3 style="margin: 0; font-size: 22px; font-weight: 800; color: #0f172a;">${escapeHtml(orgDisplayName)}</h3>
            <span style="font-size: 13px; color: #64748b;">${escapeHtml([p.village_town, p.district, getStateLabel(p.state)].filter(Boolean).join(', ') || 'Registered Agricultural Producer')}</span>
          </div>
          <div style="text-align: right; display: flex; align-items: center; gap: 14px; flex-wrap: wrap;">
            <div style="background: #f0fdf4; border: 1.5px solid #86efac; padding: 8px 14px; border-radius: 10px; text-align: left;">
              <div style="font-size: 10.5px; font-weight: 800; color: #047857; text-transform: uppercase; letter-spacing: 0.5px;">Unique Farmer ID (YYYYDDHHMMSS+CCMobile)</div>
              <div style="font-family: monospace; font-size: 15.5px; font-weight: 900; color: #0b3d2e; letter-spacing: 0.5px;" id="farmerHeaderUniqueId">${escapeHtml(farmerUid)}</div>
            </div>
            ${eCode ? `
              <div>
                <div style="font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase;">${escapeHtml(t.lblSovereignCode || 'Sovereign Code')}</div>
                <div style="font-family: monospace; font-size: 17px; font-weight: 900; color: #0b3d2e; letter-spacing: 1px;">${escapeHtml(eCode)}</div>
              </div>
            ` : ''}
            <button type="button" class="btn-wizard-action btn-wizard-draft" style="padding: 7px 14px; font-size: 12px; color: #dc2626; border-color: #fca5a5;" onclick="window.logoutEntitySession()">
              ${escapeHtml(t.btnLogOut || 'Log Out')}
            </button>
          </div>
        </div>

        <!-- 4-Tab Navigation Bar -->
        <div style="display: flex; gap: 6px; border-bottom: 2px solid #e2e8f0; margin-bottom: 22px; flex-wrap: wrap;">
          <button type="button" id="tabBtnLedger" onclick="window.switchProducerConsoleTab('ledger')" style="padding: 11px 18px; font-size: 13px; font-weight: 800; border: none; border-bottom: 3px solid #047857; background: #ecfdf5; color: #065f46; border-radius: 8px 8px 0 0; cursor: pointer; display: inline-flex; align-items: center; gap: 7px; transition: all 0.2s;">
            <span>${getIcon('sprout', 16, '#047857')}</span> <span>1. Batch &amp; Custody Ledger</span>
          </button>
          <button type="button" id="tabBtnCreateMap" onclick="window.switchProducerConsoleTab('create_map')" style="padding: 11px 18px; font-size: 13px; font-weight: 800; border: none; border-bottom: 3px solid transparent; background: transparent; color: #64748b; border-radius: 8px 8px 0 0; cursor: pointer; display: inline-flex; align-items: center; gap: 7px; transition: all 0.2s;">
            <span>${getIcon('map-pin', 16, '#047857')}</span> <span>2. Create Batch &amp; Live Movement Map</span>
          </button>
          <button type="button" id="tabBtnAnalytics" onclick="window.switchProducerConsoleTab('analytics')" style="padding: 11px 18px; font-size: 13px; font-weight: 800; border: none; border-bottom: 3px solid transparent; background: transparent; color: #64748b; border-radius: 8px 8px 0 0; cursor: pointer; display: inline-flex; align-items: center; gap: 7px; transition: all 0.2s;">
            <span>${getIcon('activity', 16, '#64748b')}</span> <span>3. Farm Stats, Lands, Crops &amp; All Data</span>
          </button>
          <button type="button" id="tabBtnProfile" onclick="window.openProducerRegistrationWizard()" style="padding: 11px 18px; font-size: 13px; font-weight: 800; border: none; border-bottom: 3px solid transparent; background: transparent; color: #64748b; border-radius: 8px 8px 0 0; cursor: pointer; display: inline-flex; align-items: center; gap: 7px; transition: all 0.2s;">
            <span>${getIcon('edit', 16, '#64748b')}</span> <span>4. Update Farm &amp; KYC Data</span>
          </button>
        </div>

        <!-- TAB 1: Harvest Lots & Custody Ledger -->
        <div id="consoleTabContentLedger" style="display: block;">
          <!-- Quick Metrics Row -->
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-bottom: 22px;">
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 14px 16px; border-radius: 12px;">
              <div style="font-size: 12px; color: #64748b; font-weight: 700;">${escapeHtml(t.statTotalLots || 'Total Harvest Lots')}</div>
              <div style="font-size: 24px; font-weight: 900; color: #0b3d2e;" id="metricTotalLots">0</div>
              <div style="font-size: 11.5px; color: #10b981;">${escapeHtml(t.statInLedger || 'Recorded on Sovereign Chain')}</div>
            </div>
            <div style="background: #ecfdf5; border: 1.5px solid #a7f3d0; padding: 14px 16px; border-radius: 12px;">
              <div style="font-size: 12px; color: #065f46; font-weight: 700;">${escapeHtml(t.statusInCustody || 'In Farm Custody')}</div>
              <div style="font-size: 24px; font-weight: 900; color: #047857;" id="metricInCustody">0</div>
              <div style="font-size: 11.5px; color: #059669;">${escapeHtml(t.statEditable || 'Editable (Pre-Handover)')}</div>
            </div>
            <div style="background: #fffbeb; border: 1.5px solid #fde68a; padding: 14px 16px; border-radius: 12px;">
              <div style="font-size: 12px; color: #92400e; font-weight: 700;">${escapeHtml(t.statusInTransit || 'Handed Over / In Transit (Locked)')}</div>
              <div style="font-size: 24px; font-weight: 900; color: #b45309;" id="metricInTransit">0</div>
              <div style="font-size: 11.5px; color: #d97706;">${escapeHtml(t.statImmutable || 'Immutable Custody Transfer')}</div>
            </div>
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 14px 16px; border-radius: 12px;">
              <div style="font-size: 12px; color: #64748b; font-weight: 700;">${escapeHtml(t.statTotalQty || 'Total Harvest Weight')}</div>
              <div style="font-size: 24px; font-weight: 900; color: #0b3d2e;" id="metricTotalWeight">0.0 Kg</div>
              <div style="font-size: 11.5px; color: #64748b;">${escapeHtml(t.statCumulative || 'Cumulative Yield')}</div>
            </div>
          </div>

          <!-- Action Bar: Register Lot CTA Button -->
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 18px; padding-bottom: 12px; border-bottom: 1px solid #f1f5f9;">
            <div>
              <h4 style="margin: 0; font-size: 17px; font-weight: 800; color: #0f172a; display: flex; align-items: center; gap: 8px;">
                <span>${getIcon('sprout', 20, '#047857')}</span> <span>${escapeHtml(t.consoleHeading || 'Harvest Lot & Custody Ledger Console')}</span>
              </h4>
            </div>
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
              <button type="button" class="btn-wizard-action btn-wizard-draft" style="padding: 10px 16px; font-size: 13px; font-weight: 800;" onclick="window.switchProducerConsoleTab('create_map')">
                <span>${getIcon('map-pin', 14, '#047857')}</span> <span>Open Dedicated Batch &amp; Live Map Tab</span>
              </button>
              <button type="button" class="btn-wizard-action btn-wizard-submit" style="padding: 10px 20px; font-size: 13.5px; font-weight: 800; box-shadow: 0 4px 12px rgba(4, 120, 87, 0.25);" onclick="openHarvestLotModal(null)">
                <span style="font-size: 17px; line-height: 1; margin-right: 4px;">+</span> <span>${escapeHtml(t.btnRegisterLot || '+ Register New Harvest Lot')}</span>
              </button>
            </div>
          </div>

          <!-- Search & Filter Controls Toolbar -->
          <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px; margin-bottom: 18px; display: grid; grid-template-columns: 2fr repeat(4, 1fr) 1.2fr; gap: 10px; align-items: center;">
            <input type="text" id="filter_search" class="form-input" style="background: #fff; font-size: 12.5px;" placeholder="${escapeHtml(t.searchLotPh || 'Search lot code, crop, variety, or plot...')}" oninput="applyLotFilters()" />
            
            <select id="filter_crop" class="form-select" style="background: #fff; font-size: 12px;" onchange="applyLotFilters()">
              <option value="ALL">${escapeHtml(t.filterAllCrops || 'All Crops')}</option>
              ${(wizardState.selectedCrops || []).map(c => `<option value="${escapeHtml(c)}">${escapeHtml(getCropLabel(c))}</option>`).join('')}
            </select>

            <select id="filter_plot" class="form-select" style="background: #fff; font-size: 12px;" onchange="applyLotFilters()">
              <option value="ALL">${escapeHtml(t.filterAllPlots || 'All Plots / Land')}</option>
              ${(wizardState.plots || []).map(pl => `<option value="${escapeHtml(pl.plot_id)}">${escapeHtml(pl.plot_name || 'Plot')} (${pl.area_acres || 0} Ac)</option>`).join('')}
            </select>

            <select id="filter_custody" class="form-select" style="background: #fff; font-size: 12px;" onchange="applyLotFilters()">
              <option value="ALL">${escapeHtml(t.filterAllCustody || 'All Custody States')}</option>
              <option value="IN_CUSTODY">${escapeHtml(t.statusInCustody || 'In Farm Custody (Editable)')}</option>
              <option value="IN_TRANSIT">${escapeHtml(t.statusInTransit || 'In Transit (Locked)')}</option>
              <option value="CLOSED">${escapeHtml(t.statusHandoverDone || 'Handover Approved')}</option>
            </select>

            <select id="filter_payment" class="form-select" style="background: #fff; font-size: 12px;" onchange="applyLotFilters()">
              <option value="ALL">${escapeHtml(t.filterAllPayment || 'All Payment Statuses')}</option>
              <option value="PENDING">${escapeHtml(t.paymentPending || 'Pending Settlement')}</option>
              <option value="ADVANCE">${escapeHtml(t.paymentAdvance || 'Advance Received')}</option>
              <option value="SETTLED">${escapeHtml(t.paymentSettled || 'Fully Settled')}</option>
            </select>

            <select id="filter_sort" class="form-select" style="background: #fff; font-size: 12px; font-weight: 700;" onchange="applyLotFilters()">
              <option value="-created_at">${escapeHtml(t.sortLatest || 'Latest to Oldest')}</option>
              <option value="created_at">${escapeHtml(t.sortOldest || 'Oldest to Latest')}</option>
              <option value="-qty">${escapeHtml(t.sortQtyHigh || 'Quantity: High to Low')}</option>
              <option value="qty">${escapeHtml(t.sortQtyLow || 'Quantity: Low to High')}</option>
            </select>
          </div>

          <!-- Harvest Lots List Container -->
          <div id="producerHarvestLotsList">
            <div style="text-align: center; padding: 40px; color: #64748b;">
              <div style="width: 28px; height: 28px; border: 2.5px solid #cbd5e1; border-top-color: #047857; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 12px;"></div>
              <span>Loading registered harvest lots from ledger...</span>
            </div>
          </div>
        </div>

        <!-- TAB 2: Dedicated Create Batch & Live Lot Movement Map Tab -->
        <div id="consoleTabContentCreateMap" style="display: none;">
          <!-- TOP SECTION: Dedicated Create New Batch Form -->
          <div style="background: #f8fafc; border: 1.5px solid #cbd5e1; border-radius: 14px; padding: 20px; margin-bottom: 24px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 16px; border-bottom: 1px solid #e2e8f0; padding-bottom: 12px;">
              <div>
                <h4 style="margin: 0; font-size: 17px; font-weight: 800; color: #0b3d2e; display: flex; align-items: center; gap: 8px;">
                  <span>${getIcon('sprout', 20, '#047857')}</span>
                  <span>Create New Harvest Batch / Lot (Unlimited Unique QR &amp; Barcode)</span>
                </h4>
                <p style="margin: 2px 0 0; font-size: 12.5px; color: #64748b;">Fill batch details below to mint a deterministic conflict-free Batch ID and track live movement underneath.</p>
              </div>
              <div style="background: #ecfdf5; border: 1.5px solid #10b981; border-radius: 10px; padding: 8px 14px;">
                <div style="font-size: 10px; font-weight: 800; color: #065f46; text-transform: uppercase;">Next Batch/Lot ID Preview (YYYYDDHHMMSS+CCMobile+Code+Seq)</div>
                <div style="font-family: monospace; font-size: 14px; font-weight: 900; color: #047857;" id="liveBatchIdPreviewCode">${escapeHtml(window.computeLiveMentorBatchIdPreview('FR'))}</div>
              </div>
            </div>

            <form id="form_inline_create_batch" onsubmit="window.submitInlineBatchForm(event)">
              <div class="form-grid-4" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 12px; margin-bottom: 12px;">
                <div class="form-group">
                  <label class="form-label">Product Category Code <span class="req">*</span></label>
                  <select class="form-select" id="inline_lot_cat_code" onchange="window.updateInlineBatchIdPreview()" required style="background: #fff; font-weight: 700;">
                    ${PRODUCT_CATEGORY_OPTIONS.map(opt => `<option value="${opt.code}" ${opt.code === 'FR' ? 'selected' : ''}>${escapeHtml(opt.name)}</option>`).join('')}
                  </select>
                </div>
                <div class="form-group">
                  <label class="form-label">Crop / Commodity Name <span class="req">*</span></label>
                  <input type="text" class="form-input" id="inline_lot_crop" value="${escapeHtml(registeredCrops[0] || 'Mango')}" placeholder="e.g. Mango, Potato, Paddy, Turmeric" required style="background: #fff;" />
                </div>
                <div class="form-group">
                  <label class="form-label">Variety / Cultivar</label>
                  <input type="text" class="form-input" id="inline_lot_variety" value="Alphonso / Premium" placeholder="e.g. Alphonso, Jyoti" style="background: #fff;" />
                </div>
                <div class="form-group">
                  <label class="form-label">Origin Plot / Land Parcel</label>
                  <select class="form-select" id="inline_lot_plot" style="background: #fff;">
                    <option value="">Registered Farm Origin</option>
                    ${plots.map(pl => `<option value="${escapeHtml(pl.plot_id)}">${escapeHtml(pl.plot_name || 'Plot')} (${pl.area_acres || 0} Ac)</option>`).join('')}
                  </select>
                </div>
              </div>

              <div class="form-grid-4" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 12px;">
                <div class="form-group">
                  <label class="form-label">Net Harvest Weight (Kg) <span class="req">*</span></label>
                  <input type="number" step="0.1" min="0.1" class="form-input" id="inline_lot_qty" value="500" required style="background: #fff;" />
                </div>
                <div class="form-group">
                  <label class="form-label">Crates / Bags Count</label>
                  <input type="number" min="1" class="form-input" id="inline_lot_packages" value="25" style="background: #fff;" />
                </div>
                <div class="form-group">
                  <label class="form-label">Harvest Date &amp; Time <span class="req">*</span></label>
                  <input type="datetime-local" class="form-input" id="inline_lot_harvest_date" value="${nowIso}" required style="background: #fff;" />
                </div>
                <div class="form-group">
                  <label class="form-label">Last Input/Spray Date (PHI)</label>
                  <input type="date" class="form-input" id="inline_lot_spray_date" style="background: #fff;" />
                </div>
              </div>

              <div class="form-grid-4" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 14px;">
                <div class="form-group">
                  <label class="form-label">Quality Grade</label>
                  <select class="form-select" id="inline_lot_grade" style="background: #fff;">
                    <option value="Grade A">Grade A (Premium)</option>
                    <option value="Grade B">Grade B (Standard)</option>
                    <option value="Grade C">Grade C (Economy)</option>
                  </select>
                </div>
                <div class="form-group">
                  <label class="form-label">Farming Practice</label>
                  <select class="form-select" id="inline_lot_method" style="background: #fff;">
                    <option value="Organic NPOP">Organic (Certified NPOP)</option>
                    <option value="PGS-India">PGS-India Natural</option>
                    <option value="Good Agri Practices">GAP Certified</option>
                    <option value="Conventional">Conventional</option>
                  </select>
                </div>
                <div class="form-group">
                  <label class="form-label">Expected Base Price (₹/Kg)</label>
                  <input type="number" step="0.5" class="form-input" id="inline_lot_price" value="40" style="background: #fff;" />
                </div>
                <div class="form-group">
                  <label class="form-label">Shelf-Life (Days)</label>
                  <input type="number" min="1" max="365" class="form-input" id="inline_lot_shelf_life" value="14" style="background: #fff;" />
                </div>
              </div>

              <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; border-top: 1px solid #e2e8f0; padding-top: 12px;">
                <span style="font-size: 12px; color: #047857; font-weight: 700;">✓ Zero-Collision Batch ID • ✓ Unlimited 2D QR &amp; 1D Barcode Stickers</span>
                <button type="submit" class="btn-wizard-action btn-wizard-submit" style="padding: 10px 24px; font-weight: 800;">
                  <span>+ Mint Unique Batch &amp; Pin to Live Map</span>
                </button>
              </div>
            </form>
          </div>

          <!-- BOTTOM SECTION: Live Lot Movement Map & Next-Party Telemetry Updates -->
          <div style="background: #ffffff; border: 1.5px solid #10b981; border-radius: 14px; padding: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 14px;">
              <div>
                <h4 style="margin: 0; font-size: 17px; font-weight: 800; color: #0b3d2e; display: flex; align-items: center; gap: 8px;">
                  <span>${getIcon('map-pin', 20, '#047857')}</span>
                  <span>Live Lot Movement Map (Farm &rarr; Aggregator &rarr; Wholesaler &rarr; Distributor &rarr; Retailer)</span>
                </h4>
                <p style="margin: 2px 0 0; font-size: 12.5px; color: #64748b;">Real-time GPS route and custody checkpoint updates as next parties accept custody and scan your batch QR code.</p>
              </div>
              <div style="display: flex; align-items: center; gap: 8px;">
                <label style="font-size: 12px; font-weight: 800; color: #334155;">Inspect Batch:</label>
                <select id="liveMovementBatchSelector" class="form-select" style="background: #fff; font-size: 12.5px; font-weight: 700; min-width: 240px;" onchange="window.renderFarmerLiveMovementMap()">
                  <option value="ALL">All Active Batches</option>
                </select>
              </div>
            </div>

            <div style="display: grid; grid-template-columns: 1.5fr 1fr; gap: 16px; align-items: start;">
              <div id="farmerLiveMovementLeafletMap" style="height: 370px; width: 100%; border-radius: 12px; border: 1.5px solid #cbd5e1; background: #f1f5f9;"></div>
              <div id="farmerLiveMovementCheckpointsFeed" style="max-height: 370px; overflow-y: auto; padding-right: 4px;"></div>
            </div>
          </div>
        </div>

        <!-- TAB 3: Analytics, Lands, Crops & All Provided Data -->
        <div id="consoleTabContentAnalytics" style="display: none;">
          <!-- Analytics Toolbar -->
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 20px; padding-bottom: 14px; border-bottom: 1px solid #f1f5f9;">
            <div>
              <h4 style="margin: 0; font-size: 17px; font-weight: 800; color: #0f172a; display: flex; align-items: center; gap: 8px;">
                <span>${getIcon('activity', 20, '#047857')}</span> <span>${escapeHtml(t.tabAnalytics || 'Farm Stats, Lands, Crops & All Provided Data')}</span>
              </h4>
              <p style="margin: 3px 0 0; font-size: 12.5px; color: #64748b;">Complete summary of your registered lands, crops, production amounts, and real-time custody analytics.</p>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
              <select id="analytics_period_filter" class="form-select" style="background: #fff; font-size: 12px; font-weight: 700; padding: 6px 12px;" onchange="renderProducerAnalytics()">
                <option value="ALL">${escapeHtml(t.periodAllLots || 'All Recorded Lots')}</option>
                <option value="30">${escapeHtml(t.periodLast30 || 'Last 30 Days')}</option>
                <option value="90">${escapeHtml(t.periodLast90 || 'Last 90 Days')}</option>
                <option value="SEASON">${escapeHtml(t.periodSeason || 'Current Season (Rabi 2026-27)')}</option>
              </select>
            </div>
          </div>

          <!-- Analytics Container Render Target -->
          <div id="producerAnalyticsRoot">
            <div style="text-align: center; padding: 40px; color: #64748b;">
              <div style="width: 28px; height: 28px; border: 2.5px solid #cbd5e1; border-top-color: #047857; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 12px;"></div>
              <span>Aggregating ledger yield and valuation telemetry...</span>
            </div>
          </div>
        </div>
      </div>
    `;

    await loadProducerLots();
  }

  async function loadProducerLots() {
    try {
      const res = await fetch('/api/v1/lots/', { headers: getAuthHeader() });
      if (res.ok) {
        const data = await res.json();
        window._producerLots = data.items || [];
        try {
          localStorage.setItem('annasutra_cached_lots', JSON.stringify(window._producerLots));
        } catch (e) {}
      } else {
        window._producerLots = [];
      }
    } catch (e) {
      window._producerLots = [];
    }
    updateLotMetrics();
    applyLotFilters();
    window.updateInlineBatchIdPreview();
    if (document.getElementById('consoleTabContentCreateMap')?.style.display !== 'none') {
      window.renderFarmerLiveMovementMap();
    }
    if (document.getElementById('consoleTabContentAnalytics')?.style.display !== 'none') {
      renderProducerAnalytics();
    }
  }

  function updateLotMetrics() {
    const lots = window._producerLots || [];
    const totalEl = document.getElementById('metricTotalLots');
    const inCustodyEl = document.getElementById('metricInCustody');
    const inTransitEl = document.getElementById('metricInTransit');
    const weightEl = document.getElementById('metricTotalWeight');

    if (totalEl) totalEl.innerText = lots.length;
    const custodyCount = lots.filter(l => l.is_editable !== false && (l.state === 'CREATED' || l.state === 'IN_CUSTODY')).length;
    const transitCount = lots.filter(l => l.is_editable === false || l.state === 'IN_TRANSIT' || l.state === 'CLOSED').length;
    const totalWeight = lots.reduce((acc, l) => acc + (parseFloat(l.net_qty_kg || l.on_hand_kg || 0) || 0), 0);

    if (inCustodyEl) inCustodyEl.innerText = custodyCount;
    if (inTransitEl) inTransitEl.innerText = transitCount;
    if (weightEl) weightEl.innerText = totalWeight.toLocaleString('en-IN', { maximumFractionDigits: 1 }) + ' Kg';

    const sel = document.getElementById('liveMovementBatchSelector');
    if (sel) {
      const curVal = sel.value || 'ALL';
      sel.innerHTML = `<option value="ALL">All Active Batches (${lots.length})</option>` +
        lots.map(l => `<option value="${escapeHtml(l.public_code)}" ${curVal === l.public_code ? 'selected' : ''}>${escapeHtml(l.public_code)} — ${escapeHtml(getCropLabel(l.crop))} (${escapeHtml(l.current_custodian_role || 'PRODUCER')})</option>`).join('');
    }
  }

  window.applyLotFilters = function () {
    const t = getI18n();
    const lots = window._producerLots || [];
    const searchVal = (document.getElementById('filter_search')?.value || '').trim().toLowerCase();
    const cropVal = document.getElementById('filter_crop')?.value || 'ALL';
    const plotVal = document.getElementById('filter_plot')?.value || 'ALL';
    const custodyVal = document.getElementById('filter_custody')?.value || 'ALL';
    const paymentVal = document.getElementById('filter_payment')?.value || 'ALL';
    const sortVal = document.getElementById('filter_sort')?.value || '-created_at';

    let filtered = lots.filter(lot => {
      if (searchVal) {
        const text = [lot.public_code, lot.crop, lot.variety, lot.origin_plot_name, lot.remarks, lot.product_category_code, lot.product_category_name].filter(Boolean).join(' ').toLowerCase();
        if (!text.includes(searchVal)) return false;
      }
      if (cropVal !== 'ALL' && String(lot.crop).toLowerCase() !== cropVal.toLowerCase()) return false;
      if (plotVal !== 'ALL' && String(lot.origin_plot_id) !== plotVal) return false;
      if (custodyVal !== 'ALL') {
        if (custodyVal === 'IN_CUSTODY' && !(lot.is_editable !== false && (lot.state === 'CREATED' || lot.state === 'IN_CUSTODY'))) return false;
        if (custodyVal === 'IN_TRANSIT' && lot.state !== 'IN_TRANSIT') return false;
        if (custodyVal === 'CLOSED' && lot.state !== 'CLOSED') return false;
      }
      if (paymentVal !== 'ALL' && (lot.payment_status || 'PENDING') !== paymentVal) return false;
      return true;
    });

    // Sorting
    filtered.sort((a, b) => {
      const dateA = new Date(a.created_at || a.harvest_date || 0).getTime();
      const dateB = new Date(b.created_at || b.harvest_date || 0).getTime();
      const qtyA = parseFloat(a.net_qty_kg || a.on_hand_kg || 0);
      const qtyB = parseFloat(b.net_qty_kg || b.on_hand_kg || 0);

      if (sortVal === 'created_at') return dateA - dateB;
      if (sortVal === '-qty') return qtyB - qtyA;
      if (sortVal === 'qty') return qtyA - qtyB;
      return dateB - dateA; // default -created_at
    });

    renderFilteredLotsList(filtered, t);
  };

  function renderFilteredLotsList(list, t) {
    const listContainer = document.getElementById('producerHarvestLotsList');
    if (!listContainer) return;

    if (!list || list.length === 0) {
      listContainer.innerHTML = `
        <div style="background: #f8fafc; border: 1.5px dashed #cbd5e1; border-radius: 12px; padding: 48px 20px; text-align: center;">
          <div style="width: 48px; height: 48px; background: #ecfdf5; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 12px;">
            ${getIcon('sprout', 24, '#047857')}
          </div>
          <h4 style="margin: 0 0 6px; font-size: 16px; color: #0f172a; font-weight: 800;">${escapeHtml(t.emptyLotsTitle || 'No harvest lots recorded in custody yet')}</h4>
          <p style="margin: 0 0 16px; font-size: 13px; color: #64748b; max-width: 460px; margin-left: auto; margin-right: auto;">${escapeHtml(t.emptyLotsSub || 'Click the button above to register your first harvest lot and generate unique QR & 1D Barcode labels.')}</p>
          <button type="button" class="btn-wizard-action btn-wizard-submit" style="padding: 9px 18px; font-size: 13px;" onclick="openHarvestLotModal(null)">
            <span>+</span> <span>${escapeHtml(t.btnRegisterLot || '+ Register New Harvest Lot')}</span>
          </button>
        </div>
      `;
      return;
    }

    listContainer.innerHTML = list.map(lot => {
      const isEditable = lot.is_editable !== false && (lot.state === 'CREATED' || lot.state === 'IN_CUSTODY');
      const pStatus = lot.payment_status || 'PENDING';
      const paymentStyles = {
        PENDING: { label: t.paymentPending || 'Pending Settlement', bg: '#fffbeb', text: '#92400e', border: '#fde68a' },
        ADVANCE: { label: t.paymentAdvance || 'Advance Received', bg: '#eff6ff', text: '#1e40af', border: '#bfdbfe' },
        SETTLED: { label: t.paymentSettled || 'Fully Settled', bg: '#ecfdf5', text: '#065f46', border: '#86efac' }
      };
      const ps = paymentStyles[pStatus] || paymentStyles.PENDING;

      const weightDisplay = (parseFloat(lot.net_qty_kg || lot.on_hand_kg || 0)).toLocaleString('en-IN') + ' ' + (lot.unit || 'Kg');
      const harvestDateDisplay = lot.harvest_date ? new Date(lot.harvest_date).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' }) : 'Recent';
      const catCode = lot.product_category_code || 'VG';
      const catName = lot.product_category_name || 'Vegetables';
      const custodianRole = lot.current_custodian_role || 'PRODUCER';
      const custodianName = lot.current_custodian_name || '';
      const pendingHo = lot.pending_handover && lot.pending_handover.status === 'PENDING_ACCEPTANCE' ? lot.pending_handover : null;

      return `
        <div class="harvest-lot-row-card" style="background: #ffffff; border: 1.5px solid ${isEditable ? '#e2e8f0' : '#fed7aa'}; border-radius: 12px; padding: 18px; margin-bottom: 12px; transition: all 0.15s ease-in-out; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
          <!-- Top Row: Public Code, Category Code, Crop & Variety, Custody Status -->
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 14px; border-bottom: 1px solid #f1f5f9; padding-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
              <span style="font-family: monospace; font-size: 13px; font-weight: 900; color: #047857; background: #ecfdf5; border: 1.5px solid #86efac; padding: 4px 10px; border-radius: 6px; letter-spacing: 0.4px;" title="Unique Batch/Lot ID">
                ${escapeHtml(lot.public_code)}
              </span>
              <span style="font-size: 11px; font-weight: 900; color: #ffffff; background: #0b3d2e; padding: 3px 8px; border-radius: 6px;">
                ${escapeHtml(catCode)} • ${escapeHtml(catName)}
              </span>
              <strong style="font-size: 16px; color: #0f172a;">${escapeHtml(getCropLabel(lot.crop))}</strong>
              ${lot.variety ? `<span style="font-size: 13.5px; color: #475569; font-weight: 600;">• ${escapeHtml(lot.variety)}</span>` : ''}
              ${lot.grade ? `<span style="font-size: 11px; font-weight: 800; color: #1e40af; background: #eff6ff; border: 1px solid #bfdbfe; padding: 2px 8px; border-radius: 12px;">${escapeHtml(lot.grade)}</span>` : ''}
              <span style="font-size: 11px; font-weight: 700; color: ${ps.text}; background: ${ps.bg}; border: 1px solid ${ps.border}; padding: 2px 8px; border-radius: 12px;">
                ${escapeHtml(ps.label)}
              </span>
              ${lot.is_retailer_verified ? `
                <span style="font-size: 11px; font-weight: 800; color: #065f46; background: #d1fae5; border: 1px solid #34d399; padding: 2px 8px; border-radius: 12px;">
                  ✓ Retailer Verified (Consumer Passport Active)
                </span>
              ` : ''}
            </div>

            <!-- Right-hand custody status & Lock/Edit action -->
            <div style="display: flex; align-items: center; gap: 10px;">
              ${isEditable ? `
                <span style="display: inline-flex; align-items: center; gap: 5px; font-size: 12px; font-weight: 800; color: #065f46; background: #ecfdf5; border: 1px solid #86efac; padding: 4px 10px; border-radius: 20px;">
                  <span>${getIcon('check', 13, '#10b981')}</span> <span>In Farm Custody (PRODUCER)</span>
                </span>
                <button type="button" class="btn-wizard-action btn-wizard-draft" style="padding: 6px 12px; font-size: 12px; display: inline-flex; align-items: center; gap: 5px;" onclick="openHarvestLotModal('${lot.public_code}')" title="Edit Harvest Lot">
                  <span>${getIcon('edit', 14, '#047857')}</span> <span>${escapeHtml(t.btnEditLot || 'Edit')}</span>
                </button>
              ` : `
                <span style="display: inline-flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 800; color: #9a3412; background: #fff7ed; border: 1.5px solid #fdba74; padding: 4px 12px; border-radius: 20px;" title="Locked: Custody accepted by ${escapeHtml(custodianRole)}.">
                  <span>${getIcon('lock', 14, '#c2410c')}</span> <span>Custody: ${escapeHtml(custodianRole)} ${custodianName ? `(${escapeHtml(custodianName)})` : ''} — Locked</span>
                </span>
              `}
            </div>
          </div>

          ${pendingHo ? `
            <div style="background: #fffbeb; border: 1.5px solid #fde68a; border-radius: 8px; padding: 8px 12px; margin-bottom: 12px; font-size: 12.5px; color: #92400e; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
              <span><strong>⏳ Custody Handover Requested:</strong> Sent to <strong>${escapeHtml(pendingHo.to_role)} (${escapeHtml(pendingHo.to_name || pendingHo.to_phone || 'Next Party')})</strong> for ${escapeHtml(String(pendingHo.declared_qty_kg || weightDisplay))} Kg — Awaiting Next-Party Confirmation.</span>
              <span style="font-family: monospace; font-size: 11px; font-weight: 800;">Status: PENDING_ACCEPTANCE</span>
            </div>
          ` : ''}

          <!-- Body Grid: Harvest Info, Land/Origin, Commercials -->
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; font-size: 13px; color: #334155; margin-bottom: 14px;">
            <div>
              <div style="font-size: 11.5px; color: #64748b; font-weight: 700; text-transform: uppercase;">Current Quantity</div>
              <div style="font-size: 15px; font-weight: 800; color: #0b3d2e;">${escapeHtml(weightDisplay)}</div>
              <div style="font-size: 12px; color: #64748b;">${lot.packages_count ? `${lot.packages_count} ${lot.package_type || 'Crates'}` : 'Bulk Harvest'}</div>
            </div>

            <div>
              <div style="font-size: 11.5px; color: #64748b; font-weight: 700; text-transform: uppercase;">Origin Plot &amp; Land</div>
              <div style="font-size: 13.5px; font-weight: 700; color: #0f172a;">${escapeHtml(lot.origin_plot_name || 'Registered Farm Parcel')}</div>
              <div style="font-size: 12px; color: #64748b;">${lot.plot_area_acres ? `${lot.plot_area_acres} Acres • ` : ''}${escapeHtml(lot.farming_method || 'Conventional')}</div>
            </div>

            <div>
              <div style="font-size: 11.5px; color: #64748b; font-weight: 700; text-transform: uppercase;">Harvest Timestamp</div>
              <div style="font-size: 13px; font-weight: 600; color: #334155;">${escapeHtml(harvestDateDisplay)}</div>
              <div style="font-size: 12px; color: #047857; font-weight: 600;">${lot.shelf_life_days ? `Shelf-Life: ~${lot.shelf_life_days} Days` : ''}</div>
            </div>

            <div>
              <div style="font-size: 11.5px; color: #64748b; font-weight: 700; text-transform: uppercase;">Custody Checkpoints</div>
              <div style="font-size: 13.5px; font-weight: 700; color: #0f172a;">
                ${(lot.journey_checkpoints || []).length} Verified Hops
              </div>
              <div style="font-size: 12px; color: #047857; font-weight: 700;">Current Stage: ${escapeHtml(custodianRole)}</div>
            </div>
          </div>

          <!-- Bottom Action Buttons: Print QR/Barcode Labels, Live Map, Public Trace & Handover Request -->
          <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px dashed #e2e8f0; padding-top: 10px; flex-wrap: wrap; gap: 8px;">
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
              <button type="button" class="btn-wizard-action btn-wizard-draft" style="padding: 6px 14px; font-size: 12px; font-weight: 700; display: inline-flex; align-items: center; gap: 6px;" onclick="openUnlimitedQrPrintModal('${lot.public_code}', '${escapeHtml(lot.crop)}', '${escapeHtml(lot.variety || '')}', '${escapeHtml(weightDisplay)}', '${escapeHtml(catCode)}')">
                <span>${getIcon('printer', 14, '#047857')}</span> <span>Print QR + 1D Barcode Stickers (Unlimited)</span>
              </button>
              <button type="button" class="btn-wizard-action btn-wizard-draft" style="padding: 6px 12px; font-size: 12px; font-weight: 700; display: inline-flex; align-items: center; gap: 5px;" onclick="window.focusLotOnMovementMap('${lot.public_code}')">
                <span>${getIcon('map-pin', 13, '#047857')}</span> <span>Track on Live Map</span>
              </button>
              <a href="/l/${encodeURIComponent(lot.public_code)}" target="_blank" style="padding: 6px 12px; font-size: 12px; font-weight: 700; color: #047857; text-decoration: none; border: 1px solid #cbd5e1; border-radius: 8px; display: inline-flex; align-items: center; gap: 5px; background: #fff;">
                <span>${getIcon('globe', 13, '#047857')}</span> <span>Consumer Trace Page</span>
              </a>
            </div>

            ${isEditable ? `
              <button type="button" class="btn-wizard-action btn-wizard-submit" style="padding: 7px 16px; font-size: 12px; font-weight: 800;" onclick="openCustodyHandoverRequestModal('${lot.public_code}', '${escapeHtml(lot.crop)}', ${parseFloat(lot.net_qty_kg || lot.on_hand_kg || 0)})">
                <span>Request Custody Handover to Next Party &rarr;</span>
              </button>
            ` : ''}
          </div>
        </div>
      `;
    }).join('');
  }

  /* --------------------------------------------------------------------------
     LOT CREATION & EDIT MODAL (ALL POSSIBLE AGRICULTURAL & COMMERCIAL FIELDS)
     -------------------------------------------------------------------------- */
  window.openHarvestLotModal = function (lotCode) {
    const t = getI18n();
    const isEdit = !!lotCode;
    const existing = isEdit ? (window._producerLots || []).find(l => l.public_code === lotCode) : null;

    let modal = document.getElementById('harvestLotModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'harvestLotModal';
      modal.className = 'wizard-modal-backdrop';
      modal.style.cssText = 'position: fixed; inset: 0; background: rgba(15, 23, 42, 0.7); backdrop-filter: blur(4px); z-index: 99999; display: flex; align-items: center; justify-content: center; padding: 16px;';
      document.body.appendChild(modal);
    }

    const plots = wizardState.plots || [];
    const registeredCrops = wizardState.selectedCrops || [];
    const nowIso = new Date().toISOString().slice(0, 16);

    modal.innerHTML = `
      <div style="background: #ffffff; border-radius: 16px; max-width: 820px; width: 100%; max-height: 90vh; overflow-y: auto; padding: 26px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2);">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1.5px solid #e2e8f0; padding-bottom: 14px; margin-bottom: 20px;">
          <div>
            <h3 style="margin: 0; font-size: 20px; font-weight: 800; color: #0b3d2e; display: flex; align-items: center; gap: 8px;">
              <span>${getIcon(isEdit ? 'edit' : 'sprout', 20, '#047857')}</span>
              <span>${isEdit ? `Edit Harvest Lot #${lotCode}` : 'Register New Harvest Lot'}</span>
            </h3>
            <span style="font-size: 12.5px; color: #64748b;">Collect and sign all agricultural traceability, quality, and commercial settlement parameters.</span>
          </div>
          <button type="button" onclick="closeHarvestLotModal()" style="background: #f1f5f9; border: none; font-size: 18px; width: 32px; height: 32px; border-radius: 50%; cursor: pointer; color: #64748b; line-height: 1;">&times;</button>
        </div>

        <form id="form_harvest_lot" onsubmit="submitHarvestLotForm(event, '${lotCode || ''}')">
          <!-- 1. Commodity & Crop Identity -->
          <fieldset style="border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px; margin-bottom: 16px;">
            <legend style="font-size: 13px; font-weight: 800; color: #047857; padding: 0 6px;">1. Produce & Crop Identity</legend>
            <div class="form-grid-3" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;">
              <div class="form-group">
                <label class="form-label">Crop / Commodity <span class="req">*</span></label>
                <select class="form-select" id="lot_inp_crop" required>
                  ${registeredCrops.map(c => `<option value="${escapeHtml(c)}" ${existing && existing.crop === c ? 'selected' : ''}>${escapeHtml(getCropLabel(c))}</option>`).join('')}
                  ${CROPS_LIST.filter(c => !registeredCrops.includes(c.id)).map(c => `<option value="${escapeHtml(c.id)}" ${existing && existing.crop === c.id ? 'selected' : ''}>${escapeHtml(getCropLabel(c.id))}</option>`).join('')}
                </select>
              </div>

              <div class="form-group">
                <label class="form-label">Variety / Cultivar</label>
                <input type="text" class="form-input" id="lot_inp_variety" value="${escapeHtml(existing?.variety || '')}" placeholder="e.g. Hybrid Red 105, Jyoti, Alphonso" />
              </div>

              <div class="form-group">
                <label class="form-label">Product Category Code (10 Official Codes) <span class="req">*</span></label>
                <select class="form-select" id="lot_inp_category">
                  ${PRODUCT_CATEGORY_OPTIONS.map(opt => `<option value="${opt.code}" ${(existing?.product_category_code || existing?.category) === opt.code ? 'selected' : ''}>${escapeHtml(opt.name)}</option>`).join('')}
                </select>
              </div>
            </div>

            <div class="form-grid-3" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 10px;">
              <div class="form-group">
                <label class="form-label">Harvest Date & Time <span class="req">*</span></label>
                <input type="datetime-local" class="form-input" id="lot_inp_harvest_date" value="${existing?.harvest_date ? existing.harvest_date.slice(0, 16) : nowIso}" required />
              </div>
              <div class="form-group">
                <label class="form-label">Last Input / Spray Date (PHI)</label>
                <input type="date" class="form-input" id="lot_inp_sowing_date" value="${existing?.last_spray_date || existing?.sowing_date || ''}" />
              </div>
              <div class="form-group">
                <label class="form-label">Estimated Shelf-Life (Days)</label>
                <input type="number" class="form-input" id="lot_inp_shelf_life" value="${existing?.shelf_life_days || 14}" min="1" max="365" />
              </div>
            </div>
          </fieldset>

          <!-- 2. Land & Origin Traceability -->
          <fieldset style="border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px; margin-bottom: 16px;">
            <legend style="font-size: 13px; font-weight: 800; color: #047857; padding: 0 6px;">2. Land & Origin Traceability</legend>
            <div class="form-grid-3" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;">
              <div class="form-group">
                <label class="form-label">Origin Plot / Land Parcel</label>
                <select class="form-select" id="lot_inp_plot">
                  <option value="">Farm Cluster / Yard (Default)</option>
                  ${plots.map(pl => `<option value="${escapeHtml(pl.plot_id)}" ${existing && existing.origin_plot_id === pl.plot_id ? 'selected' : ''}>${escapeHtml(pl.plot_name || 'Plot')} (${pl.area_acres || 0} Acres)</option>`).join('')}
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Field / Cluster Yard Location</label>
                <input type="text" class="form-input" id="lot_inp_yard" value="${escapeHtml(existing?.plot_name || 'Cluster Yard #4')}" placeholder="e.g. Cluster Yard #4" />
              </div>
              <div class="form-group">
                <label class="form-label">Soil & Irrigation Source</label>
                <select class="form-select" id="lot_inp_irrigation">
                  <option value="Drip Micro" ${existing?.irrigation_type === 'Drip Micro' ? 'selected' : ''}>Drip / Micro-Irrigation</option>
                  <option value="Rainfed" ${existing?.irrigation_type === 'Rainfed' ? 'selected' : ''}>Rainfed</option>
                  <option value="Canal / River" ${existing?.irrigation_type === 'Canal / River' ? 'selected' : ''}>Canal / River</option>
                  <option value="Borewell" ${existing?.irrigation_type === 'Borewell' ? 'selected' : ''}>Borewell</option>
                </select>
              </div>
            </div>
          </fieldset>

          <!-- 3. Quantity, Packaging & Crate Serialization -->
          <fieldset style="border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px; margin-bottom: 16px;">
            <legend style="font-size: 13px; font-weight: 800; color: #047857; padding: 0 6px;">3. Quantity, Packaging & Crates</legend>
            <div class="form-grid-4" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;">
              <div class="form-group">
                <label class="form-label">Net Harvest Weight <span class="req">*</span></label>
                <input type="number" step="0.1" class="form-input" id="lot_inp_qty" value="${existing?.net_qty_kg || existing?.on_hand_kg || 500}" required min="0.1" oninput="calculateLotValuation()" />
              </div>
              <div class="form-group">
                <label class="form-label">Unit of Measure</label>
                <select class="form-select" id="lot_inp_unit" onchange="calculateLotValuation()">
                  <option value="Kg" ${existing?.unit === 'Kg' ? 'selected' : ''}>Kilograms (Kg)</option>
                  <option value="Quintals" ${existing?.unit === 'Quintals' ? 'selected' : ''}>Quintals (Qtl)</option>
                  <option value="Metric Tons" ${existing?.unit === 'Metric Tons' ? 'selected' : ''}>Metric Tons (MT)</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Crates / Bags Count</label>
                <input type="number" class="form-input" id="lot_inp_packages" value="${existing?.packages_count || 20}" min="1" />
              </div>
              <div class="form-group">
                <label class="form-label">Packaging Material</label>
                <select class="form-select" id="lot_inp_package_type">
                  <option value="Plastic Crates" ${existing?.package_type === 'Plastic Crates' ? 'selected' : ''}>Plastic Crates (Standard)</option>
                  <option value="Jute Bags" ${existing?.package_type === 'Jute Bags' ? 'selected' : ''}>Jute Gunny Bags</option>
                  <option value="Corrugated Boxes" ${existing?.package_type === 'Corrugated Boxes' ? 'selected' : ''}>Corrugated Paper Cartons</option>
                  <option value="Bulk Loose" ${existing?.package_type === 'Bulk Loose' ? 'selected' : ''}>Bulk Loose Vehicle</option>
                </select>
              </div>
            </div>
          </fieldset>

          <!-- 4. Quality, Grade & Farming Inputs -->
          <fieldset style="border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px; margin-bottom: 16px;">
            <legend style="font-size: 13px; font-weight: 800; color: #047857; padding: 0 6px;">4. Quality Grade & Inputs</legend>
            <div class="form-grid-3" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;">
              <div class="form-group">
                <label class="form-label">Produce Grade</label>
                <select class="form-select" id="lot_inp_grade">
                  <option value="Grade A" ${existing?.grade === 'Grade A' ? 'selected' : ''}>Grade A (Premium Commercial)</option>
                  <option value="Grade B" ${existing?.grade === 'Grade B' ? 'selected' : ''}>Grade B (Standard Market)</option>
                  <option value="Grade C" ${existing?.grade === 'Grade C' ? 'selected' : ''}>Grade C (Processing / Economy)</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Farming Method</label>
                <select class="form-select" id="lot_inp_method">
                  <option value="Organic NPOP" ${existing?.farming_method === 'Organic NPOP' ? 'selected' : ''}>Organic (Certified NPOP)</option>
                  <option value="PGS-India" ${existing?.farming_method === 'PGS-India' ? 'selected' : ''}>PGS-India Natural</option>
                  <option value="Good Agri Practices" ${existing?.farming_method === 'Good Agri Practices' ? 'selected' : ''}>GAP Certified</option>
                  <option value="Conventional" ${existing?.farming_method === 'Conventional' ? 'selected' : ''}>Conventional</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Moisture Content (%)</label>
                <input type="number" step="0.1" class="form-input" id="lot_inp_moisture" value="${existing?.moisture_pct || 11.5}" />
              </div>
            </div>
            <div style="margin-top: 10px;">
              <label class="form-label">Fertilizers / Amendments Used</label>
              <input type="text" class="form-input" id="lot_inp_fertilizers" value="${escapeHtml(existing?.fertilizers || 'Vermicompost, Neem Cake, Bio-fertilizer')}" placeholder="e.g. Vermicompost, Neem Cake, Trichoderma" />
            </div>
          </fieldset>

          <!-- 5. Commercials, Pricing & Payment Details -->
          <fieldset style="border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px; margin-bottom: 16px;">
            <legend style="font-size: 13px; font-weight: 800; color: #047857; padding: 0 6px;">5. Commercial Valuation & Payment Details</legend>
            <div class="form-grid-3" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;">
              <div class="form-group">
                <label class="form-label">Expected Base Price (₹)</label>
                <input type="number" step="0.5" class="form-input" id="lot_inp_price" value="${existing?.base_price_per_unit || 25.0}" oninput="calculateLotValuation()" />
              </div>
              <div class="form-group">
                <label class="form-label">Estimated Lot Valuation (₹)</label>
                <input type="number" step="1" class="form-input" id="lot_inp_valuation" value="${existing?.estimated_value || 12500}" readonly style="background: #f8fafc; font-weight: 800; color: #047857;" />
              </div>
              <div class="form-group">
                <label class="form-label">Payment / Settlement Status</label>
                <select class="form-select" id="lot_inp_payment">
                  <option value="PENDING" ${existing?.payment_status === 'PENDING' ? 'selected' : ''}>Pending Settlement</option>
                  <option value="ADVANCE" ${existing?.payment_status === 'ADVANCE' ? 'selected' : ''}>Advance Received</option>
                  <option value="SETTLED" ${existing?.payment_status === 'SETTLED' ? 'selected' : ''}>Fully Settled</option>
                </select>
              </div>
            </div>
            <div style="margin-top: 10px;">
              <label class="form-label">Intended Buyer / Distribution Channel</label>
              <select class="form-select" id="lot_inp_buyer">
                <option value="APMC Mandi Aggregator" ${existing?.intended_buyer === 'APMC Mandi Aggregator' ? 'selected' : ''}>APMC Mandi Aggregator (Auction)</option>
                <option value="Direct Retailer" ${existing?.intended_buyer === 'Direct Retailer' ? 'selected' : ''}>Direct Retailer / Supermarket</option>
                <option value="Cold Storage Warehouse" ${existing?.intended_buyer === 'Cold Storage Warehouse' ? 'selected' : ''}>Cold Storage Terminal</option>
                <option value="Food Processing Unit" ${existing?.intended_buyer === 'Food Processing Unit' ? 'selected' : ''}>Food Processing Company</option>
              </select>
            </div>
          </fieldset>

          <!-- 6. Remarks & Statutory Attestation -->
          <div class="form-group" style="margin-bottom: 16px;">
            <label class="form-label">Farmer Remarks & Quality Notes</label>
            <textarea class="form-input" id="lot_inp_remarks" rows="2" placeholder="Early morning harvest, sorted and washed.">${escapeHtml(existing?.remarks || '')}</textarea>
          </div>

          <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; border-top: 1.5px solid #e2e8f0; padding-top: 16px;">
            <button type="button" class="btn-wizard-action btn-wizard-draft" onclick="closeHarvestLotModal()">Cancel</button>
            <button type="submit" class="btn-wizard-action btn-wizard-submit" style="padding: 10px 24px; font-weight: 800;">
              <span>${getIcon('check', 14, '#ffffff')}</span> <span>${isEdit ? 'Save Changes' : 'Confirm & Mint Harvest Lot'}</span>
            </button>
          </div>
        </form>
      </div>
    `;
    modal.style.display = 'flex';
  };

  window.closeHarvestLotModal = function () {
    const modal = document.getElementById('harvestLotModal');
    if (modal) modal.style.display = 'none';
  };

  window.calculateLotValuation = function () {
    const qty = parseFloat(document.getElementById('lot_inp_qty')?.value || 0);
    const price = parseFloat(document.getElementById('lot_inp_price')?.value || 0);
    const valEl = document.getElementById('lot_inp_valuation');
    if (valEl) valEl.value = Math.round(qty * price);
  };

  window.submitHarvestLotForm = async function (e, lotCode) {
    e.preventDefault();
    const isEdit = !!lotCode;
    const crop = document.getElementById('lot_inp_crop')?.value;
    const variety = document.getElementById('lot_inp_variety')?.value;
    const category = document.getElementById('lot_inp_category')?.value;
    const harvestDate = document.getElementById('lot_inp_harvest_date')?.value;
    const sowingDate = document.getElementById('lot_inp_sowing_date')?.value;
    const shelfLife = parseInt(document.getElementById('lot_inp_shelf_life')?.value || 14);
    const plotId = document.getElementById('lot_inp_plot')?.value || null;
    const yard = document.getElementById('lot_inp_yard')?.value;
    const irrigation = document.getElementById('lot_inp_irrigation')?.value;
    const qty = parseFloat(document.getElementById('lot_inp_qty')?.value);
    const unit = document.getElementById('lot_inp_unit')?.value;
    const packages = parseInt(document.getElementById('lot_inp_packages')?.value || 1);
    const packageType = document.getElementById('lot_inp_package_type')?.value;
    const grade = document.getElementById('lot_inp_grade')?.value;
    const method = document.getElementById('lot_inp_method')?.value;
    const moisture = parseFloat(document.getElementById('lot_inp_moisture')?.value || 0);
    const fertilizers = document.getElementById('lot_inp_fertilizers')?.value;
    const price = parseFloat(document.getElementById('lot_inp_price')?.value || 0);
    const valuation = parseFloat(document.getElementById('lot_inp_valuation')?.value || 0);
    const paymentStatus = document.getElementById('lot_inp_payment')?.value;
    const buyer = document.getElementById('lot_inp_buyer')?.value;
    const remarks = document.getElementById('lot_inp_remarks')?.value;

    const payload = {
      crop,
      product_category_code: category,
      product: { name: crop, variety, category },
      variety,
      category,
      harvest_date: harvestDate,
      sowing_date: sowingDate,
      last_spray_date: sowingDate,
      shelf_life_days: shelfLife,
      origin_plot_id: plotId,
      plot_id: plotId,
      plot_name: yard,
      irrigation_type: irrigation,
      net_qty_kg: qty,
      unit,
      packages_count: packages,
      package_type: packageType,
      grade,
      farming_method: method,
      moisture_pct: moisture,
      fertilizers,
      base_price_per_unit: price,
      estimated_value: valuation,
      payment_status: paymentStatus,
      intended_buyer: buyer,
      remarks
    };

    try {
      const url = isEdit ? `/api/v1/lots/${encodeURIComponent(lotCode)}` : '/api/v1/lots/';
      const methodHttp = isEdit ? 'PUT' : 'POST';
      const res = await fetch(url, {
        method: methodHttp,
        headers: Object.assign({}, getAuthHeader(), { 'Content-Type': 'application/json' }),
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const err = await res.json();
        alert(err.detail || 'Failed to save harvest lot.');
        return;
      }

      closeHarvestLotModal();
      showToast(isEdit ? 'Harvest lot updated successfully.' : 'New harvest lot registered and signed into ledger.', 'success');
      await loadProducerLots();
    } catch (err) {
      alert('Network error while saving harvest lot.');
    }
  };

  window.submitInlineBatchForm = async function (e) {
    e.preventDefault();
    const catCode = document.getElementById('inline_lot_cat_code')?.value || 'FR';
    const crop = document.getElementById('inline_lot_crop')?.value || 'Mango';
    const variety = document.getElementById('inline_lot_variety')?.value || '';
    const plotId = document.getElementById('inline_lot_plot')?.value || null;
    const qty = parseFloat(document.getElementById('inline_lot_qty')?.value || 500);
    const packages = parseInt(document.getElementById('inline_lot_packages')?.value || 25);
    const harvestDate = document.getElementById('inline_lot_harvest_date')?.value || new Date().toISOString().slice(0, 16);
    const sprayDate = document.getElementById('inline_lot_spray_date')?.value || '';
    const grade = document.getElementById('inline_lot_grade')?.value || 'Grade A';
    const method = document.getElementById('inline_lot_method')?.value || 'Organic NPOP';
    const price = parseFloat(document.getElementById('inline_lot_price')?.value || 40);
    const shelfLife = parseInt(document.getElementById('inline_lot_shelf_life')?.value || 14);

    const payload = {
      crop,
      product_category_code: catCode,
      product: { name: crop, variety, category: catCode },
      variety,
      category: catCode,
      harvest_date: harvestDate,
      last_spray_date: sprayDate,
      shelf_life_days: shelfLife,
      origin_plot_id: plotId,
      plot_id: plotId,
      net_qty_kg: qty,
      unit: 'Kg',
      packages_count: packages,
      package_type: 'Plastic Crates',
      grade,
      farming_method: method,
      base_price_per_unit: price,
      estimated_value: Math.round(qty * price),
      payment_status: 'PENDING'
    };

    try {
      const res = await fetch('/api/v1/lots/', {
        method: 'POST',
        headers: Object.assign({}, getAuthHeader(), { 'Content-Type': 'application/json' }),
        body: JSON.stringify(payload)
      });
      if (!res.ok) {
        const err = await res.json();
        showToast(err.detail || 'Could not create batch.', 'error');
        return;
      }
      const created = await res.json();
      showToast(`Batch #${created.public_code} minted! Pinned to Live Movement Map.`, 'success');
      await loadProducerLots();
      const sel = document.getElementById('liveMovementBatchSelector');
      if (sel && created.public_code) {
        sel.value = created.public_code;
      }
      window.renderFarmerLiveMovementMap();
    } catch (err) {
      showToast('Network error minting batch.', 'error');
    }
  };

  /* --------------------------------------------------------------------------
     1D LINEAR BARCODE SVG (CODE-128 STYLE) + UNLIMITED QR STICKER GENERATOR
     -------------------------------------------------------------------------- */
  window.generateBarcode128Svg = function (codeText, heightPx) {
    const str = String(codeText || 'ANNASUTRA');
    const h = heightPx || 32;
    let bars = '<rect x="0" y="0" width="2" height="' + h + '" fill="#0f172a"/><rect x="3" y="0" width="1" height="' + h + '" fill="#0f172a"/><rect x="6" y="0" width="2" height="' + h + '" fill="#0f172a"/>';
    let x = 10;
    for (let i = 0; i < str.length; i++) {
      const code = str.charCodeAt(i);
      const w1 = (code % 3) + 1;
      const g1 = ((code >> 2) % 2) + 1;
      const w2 = ((code >> 3) % 2) + 1;
      const g2 = ((code >> 4) % 2) + 1;
      bars += `<rect x="${x}" y="0" width="${w1}" height="${h}" fill="#0f172a"/>`;
      x += w1 + g1;
      bars += `<rect x="${x}" y="0" width="${w2}" height="${h}" fill="#0f172a"/>`;
      x += w2 + g2;
    }
    bars += `<rect x="${x}" y="0" width="2" height="${h}" fill="#0f172a"/><rect x="${x + 3}" y="0" width="1.5" height="${h}" fill="#0f172a"/>`;
    const totalW = x + 6;
    return `<svg viewBox="0 0 ${totalW} ${h}" width="100%" height="${h}" preserveAspectRatio="none" style="display:block;">${bars}</svg>`;
  };

  window.openUnlimitedQrPrintModal = function (lotCode, cropName, variety, weightDisplay, catCode) {
    let modal = document.getElementById('unlimitedQrModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'unlimitedQrModal';
      modal.className = 'wizard-modal-backdrop';
      modal.style.cssText = 'position: fixed; inset: 0; background: rgba(15, 23, 42, 0.7); backdrop-filter: blur(4px); z-index: 99999; display: flex; align-items: center; justify-content: center; padding: 16px;';
      document.body.appendChild(modal);
    }

    const cCode = catCode || 'VG';

    modal.innerHTML = `
      <div style="background: #ffffff; border-radius: 16px; max-width: 760px; width: 100%; max-height: 90vh; overflow-y: auto; padding: 26px;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1.5px solid #e2e8f0; padding-bottom: 14px; margin-bottom: 18px;">
          <div>
            <h3 style="margin: 0; font-size: 19px; font-weight: 800; color: #0b3d2e;">Generate &amp; Print Unlimited 2D QR + 1D Barcode Crate Stickers</h3>
            <span style="font-size: 12.5px; color: #64748b;">Dual-format (QR Code + Linear Code-128 Barcode) stickers for Batch #${escapeHtml(lotCode)}.</span>
          </div>
          <button type="button" onclick="document.getElementById('unlimitedQrModal').style.display='none'" style="background: #f1f5f9; border: none; font-size: 18px; width: 32px; height: 32px; border-radius: 50%; cursor: pointer;">&times;</button>
        </div>

        <div style="display: flex; gap: 12px; align-items: center; margin-bottom: 16px; background: #f8fafc; padding: 12px 16px; border-radius: 10px; flex-wrap: wrap;">
          <label style="font-size: 13px; font-weight: 700; color: #334155;">Quantity of Stickers to Print:</label>
          <select id="qr_print_count" class="form-select" style="width: 160px; background: #fff;" onchange="renderQrStickersPreview('${lotCode}', '${escapeHtml(cropName)}', '${escapeHtml(variety)}', '${escapeHtml(weightDisplay)}', '${escapeHtml(cCode)}')">
            <option value="1">1 Sticker</option>
            <option value="6" selected>6 Stickers (1 Sheet)</option>
            <option value="12">12 Stickers</option>
            <option value="24">24 Stickers</option>
            <option value="48">48 Stickers</option>
            <option value="100">100 Stickers</option>
          </select>
          <span style="font-size: 12px; color: #047857; font-weight: 800;">✓ Unlimited 2D QR + 1D Barcode Generator</span>
        </div>

        <!-- Preview Sheet Area -->
        <div id="qrStickersPreviewContainer" style="border: 1px solid #cbd5e1; border-radius: 10px; padding: 16px; max-height: 410px; overflow-y: auto; background: #f1f5f9; display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;">
        </div>

        <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 18px; border-top: 1.5px solid #e2e8f0; padding-top: 14px;">
          <button type="button" class="btn-wizard-action btn-wizard-draft" onclick="document.getElementById('unlimitedQrModal').style.display='none'">Close</button>
          <button type="button" class="btn-wizard-action btn-wizard-submit" style="padding: 10px 22px; font-weight: 800;" onclick="window.print()">
            <span>${getIcon('printer', 15, '#ffffff')}</span> <span>Print QR + Barcode Sheet</span>
          </button>
        </div>
      </div>
    `;

    modal.style.display = 'flex';
    renderQrStickersPreview(lotCode, cropName, variety, weightDisplay, cCode);
  };

  function renderQrStickersPreview(lotCode, cropName, variety, weightDisplay, catCode) {
    const container = document.getElementById('qrStickersPreviewContainer');
    if (!container) return;
    const count = parseInt(document.getElementById('qr_print_count')?.value || 6);
    const orgName = wizardState.profile?.organisation_name || 'AnnaSutra Producer';
    const farmerUid = wizardState.profile?.farmer_uid || localStorage.getItem('annasutra_farmer_uid') || '';
    const qrTargetUrl = `${window.location.origin}/l/${encodeURIComponent(lotCode)}`;
    const barcodeSvg = window.generateBarcode128Svg(lotCode, 26);

    let html = '';
    for (let i = 1; i <= count; i++) {
      html += `
        <div style="background: #ffffff; border: 1.5px solid #0b3d2e; border-radius: 8px; padding: 10px; display: flex; flex-direction: column; gap: 8px;">
          <div style="display: flex; gap: 10px; align-items: center;">
            <div style="width: 72px; height: 72px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
              <img src="https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=${encodeURIComponent(qrTargetUrl)}" alt="QR" style="width: 64px; height: 64px;" />
            </div>
            <div style="flex: 1; overflow: hidden;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 9px; font-weight: 800; color: #047857; text-transform: uppercase; letter-spacing: 0.5px;">AnnaSutra C-DAC</span>
                <span style="font-size: 9.5px; font-weight: 900; background: #0b3d2e; color: #fff; padding: 1px 6px; border-radius: 4px;">${escapeHtml(catCode || 'VG')} • #${String(i).padStart(4, '0')}</span>
              </div>
              <div style="font-size: 13px; font-weight: 800; color: #0f172a; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 2px;">${escapeHtml(cropName)} ${variety ? `• ${escapeHtml(variety)}` : ''} (${escapeHtml(weightDisplay)})</div>
              <div style="font-family: monospace; font-size: 10.5px; font-weight: 900; color: #0b3d2e; word-break: break-all;">Batch: ${escapeHtml(lotCode)}</div>
              ${farmerUid ? `<div style="font-family: monospace; font-size: 9.5px; color: #475569;">Farmer ID: ${escapeHtml(farmerUid)}</div>` : `<div style="font-size: 10px; color: #64748b;">${escapeHtml(orgName)}</div>`}
            </div>
          </div>
          <div style="border-top: 1px dashed #cbd5e1; padding-top: 6px; text-align: center;">
            ${barcodeSvg}
            <div style="font-family: monospace; font-size: 9px; font-weight: 800; color: #334155; letter-spacing: 0.8px; margin-top: 2px;">${escapeHtml(lotCode)}</div>
          </div>
        </div>
      `;
    }
    container.innerHTML = html;
  }

  /* --------------------------------------------------------------------------
     ADMIN TRASH & CONFIRMATION MECHANISM
     -------------------------------------------------------------------------- */
  window.openDeleteProducerModal = function (entityId, entityName, isPurge) {
    const t = getI18n();
    let modal = document.getElementById('adminDeleteConfirmModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'adminDeleteConfirmModal';
      modal.className = 'wizard-modal-backdrop';
      modal.style.cssText = 'position: fixed; inset: 0; background: rgba(15, 23, 42, 0.75); backdrop-filter: blur(4px); z-index: 999999; display: flex; align-items: center; justify-content: center; padding: 16px;';
      document.body.appendChild(modal);
    }

    modal.innerHTML = `
      <div style="background: #ffffff; border-radius: 16px; max-width: 520px; width: 100%; padding: 26px; border: 2px solid ${isPurge ? '#7f1d1d' : '#dc2626'}; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 14px;">
          <div style="width: 40px; height: 40px; background: #fee2e2; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
            ${getIcon('alert', 22, '#dc2626')}
          </div>
          <div>
            <h3 style="margin: 0; font-size: 18px; font-weight: 800; color: #991b1b;">
              ${isPurge ? 'Permanent Producer Purge' : 'Move Producer to Trash'}
            </h3>
            <span style="font-size: 12px; color: #64748b;">${escapeHtml(entityName)}</span>
          </div>
        </div>

        <p style="font-size: 13.5px; color: #334155; line-height: 1.5; margin-bottom: 16px;">
          ${isPurge ? `
            <strong>DANGER:</strong> This action is permanent and cannot be reversed. All KYC documents, plots, and sensitive records for <strong>${escapeHtml(entityName)}</strong> will be wiped.
          ` : `
            This producer will be moved to the <strong>Admin Trash</strong>. Their sovereign code access will be suspended immediately. You can restore them anytime from the Trash tab.
          `}
        </p>

        <div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 10px; padding: 14px; margin-bottom: 18px;">
          <label style="display: block; font-size: 12.5px; font-weight: 800; color: #991b1b; margin-bottom: 6px;">
            ${escapeHtml(t.confirmDeletePrompt || 'To confirm, type DELETE in capital letters below:')}
          </label>
          <input type="text" id="inp_del_word_confirm" class="form-input" style="font-family: monospace; font-size: 14px; font-weight: 800; text-transform: uppercase; border-color: #f87171;" placeholder="DELETE" oninput="checkDeleteWordConfirm(this, '${isPurge ? 'PURGE' : 'TRASH'}')" />
        </div>

        <div style="display: flex; justify-content: flex-end; gap: 10px;">
          <button type="button" class="btn-wizard-action btn-wizard-draft" onclick="document.getElementById('adminDeleteConfirmModal').style.display='none'">Cancel</button>
          <button type="button" id="btn_admin_exec_delete" class="btn-wizard-action" style="color: #ffffff; background: #94a3b8; border-color: #94a3b8; cursor: not-allowed; font-weight: 800;" disabled onclick="executeAdminProducerDeletion('${entityId}', ${isPurge})">
            ${isPurge ? 'Permanently Purge Data' : 'Confirm Move to Trash'}
          </button>
        </div>
      </div>
    `;

    modal.style.display = 'flex';
  };

  window.checkDeleteWordConfirm = function (input, mode) {
    const val = input.value.trim().toUpperCase();
    const btn = document.getElementById('btn_admin_exec_delete');
    if (!btn) return;
    if (val === 'DELETE') {
      btn.disabled = false;
      btn.style.background = '#dc2626';
      btn.style.borderColor = '#b91c1c';
      btn.style.cursor = 'pointer';
    } else {
      btn.disabled = true;
      btn.style.background = '#94a3b8';
      btn.style.borderColor = '#94a3b8';
      btn.style.cursor = 'not-allowed';
    }
  };

  window.executeAdminProducerDeletion = async function (entityId, isPurge) {
    const modal = document.getElementById('adminDeleteConfirmModal');
    try {
      if (isPurge) {
        const res = await fetch(`/api/v1/admin/entities/${entityId}/purge`, {
          method: 'POST',
          headers: Object.assign({}, getAuthHeader(), { 'Content-Type': 'application/json' }),
          body: JSON.stringify({ confirmation: 'DELETE' })
        });
        if (!res.ok) {
          const err = await res.json();
          alert(err.detail || 'Failed to purge producer.');
          return;
        }
        showToast('Producer data permanently purged.', 'success');
      } else {
        const res = await fetch(`/api/v1/admin/entities/${entityId}/decision`, {
          method: 'POST',
          headers: Object.assign({}, getAuthHeader(), { 'Content-Type': 'application/json' }),
          body: JSON.stringify({ decision: 'TRASH', reason: 'Moved to trash by administrator.' })
        });
        if (!res.ok) {
          const err = await res.json();
          alert(err.detail || 'Failed to move producer to trash.');
          return;
        }
        showToast('Producer moved to trash successfully.', 'success');
      }

      if (modal) modal.style.display = 'none';
      wizardState.adminInspectedEntity = null;
      const contentArea = document.getElementById('workspaceDynamicContent');
      if (contentArea) await loadAdminQueueAndRender(contentArea);
    } catch (err) {
      alert('Network error while processing deletion.');
    }
  };

  window.restoreAdminProducer = async function (entityId) {
    try {
      const res = await fetch(`/api/v1/admin/entities/${entityId}/restore`, {
        method: 'POST',
        headers: getAuthHeader()
      });
      if (res.ok) {
        showToast('Producer restored successfully from Trash.', 'success');
        wizardState.adminInspectedEntity = null;
        const contentArea = document.getElementById('workspaceDynamicContent');
        if (contentArea) await loadAdminQueueAndRender(contentArea);
      } else {
        const err = await res.json();
        alert(err.detail || 'Failed to restore producer.');
      }
    } catch (e) {
      alert('Network error while restoring producer.');
    }
  };

  /* --------------------------------------------------------------------------
     2-WAY CUSTODY HANDOVER REQUEST MODAL (FARMER / CURRENT CUSTODIAN -> NEXT PARTY)
     -------------------------------------------------------------------------- */
  window.openCustodyHandoverRequestModal = function (lotCode, cropName, maxQty) {
    let modal = document.getElementById('custodyHandoverRequestModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'custodyHandoverRequestModal';
      modal.className = 'wizard-modal-backdrop';
      modal.style.cssText = 'position: fixed; inset: 0; background: rgba(15, 23, 42, 0.72); backdrop-filter: blur(4px); z-index: 99999; display: flex; align-items: center; justify-content: center; padding: 16px;';
      document.body.appendChild(modal);
    }

    modal.innerHTML = `
      <div style="background: #ffffff; border-radius: 16px; max-width: 560px; width: 100%; padding: 26px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.25);">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1.5px solid #e2e8f0; padding-bottom: 12px; margin-bottom: 16px;">
          <div>
            <h3 style="margin: 0; font-size: 18px; font-weight: 800; color: #0b3d2e;">Request Custody Handover Acknowledgement</h3>
            <span style="font-size: 12px; color: #64748b;">Batch #${escapeHtml(lotCode)} (${escapeHtml(cropName || 'Produce')})</span>
          </div>
          <button type="button" onclick="document.getElementById('custodyHandoverRequestModal').style.display='none'" style="background: #f1f5f9; border: none; font-size: 18px; width: 32px; height: 32px; border-radius: 50%; cursor: pointer;">&times;</button>
        </div>

        <div style="background: #ecfdf5; border: 1px solid #86efac; border-radius: 10px; padding: 10px 14px; font-size: 12px; color: #065f46; margin-bottom: 14px;">
          <strong>2-Way Cryptographic Handover:</strong> The next party will receive this handover request in their dashboard. Once they confirm &amp; scan the QR code, your custody record locks permanently (🔒) and they gain append-only rights.
        </div>

        <form onsubmit="window.submitCustodyHandoverRequest(event, '${lotCode}')">
          <div class="form-grid-2" style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
            <div class="form-group">
              <label class="form-label">Next Party Role <span class="req">*</span></label>
              <select id="ho_req_to_role" class="form-select" required>
                <option value="AGGREGATOR">Aggregator (APMC / FPO Hub)</option>
                <option value="WHOLESALER">Wholesaler</option>
                <option value="DISTRIBUTOR">Distributor / Logistics</option>
                <option value="RETAILER">Retailer Shop (Final Consumer Point)</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Declared Handover Weight (Kg) <span class="req">*</span></label>
              <input type="number" step="0.1" min="0.1" id="ho_req_qty" class="form-input" value="${maxQty || 500}" required />
            </div>
          </div>

          <div class="form-grid-2" style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
            <div class="form-group">
              <label class="form-label">Next Party Name / Enterprise <span class="req">*</span></label>
              <input type="text" id="ho_req_to_name" class="form-input" value="Hooghly APMC Aggregator Hub" required />
            </div>
            <div class="form-group">
              <label class="form-label">Next Party Mobile (+91...)</label>
              <input type="text" id="ho_req_to_phone" class="form-input" placeholder="+919876543211" />
            </div>
          </div>

          <div class="form-grid-2" style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px;">
            <div class="form-group">
              <label class="form-label">Transport Vehicle No.</label>
              <input type="text" id="ho_req_vehicle" class="form-input" placeholder="WB-15-C-8921" />
            </div>
            <div class="form-group">
              <label class="form-label">Handover Notes</label>
              <input type="text" id="ho_req_notes" class="form-input" placeholder="Sealed crates, sound condition" />
            </div>
          </div>

          <div style="display: flex; justify-content: flex-end; gap: 10px; border-top: 1px solid #e2e8f0; padding-top: 14px;">
            <button type="button" class="btn-wizard-action btn-wizard-draft" onclick="document.getElementById('custodyHandoverRequestModal').style.display='none'">Cancel</button>
            <button type="submit" class="btn-wizard-action btn-wizard-submit" style="padding: 9px 20px; font-weight: 800;">
              <span>Send Handover Request to Next Party &rarr;</span>
            </button>
          </div>
        </form>
      </div>
    `;
    modal.style.display = 'flex';
  };
  window.openQuickDispatchModal = window.openCustodyHandoverRequestModal;

  window.submitCustodyHandoverRequest = async function (e, lotCode) {
    e.preventDefault();
    const toRole = document.getElementById('ho_req_to_role')?.value || 'AGGREGATOR';
    const qty = parseFloat(document.getElementById('ho_req_qty')?.value || 500);
    const toName = document.getElementById('ho_req_to_name')?.value || 'Next Party';
    const toPhone = document.getElementById('ho_req_to_phone')?.value || '';
    const vehicle = document.getElementById('ho_req_vehicle')?.value || '';
    const notes = document.getElementById('ho_req_notes')?.value || '';

    try {
      const res = await fetch(`/api/v1/lots/${encodeURIComponent(lotCode)}/handover-request`, {
        method: 'POST',
        headers: Object.assign({}, getAuthHeader(), { 'Content-Type': 'application/json' }),
        body: JSON.stringify({
          to_role: toRole,
          to_name: toName,
          to_phone: toPhone,
          declared_qty_kg: qty,
          vehicle_no: vehicle,
          notes: notes
        })
      });
      const data = await res.json();
      if (res.ok) {
        document.getElementById('custodyHandoverRequestModal').style.display = 'none';
        showToast(`Custody handover request sent to ${toRole} (${toName}). Awaiting their confirmation!`, 'success');
        if (typeof currentRole !== 'undefined' && currentRole === 'PRODUCER') {
          await loadProducerLots();
        } else {
          const contentArea = document.getElementById('workspaceDynamicContent');
          if (contentArea) await renderDownstreamCustodyConsole(contentArea, currentRole);
        }
      } else {
        showToast(data.detail || 'Could not send handover request.', 'error');
      }
    } catch (err) {
      showToast('Network error sending handover request.', 'error');
    }
  };

  /* --------------------------------------------------------------------------
     LIVE LOT MOVEMENT MAP (LEAFLET) & NEXT-PARTY CHECKPOINTS FEED
     -------------------------------------------------------------------------- */
  window._liveMovementMapInstance = null;

  window.focusLotOnMovementMap = function (lotCode) {
    window.switchProducerConsoleTab('create_map');
    setTimeout(() => {
      const sel = document.getElementById('liveMovementBatchSelector');
      if (sel) sel.value = lotCode;
      window.renderFarmerLiveMovementMap();
    }, 80);
  };

  window.renderFarmerLiveMovementMap = function () {
    const mapDiv = document.getElementById('farmerLiveMovementLeafletMap');
    const feedDiv = document.getElementById('farmerLiveMovementCheckpointsFeed');
    if (!mapDiv || !feedDiv) return;

    const lots = window._producerLots || [];
    const selectedCode = document.getElementById('liveMovementBatchSelector')?.value || 'ALL';
    const targetLots = selectedCode === 'ALL' ? lots : lots.filter(l => l.public_code === selectedCode);

    // Collect all checkpoints across target lots
    const allCheckpoints = [];
    targetLots.forEach(lot => {
      const cps = lot.journey_checkpoints && lot.journey_checkpoints.length > 0
        ? lot.journey_checkpoints
        : [{
            hop_index: 1,
            actor_role: 'PRODUCER',
            actor_name: lot.current_custodian_name || 'Farm Origin',
            action: 'BATCH_CREATED',
            weight_kg: parseFloat(lot.net_qty_kg || 500),
            condition: lot.grade || 'Grade A',
            storage_temp: 'Ambient',
            lat: 22.9868,
            lng: 87.8550,
            location_label: lot.origin_plot_name || 'Farm Origin',
            timestamp: lot.harvest_date || lot.created_at
          }];
      cps.forEach(cp => {
        allCheckpoints.push(Object.assign({}, cp, { lot_code: lot.public_code, crop: lot.crop }));
      });
    });

    if (allCheckpoints.length === 0) {
      feedDiv.innerHTML = `<div style="padding: 28px; text-align: center; color: #64748b; background: #f8fafc; border-radius: 10px; border: 1px dashed #cbd5e1;">Create a batch above to visualize its live GPS movement from Farm to Retailer.</div>`;
    } else {
      feedDiv.innerHTML = allCheckpoints.map((cp, idx) => `
        <div style="background: #f8fafc; border-left: 4px solid ${cp.actor_role === 'RETAILER' ? '#10b981' : cp.actor_role === 'PRODUCER' ? '#047857' : '#f59e0b'}; border-radius: 8px; padding: 10px 12px; margin-bottom: 10px; border-top: 1px solid #e2e8f0; border-right: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 11px; font-weight: 900; color: #0b3d2e; background: #d1fae5; padding: 2px 7px; border-radius: 10px;">Hop #${cp.hop_index || (idx + 1)} • ${escapeHtml(cp.actor_role)}</span>
            <span style="font-family: monospace; font-size: 10.5px; color: #64748b;">${escapeHtml(cp.lot_code.slice(-10))}</span>
          </div>
          <div style="font-size: 13px; font-weight: 800; color: #0f172a; margin-top: 4px;">${escapeHtml(cp.actor_name || cp.actor_role)} — ${escapeHtml(cp.location_label || '')}</div>
          <div style="font-size: 11.5px; color: #334155; margin-top: 2px;">
            Weight: <strong>${escapeHtml(String(cp.weight_kg || ''))} Kg</strong> • Condition: <strong>${escapeHtml(cp.condition || 'Sound')}</strong> • Temp: <strong>${escapeHtml(cp.storage_temp || 'Ambient')}</strong>
          </div>
          ${cp.photo_url ? `<div style="margin-top: 6px;"><img src="${escapeHtml(cp.photo_url)}" alt="Lot" style="max-height: 54px; border-radius: 6px; border: 1px solid #cbd5e1;" /></div>` : ''}
          <div style="font-size: 10.5px; color: #64748b; margin-top: 4px;">GPS: ${Number(cp.lat || 22.9868).toFixed(4)}, ${Number(cp.lng || 87.8550).toFixed(4)}</div>
        </div>
      `).join('');
    }

    if (typeof L === 'undefined') {
      mapDiv.innerHTML = `<div style="padding: 40px; text-align: center; color: #475569;">Interactive Map Ready (${allCheckpoints.length} GPS checkpoints plotted)</div>`;
      return;
    }

    try {
      if (window._liveMovementMapInstance) {
        try { window._liveMovementMapInstance.remove(); } catch (e) {}
        window._liveMovementMapInstance = null;
      }
      if (mapDiv._leaflet_id) delete mapDiv._leaflet_id;

      const map = L.map('farmerLiveMovementLeafletMap').setView([22.9868, 87.8550], 9);
      window._liveMovementMapInstance = map;
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap'
      }).addTo(map);

      const latLngs = [];
      allCheckpoints.forEach((cp, idx) => {
        const lat = parseFloat(cp.lat) || (22.9868 + idx * 0.03);
        const lng = parseFloat(cp.lng) || (87.8550 + idx * 0.03);
        latLngs.push([lat, lng]);
        L.circleMarker([lat, lng], {
          radius: 8,
          color: '#0b3d2e',
          fillColor: cp.actor_role === 'RETAILER' ? '#10b981' : cp.actor_role === 'PRODUCER' ? '#047857' : '#f59e0b',
          fillOpacity: 0.9,
          weight: 2
        }).bindPopup(`<b>${escapeHtml(cp.actor_role)}: ${escapeHtml(cp.actor_name || '')}</b><br/>Batch: ${escapeHtml(cp.lot_code)}<br/>Weight: ${cp.weight_kg} Kg | Condition: ${escapeHtml(cp.condition || 'Good')}`).addTo(map);
      });

      if (latLngs.length > 1) {
        L.polyline(latLngs, { color: '#047857', weight: 3.5, dashArray: '6, 6' }).addTo(map);
        map.fitBounds(latLngs, { padding: [30, 30] });
      } else if (latLngs.length === 1) {
        map.setView(latLngs[0], 12);
      }
    } catch (e) {}
  };

  /* --------------------------------------------------------------------------
     DOWNSTREAM CUSTODY & APPEND-ONLY QR SCAN CONSOLE
     (AGGREGATOR, WHOLESALER, DISTRIBUTOR, RETAILER)
     -------------------------------------------------------------------------- */
  window.renderDownstreamCustodyConsole = async function (container, role) {
    const activeRole = String(role || currentRole || 'AGGREGATOR').toUpperCase();
    let incomingRequests = [];
    let myCustodyLots = [];

    try {
      const res = await fetch('/api/v1/lots/handovers/incoming', { headers: getAuthHeader() });
      if (res.ok) {
        const data = await res.json();
        incomingRequests = data.incoming_requests || [];
        myCustodyLots = data.my_custody_lots || [];
      }
    } catch (e) {}

    const farmerUid = localStorage.getItem('annasutra_farmer_uid') || '';

    container.innerHTML = `
      <div style="background: #ffffff; border-radius: 16px; border: 1.5px solid #047857; padding: 24px; margin: 12px 0; box-shadow: 0 4px 16px rgba(4, 120, 87, 0.08);">
        <!-- Header Banner -->
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; border-bottom: 1.5px solid #e2e8f0; padding-bottom: 14px; margin-bottom: 18px;">
          <div>
            <span style="display: inline-block; background: #ecfdf5; border: 1px solid #86efac; color: #065f46; font-size: 11.5px; font-weight: 900; padding: 4px 10px; border-radius: 20px; margin-bottom: 6px;">
              VERIFIED ${escapeHtml(activeRole)} CUSTODY &amp; QR APPEND NODE
            </span>
            <h3 style="margin: 0; font-size: 21px; font-weight: 800; color: #0f172a;">${escapeHtml(activeRole)} Supply-Chain Handover &amp; QR Telemetry Console</h3>
            <p style="margin: 3px 0 0; font-size: 12.5px; color: #64748b;">
              Confirm incoming custody handovers and append live weight, product condition, storage temperature, and photos via QR scan.
            </p>
          </div>
          <div style="display: flex; align-items: center; gap: 10px;">
            ${farmerUid ? `<div style="font-family: monospace; font-size: 12px; font-weight: 800; color: #0b3d2e; background: #f8fafc; border: 1px solid #cbd5e1; padding: 6px 10px; border-radius: 8px;">Node ID: ${escapeHtml(farmerUid)}</div>` : ''}
            <button type="button" class="btn-wizard-action btn-wizard-draft" style="padding: 7px 14px; font-size: 12px; color: #dc2626; border-color: #fca5a5;" onclick="window.logoutEntitySession()">Log Out</button>
          </div>
        </div>

        <!-- Quick QR / Batch ID Scan Bar -->
        <div style="background: #f0fdf4; border: 1.5px solid #86efac; border-radius: 12px; padding: 14px 16px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
          <div style="flex: 1; min-width: 240px;">
            <strong style="font-size: 13.5px; color: #065f46; display: block;">Scan or Enter Batch QR / Barcode ID</strong>
            <span style="font-size: 12px; color: #047857;">Scan the sticker on the crate/lot to immediately Accept Custody or Append Condition/Weight/Photo.</span>
          </div>
          <div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center;">
            <input type="text" id="downstream_scan_lot_code" class="form-input" style="background: #fff; font-family: monospace; min-width: 260px;" placeholder="Paste or scan Batch ID (e.g. 2026...FR0001)" />
            <button type="button" class="btn-wizard-action btn-wizard-submit" style="padding: 9px 16px; font-size: 12.5px; font-weight: 800;" onclick="window.handleQuickDownstreamScan('ACCEPT')">
              ✓ Confirm &amp; Accept Custody
            </button>
            <button type="button" class="btn-wizard-action btn-wizard-draft" style="padding: 9px 16px; font-size: 12.5px; font-weight: 800; background: #fff;" onclick="window.handleQuickDownstreamScan('APPEND')">
              + Append Weight / Condition / Photo
            </button>
          </div>
        </div>

        <!-- Section 1: Incoming Custody Handover Requests -->
        <div style="margin-bottom: 24px;">
          <h4 style="margin: 0 0 10px; font-size: 16px; font-weight: 800; color: #0f172a;">
            1. Incoming Custody Handover Requests Awaiting Your Confirmation (${incomingRequests.length})
          </h4>
          ${incomingRequests.length === 0 ? `
            <div style="background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 10px; padding: 20px; text-align: center; color: #64748b; font-size: 13px;">
              No pending handover requests waiting in queue. You can also scan any Batch QR ID above to accept custody directly.
            </div>
          ` : incomingRequests.map(lot => {
            const pho = lot.pending_handover || {};
            return `
              <div style="background: #fffbeb; border: 1.5px solid #fde68a; border-radius: 12px; padding: 16px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                <div>
                  <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                    <span style="font-family: monospace; font-size: 13px; font-weight: 900; color: #0b3d2e; background: #fff; border: 1px solid #cbd5e1; padding: 3px 8px; border-radius: 6px;">${escapeHtml(lot.public_code)}</span>
                    <span style="font-size: 11px; font-weight: 900; background: #0b3d2e; color: #fff; padding: 2px 7px; border-radius: 4px;">${escapeHtml(lot.product_category_code || 'VG')}</span>
                    <strong style="font-size: 15px; color: #0f172a;">${escapeHtml(lot.crop)} ${lot.variety ? `• ${escapeHtml(lot.variety)}` : ''}</strong>
                  </div>
                  <div style="font-size: 12.5px; color: #92400e; margin-top: 4px;">
                    From: <strong>${escapeHtml(pho.from_name || pho.from_role || 'Farmer')}</strong> • Declared Weight: <strong>${escapeHtml(String(pho.declared_qty_kg || lot.net_qty_kg))} Kg</strong>
                  </div>
                </div>
                <button type="button" class="btn-wizard-action btn-wizard-submit" style="padding: 9px 18px; font-size: 12.5px; font-weight: 800;" onclick="window.openAcceptCustodyModal('${lot.public_code}', ${parseFloat(pho.declared_qty_kg || lot.net_qty_kg || 500)})">
                  ✓ Confirm &amp; Accept Custody
                </button>
              </div>
            `;
          }).join('')}
        </div>

        <!-- Section 2: Batches Currently in Your Custody (Append-Only Updates) -->
        <div>
          <h4 style="margin: 0 0 10px; font-size: 16px; font-weight: 800; color: #0f172a;">
            2. Batches in Your Custody — Append Scan Data &amp; Next Handover (${myCustodyLots.length})
          </h4>
          ${myCustodyLots.length === 0 ? `
            <div style="background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 10px; padding: 20px; text-align: center; color: #64748b; font-size: 13px;">
              Once you accept custody of a batch, it appears here so you can append weight, condition, photos, or hand over to the next party.
            </div>
          ` : myCustodyLots.map(lot => `
            <div style="background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 12px; padding: 16px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
              <div>
                <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                  <span style="font-family: monospace; font-size: 13px; font-weight: 900; color: #047857; background: #ecfdf5; border: 1px solid #86efac; padding: 3px 8px; border-radius: 6px;">${escapeHtml(lot.public_code)}</span>
                  <strong style="font-size: 15px; color: #0f172a;">${escapeHtml(lot.crop)}</strong>
                  <span style="font-size: 12px; color: #334155; font-weight: 700;">Current Weight: ${escapeHtml(String(lot.net_qty_kg || lot.on_hand_kg))} Kg</span>
                  ${lot.is_retailer_verified ? `<span style="font-size: 11px; font-weight: 800; background: #d1fae5; color: #065f46; padding: 2px 8px; border-radius: 12px;">✓ Retail Shelf Active (Consumer QR Unlocked)</span>` : ''}
                </div>
                <div style="font-size: 12px; color: #64748b; margin-top: 4px;">
                  Origin Farmer ID: <span style="font-family: monospace;">${escapeHtml(lot.farmer_uid || 'Locked')}</span> (🔒 Immutable Origin) • Checkpoints: ${(lot.journey_checkpoints || []).length}
                </div>
              </div>
              <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                <button type="button" class="btn-wizard-action btn-wizard-draft" style="padding: 8px 14px; font-size: 12px; font-weight: 800;" onclick="window.openAppendScanModal('${lot.public_code}', ${parseFloat(lot.net_qty_kg || lot.on_hand_kg || 500)})">
                  + Scan QR &amp; Append Weight / Condition / Photo
                </button>
                ${activeRole !== 'RETAILER' ? `
                  <button type="button" class="btn-wizard-action btn-wizard-submit" style="padding: 8px 14px; font-size: 12px; font-weight: 800;" onclick="window.openCustodyHandoverRequestModal('${lot.public_code}', '${escapeHtml(lot.crop)}', ${parseFloat(lot.net_qty_kg || lot.on_hand_kg || 500)})">
                    Handover to Next Party &rarr;
                  </button>
                ` : `
                  <a href="/l/${encodeURIComponent(lot.public_code)}" target="_blank" class="btn-wizard-action btn-wizard-submit" style="padding: 8px 14px; font-size: 12px; font-weight: 800; text-decoration: none;">
                    View Consumer Retail Passport &rarr;
                  </a>
                `}
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  };

  window.handleQuickDownstreamScan = function (mode) {
    const code = (document.getElementById('downstream_scan_lot_code')?.value || '').trim();
    if (!code) {
      showToast('Please enter or scan a Batch QR ID first.', 'warning');
      return;
    }
    if (mode === 'ACCEPT') {
      window.openAcceptCustodyModal(code, 500);
    } else {
      window.openAppendScanModal(code, 500);
    }
  };

  window.openAcceptCustodyModal = function (lotCode, defaultQty) {
    window._openDownstreamTelemetryModal('ACCEPT', lotCode, defaultQty);
  };

  window.openAppendScanModal = function (lotCode, defaultQty) {
    window._openDownstreamTelemetryModal('APPEND', lotCode, defaultQty);
  };

  window._openDownstreamTelemetryModal = function (mode, lotCode, defaultQty) {
    const isAccept = mode === 'ACCEPT';
    let modal = document.getElementById('downstreamTelemetryModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'downstreamTelemetryModal';
      modal.className = 'wizard-modal-backdrop';
      modal.style.cssText = 'position: fixed; inset: 0; background: rgba(15, 23, 42, 0.72); backdrop-filter: blur(4px); z-index: 99999; display: flex; align-items: center; justify-content: center; padding: 16px;';
      document.body.appendChild(modal);
    }

    modal.innerHTML = `
      <div style="background: #ffffff; border-radius: 16px; max-width: 560px; width: 100%; padding: 26px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.25);">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1.5px solid #e2e8f0; padding-bottom: 12px; margin-bottom: 14px;">
          <div>
            <h3 style="margin: 0; font-size: 18px; font-weight: 800; color: #0b3d2e;">
              ${isAccept ? 'Confirm & Accept Custody Handover' : 'Append-Only QR Scan Update'}
            </h3>
            <span style="font-family: monospace; font-size: 12px; color: #047857; font-weight: 800;">Batch #${escapeHtml(lotCode)}</span>
          </div>
          <button type="button" onclick="document.getElementById('downstreamTelemetryModal').style.display='none'" style="background: #f1f5f9; border: none; font-size: 18px; width: 32px; height: 32px; border-radius: 50%; cursor: pointer;">&times;</button>
        </div>

        <form onsubmit="window.submitDownstreamTelemetry(event, '${mode}', '${lotCode}')">
          <div class="form-grid-2" style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
            <div class="form-group">
              <label class="form-label">Current / Received Weight (Kg) <span class="req">*</span></label>
              <input type="number" step="0.1" min="0.1" id="ds_inp_weight" class="form-input" value="${defaultQty || 500}" required />
            </div>
            <div class="form-group">
              <label class="form-label">Product Condition <span class="req">*</span></label>
              <select id="ds_inp_condition" class="form-select" required>
                <option value="FRESH_GRADE_A">Fresh / Sound Grade A</option>
                <option value="COLD_CHAIN_INTACT">Cold-Chain Intact (Optimal)</option>
                <option value="GOOD_MARKET_READY">Good / Retail Shelf Ready</option>
                <option value="MINOR_TRANSIT_LOSS">Minor Transit Moisture Loss</option>
                <option value="DAMAGED">Damaged / Partial Reject</option>
              </select>
            </div>
          </div>

          <div class="form-grid-2" style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
            <div class="form-group">
              <label class="form-label">Storage / Transit Temp</label>
              <input type="text" id="ds_inp_temp" class="form-input" value="4.0°C Cold Chain" />
            </div>
            <div class="form-group">
              <label class="form-label">Checkpoint Facility / Shop Name</label>
              <input type="text" id="ds_inp_location" class="form-input" value="${escapeHtml((typeof currentRole !== 'undefined' ? currentRole : 'Custodian') + ' Checkpoint Hub')}" />
            </div>
          </div>

          <div class="form-group" style="margin-bottom: 12px;">
            <label class="form-label">Capture / Upload Lot Condition Photo (Optional)</label>
            <input type="file" accept="image/*" id="ds_inp_photo_file" class="form-input" onchange="window.previewDownstreamPhoto(this)" />
            <input type="hidden" id="ds_inp_photo_data_url" value="" />
          </div>

          <div class="form-group" style="margin-bottom: 16px;">
            <label class="form-label">Inspection Notes</label>
            <input type="text" id="ds_inp_notes" class="form-input" placeholder="QR verified on crate, weight and quality checked." />
          </div>

          <div style="display: flex; justify-content: flex-end; gap: 10px; border-top: 1px solid #e2e8f0; padding-top: 14px;">
            <button type="button" class="btn-wizard-action btn-wizard-draft" onclick="document.getElementById('downstreamTelemetryModal').style.display='none'">Cancel</button>
            <button type="submit" class="btn-wizard-action btn-wizard-submit" style="padding: 9px 20px; font-weight: 800;">
              <span>${isAccept ? '✓ Confirm Custody & Lock Previous Party' : '+ Append Scan Record to Ledger'}</span>
            </button>
          </div>
        </form>
      </div>
    `;
    modal.style.display = 'flex';
  };

  window.previewDownstreamPhoto = function (input) {
    const file = input.files && input.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = function (ev) {
      const hidden = document.getElementById('ds_inp_photo_data_url');
      if (hidden) hidden.value = ev.target.result;
    };
    reader.readAsDataURL(file);
  };

  window.submitDownstreamTelemetry = async function (e, mode, lotCode) {
    e.preventDefault();
    const isAccept = mode === 'ACCEPT';
    const weightKg = parseFloat(document.getElementById('ds_inp_weight')?.value || 500);
    const condition = document.getElementById('ds_inp_condition')?.value || 'FRESH_GRADE_A';
    const storageTemp = document.getElementById('ds_inp_temp')?.value || 'Ambient';
    const locationLabel = document.getElementById('ds_inp_location')?.value || '';
    const photoUrl = document.getElementById('ds_inp_photo_data_url')?.value || '';
    const notes = document.getElementById('ds_inp_notes')?.value || '';
    const actorRole = (typeof currentRole !== 'undefined' && currentRole) ? currentRole : 'AGGREGATOR';

    const endpoint = isAccept
      ? `/api/v1/lots/${encodeURIComponent(lotCode)}/handover-accept`
      : `/api/v1/lots/${encodeURIComponent(lotCode)}/append-scan`;

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: Object.assign({}, getAuthHeader(), { 'Content-Type': 'application/json' }),
        body: JSON.stringify({
          actor_role: actorRole,
          actor_name: `${actorRole} Node`,
          received_qty_kg: weightKg,
          weight_kg: weightKg,
          condition: condition,
          storage_temp: storageTemp,
          location_label: locationLabel,
          photo_url: photoUrl,
          notes: notes,
          lat: 22.82 + Math.random() * 0.15,
          lng: 88.15 + Math.random() * 0.15
        })
      });
      const data = await res.json();
      if (res.ok) {
        document.getElementById('downstreamTelemetryModal').style.display = 'none';
        showToast(
          isAccept
            ? `Custody accepted for Batch #${lotCode}! Previous custodian locked (🔒).`
            : `Telemetry appended to Batch #${lotCode}! Farmer Live Map updated.`,
          'success'
        );
        const contentArea = document.getElementById('workspaceDynamicContent');
        if (contentArea) await renderDownstreamCustodyConsole(contentArea, actorRole);
      } else {
        showToast(data.detail || 'Action failed.', 'error');
      }
    } catch (err) {
      showToast('Network error submitting custody telemetry.', 'error');
    }
  };

  window.downloadMyQrPdfSheet = async function () {
    try {
      const res = await fetch('/api/v1/me/qr-blocks', { headers: getAuthHeader() });
      if (res.ok) {
        const data = await res.json();
        if (data.blocks && data.blocks.length > 0) {
          const block = data.blocks[0];
          window.open(block.download_pdf_url, '_blank');
        } else {
          showToast('No QR blocks allocated yet.', 'warning');
        }
      } else {
        showToast('Unable to load QR blocks.', 'error');
      }
    } catch (e) {
      showToast('Network error loading QR sheet.', 'error');
    }
  };

  /* --------------------------------------------------------------------------
     5-STEP PRODUCER REGISTRATION WIZARD
     -------------------------------------------------------------------------- */
  function renderWizardInterface(container) {
    const t = getI18n();
    const p = wizardState.profile || {};
    const sens = wizardState.sensitive || {};
    const step = wizardState.currentStep;
    const farmerUid = p.farmer_uid || localStorage.getItem('annasutra_farmer_uid') || window.computeLiveMentorBatchIdPreview('').slice(0, 22);

    container.innerHTML = `
      <div class="wizard-card">
        <!-- Quick Switch Bar to Operational Dashboard & Batch Creation -->
        <div style="background: #ecfdf5; border: 1.5px solid #10b981; border-radius: 12px; padding: 12px 16px; margin-bottom: 18px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
          <div>
            <div style="font-size: 11px; font-weight: 800; color: #065f46; text-transform: uppercase;">Unique Farmer ID (YYYYDDHHMMSS+CountryCodeMobile)</div>
            <div style="font-family: monospace; font-size: 15px; font-weight: 900; color: #0b3d2e;">${escapeHtml(farmerUid)}</div>
          </div>
          <div style="display: flex; gap: 8px; flex-wrap: wrap;">
            <button type="button" class="btn-wizard-action btn-wizard-submit" style="padding: 8px 16px; font-size: 12.5px; font-weight: 800;" onclick="window.openProducerOperationalDashboard('create_map')">
              <span>+ Create Batch &amp; Live Lot Movement Map &rarr;</span>
            </button>
            <button type="button" class="btn-wizard-action btn-wizard-draft" style="padding: 8px 14px; font-size: 12.5px; font-weight: 800; background: #fff;" onclick="window.openProducerOperationalDashboard('ledger')">
              <span>Open Farmer Dashboard (${(window._producerLots || []).length} Lots)</span>
            </button>
          </div>
        </div>

        <!-- 1. Stepper Bar -->
        <div class="wizard-stepper">
          <div class="step-node ${step === 1 ? 'active' : step > 1 ? 'completed' : ''}" onclick="goToStep(1)">
            <div class="step-circle">${step > 1 ? getIcon('check', 12, '#ffffff', 2.8) : '1'}</div>
            <span class="step-label">${escapeHtml(t.stepTab1)}</span>
          </div>
          <div class="step-line ${step > 1 ? 'completed' : ''}"></div>

          <div class="step-node ${step === 2 ? 'active' : step > 2 ? 'completed' : ''}" onclick="goToStep(2)">
            <div class="step-circle">${step > 2 ? getIcon('check', 12, '#ffffff', 2.8) : '2'}</div>
            <span class="step-label">${escapeHtml(t.stepTab2)}</span>
          </div>
          <div class="step-line ${step > 2 ? 'completed' : ''}"></div>

          <div class="step-node ${step === 3 ? 'active' : step > 3 ? 'completed' : ''}" onclick="goToStep(3)">
            <div class="step-circle">${step > 3 ? getIcon('check', 12, '#ffffff', 2.8) : '3'}</div>
            <span class="step-label">${escapeHtml(t.stepTab3)}</span>
          </div>
          <div class="step-line ${step > 3 ? 'completed' : ''}"></div>

          <div class="step-node ${step === 4 ? 'active' : step > 4 ? 'completed' : ''}" onclick="goToStep(4)">
            <div class="step-circle">${step > 4 ? getIcon('check', 12, '#ffffff', 2.8) : '4'}</div>
            <span class="step-label">${escapeHtml(t.stepTab4)}</span>
          </div>
          <div class="step-line ${step > 4 ? 'completed' : ''}"></div>

          <div class="step-node ${step === 5 ? 'active' : ''}" onclick="goToStep(5)">
            <div class="step-circle">5</div>
            <span class="step-label">${escapeHtml(t.stepTab5)}</span>
          </div>
        </div>

        <!-- 2. Step View Content Container -->
        <div id="stepViewContainer">
          ${renderStepContent(step, t, p, sens)}
        </div>

        <!-- 3. Actions Bar -->
        <div class="wizard-actions-bar">
          <div>
            ${step > 1 ? `<button class="btn-wizard-action btn-wizard-prev" onclick="goToStep(${step - 1})">${escapeHtml(t.btnPrev)}</button>` : ''}
          </div>
          <div style="display: flex; gap: 10px; flex-wrap: wrap;">
            <button class="btn-wizard-action btn-wizard-draft" onclick="saveDraftManual(true)">${escapeHtml(t.btnSaveDraft)}</button>
            ${step < 5
              ? `<button class="btn-wizard-action btn-wizard-next" onclick="validateAndAdvanceStep(${step})">${escapeHtml(t.btnNext)}</button>`
              : `<button class="btn-wizard-action btn-wizard-submit" id="btnSubmitProfile" onclick="submitFinalRegistration()">${escapeHtml(t.btnSubmit)}</button>`
            }
          </div>
        </div>
      </div>
    `;

    if (step === 2) {
      setTimeout(initPlotMap, 100);
    }
  }

  function renderStepContent(step, t, p, sens) {
    if (step === 1) {
      return `
        <div class="wizard-step-header">
          <h3 class="wizard-step-title"><span>${getIcon('sprout', 18, '#047857')}</span> ${escapeHtml(t.step1Title)}</h3>
          <p class="wizard-step-desc">${escapeHtml(t.step1Desc)}</p>
        </div>

        <div class="photo-uploader-box">
          <img src="${p.photo_object_key ? '/media/' + p.photo_object_key : '/static/publicview/images/annasutra_emblem.png'}" class="photo-preview-avatar" id="farmerPhotoPreview" alt="Profile" />
          <div class="photo-upload-meta">
            <strong style="font-size: 14px; color: #0f172a; display: block; margin-bottom: 4px;">${escapeHtml(t.photoLabel)}</strong>
            <p style="font-size: 12px; color: #64748b; margin: 0 0 10px;">${escapeHtml(t.photoHint)}</p>
            <label class="btn-upload-file">
              <span>${escapeHtml(t.photoUploadBtn)}</span>
              <input type="file" id="farmerPhotoInput" accept="image/jpeg,image/png,image/webp" style="display: none;" onchange="handlePhotoUpload(this)" />
            </label>
            <span id="photoStatusBadge" style="display: ${p.photo_object_key ? 'inline-block' : 'none'}; font-size: 11.5px; color: #059669; font-weight: 700; margin-left: 10px;">${escapeHtml(t.photoScrubbed)}</span>
          </div>
        </div>

        <div class="form-grid-2">
          <div class="form-group">
            <label class="form-label">${escapeHtml(t.firstName)} <span class="req">*</span></label>
            <input type="text" class="form-input" id="inp_first_name" value="${escapeHtml(p.first_name || '')}" placeholder="${escapeHtml(t.firstNamePh)}" />
          </div>
          <div class="form-group">
            <label class="form-label">${escapeHtml(t.lastName)} <span class="req">*</span></label>
            <input type="text" class="form-input" id="inp_last_name" value="${escapeHtml(p.last_name || '')}" placeholder="${escapeHtml(t.lastNamePh)}" />
          </div>
        </div>

        <div class="form-grid-2">
          <div class="form-group">
            <label class="form-label">${escapeHtml(t.orgName)} <span class="req">*</span></label>
            <input type="text" class="form-input" id="inp_org_name" value="${escapeHtml(p.organisation_name || '')}" placeholder="${escapeHtml(t.orgNamePh)}" />
          </div>
          <div class="form-group">
            <label class="form-label">${escapeHtml(t.gender)}</label>
            <select class="form-select" id="inp_gender">
              <option value="UNSPECIFIED" ${(!p.gender || p.gender === 'UNSPECIFIED') ? 'selected' : ''}>${escapeHtml(t.genderSelect)}</option>
              <option value="MALE" ${(p.gender === 'MALE' || p.gender === 'M') ? 'selected' : ''}>${escapeHtml(t.genderMale)}</option>
              <option value="FEMALE" ${(p.gender === 'FEMALE' || p.gender === 'F') ? 'selected' : ''}>${escapeHtml(t.genderFemale)}</option>
              <option value="OTHER" ${(p.gender === 'OTHER' || p.gender === 'O') ? 'selected' : ''}>${escapeHtml(t.genderOther)}</option>
            </select>
          </div>
        </div>

        <div class="form-grid-3">
          <div class="form-group">
            <label class="form-label">${escapeHtml(t.state)} <span class="req">*</span></label>
            <select class="form-select" id="inp_state">
              <option value="">${escapeHtml(t.stateSelect)}</option>
              ${STATES_LIST.map(s => `<option value="${escapeHtml(s.id)}" ${p.state === s.id ? 'selected' : ''}>${escapeHtml(getStateLabel(s.id))}</option>`).join('')}
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">${escapeHtml(t.district)} <span class="req">*</span></label>
            <input type="text" class="form-input" id="inp_district" value="${escapeHtml(p.district || '')}" placeholder="${escapeHtml(t.districtPh)}" />
          </div>
          <div class="form-group">
            <label class="form-label">${escapeHtml(t.pincode)} <span class="req">*</span></label>
            <input type="text" class="form-input" id="inp_pincode" maxlength="6" value="${escapeHtml(p.pincode && p.pincode !== '000000' ? p.pincode : '')}" placeholder="${escapeHtml(t.pincodePh)}" />
          </div>
        </div>

        <div class="form-grid-2">
          <div class="form-group">
            <label class="form-label">${escapeHtml(t.village)} <span class="req">*</span></label>
            <input type="text" class="form-input" id="inp_village" value="${escapeHtml(p.village_town || '')}" placeholder="${escapeHtml(t.villagePh)}" />
          </div>
          <div class="form-group">
            <label class="form-label">${escapeHtml(t.address)} <span class="req">*</span></label>
            <input type="text" class="form-input" id="inp_address1" value="${escapeHtml(p.address_line1 || '')}" placeholder="${escapeHtml(t.addressPh)}" />
          </div>
        </div>
      `;
    }

    if (step === 2) {
      const plots = wizardState.plots || [];
      const totalAcres = plots.reduce((acc, pl) => acc + (parseFloat(pl.area_acres) || 0), 0);

      return `
        <div class="wizard-step-header">
          <h3 class="wizard-step-title"><span>${getIcon('map-pin', 18, '#047857')}</span> ${escapeHtml(t.step2Title)}</h3>
          <p class="wizard-step-desc">${escapeHtml(t.step2Desc)}</p>
        </div>

        <div class="plot-map-wrapper">
          <div class="plot-map-toolbar">
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
              <button type="button" class="btn-upload-file" style="background: #0b3d2e;" onclick="startPolygonDraw()">
                <span>${getIcon('map-pin', 14, '#ffffff')}</span> <span>${escapeHtml(t.btnDrawPolygon)}</span>
              </button>
              <button type="button" class="btn-wizard-action btn-wizard-draft" style="padding: 6px 12px; font-size: 12px;" onclick="clearPolygonDraw()">
                ${escapeHtml(t.btnClearPoints)}
              </button>
              <button type="button" class="btn-wizard-action btn-wizard-draft" style="padding: 6px 12px; font-size: 12px;" onclick="geolocatePlot()">
                <span>${getIcon('map-pin', 14, '#047857')}</span> <span>${escapeHtml(t.btnUseGps)}</span>
              </button>
            </div>
            <div class="acre-badge-live" id="liveAcreIndicator">${escapeHtml(t.estAreaLabel)}: 0.00 ${escapeHtml(t.acresUnit)}</div>
          </div>
          <div id="plotLeafletMap" class="plot-map-canvas"></div>
        </div>

        <div class="form-grid-3" style="align-items: end; background: #f8fafc; padding: 14px; border-radius: 10px; border: 1px solid #e2e8f0;">
          <div class="form-group" style="margin-bottom: 0;">
            <label class="form-label">${escapeHtml(t.plotNameLabel)} <span class="req">*</span></label>
            <input type="text" class="form-input" id="inp_plot_name" placeholder="${escapeHtml(t.plotNamePh)}" />
          </div>
          <div class="form-group" style="margin-bottom: 0;">
            <label class="form-label">${escapeHtml(t.plotAreaLabel)} <span class="req">*</span></label>
            <input type="number" step="0.01" class="form-input" id="inp_plot_acres" placeholder="${escapeHtml(t.plotAreaPh)}" />
          </div>
          <div>
            <button type="button" class="btn-wizard-action btn-wizard-next" style="width: 100%; justify-content: center;" onclick="addCurrentPlotToList()">
              ${escapeHtml(t.btnAddPlot)}
            </button>
          </div>
        </div>

        <div style="margin-top: 16px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <strong style="font-size: 13px; color: #0f172a;">${escapeHtml(t.registeredPlotsTitle)} (${plots.length})</strong>
            <span style="font-size: 13px; font-weight: 800; color: #059669;">${escapeHtml(t.totalLabel)}: ${totalAcres.toFixed(2)} ${escapeHtml(t.acresUnit)}</span>
          </div>
          <div class="plot-list-box" id="registeredPlotsContainer">
            ${plots.length === 0
              ? `<div style="padding: 16px; text-align: center; color: #64748b; font-size: 12.5px; background: #f8fafc; border-radius: 8px; border: 1px dashed #cbd5e1;">${escapeHtml(t.noPlotsYet)}</div>`
              : plots.map((pl, idx) => `
                  <div class="plot-row-item">
                    <div>
                      <strong style="color: #0f172a;">${escapeHtml(pl.plot_name)}</strong>
                      <span style="color: #64748b; font-size: 12px; margin-left: 8px;">• ${escapeHtml(pl.district || p.district || '')}</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 12px;">
                      <span class="acre-badge-live">${parseFloat(pl.area_acres).toFixed(2)} ${escapeHtml(t.acresUnit)}</span>
                      <button type="button" style="background: none; border: none; color: #ef4444; cursor: pointer; font-weight: 800; font-size: 12px;" onclick="removePlot(${idx})">${escapeHtml(t.btnRemove)}</button>
                    </div>
                  </div>
                `).join('')
            }
          </div>
        </div>
      `;
    }

    if (step === 3) {
      const rDet = (p.role_details || {});
      const selectedCrops = wizardState.selectedCrops || [];

      return `
        <div class="wizard-step-header">
          <h3 class="wizard-step-title"><span>${getIcon('wheat', 18, '#047857')}</span> ${escapeHtml(t.step3Title)}</h3>
          <p class="wizard-step-desc">${escapeHtml(t.step3Desc)}</p>
        </div>

        <div class="form-grid-2">
          <div class="form-group">
            <label class="form-label">${escapeHtml(t.farmType)} <span class="req">*</span></label>
            <select class="form-select" id="inp_farm_type">
              <option value="INDIVIDUAL_FARMER" ${rDet.farm_type === 'INDIVIDUAL_FARMER' ? 'selected' : ''}>${escapeHtml(t.farmTypeInd)}</option>
              <option value="FPO_PRODUCER" ${rDet.farm_type === 'FPO_PRODUCER' ? 'selected' : ''}>${escapeHtml(t.farmTypeFpo)}</option>
              <option value="SHG_COLLECTIVE" ${rDet.farm_type === 'SHG_COLLECTIVE' ? 'selected' : ''}>${escapeHtml(t.farmTypeShg)}</option>
              <option value="COOPERATIVE" ${rDet.farm_type === 'COOPERATIVE' ? 'selected' : ''}>${escapeHtml(t.farmTypeCoop)}</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">${escapeHtml(t.irrigation)} <span class="req">*</span></label>
            <select class="form-select" id="inp_irrigation">
              <option value="RAINFED" ${rDet.irrigation === 'RAINFED' ? 'selected' : ''}>${escapeHtml(t.irrRain)}</option>
              <option value="CANAL_RIVER" ${rDet.irrigation === 'CANAL_RIVER' ? 'selected' : ''}>${escapeHtml(t.irrCanal)}</option>
              <option value="BOREWELL" ${rDet.irrigation === 'BOREWELL' ? 'selected' : ''}>${escapeHtml(t.irrBore)}</option>
              <option value="DRIP_MICRO" ${rDet.irrigation === 'DRIP_MICRO' ? 'selected' : ''}>${escapeHtml(t.irrDrip)}</option>
            </select>
          </div>
        </div>

        <div class="form-group">
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
        </div>

        <div class="form-group" style="margin-top: 16px;">
          <label class="form-label">${escapeHtml(t.certifications)}</label>
          <select class="form-select" id="inp_certifications">
            <option value="NONE" ${rDet.certification === 'NONE' ? 'selected' : ''}>${escapeHtml(t.certNone)}</option>
            <option value="NPOP_ORGANIC" ${rDet.certification === 'NPOP_ORGANIC' ? 'selected' : ''}>${escapeHtml(t.certNpop)}</option>
            <option value="PGS_INDIA" ${rDet.certification === 'PGS_INDIA' ? 'selected' : ''}>${escapeHtml(t.certPgs)}</option>
            <option value="GOOD_AGRI_PRACTICES" ${rDet.certification === 'GOOD_AGRI_PRACTICES' ? 'selected' : ''}>${escapeHtml(t.certGap)}</option>
          </select>
        </div>
      `;
    }

    if (step === 4) {
      return `
        <div class="wizard-step-header">
          <h3 class="wizard-step-title"><span>${getIcon('lock', 18, '#047857')}</span> ${escapeHtml(t.step4Title)}</h3>
          <p class="wizard-step-desc">${escapeHtml(t.step4Desc)}</p>
        </div>

        <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 10px; padding: 12px 16px; margin-bottom: 18px; display: flex; align-items: center; gap: 12px; font-size: 12.5px; color: #1e3a8a;">
          <span>${getIcon('shield', 20, '#047857')}</span>
          <div>${escapeHtml(t.kycVaultNotice)}</div>
        </div>

        <div class="form-grid-2">
          <div class="form-group">
            <label class="form-label">${escapeHtml(t.panLabel)} <span class="req">*</span></label>
            <input type="text" class="form-input" id="inp_pan" maxlength="10" style="text-transform: uppercase; font-family: monospace;" placeholder="${escapeHtml(t.panPh)}" oninput="handlePanInput(this)" />
            <div class="masked-preview-pill" id="panMaskPreview">${escapeHtml(t.maskedPreview)}: ${escapeHtml(sens.pan_masked || 'AB******5C')}</div>
          </div>

          <div class="form-group">
            <label class="form-label">${escapeHtml(t.aadhaarLabel)}</label>
            <input type="text" class="form-input" id="inp_aadhaar4" maxlength="4" value="${escapeHtml(sens.aadhaar_last4 || '')}" style="font-family: monospace; letter-spacing: 3px;" placeholder="${escapeHtml(t.aadhaarPh)}" oninput="this.value = this.value.replace(/\\D/g, '').slice(0, 4)" />
            <span class="form-hint" style="color: #059669; font-weight: 600;">${escapeHtml(t.aadhaarNotice)}</span>
          </div>
        </div>

        <div class="form-grid-2">
          <div class="form-group">
            <label class="form-label">${escapeHtml(t.bankName)} <span class="req">*</span></label>
            <input type="text" class="form-input" id="inp_bank_name" value="${escapeHtml(sens.bank_name || '')}" placeholder="${escapeHtml(t.bankNamePh)}" />
          </div>
          <div class="form-group">
            <label class="form-label">${escapeHtml(t.ifsc)} <span class="req">*</span></label>
            <input type="text" class="form-input" id="inp_ifsc" maxlength="11" style="text-transform: uppercase; font-family: monospace;" placeholder="${escapeHtml(t.ifscPh)}" oninput="this.value = this.value.toUpperCase()" />
          </div>
        </div>

        <div class="form-grid-3">
          <div class="form-group">
            <label class="form-label">${escapeHtml(t.accountNo)} <span class="req">*</span></label>
            <input type="password" class="form-input" id="inp_account_no" placeholder="${escapeHtml(t.accountNoPh)}" oninput="handleAccountInput(this)" />
            <div class="masked-preview-pill" id="accountMaskPreview">${escapeHtml(t.maskedPreview)}: ${escapeHtml(sens.bank_account_masked || 'XXXXXXXX1234')}</div>
          </div>
          <div class="form-group">
            <label class="form-label">${escapeHtml(t.confirmAccountNo)} <span class="req">*</span></label>
            <input type="text" class="form-input" id="inp_confirm_account_no" placeholder="${escapeHtml(t.confirmAccountNoPh)}" />
          </div>
          <div class="form-group">
            <label class="form-label">${escapeHtml(t.upi)}</label>
            <input type="text" class="form-input" id="inp_upi" placeholder="${escapeHtml(t.upiPh)}" />
          </div>
        </div>

        <div class="form-group" style="margin-top: 12px; background: #f8fafc; padding: 14px; border-radius: 10px; border: 1px solid #e2e8f0;">
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
              <strong style="font-size: 13px; color: #0f172a; display: block;">${escapeHtml(t.docTitle)}</strong>
              <span style="font-size: 11.5px; color: #64748b;">${escapeHtml(t.docSub)}</span>
            </div>
            <div style="display: flex; align-items: center; gap: 10px;">
              <select class="form-select" id="inp_doc_type" style="width: auto; padding: 6px 10px; font-size: 12px;">
                <option value="LAND_RECORD">${escapeHtml(t.docLand)}</option>
                <option value="FPO_REG">${escapeHtml(t.docFpo)}</option>
                <option value="ORGANIC_CERT">${escapeHtml(t.docOrg)}</option>
              </select>
              <label class="btn-upload-file" style="margin: 0;">
                <span>${getIcon('file-text', 14, '#047857')}</span> <span>${escapeHtml(t.docBtnUpload)}</span>
                <input type="file" accept=".jpg,.jpeg,.png,.pdf" style="display: none;" onchange="handleDocumentUpload(this)" />
              </label>
            </div>
          </div>
          <div id="docUploadStatus" style="margin-top: 8px; font-size: 12px; color: #059669; font-weight: 700; display: none;"></div>
        </div>
      `;
    }

    if (step === 5) {
      const plots = wizardState.plots || [];
      const totalAcres = plots.reduce((acc, pl) => acc + (parseFloat(pl.area_acres) || 0), 0);
      const cropsDisplay = (wizardState.selectedCrops || []).map(getCropLabel).join(', ');

      return `
        <div class="wizard-step-header">
          <h3 class="wizard-step-title"><span>${getIcon('check', 18, '#15803d', 2.8)}</span> ${escapeHtml(t.step5Title)}</h3>
          <p class="wizard-step-desc">${escapeHtml(t.step5Desc)}</p>
        </div>

        <div class="submitted-details-grid" style="margin-top: 0; margin-bottom: 20px;">
          <div class="detail-item-box">
            <div class="detail-item-label">${escapeHtml(t.sumApplicant)}</div>
            <div class="detail-item-value">${escapeHtml(p.first_name || '')} ${escapeHtml(p.last_name || '')}</div>
          </div>
          <div class="detail-item-box">
            <div class="detail-item-label">${escapeHtml(t.sumEnterprise)}</div>
            <div class="detail-item-value">${escapeHtml(p.organisation_name || t.notEntered)}</div>
          </div>
          <div class="detail-item-box">
            <div class="detail-item-label">${escapeHtml(t.sumJurisdiction)}</div>
            <div class="detail-item-value">${escapeHtml([p.village_town, p.district, getStateLabel(p.state)].filter(Boolean).join(', ') || t.notEntered)}</div>
          </div>
          <div class="detail-item-box">
            <div class="detail-item-label">${escapeHtml(t.sumLand)}</div>
            <div class="detail-item-value">${totalAcres.toFixed(2)} ${escapeHtml(t.acresUnit)} (${plots.length} ${escapeHtml(t.plotsWord)})</div>
          </div>
          <div class="detail-item-box">
            <div class="detail-item-label">${escapeHtml(t.sumCrops)}</div>
            <div class="detail-item-value">${escapeHtml(cropsDisplay || t.noneSelected)}</div>
          </div>
          <div class="detail-item-box">
            <div class="detail-item-label">${escapeHtml(t.sumIdentity)}</div>
            <div class="detail-item-value">${escapeHtml(sens.pan_masked || (sens.aadhaar_last4 ? '•••• ' + sens.aadhaar_last4 : 'AES-256'))} | ${escapeHtml(sens.bank_name || '')}</div>
          </div>
        </div>

        <div class="consent-box- statutory">
          <h4 style="margin: 0 0 12px; font-size: 14px; color: #0b3d2e; display: flex; align-items: center; gap: 6px;">
            <span>${getIcon('scale', 16, '#047857')}</span> ${escapeHtml(t.consentHeader)}
          </h4>
          <label class="consent-check-row">
            <input type="checkbox" id="chk_consent_1" checked />
            <span>${escapeHtml(t.consent1)}</span>
          </label>
          <label class="consent-check-row">
            <input type="checkbox" id="chk_consent_2" checked />
            <span>${escapeHtml(t.consent2)}</span>
          </label>
          <label class="consent-check-row">
            <input type="checkbox" id="chk_consent_3" checked />
            <span>${escapeHtml(t.consent3)}</span>
          </label>
        </div>
      `;
    }
  }

  /* --------------------------------------------------------------------------
     NAVIGATION & STEP VALIDATION
     -------------------------------------------------------------------------- */
  window.goToStep = function (targetStep) {
    captureCurrentStepInputs(wizardState.currentStep);
    wizardState.currentStep = targetStep;
    const contentArea = document.getElementById('workspaceDynamicContent');
    if (contentArea) {
      renderWizardInterface(contentArea);
    }
  };

  function captureCurrentStepInputs(step) {
    if (!wizardState.profile) wizardState.profile = {};
    const p = wizardState.profile;

    if (step === 1) {
      const fn = document.getElementById('inp_first_name');
      const ln = document.getElementById('inp_last_name');
      const org = document.getElementById('inp_org_name');
      const gen = document.getElementById('inp_gender');
      const st = document.getElementById('inp_state');
      const dist = document.getElementById('inp_district');
      const pin = document.getElementById('inp_pincode');
      const vil = document.getElementById('inp_village');
      const addr = document.getElementById('inp_address1');

      if (fn) p.first_name = fn.value.trim();
      if (ln) p.last_name = ln.value.trim();
      if (org) p.organisation_name = org.value.trim();
      if (gen) p.gender = gen.value;
      if (st) p.state = st.value;
      if (dist) p.district = dist.value.trim();
      if (pin) p.pincode = pin.value.trim();
      if (vil) p.village_town = vil.value.trim();
      if (addr) p.address_line1 = addr.value.trim();
      updateRegisteredHeaderBanner(p);
    }

    if (step === 3) {
      if (!p.role_details) p.role_details = {};
      const ft = document.getElementById('inp_farm_type');
      const irr = document.getElementById('inp_irrigation');
      const cert = document.getElementById('inp_certifications');

      if (ft) p.role_details.farm_type = ft.value;
      if (irr) p.role_details.irrigation = irr.value;
      if (cert) p.role_details.certification = cert.value;
      p.role_details.commodities = wizardState.selectedCrops || [];
    }
  }

  window.validateAndAdvanceStep = async function (step) {
    captureCurrentStepInputs(step);
    const p = wizardState.profile || {};

    if (step === 1) {
      if (!p.first_name || p.first_name.length < 2) {
        showToast('Please enter your First Name (minimum 2 characters).', 'warning');
        return;
      }
      if (!p.last_name) {
        showToast('Please enter your Last Name.', 'warning');
        return;
      }
      if (!p.organisation_name || p.organisation_name.length < 2) {
        showToast('Please enter your Farm or Enterprise Name.', 'warning');
        return;
      }
      if (!p.state) {
        showToast('Please select your State.', 'warning');
        return;
      }
      if (!p.district) {
        showToast('Please enter your District.', 'warning');
        return;
      }
      if (!p.pincode || !/^[0-9]{6}$/.test(p.pincode)) {
        showToast('Please enter a valid 6-digit PIN Code.', 'warning');
        return;
      }
      if (!p.village_town) {
        showToast('Please enter your Village or Town.', 'warning');
        return;
      }
      if (!p.address_line1 || p.address_line1.length < 3) {
        showToast('Please enter your Street Address / Plot Location.', 'warning');
        return;
      }

      await saveDraftManual(false);
      goToStep(2);
      return;
    }

    if (step === 2) {
      const nameInp = document.getElementById('inp_plot_name');
      const acresInp = document.getElementById('inp_plot_acres');
      if (nameInp && nameInp.value.trim() && acresInp && parseFloat(acresInp.value) > 0) {
        addCurrentPlotToList();
      }

      if (!wizardState.plots || wizardState.plots.length === 0) {
        showToast('Please add at least one Farm Plot boundary to proceed.', 'warning');
        return;
      }

      await savePlotsToServer();
      goToStep(3);
      return;
    }

    if (step === 3) {
      if (!wizardState.selectedCrops || wizardState.selectedCrops.length === 0) {
        showToast('Please select at least one primary agricultural crop.', 'warning');
        return;
      }
      await saveDraftManual(false);
      goToStep(4);
      return;
    }

    if (step === 4) {
      const ok = await saveSensitiveToServer();
      if (!ok) return;
      goToStep(5);
      return;
    }
  };

  /* --------------------------------------------------------------------------
     API PERSISTENCE HANDLERS
     -------------------------------------------------------------------------- */
  window.saveDraftManual = async function (notifyUser) {
    captureCurrentStepInputs(wizardState.currentStep);
    const p = wizardState.profile || {};

    const payload = {
      role: 'PRODUCER',
      first_name: p.first_name || '',
      last_name: p.last_name || '',
      organisation_name: p.organisation_name || '',
      gender: p.gender || '',
      state: p.state || '',
      district: p.district || '',
      village_town: p.village_town || '',
      pincode: p.pincode || '000000',
      address_line1: p.address_line1 || '',
      role_details: p.role_details || { commodities: wizardState.selectedCrops || [] }
    };

    try {
      const res = await fetch('/api/v1/me/profile', {
        method: 'PUT',
        headers: getAuthHeader(),
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        const updated = await res.json();
        wizardState.profile = updated;
        updateRegisteredHeaderBanner(updated);
        if (notifyUser) {
          showToast('Draft profile saved.', 'success');
        }
      } else if (notifyUser) {
        showToast('Could not save draft.', 'warning');
      }
    } catch (e) {
      if (notifyUser) {
        showToast('Network error saving draft.', 'error');
      }
    }
  };

  async function savePlotsToServer() {
    try {
      const res = await fetch('/api/v1/me/plots', {
        method: 'PUT',
        headers: getAuthHeader(),
        body: JSON.stringify({ plots: wizardState.plots })
      });
      if (res.ok) {
        const data = await res.json();
        wizardState.plots = data.plots || wizardState.plots;
        if (wizardState.profile) {
          wizardState.profile.total_land_acres = data.total_acres;
        }
      }
    } catch (e) {}
  }

  async function saveSensitiveToServer() {
    const panEl = document.getElementById('inp_pan');
    const a4El = document.getElementById('inp_aadhaar4');
    const bankEl = document.getElementById('inp_bank_name');
    const ifscEl = document.getElementById('inp_ifsc');
    const accEl = document.getElementById('inp_account_no');
    const confAccEl = document.getElementById('inp_confirm_account_no');
    const upiEl = document.getElementById('inp_upi');

    const pan = panEl ? panEl.value.trim().toUpperCase() : '';
    const a4 = a4El ? a4El.value.trim() : '';
    const bank = bankEl ? bankEl.value.trim() : '';
    const ifsc = ifscEl ? ifscEl.value.trim().toUpperCase() : '';
    const acc = accEl ? accEl.value.trim() : '';
    const confAcc = confAccEl ? confAccEl.value.trim() : '';
    const upi = upiEl ? upiEl.value.trim() : '';

    const existingSens = wizardState.sensitive || {};

    if (!pan && !a4 && !existingSens.pan_masked && !existingSens.aadhaar_last4) {
      showToast('Please provide either a 10-character PAN or voluntary Aadhaar last-4 digits.', 'warning');
      return false;
    }

    if (pan && !/^[A-Z]{5}[0-9]{4}[A-Z]{1}$/.test(pan)) {
      showToast('Invalid PAN format. Must be 5 letters, 4 digits, and 1 letter.', 'error');
      return false;
    }

    if (a4 && !/^[0-9]{4}$/.test(a4)) {
      showToast('Voluntary Aadhaar field must contain exactly 4 digits.', 'error');
      return false;
    }

    if (!bank && !existingSens.bank_name) {
      showToast('Please enter your Bank Name.', 'warning');
      return false;
    }

    if (ifsc && !/^[A-Z]{4}0[A-Z0-9]{6}$/.test(ifsc)) {
      showToast('Invalid IFSC format (11 characters, 5th character must be 0).', 'error');
      return false;
    }

    if (!ifsc && !existingSens.ifsc_masked) {
      showToast('Please enter your Bank IFSC code.', 'warning');
      return false;
    }

    if (acc) {
      if (acc.length < 6 || !/^\d+$/.test(acc)) {
        showToast('Bank account number must contain digits only (minimum 6 digits).', 'error');
        return false;
      }
      if (acc !== confAcc) {
        showToast('Bank account numbers do not match.', 'error');
        return false;
      }
    } else if (!existingSens.bank_account_masked) {
      showToast('Please enter your Bank Account Number.', 'warning');
      return false;
    }

    const payload = { bank_name: bank };
    if (pan) payload.pan = pan;
    if (a4) payload.aadhaar_last4 = a4;
    if (ifsc) payload.ifsc = ifsc;
    if (acc) payload.bank_account = acc;
    if (upi) payload.upi_id = upi;

    try {
      const res = await fetch('/api/v1/me/sensitive', {
        method: 'PUT',
        headers: getAuthHeader(),
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        const sData = await res.json();
        wizardState.sensitive = Object.assign({}, wizardState.sensitive, sData);
        return true;
      } else {
        const err = await res.json();
        showToast(err.detail || 'Validation error saving encrypted identity details.', 'error');
        return false;
      }
    } catch (e) {
      showToast('Network error saving identity details.', 'error');
      return false;
    }
  }

  window.submitFinalRegistration = async function () {
    const c1 = document.getElementById('chk_consent_1');
    const c2 = document.getElementById('chk_consent_2');
    const c3 = document.getElementById('chk_consent_3');

    if ((c1 && !c1.checked) || (c2 && !c2.checked) || (c3 && !c3.checked)) {
      showToast('Please accept all three statutory DPDP Act 2023 declarations.', 'warning');
      return;
    }

    const t = getI18n();
    const btn = document.getElementById('btnSubmitProfile');
    if (btn) {
      btn.disabled = true;
      btn.innerText = t.submitting;
    }

    try {
      await fetch('/api/v1/me/consent', {
        method: 'POST',
        headers: getAuthHeader(),
        body: JSON.stringify({
          notice_version: 'v1.0-2026',
          language: getLang(),
          purposes: ['DPDP_PURPOSE_LIMITATION', 'AADHAAR_VOLUNTARY_LAST4', 'TRACEABILITY_PILOT_TERMS']
        })
      });

      const res = await fetch('/api/v1/me/profile/submit', {
        method: 'POST',
        headers: getAuthHeader()
      });

      const data = await res.json();
      if (res.ok) {
        showToast(t.underReviewTitle, 'success');
        wizardState.profile = data.profile;
        updateRegisteredHeaderBanner(wizardState.profile);
        const contentArea = document.getElementById('workspaceDynamicContent');
        if (contentArea) renderUnderReviewCard(contentArea);
      } else {
        if (btn) {
          btn.disabled = false;
          btn.innerText = t.btnSubmit;
        }
        if (data.errors) {
          const firstErr = Object.values(data.errors)[0];
          showToast(firstErr, 'error');
        } else {
          showToast(data.detail || 'Failed to submit application.', 'error');
        }
      }
    } catch (err) {
      if (btn) {
        btn.disabled = false;
        btn.innerText = t.btnSubmit;
      }
      showToast('Network error during submission.', 'error');
    }
  };

  /* --------------------------------------------------------------------------
     PHOTO & DOCUMENT UPLOAD WITH EXIF STRIP & SHA-256
     -------------------------------------------------------------------------- */
  window.handlePhotoUpload = function (input) {
    const file = input.files && input.files[0];
    if (!file) return;

    if (file.size > 5 * 1024 * 1024) {
      showToast('Photo exceeds 5MB size limit.', 'error');
      return;
    }

    const reader = new FileReader();
    reader.onload = function (e) {
      const img = new Image();
      img.onload = function () {
        const canvas = document.createElement('canvas');
        const maxDim = 800;
        let w = img.width;
        let h = img.height;
        if (w > maxDim || h > maxDim) {
          if (w > h) {
            h = Math.round((h * maxDim) / w);
            w = maxDim;
          } else {
            w = Math.round((w * maxDim) / h);
            h = maxDim;
          }
        }
        canvas.width = w;
        canvas.height = h;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, w, h);

        canvas.toBlob(async function (blob) {
          if (!blob) return;
          const previewImg = document.getElementById('farmerPhotoPreview');
          if (previewImg) previewImg.src = canvas.toDataURL('image/jpeg', 0.85);

          const formData = new FormData();
          formData.append('photo', blob, 'farmer_portrait.jpg');

          try {
            const token = localStorage.getItem('annasutra_access_token');
            const phone = localStorage.getItem('annasutra_phone') || '';
            const upHeaders = {};
            if (token) upHeaders['Authorization'] = 'Bearer ' + token;
            if (phone) upHeaders['X-Entity-Phone'] = phone;
            const upRes = await fetch('/api/v1/me/photo', {
              method: 'POST',
              headers: upHeaders,
              body: formData
            });

            if (upRes.ok) {
              const resData = await upRes.json();
              if (!wizardState.profile) wizardState.profile = {};
              wizardState.profile.photo_object_key = resData.photo_object_key;
              const badge = document.getElementById('photoStatusBadge');
              if (badge) badge.style.display = 'inline-block';
              showToast(getI18n().photoScrubbed, 'success');
            } else {
              let errMsg = 'Failed to upload photo.';
              try {
                const errJson = await upRes.json();
                if (errJson && errJson.detail) errMsg = errJson.detail;
              } catch (e) {}
              showToast(errMsg, 'error');
            }
          } catch (err) {
            showToast('Network error uploading photo.', 'error');
          }
        }, 'image/jpeg', 0.85);
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  };

  window.handleDocumentUpload = async function (input) {
    const file = input.files && input.files[0];
    if (!file) return;

    if (file.size > 5 * 1024 * 1024) {
      showToast('Document exceeds 5MB limit.', 'error');
      return;
    }

    const docTypeEl = document.getElementById('inp_doc_type');
    const docType = docTypeEl ? docTypeEl.value : 'LAND_RECORD';

    const formData = new FormData();
    formData.append('document', file);
    formData.append('doc_type', docType);

    try {
      const token = localStorage.getItem('annasutra_access_token');
      const phone = localStorage.getItem('annasutra_phone') || '';
      const docHeaders = {};
      if (token) docHeaders['Authorization'] = 'Bearer ' + token;
      if (phone) docHeaders['X-Entity-Phone'] = phone;
      const res = await fetch('/api/v1/me/documents', {
        method: 'POST',
        headers: docHeaders,
        body: formData
      });
      if (res.ok) {
        const data = await res.json();
        const statusEl = document.getElementById('docUploadStatus');
        const t = getI18n();
        if (statusEl) {
          statusEl.style.display = 'block';
          statusEl.innerHTML = `${getIcon('check', 14, '#059669', 2.8)} ${escapeHtml(file.name)} — ${escapeHtml(t.docUploadedBadge)} (SHA-256: <code>${escapeHtml(data.sha256.slice(0, 16))}...</code>)`;
        }
        showToast(t.docUploadedBadge, 'success');
      } else {
        showToast('Document upload failed.', 'error');
      }
    } catch (e) {
      showToast('Network error uploading document.', 'error');
    }
  };

  /* --------------------------------------------------------------------------
     LEAFLET MAP & TURF.JS PLOT MANAGEMENT
     -------------------------------------------------------------------------- */
  function initPlotMap() {
    const mapDiv = document.getElementById('plotLeafletMap');
    if (!mapDiv) return;
    const t = getI18n();

    if (typeof L === 'undefined') {
      mapDiv.innerHTML = `
        <div style="height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; background: #f1f5f9; color: #475569; padding: 20px; text-align: center;">
          <span style="display:inline-block; margin-bottom: 8px;">${getIcon('map-pin', 32, '#94a3b8')}</span>
          <strong style="font-size: 14px; color: #0b3d2e;">${escapeHtml(t.step2Title)}</strong>
          <p style="font-size: 12px; max-width: 420px; margin: 4px 0 12px;">${escapeHtml(t.plotMapInstructions)}</p>
        </div>
      `;
      return;
    }

    try {
      if (wizardState.leafletMap) {
        try { wizardState.leafletMap.remove(); } catch (err) {}
        wizardState.leafletMap = null;
      }
      if (mapDiv._leaflet_id) {
        delete mapDiv._leaflet_id;
      }

      const defaultLat = 22.9868;
      const defaultLng = 87.8550;

      wizardState.leafletMap = L.map('plotLeafletMap').setView([defaultLat, defaultLng], 13);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap'
      }).addTo(wizardState.leafletMap);

      wizardState.leafletMap.on('click', onMapClick);
      wizardState.leafletAvailable = true;

      renderExistingPlotPolygons();
    } catch (e) {}
  }

  function onMapClick(e) {
    if (!wizardState.leafletMap) return;
    const lat = parseFloat(e.latlng.lat.toFixed(6));
    const lng = parseFloat(e.latlng.lng.toFixed(6));
    wizardState.drawnPoints.push([lng, lat]);
    updateDrawnPolygonLayer();
  }

  function updateDrawnPolygonLayer() {
    if (!wizardState.leafletMap || !window.L) return;
    if (wizardState.polygonLayer) {
      wizardState.leafletMap.removeLayer(wizardState.polygonLayer);
    }

    const latLngs = wizardState.drawnPoints.map(pt => [pt[1], pt[0]]);
    if (latLngs.length > 0) {
      wizardState.polygonLayer = L.polygon(latLngs, {
        color: '#10b981',
        fillColor: '#86efac',
        fillOpacity: 0.45,
        weight: 3
      }).addTo(wizardState.leafletMap);
    }

    calculateAcreageFromPoints();
  }

  function calculateAcreageFromPoints() {
    const t = getI18n();
    const pts = wizardState.drawnPoints;
    const indicator = document.getElementById('liveAcreIndicator');
    const acresInp = document.getElementById('inp_plot_acres');

    if (pts.length < 3) {
      if (indicator) indicator.innerText = `${t.estAreaLabel}: 0.00 ${t.acresUnit}`;
      return;
    }

    let calculatedAcres = 0;
    try {
      if (typeof turf !== 'undefined') {
        const closed = [...pts, pts[0]];
        const poly = turf.polygon([closed]);
        const sqMeters = turf.area(poly);
        calculatedAcres = sqMeters * 0.000247105;
      } else {
        calculatedAcres = (pts.length * 0.75);
      }
    } catch (e) {
      calculatedAcres = 1.00;
    }

    const formatted = calculatedAcres.toFixed(2);
    if (indicator) indicator.innerText = `${t.estAreaLabel}: ${formatted} ${t.acresUnit}`;
    if (acresInp && (!acresInp.value || acresInp.value === '0')) acresInp.value = formatted;
  }

  window.startPolygonDraw = function () {
    showToast(getI18n().plotMapInstructions, 'info');
  };

  window.clearPolygonDraw = function () {
    const t = getI18n();
    wizardState.drawnPoints = [];
    if (wizardState.polygonLayer && wizardState.leafletMap) {
      wizardState.leafletMap.removeLayer(wizardState.polygonLayer);
    }
    const indicator = document.getElementById('liveAcreIndicator');
    if (indicator) indicator.innerText = `${t.estAreaLabel}: 0.00 ${t.acresUnit}`;
  };

  window.geolocatePlot = function () {
    if (!navigator.geolocation) {
      showToast('Geolocation is not supported on this device.', 'warning');
      return;
    }
    navigator.geolocation.getCurrentPosition(
      function (pos) {
        const lat = parseFloat(pos.coords.latitude.toFixed(6));
        const lng = parseFloat(pos.coords.longitude.toFixed(6));
        if (wizardState.leafletMap) {
          wizardState.leafletMap.setView([lat, lng], 16);
        }
        const d = 0.0012;
        wizardState.drawnPoints = [
          [lng - d, lat - d],
          [lng + d, lat - d],
          [lng + d, lat + d],
          [lng - d, lat + d]
        ];
        updateDrawnPolygonLayer();
      },
      function () {
        showToast('Unable to retrieve GPS coordinates. Please click on the map to draw your plot.', 'warning');
      },
      { enableHighAccuracy: true, timeout: 8000 }
    );
  };

  window.addCurrentPlotToList = function () {
    const nameInp = document.getElementById('inp_plot_name');
    const acresInp = document.getElementById('inp_plot_acres');
    const name = nameInp ? nameInp.value.trim() : '';
    const acres = acresInp ? parseFloat(acresInp.value) : 0;

    if (!name) {
      showToast('Please enter a Plot Name or survey reference.', 'warning');
      return;
    }
    if (!acres || acres <= 0) {
      showToast('Plot area must be greater than 0 acres.', 'warning');
      return;
    }

    const pts = wizardState.drawnPoints.length >= 3
      ? [...wizardState.drawnPoints, wizardState.drawnPoints[0]]
      : [[87.852, 23.238], [87.858, 23.238], [87.858, 23.244], [87.852, 23.238]];

    const newPlot = {
      plot_name: name,
      area_acres: acres,
      district: (wizardState.profile && wizardState.profile.district) || '',
      geojson: {
        type: 'Polygon',
        coordinates: [pts]
      }
    };

    if (!wizardState.plots) wizardState.plots = [];
    wizardState.plots.push(newPlot);

    clearPolygonDraw();
    if (nameInp) nameInp.value = '';
    if (acresInp) acresInp.value = '';

    goToStep(2);
  };

  window.removePlot = function (idx) {
    if (wizardState.plots && wizardState.plots[idx]) {
      wizardState.plots.splice(idx, 1);
      goToStep(2);
    }
  };

  function renderExistingPlotPolygons() {
    if (!wizardState.leafletMap || !window.L || !wizardState.plots) return;
    const t = getI18n();
    wizardState.plots.forEach(p => {
      try {
        if (p.geojson && p.geojson.coordinates && p.geojson.coordinates[0]) {
          const latLngs = p.geojson.coordinates[0].map(pt => [pt[1], pt[0]]);
          L.polygon(latLngs, {
            color: '#059669',
            fillColor: '#10b981',
            fillOpacity: 0.35,
            weight: 2
          }).bindPopup(`<b>${escapeHtml(p.plot_name)}</b><br/>${parseFloat(p.area_acres).toFixed(2)} ${escapeHtml(t.acresUnit)}`).addTo(wizardState.leafletMap);
        }
      } catch (e) {}
    });
  }

  /* --------------------------------------------------------------------------
     CROPS & SENSITIVE PREVIEW HELPERS
     -------------------------------------------------------------------------- */
  window.toggleCropSelection = function (cropId, el) {
    if (!wizardState.selectedCrops) wizardState.selectedCrops = [];
    const idx = wizardState.selectedCrops.indexOf(cropId);
    if (idx > -1) {
      wizardState.selectedCrops.splice(idx, 1);
      el.classList.remove('selected');
    } else {
      wizardState.selectedCrops.push(cropId);
      el.classList.add('selected');
    }
  };

  window.handlePanInput = function (input) {
    const t = getI18n();
    input.value = input.value.toUpperCase();
    const clean = input.value.trim();
    const preview = document.getElementById('panMaskPreview');
    if (preview) {
      if (clean.length === 10) {
        preview.innerText = `${t.maskedPreview}: ${clean.slice(0, 2)}******${clean.slice(8)}`;
      } else {
        preview.innerText = `${t.maskedPreview}: AB******5C`;
      }
    }
  };

  window.handleAccountInput = function (input) {
    const t = getI18n();
    const clean = input.value.trim().replace(/\D/g, '');
    const preview = document.getElementById('accountMaskPreview');
    if (preview) {
      if (clean.length >= 6) {
        preview.innerText = `${t.maskedPreview}: ${'X'.repeat(clean.length - 4)}${clean.slice(-4)}`;
      } else {
        preview.innerText = `${t.maskedPreview}: XXXXXXXX1234`;
      }
    }
  };

  window.renderAdminConsoleUI = renderAdminConsoleUI;
  window.renderWizardInterface = renderWizardInterface;
})();

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


  /* --------------------------------------------------------------------------
     PRODUCER HARVEST LOT ANALYTICS & STATISTICAL VISUALIZATION ENGINE
     -------------------------------------------------------------------------- */
  window._analyticsDonutMode = 'weight'; // 'weight' or 'value'

  window.switchProducerConsoleTab = function (tabName) {
    const tabLedgerBtn = document.getElementById('tabBtnLedger');
    const tabCreateMapBtn = document.getElementById('tabBtnCreateMap');
    const tabAnalyticsBtn = document.getElementById('tabBtnAnalytics');
    const contentLedger = document.getElementById('consoleTabContentLedger');
    const contentCreateMap = document.getElementById('consoleTabContentCreateMap');
    const contentAnalytics = document.getElementById('consoleTabContentAnalytics');

    if (!tabLedgerBtn || !tabAnalyticsBtn || !contentLedger || !contentAnalytics) return;

    const resetBtn = btn => {
      if (!btn) return;
      btn.style.color = '#64748b';
      btn.style.borderBottom = '3px solid transparent';
      btn.style.background = 'transparent';
    };
    const activateBtn = btn => {
      if (!btn) return;
      btn.style.color = '#065f46';
      btn.style.borderBottom = '3px solid #047857';
      btn.style.background = '#ecfdf5';
    };

    resetBtn(tabLedgerBtn);
    resetBtn(tabCreateMapBtn);
    resetBtn(tabAnalyticsBtn);

    contentLedger.style.display = 'none';
    if (contentCreateMap) contentCreateMap.style.display = 'none';
    contentAnalytics.style.display = 'none';

    if (tabName === 'create_map') {
      activateBtn(tabCreateMapBtn);
      if (contentCreateMap) contentCreateMap.style.display = 'block';
      window.updateInlineBatchIdPreview();
      setTimeout(() => window.renderFarmerLiveMovementMap(), 60);
    } else if (tabName === 'analytics') {
      activateBtn(tabAnalyticsBtn);
      contentAnalytics.style.display = 'block';
      renderProducerAnalytics();
    } else {
      activateBtn(tabLedgerBtn);
      contentLedger.style.display = 'block';
    }
  };

  window.setAnalyticsDonutMode = function (mode) {
    window._analyticsDonutMode = mode;
    renderProducerAnalytics();
  };

  window.renderProducerAnalytics = function () {
    const root = document.getElementById('producerAnalyticsRoot');
    if (!root) return;
    const t = getI18n();
    const p = wizardState.profile || {};
    const plots = wizardState.plots || [];
    const totalAcres = plots.reduce((acc, pl) => acc + (parseFloat(pl.area_acres) || 0), 0) || parseFloat(p.total_land_acres || 0);
    const cropsListDisplay = (wizardState.selectedCrops || []).map(getCropLabel).join(', ') || 'All Seasonal Crops';
    const farmerUid = p.farmer_uid || localStorage.getItem('annasutra_farmer_uid') || '';

    const providedDataSummaryHtml = `
      <div style="background: #f0fdf4; border: 1.5px solid #86efac; border-radius: 14px; padding: 18px; margin-bottom: 22px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
          <h5 style="margin: 0; font-size: 15px; font-weight: 800; color: #0b3d2e;">All Provided Farmer, Land, Crop &amp; Enterprise Data</h5>
          <button type="button" class="btn-wizard-action btn-wizard-draft" style="padding: 5px 12px; font-size: 11.5px; background: #fff;" onclick="window.openProducerRegistrationWizard()">Edit Registration &amp; Land Data &rarr;</button>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; font-size: 12.5px;">
          <div style="background: #ffffff; border: 1px solid #d1fae5; border-radius: 10px; padding: 10px 12px;">
            <div style="font-size: 11px; color: #64748b; font-weight: 700;">UNIQUE FARMER ID</div>
            <div style="font-family: monospace; font-size: 13px; font-weight: 900; color: #047857; margin-top: 2px;">${escapeHtml(farmerUid || 'Registered')}</div>
          </div>
          <div style="background: #ffffff; border: 1px solid #d1fae5; border-radius: 10px; padding: 10px 12px;">
            <div style="font-size: 11px; color: #64748b; font-weight: 700;">LANDS &amp; MAPPED PLOTS</div>
            <div style="font-size: 14px; font-weight: 800; color: #0f172a; margin-top: 2px;">${totalAcres.toFixed(2)} Acres (${plots.length} Plots)</div>
          </div>
          <div style="background: #ffffff; border: 1px solid #d1fae5; border-radius: 10px; padding: 10px 12px;">
            <div style="font-size: 11px; color: #64748b; font-weight: 700;">CROPS PRODUCED</div>
            <div style="font-size: 13px; font-weight: 800; color: #0f172a; margin-top: 2px;">${escapeHtml(cropsListDisplay)}</div>
          </div>
          <div style="background: #ffffff; border: 1px solid #d1fae5; border-radius: 10px; padding: 10px 12px;">
            <div style="font-size: 11px; color: #64748b; font-weight: 700;">FARM LOCATION &amp; IRRIGATION</div>
            <div style="font-size: 13px; font-weight: 800; color: #0f172a; margin-top: 2px;">${escapeHtml([p.village_town, p.district, getStateLabel(p.state)].filter(Boolean).join(', ') || 'Registered Node')} • ${escapeHtml((p.role_details && p.role_details.irrigation) || 'Standard')}</div>
          </div>
        </div>
      </div>
    `;

    const lots = window._producerLots || [];
    if (!lots || lots.length === 0) {
      root.innerHTML = providedDataSummaryHtml + `
        <div style="background: #f8fafc; border: 1.5px dashed #cbd5e1; border-radius: 16px; padding: 48px 24px; text-align: center;">
          <div style="width: 56px; height: 56px; background: #ecfdf5; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px;">
            ${getIcon('sprout', 28, '#047857')}
          </div>
          <h4 style="margin: 0 0 8px; font-size: 18px; font-weight: 800; color: #0f172a;">${escapeHtml(t.noAnalyticsLots || 'No harvest lots recorded yet.')}</h4>
          <p style="margin: 0 auto 20px; font-size: 13.5px; color: #64748b; max-width: 440px;">
            Register your harvest batches to automatically generate yield distribution charts, monthly harvest cadence trends, and commercial cashflow graphs.
          </p>
          <button type="button" class="btn-wizard-action btn-wizard-submit" style="padding: 10px 22px; font-weight: 800;" onclick="switchProducerConsoleTab('create_map');">
            + ${escapeHtml(t.btnRegisterLot || 'Register New Harvest Lot')}
          </button>
        </div>
      `;
      return;
    }

    // 1. KPI Statistics Computations
    let totalWeight = 0;
    let totalValuation = 0;
    let realizedRevenue = 0;
    let gradeACount = 0;
    let inCustodyCount = 0;
    let inCustodyWeight = 0;
    let inTransitCount = 0;
    let deliveredCount = 0;
    let closedCount = 0;

    const cropMap = {}; // { cropName: { weight, value, count } }
    const paymentMap = { FULLY_PAID: 0, ADVANCE_PAID: 0, ESCROW_LOCKED: 0, UNPAID: 0 };
    const timelineMap = {}; // { dateKey: weight }

    lots.forEach(lot => {
      const wt = parseFloat(lot.net_qty_kg || lot.on_hand_kg || 0) || 0;
      const val = parseFloat(lot.estimated_value || 0) || 0;
      totalWeight += wt;
      totalValuation += val;

      // Grade A ratio
      const gr = (lot.quality_grade || lot.grade || '').toUpperCase();
      if (gr === 'GRADE_A' || gr.includes('A')) gradeACount++;

      // Custody state
      const st = (lot.state || 'IN_CUSTODY').toUpperCase();
      if (st === 'IN_CUSTODY' || st === 'CREATED') {
        inCustodyCount++;
        inCustodyWeight += wt;
      } else if (st === 'IN_TRANSIT') {
        inTransitCount++;
      } else if (st === 'DELIVERED') {
        deliveredCount++;
      } else if (st === 'CLOSED' || st === 'TRANSFERRED') {
        closedCount++;
      }

      // Payment Settlement
      const pay = (lot.payment_status || 'UNPAID').toUpperCase();
      if (pay === 'SETTLED' || pay === 'FULLY_PAID') {
        realizedRevenue += val;
        paymentMap.FULLY_PAID += val;
      } else if (pay === 'ADVANCE' || pay === 'ADVANCE_PAID') {
        realizedRevenue += (val * 0.5);
        paymentMap.ADVANCE_PAID += val;
      } else if (pay === 'ESCROW_LOCKED') {
        paymentMap.ESCROW_LOCKED += val;
      } else {
        paymentMap.UNPAID += val;
      }

      // Crop aggregation
      const cropName = lot.crop || 'Produce';
      if (!cropMap[cropName]) cropMap[cropName] = { weight: 0, value: 0, count: 0 };
      cropMap[cropName].weight += wt;
      cropMap[cropName].value += val;
      cropMap[cropName].count += 1;

      // Timeline aggregation
      const d = (lot.harvest_date || lot.created_at || '').substring(0, 10);
      if (d) {
        timelineMap[d] = (timelineMap[d] || 0) + wt;
      }
    });

    const gradeAPct = lots.length > 0 ? ((gradeACount / lots.length) * 100).toFixed(1) : 0;
    const avgPricePerKg = totalWeight > 0 ? (totalValuation / totalWeight).toFixed(1) : 0;

    // Palette for charts
    const PALETTE = ['#047857', '#10b981', '#f59e0b', '#3b82f6', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'];

    // 2. Prepare Donut Slices
    const isWeightMode = window._analyticsDonutMode === 'weight';
    const donutSlices = Object.keys(cropMap).map((k, idx) => ({
      label: getCropLabel(k),
      value: isWeightMode ? cropMap[k].weight : cropMap[k].value,
      color: PALETTE[idx % PALETTE.length],
      rawCrop: k
    })).sort((a, b) => b.value - a.value);

    const donutSvg = generateSvgDonut(donutSlices, isWeightMode ? totalWeight : totalValuation, isWeightMode ? 'Kg' : '₹');

    // 3. Prepare Timeline Points
    const sortedDates = Object.keys(timelineMap).sort();
    const timelinePoints = sortedDates.slice(-7).map(d => {
      const parts = d.split('-');
      const label = parts.length === 3 ? `${parts[2]}/${parts[1]}` : d;
      return { date: d, label: label, qty: timelineMap[d] };
    });
    const timelineSvg = generateSvgTimeline(timelinePoints);

    // 4. Custody Stages
    const custodyStages = [
      { name: 'In Farm Custody', count: inCustodyCount, color: '#10b981', weight: inCustodyWeight, pct: totalWeight > 0 ? ((inCustodyWeight / totalWeight) * 100).toFixed(1) : 0 },
      { name: 'In Transit (Locked)', count: inTransitCount, color: '#f59e0b', weight: 0, pct: lots.length > 0 ? ((inTransitCount / lots.length) * 100).toFixed(1) : 0 },
      { name: 'Delivered to Mandi / Hub', count: deliveredCount, color: '#3b82f6', weight: 0, pct: lots.length > 0 ? ((deliveredCount / lots.length) * 100).toFixed(1) : 0 },
      { name: 'Transferred / Custody Closed', count: closedCount, color: '#64748b', weight: 0, pct: lots.length > 0 ? ((closedCount / lots.length) * 100).toFixed(1) : 0 }
    ];

    root.innerHTML = providedDataSummaryHtml + `
      <!-- 6 High-Impact Stat Tiles -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 24px;">
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 14px; border-radius: 12px;">
          <div style="font-size: 11.5px; color: #64748b; font-weight: 700; text-transform: uppercase;">Total Harvest Volume</div>
          <div style="font-size: 22px; font-weight: 900; color: #0b3d2e; margin: 4px 0;">${totalWeight.toLocaleString('en-IN', { maximumFractionDigits: 1 })} Kg</div>
          <div style="font-size: 11px; color: #059669; font-weight: 600;">${(totalWeight / 100).toFixed(1)} Quintals recorded</div>
        </div>

        <div style="background: #ecfdf5; border: 1.5px solid #a7f3d0; padding: 14px; border-radius: 12px;">
          <div style="font-size: 11.5px; color: #065f46; font-weight: 700; text-transform: uppercase;">Gross Crop Valuation</div>
          <div style="font-size: 22px; font-weight: 900; color: #047857; margin: 4px 0;">₹ ${totalValuation.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</div>
          <div style="font-size: 11px; color: #047857; font-weight: 600;">Across ${lots.length} harvest lots</div>
        </div>

        <div style="background: #f0fdf4; border: 1px solid #bbf7d0; padding: 14px; border-radius: 12px;">
          <div style="font-size: 11.5px; color: #166534; font-weight: 700; text-transform: uppercase;">Realized Revenue</div>
          <div style="font-size: 22px; font-weight: 900; color: #15803d; margin: 4px 0;">₹ ${realizedRevenue.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</div>
          <div style="font-size: 11px; color: #16a34a; font-weight: 600;">Settled & Advance funds</div>
        </div>

        <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 14px; border-radius: 12px;">
          <div style="font-size: 11.5px; color: #64748b; font-weight: 700; text-transform: uppercase;">Grade A Quality Ratio</div>
          <div style="font-size: 22px; font-weight: 900; color: #0b3d2e; margin: 4px 0;">${gradeAPct}%</div>
          <div style="font-size: 11px; color: #059669; font-weight: 600;">${gradeACount} of ${lots.length} Grade A lots</div>
        </div>

        <div style="background: #fffbeb; border: 1.5px solid #fde68a; padding: 14px; border-radius: 12px;">
          <div style="font-size: 11.5px; color: #92400e; font-weight: 700; text-transform: uppercase;">Active Farm Custody</div>
          <div style="font-size: 22px; font-weight: 900; color: #b45309; margin: 4px 0;">${inCustodyCount} Lots</div>
          <div style="font-size: 11px; color: #d97706; font-weight: 600;">${inCustodyWeight.toLocaleString('en-IN', { maximumFractionDigits: 0 })} Kg on farm</div>
        </div>

        <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 14px; border-radius: 12px;">
          <div style="font-size: 11.5px; color: #64748b; font-weight: 700; text-transform: uppercase;">Avg Realized Base Price</div>
          <div style="font-size: 22px; font-weight: 900; color: #0b3d2e; margin: 4px 0;">₹ ${avgPricePerKg} / Kg</div>
          <div style="font-size: 11px; color: #64748b; font-weight: 600;">Weighted average price</div>
        </div>
      </div>

      <!-- 4-Chart Grid (2x2) -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap: 18px;">
        <!-- GRAPH 1: Crop Volume & Valuation Share -->
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 8px;">
            <div>
              <h5 style="margin: 0; font-size: 15px; font-weight: 800; color: #0f172a;">${escapeHtml(t.chartCropShare || 'Crop Volume & Valuation Share')}</h5>
              <div style="font-size: 12px; color: #64748b;">Distribution of produce yield and valuation across crops</div>
            </div>
            <div style="display: flex; gap: 4px; background: #f1f5f9; padding: 3px; border-radius: 8px;">
              <button type="button" onclick="setAnalyticsDonutMode('weight')" style="border: none; padding: 4px 10px; font-size: 11.5px; font-weight: 700; border-radius: 6px; cursor: pointer; ${isWeightMode ? 'background: #ffffff; color: #047857; box-shadow: 0 1px 3px rgba(0,0,0,0.1);' : 'background: transparent; color: #64748b;'}">
                ${escapeHtml(t.btnToggleWeight || 'Weight (Kg)')}
              </button>
              <button type="button" onclick="setAnalyticsDonutMode('value')" style="border: none; padding: 4px 10px; font-size: 11.5px; font-weight: 700; border-radius: 6px; cursor: pointer; ${!isWeightMode ? 'background: #ffffff; color: #047857; box-shadow: 0 1px 3px rgba(0,0,0,0.1);' : 'background: transparent; color: #64748b;'}">
                ${escapeHtml(t.btnToggleValue || 'Value (₹)')}
              </button>
            </div>
          </div>
          
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; align-items: center;">
            <div>${donutSvg}</div>
            <div style="display: flex; flex-direction: column; gap: 8px; max-height: 240px; overflow-y: auto; padding-right: 4px;">
              ${donutSlices.map(s => `
                <div style="display: flex; align-items: center; justify-content: space-between; font-size: 12px; padding: 6px 8px; background: #f8fafc; border-radius: 6px;">
                  <span style="display: flex; align-items: center; gap: 6px; font-weight: 700; color: #334155;">
                    <span style="width: 10px; height: 10px; border-radius: 50%; background: ${s.color}; display: inline-block;"></span>
                    <span>${escapeHtml(s.label)}</span>
                  </span>
                  <span style="font-weight: 800; color: #0f172a;">${s.value.toLocaleString('en-IN', { maximumFractionDigits: 1 })} ${isWeightMode ? 'Kg' : '₹'}</span>
                </div>
              `).join('')}
            </div>
          </div>
        </div>

        <!-- GRAPH 2: Monthly Harvest Cadence Timeline -->
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
          <div style="margin-bottom: 16px;">
            <h5 style="margin: 0; font-size: 15px; font-weight: 800; color: #0f172a;">${escapeHtml(t.chartYieldTimeline || 'Harvest Yield Cadence Timeline')}</h5>
            <div style="font-size: 12px; color: #64748b;">Chronological harvest batches logged on sovereign chain</div>
          </div>
          <div>${timelineSvg}</div>
        </div>

        <!-- GRAPH 3: Custody Logistics & Sales Pipeline Flow -->
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
          <div style="margin-bottom: 16px;">
            <h5 style="margin: 0; font-size: 15px; font-weight: 800; color: #0f172a;">${escapeHtml(t.chartCustodyPipeline || 'Custody & Logistics Pipeline Flow')}</h5>
            <div style="font-size: 12px; color: #64748b;">Supply-chain transit velocity from farm genesis to mandi/retail</div>
          </div>

          <div style="display: flex; flex-direction: column; gap: 14px;">
            ${custodyStages.map(st => `
              <div>
                <div style="display: flex; justify-content: space-between; font-size: 12px; font-weight: 700; margin-bottom: 4px;">
                  <span style="color: #334155;">${escapeHtml(st.name)}</span>
                  <span style="color: #0f172a;">${st.count} Lots (${st.pct}%)</span>
                </div>
                <div style="height: 10px; background: #f1f5f9; border-radius: 6px; overflow: hidden;">
                  <div style="height: 100%; width: ${Math.max(2, st.pct)}%; background: ${st.color}; border-radius: 6px; transition: width 0.5s ease;"></div>
                </div>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- GRAPH 4: Commercial Payment & Settlement Health -->
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
          <div style="margin-bottom: 16px;">
            <h5 style="margin: 0; font-size: 15px; font-weight: 800; color: #0f172a;">${escapeHtml(t.chartPaymentHealth || 'Commercial Payment & Settlement Health')}</h5>
            <div style="font-size: 12px; color: #64748b;">Farmer trade settlement breakdown and outstanding escrow telemetry</div>
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px;">
            <div style="background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 10px; padding: 12px;">
              <div style="font-size: 11px; font-weight: 700; color: #065f46; text-transform: uppercase;">Fully Settled</div>
              <div style="font-size: 18px; font-weight: 900; color: #047857; margin-top: 2px;">₹ ${paymentMap.FULLY_PAID.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</div>
            </div>
            <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 10px; padding: 12px;">
              <div style="font-size: 11px; font-weight: 700; color: #166534; text-transform: uppercase;">Advance Received</div>
              <div style="font-size: 18px; font-weight: 900; color: #16a34a; margin-top: 2px;">₹ ${paymentMap.ADVANCE_PAID.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</div>
            </div>
            <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 10px; padding: 12px;">
              <div style="font-size: 11px; font-weight: 700; color: #92400e; text-transform: uppercase;">Escrow Locked</div>
              <div style="font-size: 18px; font-weight: 900; color: #b45309; margin-top: 2px;">₹ ${paymentMap.ESCROW_LOCKED.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</div>
            </div>
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px;">
              <div style="font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase;">Pending Settlement</div>
              <div style="font-size: 18px; font-weight: 900; color: #dc2626; margin-top: 2px;">₹ ${paymentMap.UNPAID.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</div>
            </div>
          </div>

          <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px; font-size: 12px; color: #475569; display: flex; justify-content: space-between; align-items: center;">
            <span>Payment Assurance Rate:</span>
            <strong style="color: #047857;">${totalValuation > 0 ? (((paymentMap.FULLY_PAID + paymentMap.ADVANCE_PAID) / totalValuation) * 100).toFixed(1) : 100}% guaranteed</strong>
          </div>
        </div>
      </div>
    `;
  };

  // Helper: SVG Donut Generator
  function generateSvgDonut(slices, totalNum, unitLabel) {
    const cx = 110, cy = 110, rOuter = 95, rInner = 60;
    const total = slices.reduce((acc, s) => acc + s.value, 0) || 1;
    let currentAngle = -90.0;
    const paths = [];

    slices.forEach(s => {
      if (s.value <= 0) return;
      let sliceAngle = (s.value / total) * 360.0;
      if (sliceAngle >= 359.9) sliceAngle = 359.9;

      const startRad = (currentAngle * Math.PI) / 180.0;
      const endRad = ((currentAngle + sliceAngle) * Math.PI) / 180.0;

      const x1Out = cx + rOuter * Math.cos(startRad);
      const y1Out = cy + rOuter * Math.sin(startRad);
      const x2Out = cx + rOuter * Math.cos(endRad);
      const y2Out = cy + rOuter * Math.sin(endRad);

      const x1In = cx + rInner * Math.cos(endRad);
      const y1In = cy + rInner * Math.sin(endRad);
      const x2In = cx + rInner * Math.cos(startRad);
      const y2In = cy + rInner * Math.sin(startRad);

      const largeArc = sliceAngle > 180 ? 1 : 0;
      const d = `M ${x1Out.toFixed(1)} ${y1Out.toFixed(1)} A ${rOuter} ${rOuter} 0 ${largeArc} 1 ${x2Out.toFixed(1)} ${y2Out.toFixed(1)} L ${x1In.toFixed(1)} ${y1In.toFixed(1)} A ${rInner} ${rInner} 0 ${largeArc} 0 ${x2In.toFixed(1)} ${y2In.toFixed(1)} Z`;
      const pct = ((s.value / total) * 100).toFixed(1);
      const tooltip = `${s.label}: ${s.value.toLocaleString('en-IN', { maximumFractionDigits: 1 })} ${unitLabel} (${pct}%)`;

      paths.push(`<path d="${d}" fill="${s.color}" stroke="#ffffff" stroke-width="2.5"><title>${escapeHtml(tooltip)}</title></path>`);
      currentAngle += sliceAngle;
    });

    return `
      <svg viewBox="0 0 220 220" width="100%" height="220" style="overflow: visible; display: block; margin: 0 auto;">
        ${paths.join('')}
        <circle cx="${cx}" cy="${cy}" r="${rInner - 2}" fill="#ffffff"/>
        <text x="${cx}" y="${cy - 4}" font-size="17" font-weight="900" fill="#0b3d2e" text-anchor="middle">${totalNum.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</text>
        <text x="${cx}" y="${cy + 14}" font-size="11" font-weight="700" fill="#64748b" text-anchor="middle">${unitLabel}</text>
      </svg>
    `;
  }

  // Helper: SVG Timeline Generator
  function generateSvgTimeline(dataPoints) {
    const w = 440, h = 190;
    const padL = 40, padR = 20, padT = 20, padB = 30;
    const pw = w - padL - padR;
    const ph = h - padT - padB;

    if (!dataPoints || dataPoints.length === 0) {
      return `<svg viewBox="0 0 ${w} ${h}" width="100%" height="${h}"><text x="${w / 2}" y="${h / 2}" fill="#94a3b8" font-size="12" text-anchor="middle">No harvest date timeline available</text></svg>`;
    }

    const maxVal = Math.max(...dataPoints.map(p => p.qty), 1);
    const maxY = maxVal * 1.25;
    const n = dataPoints.length;

    const coords = dataPoints.map((p, idx) => {
      const x = padL + (n > 1 ? (idx / (n - 1)) * pw : pw / 2);
      const y = padT + ph - (p.qty / maxY) * ph;
      return { x, y, p };
    });

    const lineParts = [`M ${coords[0].x.toFixed(1)} ${coords[0].y.toFixed(1)}`];
    for (let i = 1; i < coords.length; i++) {
      const prev = coords[i - 1];
      const curr = coords[i];
      const cx1 = prev.x + (curr.x - prev.x) / 2;
      const cx2 = cx1;
      lineParts.push(`C ${cx1.toFixed(1)} ${prev.y.toFixed(1)}, ${cx2.toFixed(1)} ${curr.y.toFixed(1)}, ${curr.x.toFixed(1)} ${curr.y.toFixed(1)}`);
    }
    const lineD = lineParts.join(' ');
    const areaD = `${lineD} L ${coords[coords.length - 1].x.toFixed(1)} ${padT + ph} L ${coords[0].x.toFixed(1)} ${padT + ph} Z`;

    const gridLines = [];
    for (let s = 0; s < 4; s++) {
      const gy = padT + (s / 3) * ph;
      const gval = maxY * (1 - s / 3);
      gridLines.push(`<line x1="${padL}" y1="${gy.toFixed(1)}" x2="${w - padR}" y2="${gy.toFixed(1)}" stroke="#f1f5f9" stroke-width="1" stroke-dasharray="3,3"/>`);
      gridLines.push(`<text x="${padL - 6}" y="${gy + 3.5}" font-size="9" fill="#94a3b8" text-anchor="end">${gval.toFixed(0)}</text>`);
    }

    const markers = coords.map(c => `
      <circle cx="${c.x.toFixed(1)}" cy="${c.y.toFixed(1)}" r="4.5" fill="#ffffff" stroke="#047857" stroke-width="2.5">
        <title>${c.p.label}: ${c.p.qty.toFixed(1)} Kg</title>
      </circle>
      <text x="${c.x.toFixed(1)}" y="${padT + ph + 16}" font-size="9.5" font-weight="600" fill="#64748b" text-anchor="middle">${c.p.label}</text>
    `);

    return `
      <svg viewBox="0 0 ${w} ${h}" width="100%" height="${h}" style="overflow: visible;">
        <defs>
          <linearGradient id="yieldAreaGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#047857" stop-opacity="0.32"/>
            <stop offset="100%" stop-color="#10b981" stop-opacity="0.02"/>
          </linearGradient>
        </defs>
        ${gridLines.join('')}
        <path d="${areaD}" fill="url(#yieldAreaGrad)"/>
        <path d="${lineD}" fill="none" stroke="#047857" stroke-width="2.8" stroke-linecap="round"/>
        ${markers.join('')}
      </svg>
    `;
  }
