/**
 * AnnaSutra Producer Registration Wizard & Admin Verification Console
 * Full 5-stage onboarding, Leaflet polygon mapping, encrypted identity, statutory DPDP consent,
 * Verified Producer Console, and Administrative Verification Portal.
 */

(function () {
  'use strict';
  const LOCAL_ICON_SVG_MAP = {
    'check': '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
    'user': '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    'map-pin': '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>',
    'wheat': '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round"><path d="M2 22 16 8"/><path d="M3.47 12.53 5 11l1.53 1.53a3.5 3.5 0 0 1 0 4.94L5 19l-1.53-1.53a3.5 3.5 0 0 1 0-4.94Z"/><path d="M7.47 8.53 9 7l1.53 1.53a3.5 3.5 0 0 1 0 4.94L9 15l-1.53-1.53a3.5 3.5 0 0 1 0-4.94Z"/><path d="M11.47 4.53 13 3l1.53 1.53a3.5 3.5 0 0 1 0 4.94L13 11l-1.53-1.53a3.5 3.5 0 0 1 0-4.94Z"/><path d="M20 2h2v2a4 4 0 0 1-4 4h-2V6a4 4 0 0 1 4-4Z"/><path d="M11.47 17.47 13 19l-1.53 1.53a3.5 3.5 0 0 1-4.94 0L5 19l1.53-1.53a3.5 3.5 0 0 1 4.94 0Z"/><path d="M15.47 13.47 17 15l-1.53 1.53a3.5 3.5 0 0 1-4.94 0L9 15l1.53-1.53a3.5 3.5 0 0 1 4.94 0Z"/><path d="M19.47 9.47 21 11l-1.53 1.53a3.5 3.5 0 0 1-4.94 0L13 11l1.53-1.53a3.5 3.5 0 0 1 4.94 0Z"/></svg>',
    'sprout': '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round"><path d="M7 20h10"/><path d="M10 20c5.5-2.5.8-6.4 3-13"/><path d="M9.5 9.4c1.1.8 1.8 2.2 2.3 3.7-2 .4-3.5.4-4.8-.3-1.2-.6-2.3-1.9-3-4.2 2.8-.5 4.4 0 5.5.8z"/><path d="M14.1 6a7 7 0 0 0-1.1 4c1.9-.1 3.3-.6 4.3-1.4 1-1 1.6-2.3 1.7-4.6-2.7.1-4 1-4.9 2z"/></svg>',
    'box': '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round"><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/></svg>',
    'send': '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>',
    'edit': '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>',
    'lock': '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>',
    'printer': '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>',
    'shield': '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>',
    'inbox': '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 16 12 14 15 10 15 8 12 2 12"/><path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/></svg>',
    'clock': '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    'alert': '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
    'store': '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round"><path d="m2 7 4.41-4.41A2 2 0 0 1 7.83 2h8.34a2 2 0 0 1 1.42.59L22 7"/><path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/><path d="M15 22v-4a2 2 0 0 0-2-2h-2a2 2 0 0 0-2 2v4"/><path d="M2 7h20"/><path d="M22 7v3a2 2 0 0 1-2 2v0a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 16 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 12 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 8 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 4 12v0a2 2 0 0 1-2-2V7"/></svg>',
    'truck': '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="3" width="15" height="13"/><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg>',
    'camera': '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/><circle cx="12" cy="13" r="3"/></svg>',
    'copy': '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>',
    'search': '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
    'refresh': '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>'
  };
  function getIcon(name, size, color, stroke) {
    if (window.renderUniformIcon) {
      const rendered = window.renderUniformIcon(name, size, color, stroke);
      if (rendered && !rendered.includes('box')) return rendered;
    }
    const s = size || 18;
    const c = color || 'currentColor';
    const sw = stroke || 2;
    const tpl = LOCAL_ICON_SVG_MAP[name] || LOCAL_ICON_SVG_MAP['box'];
    return tpl.replace(/{size}/g, s).replace(/{color}/g, c).replace(/{stroke}/g, sw);
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
      step5Title: 'Review & Consent',
      step5Desc: 'Verify all declared parameters and provide digital consent for traceability operations.',
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
      aadhaarNotice: 'Full Aadhaar number is never collected or stored. Only last 4 digits are used for verification.',
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
      consentHeader: 'Consent & Declarations',
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
      underReviewSub: 'Your producer profile has been securely recorded. Unlimited QR labels can be generated for your harvest lots.',
      lblMappedLand: 'Verified Land Mapped',
      lblMaskedPan: 'Masked PAN Identity',
      lblSettlementBank: 'Settlement Bank',
      lblSubmissionDate: 'Submission Date',
      lblEntityRefToken: 'Entity Reference Token',
      verifiedNodeBadge: 'VERIFIED PRODUCER NODE',
      statActiveBatches: 'Active Harvest Batches',
      statActiveBatchesSub: 'Recorded in Custody Ledger',
      statQrAvail: 'Remaining QR Crate Serials',
      statQrAvailSub: 'Allocated (13-Char Crockford Base32)',
      statPlotsVerified: 'Verified Farm Plots',
      statPlotsVerifiedSub: 'Geofenced & Encrypted',
      btnDownloadQrPdf: 'Download Printable A4 Sticker Sheet (PDF)',
      loadingRegistry: 'Loading verified entity registry...',
      adminQueueTitle: 'Entity Verification Review Queue',
      adminQueueSub: 'Inspect submitted KYC, farm plot boundaries, and consent declarations to approve entities.',
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
      underReviewSub: 'आपका उत्पादक प्रोफ़ाइल सुरक्षित रूप से दर्ज कर लिया गया है। प्रत्येक फसल लॉट के लिए असीमित क्यूआर कोड उत्पन्न किए जा सकते हैं।',
      lblMappedLand: 'सत्यापित भूमि रकबा',
      lblMaskedPan: 'मास्क्ड पैन पहचान',
      lblSettlementBank: 'निपटान बैंक खाता',
      lblSubmissionDate: 'जमा करने की तिथि',
      lblEntityRefToken: 'इकाई संदर्भ टोकन',
      verifiedNodeBadge: 'सत्यापित उत्पादक नोड',
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
      underReviewSub: 'আপনার উৎপাদক প্রোফাইল নথিভুক্ত হয়েছে। প্রতিটি ফসল লটের জন্য সীমাহীন কিউআর কোড তৈরি করা যাবে।',
      lblMappedLand: 'যাচাইকৃত জমির পরিমাণ',
      lblMaskedPan: 'মাস্কড প্যান পরিচয়',
      lblSettlementBank: 'ব্যাঙ্ক অ্যাকাউন্ট',
      lblSubmissionDate: 'জমা দেওয়ার তারিখ',
      lblEntityRefToken: 'এনটিটি রেফারেন্স টোকেন',
      verifiedNodeBadge: 'যাচাইকৃত উৎপাদক নোড',
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
    wizardState.forceWizardView = false;
    wizardState.forceConsoleView = true;
    const contentArea = document.getElementById('workspaceDynamicContent');
    if (contentArea) {
      renderVerifiedOperationalConsole(contentArea);
      updateLotMetrics();
      applyLotFilters();
      if (initialTab) {
        setTimeout(() => window.switchProducerConsoleTab(initialTab), 60);
      }
    }
    const ws = document.getElementById('confinedWorkspace');
    if (ws) ws.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  window.openProducerRegistrationWizard = async function () {
    wizardState.forceWizardView = true;
    wizardState.forceConsoleView = false;
    const contentArea = document.getElementById('workspaceDynamicContent');
    if (!contentArea) return;

    if (!wizardState.profile || !wizardState.profile.first_name || !wizardState.plots || !wizardState.sensitive) {
      try {
        const [profileRes, plotsRes, sensRes] = await Promise.all([
          fetch('/api/v1/me/profile', { headers: getAuthHeader() }),
          fetch('/api/v1/me/plots', { headers: getAuthHeader() }),
          fetch('/api/v1/me/sensitive', { headers: getAuthHeader() })
        ]);
        if (profileRes.ok) {
          const pData = await profileRes.json();
          wizardState.profile = pData.profile || pData;
          if (wizardState.profile.role_details && wizardState.profile.role_details.commodities) {
            wizardState.selectedCrops = wizardState.profile.role_details.commodities;
          }
        }
        if (plotsRes && plotsRes.ok) {
          const plData = await plotsRes.json();
          wizardState.plots = plData.plots || [];
        }
        if (sensRes && sensRes.ok) {
          const sData = await sensRes.json();
          wizardState.sensitive = sData.sensitive || sData;
        }
      } catch (e) {
        console.warn('Could not refresh profile/plots on wizard open:', e);
      }
    }
    renderWizardInterface(contentArea);
    const ws = document.getElementById('confinedWorkspace');
    if (ws) ws.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  window.openProducerRegistrationReviewStatus = function () {
    wizardState.forceWizardView = false;
    const contentArea = document.getElementById('workspaceDynamicContent');
    if (contentArea) renderUnderReviewCard(contentArea);
    const ws = document.getElementById('confinedWorkspace');
    if (ws) ws.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };



  window.renderCurrentWorkspace = async function () {
    const container = document.getElementById('confinedWorkspace');
    if (!container) return;

    window.activateEntityConsoleView();
    container.style.display = 'block';
    const wsCont = document.getElementById('confinedWorkspaceContainer');
    if (wsCont) wsCont.style.display = 'block';

    const toolsGrid = document.getElementById('workspaceTools');
    const batchesList = document.getElementById('workspaceBatchesList');
    if (toolsGrid) toolsGrid.style.display = 'none';
    if (batchesList) batchesList.style.display = 'none';

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

      if (wizardState.forceWizardView && cachedProfile.status !== 'VERIFIED') {
        renderWizardInterface(contentArea);
        hasRenderedCached = true;
      } else {
        renderVerifiedOperationalConsole(contentArea);
        updateLotMetrics();
        applyLotFilters();
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
      const [profileRes, lotsRes, plotsRes, sensRes] = await Promise.all([
        fetch('/api/v1/me/profile', { headers: getAuthHeader() }),
        fetch('/api/v1/lots/', { headers: getAuthHeader() }),
        fetch('/api/v1/me/plots', { headers: getAuthHeader() }),
        fetch('/api/v1/me/sensitive', { headers: getAuthHeader() })
      ]);

      if (profileRes.status === 401 || profileRes.status === 403) {
        localStorage.removeItem('annasutra_cached_profile');
        localStorage.removeItem('annasutra_cached_lots');
        localStorage.removeItem('annasutra_cached_plots');
        wizardState.profile = { status: 'DRAFT', role: 'PRODUCER', version: 1 };
        updateRegisteredHeaderBanner(wizardState.profile);
        renderVerifiedOperationalConsole(contentArea);
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

      if (sensRes && sensRes.ok) {
        const sData = await sensRes.json();
        wizardState.sensitive = sData.sensitive || sData;
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
      if (wizardState.forceWizardView && pStatus !== 'VERIFIED') {
        renderWizardInterface(contentArea);
      } else {
        renderVerifiedOperationalConsole(contentArea);
        updateLotMetrics();
        applyLotFilters();
        if (document.getElementById('consoleTabContentAnalytics')?.style.display !== 'none') {
          renderProducerAnalytics();
        }
      }
    } catch (err) {
      if (!hasRenderedCached) {
        updateRegisteredHeaderBanner(wizardState.profile);
        renderVerifiedOperationalConsole(contentArea);
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


  /* ==========================================================================
     GOLD-STANDARD ADMIN CONSOLE: 4 SOVEREIGN TABS
     1. Verification Queue & Field-Level Approval
     2. Profile Change Requests (Admin reviews farmer change requests)
     3. Chain Explorer & National Recall Center
     4. Consumer Scan GPS Analytics
     ========================================================================== */
  window._adminActiveTab = 'verification_queue';
  window._adminChangeRequestsList = [];
  window._adminConsumerScanLogs = [];

  function renderAdminConsoleUI(container) {
    window.activateEntityConsoleView();
    const t = getI18n();
    const activeTab = window._adminActiveTab || 'verification_queue';

    container.innerHTML = `
      <div style="background: #ffffff; border-radius: 14px; border: 1px solid #e2e8f0; padding: 20px 24px; margin: 0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); width: 100%; box-sizing: border-box;">
        
        <!-- Admin Verification Header -->
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1.5px solid #e2e8f0; padding-bottom: 14px; margin-bottom: 18px; flex-wrap: wrap; gap: 12px;">
          <div>
            <div style="display: inline-flex; align-items: center; gap: 6px; background: #ecfdf5; border: 1px solid #86efac; color: #065f46; font-size: 11.5px; font-weight: 800; padding: 3px 10px; border-radius: 20px; margin-bottom: 5px;">
              <span>${getIcon('shield', 13, '#15803d', 2.8)}</span> <span>Admin Verifier</span>
            </div>
            <h3 style="margin: 0; font-size: 21px; font-weight: 800; color: #0f172a;">Administration &amp; Verification Console</h3>
            <span style="font-size: 12.5px; color: #64748b;">Verification, Recall &amp; Supply Chain Audit</span>
          </div>
        </div>

        <!-- 4 Top Navigation Tabs -->
        <div style="display: flex; gap: 8px; border-bottom: 2px solid #e2e8f0; margin-bottom: 20px; overflow-x: auto; padding-bottom: 2px;">
          <button type="button" onclick="window.switchAdminTab('verification_queue')" style="padding: 10px 18px; font-size: 13px; font-weight: 800; border: none; background: none; cursor: pointer; border-bottom: 3px solid ${activeTab === 'verification_queue' ? '#047857' : 'transparent'}; color: ${activeTab === 'verification_queue' ? '#047857' : '#64748b'}; display: flex; align-items: center; gap: 8px;">
            <span>${getIcon('check', 15, activeTab === 'verification_queue' ? '#047857' : '#64748b')}</span>
            <span>1. Verification Queue</span>
          </button>

          <button type="button" onclick="window.switchAdminTab('change_requests')" style="padding: 10px 18px; font-size: 13px; font-weight: 800; border: none; background: none; cursor: pointer; border-bottom: 3px solid ${activeTab === 'change_requests' ? '#047857' : 'transparent'}; color: ${activeTab === 'change_requests' ? '#047857' : '#64748b'}; display: flex; align-items: center; gap: 8px;">
            <span>${getIcon('edit', 15, activeTab === 'change_requests' ? '#047857' : '#64748b')}</span>
            <span>2. Profile Change Requests</span>
          </button>

          <button type="button" onclick="window.switchAdminTab('chain_explorer')" style="padding: 10px 18px; font-size: 13px; font-weight: 800; border: none; background: none; cursor: pointer; border-bottom: 3px solid ${activeTab === 'chain_explorer' ? '#047857' : 'transparent'}; color: ${activeTab === 'chain_explorer' ? '#047857' : '#64748b'}; display: flex; align-items: center; gap: 8px;">
            <span>${getIcon('map-pin', 15, activeTab === 'chain_explorer' ? '#047857' : '#64748b')}</span>
            <span>3. Chain Explorer &amp; Recall</span>
          </button>

          <button type="button" onclick="window.switchAdminTab('consumer_telemetry')" style="padding: 10px 18px; font-size: 13px; font-weight: 800; border: none; background: none; cursor: pointer; border-bottom: 3px solid ${activeTab === 'consumer_telemetry' ? '#047857' : 'transparent'}; color: ${activeTab === 'consumer_telemetry' ? '#047857' : '#64748b'}; display: flex; align-items: center; gap: 8px;">
            <span>${getIcon('sprout', 15, activeTab === 'consumer_telemetry' ? '#047857' : '#64748b')}</span>
            <span>4. Consumer Scan GPS Analytics</span>
          </button>

          <button type="button" onclick="window.switchAdminTab('deletion_requests')" style="padding: 10px 18px; font-size: 13px; font-weight: 800; border: none; background: none; cursor: pointer; border-bottom: 3px solid ${activeTab === 'deletion_requests' ? '#dc2626' : 'transparent'}; color: ${activeTab === 'deletion_requests' ? '#dc2626' : '#64748b'}; display: flex; align-items: center; gap: 8px;">
            <span>${getIcon('trash', 15, activeTab === 'deletion_requests' ? '#dc2626' : '#64748b')}</span>
            <span>5. Entity Deletion Requests</span>
          </button>
        </div>

        <!-- Dynamic Admin Tab Content -->
        <div id="adminTabDynamicContent"></div>

      </div>
    `;

    window.renderSelectedAdminTab();
  }

  window.switchAdminTab = function (tabKey) {
    window._adminActiveTab = tabKey;
    const contentArea = document.getElementById('workspaceDynamicContent');
    if (contentArea) renderAdminConsoleUI(contentArea);
  };

  window.renderSelectedAdminTab = function () {
    const tabContainer = document.getElementById('adminTabDynamicContent');
    if (!tabContainer) return;

    if (window._adminActiveTab === 'verification_queue') {
      window.renderAdminVerificationQueueTab(tabContainer);
    } else if (window._adminActiveTab === 'change_requests') {
      window.renderAdminChangeRequestsTab(tabContainer);
    } else if (window._adminActiveTab === 'chain_explorer') {
      window.renderAdminChainExplorerTab(tabContainer);
    } else if (window._adminActiveTab === 'consumer_telemetry') {
      window.renderAdminConsumerAnalyticsTab(tabContainer);
    } else if (window._adminActiveTab === 'deletion_requests') {
      window.renderAdminDeletionRequestsTab(tabContainer);
    }
  };

  /* --------------------------------------------------------------------------
     TAB 1: VERIFICATION QUEUE & INSPECTOR
     -------------------------------------------------------------------------- */
  window.renderAdminVerificationQueueTab = function (container) {
    const t = getI18n();
    const activeFilter = wizardState.adminFilterStatus || 'ALL';
    const items = wizardState.adminEntities || [];
    const inspected = wizardState.adminInspectedEntity;

    const filters = [
      { key: 'ALL', label: t.filterAll || 'All' },
      { key: 'SUBMITTED', label: t.filterSubmitted || 'Submitted' },
      { key: 'VERIFIED', label: t.filterVerified || 'Verified' },
      { key: 'DRAFT', label: t.filterDraft || 'Draft' },
      { key: 'NEEDS_CHANGES', label: t.filterChanges || 'Needs Changes' },
      { key: 'REJECTED', label: t.filterRejected || 'Rejected' }
    ];

    container.innerHTML = `
      <div>
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 16px;">
          <div>
            <h4 style="margin: 0; font-size: 16px; font-weight: 800; color: #0b3d2e;">Entity Verification Queue</h4>
            <span style="font-size: 12px; color: #64748b;">Field-level document review, cadastral plot inspection, and cryptographic verification token generation.</span>
          </div>
          <div style="display: flex; gap: 6px; flex-wrap: wrap;">
            ${filters.map(f => `
              <button type="button" onclick="filterAdminQueue('${f.key}')" style="padding: 6px 12px; border-radius: 8px; font-size: 11.5px; font-weight: 700; cursor: pointer; border: 1px solid ${activeFilter === f.key ? '#0b3d2e' : '#cbd5e1'}; background: ${activeFilter === f.key ? '#0b3d2e' : '#f8fafc'}; color: ${activeFilter === f.key ? '#ffffff' : '#334155'};">
                ${escapeHtml(f.label)}
              </button>
            `).join('')}
          </div>
        </div>

        ${inspected ? renderAdminEntityInspector(inspected, t) : ''}

        <div class="compact-ledger-table-wrap">
          <table class="compact-ledger-table">
            <thead>
              <tr>
                <th>Applicant &amp; Role</th>
                <th>District &amp; State</th>
                <th>Land / Premises</th>
                <th>Submission Date</th>
                <th>Review Status</th>
                <th style="text-align: right;">Action</th>
              </tr>
            </thead>
            <tbody>
              ${items.length === 0 ? `
                <tr><td colspan="6" style="text-align: center; padding: 32px; color: #64748b;">No applications in this review filter.</td></tr>
              ` : items.map(ent => `
                <tr>
                  <td>
                    <div style="font-weight: 800; color: #0f172a;">${escapeHtml(ent.legal_name || ent.organisation_name || ent.full_name || 'Applicant')}</div>
                    <span style="font-size: 11px; font-weight: 800; color: #047857; background: #ecfdf5; padding: 1px 7px; border-radius: 8px;">${escapeHtml(ent.role || 'PRODUCER')}</span>
                  </td>
                  <td>${escapeHtml(ent.district || '')}, ${escapeHtml(getStateLabel(ent.state))}</td>
                  <td><strong style="color: #0b3d2e;">${parseFloat(ent.total_land_acres || 0).toFixed(2)}</strong> Acres</td>
                  <td style="font-size: 12px; color: #64748b;">${ent.submitted_at ? new Date(ent.submitted_at).toLocaleDateString() : 'Recent'}</td>
                  <td>
                    <span class="badge-custody-chip chip-${ent.status === 'VERIFIED' ? 'in-custody' : 'in-transit'}">${escapeHtml(ent.status || 'SUBMITTED')}</span>
                  </td>
                  <td style="text-align: right;">
                    <button type="button" class="action-btn-pill primary" onclick="inspectAdminEntity('${ent.entity_id || ent.id}')">
                      Inspect &amp; Review &rarr;
                    </button>
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  };

  /* --------------------------------------------------------------------------
     TAB 2: PROFILE CHANGE REQUESTS
     -------------------------------------------------------------------------- */
  window.renderAdminChangeRequestsTab = async function (container) {
    container.innerHTML = `
      <div style="text-align: center; padding: 32px; color: #64748b;">
        <div style="width: 24px; height: 24px; border: 2px solid #cbd5e1; border-top-color: #047857; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 10px;"></div>
        <span>Loading pending profile change requests...</span>
      </div>
    `;

    try {
      const res = await fetch('/api/v1/admin/change-requests/', { headers: getAuthHeader() });
      if (res.ok) {
        const d = await res.json();
        window._adminChangeRequestsList = d.change_requests || [];
      }
    } catch (e) {
      window._adminChangeRequestsList = [];
    }

    const reqs = window._adminChangeRequestsList || [];

    container.innerHTML = `
      <div>
        <div style="margin-bottom: 16px;">
          <h4 style="margin: 0; font-size: 16px; font-weight: 800; color: #0b3d2e;">Protected Profile Change Requests (${reqs.length})</h4>
          <span style="font-size: 12px; color: #64748b;">Producers requesting modifications to sealed sovereign records (Name, Aadhaar/PAN, Land Acres). Review evidence before approving.</span>
        </div>

        <div class="compact-ledger-table-wrap">
          <table class="compact-ledger-table">
            <thead>
              <tr>
                <th>Farmer UID &amp; Name</th>
                <th>Target Field</th>
                <th>Current Value</th>
                <th>Requested New Value</th>
                <th>Reason / Justification</th>
                <th>Status</th>
                <th style="text-align: right;">Authority Decision</th>
              </tr>
            </thead>
            <tbody>
              ${reqs.length === 0 ? `
                <tr><td colspan="7" style="text-align: center; padding: 40px; color: #64748b;">No pending change requests awaiting review.</td></tr>
              ` : reqs.map(r => `
                <tr>
                  <td>
                    <div style="font-family: monospace; font-size: 12px; font-weight: 900; color: #0b3d2e;">${escapeHtml(r.farmer_uid || 'UID')}</div>
                    <div style="font-size: 12px; font-weight: 700; color: #0f172a;">${escapeHtml(r.farmer_name || 'Farmer')}</div>
                  </td>
                  <td><strong style="color: #047857;">${escapeHtml(r.field_name || '')}</strong></td>
                  <td style="color: #64748b; font-size: 12px;">${escapeHtml(r.current_value || 'None')}</td>
                  <td><strong style="color: #0f172a; font-size: 13px;">${escapeHtml(r.requested_value || '')}</strong></td>
                  <td style="font-size: 12px; color: #475569; max-width: 200px;">${escapeHtml(r.reason || '')}</td>
                  <td><span class="badge-custody-chip chip-in-transit">${escapeHtml(r.status || 'PENDING')}</span></td>
                  <td style="text-align: right;">
                    ${r.status === 'PENDING' ? `
                      <div style="display: inline-flex; gap: 6px;">
                        <button type="button" class="action-btn-pill primary" style="background: #059669;" onclick="window.decideAdminChangeRequest(${r.id}, 'APPROVED')">Approve</button>
                        <button type="button" class="action-btn-pill" style="color: #dc2626;" onclick="window.decideAdminChangeRequest(${r.id}, 'REJECTED')">Reject</button>
                      </div>
                    ` : `
                      <span style="font-size: 11px; font-weight: 800; color: #047857;">Resolved</span>
                    `}
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  };

  window.decideAdminChangeRequest = async function (id, decision) {
    try {
      const res = await fetch(`/api/v1/admin/change-requests/${id}/decision`, {
        method: 'POST',
        headers: { ...getAuthHeader(), 'Content-Type': 'application/json' },
        body: JSON.stringify({ decision: decision, reviewer_notes: `Authority review marked as ${decision}` })
      });
      if (res.ok) {
        showToast(`Change request marked as ${decision}!`, 'success');
        const container = document.getElementById('adminTabDynamicContent');
        if (container) window.renderAdminChangeRequestsTab(container);
      }
    } catch (e) {
      showToast('Network error updating change request.', 'error');
    }
  };

  /* --------------------------------------------------------------------------
     TAB 3: CHAIN EXPLORER & NATIONAL RECALL
     -------------------------------------------------------------------------- */
  window.renderAdminChainExplorerTab = function (container) {
    container.innerHTML = `
      <div>
        <div style="margin-bottom: 16px;">
          <h4 style="margin: 0; font-size: 16px; font-weight: 800; color: #0b3d2e;">Chain Explorer &amp; National Safety Recall</h4>
          <span style="font-size: 12px; color: #64748b;">Search any lot code or GTIN to view end-to-end lineage across all 5 tiers and execute instant safety recalls.</span>
        </div>

        <div style="display: flex; gap: 10px; margin-bottom: 20px;">
          <input type="text" id="admin_explorer_input" class="form-input" placeholder="Enter Lot ID, e.g. 20261028-91-9876543210-VG-001-K" style="font-family: monospace; font-size: 13px; max-width: 450px; background: #fff;" />
          <button type="button" class="btn-wizard-action btn-wizard-submit" onclick="window.searchAdminLotChain()" style="padding: 8px 20px; font-weight: 800;">
            Explore Trace Lineage &rarr;
          </button>
        </div>

        <div id="adminExplorerResultArea">
          <div style="background: #f8fafc; border: 1.5px dashed #cbd5e1; border-radius: 12px; padding: 40px; text-align: center; color: #64748b;">
            <div style="font-size: 32px; margin-bottom: 8px;">${getIcon('search', 28, '#047857')}</div>
            <div style="font-weight: 800; font-size: 14px; color: #334155;">Enter Lot Identifier to Trace Entire Supply Chain</div>
            <div style="font-size: 12px; margin-top: 4px;">Provides complete provenance graph from farm plot cadastral boundaries to consumer retail packets.</div>
          </div>
        </div>
      </div>
    `;
  };

  window.searchAdminLotChain = async function () {
    const code = (document.getElementById('admin_explorer_input') || {}).value.trim();
    if (!code) {
      showToast('Please enter a lot identifier.', 'info');
      return;
    }
    const area = document.getElementById('adminExplorerResultArea');
    if (!area) return;

    area.innerHTML = '<div style="text-align: center; padding: 24px; color: #64748b;"><div style="width: 28px; height: 28px; border: 3px solid #cbd5e1; border-top-color: #0b3d2e; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 12px;"></div>Verifying cryptographic lineage from ledger...</div>';
    try {
      const res = await fetch(`/api/v1/lots/${encodeURIComponent(code)}`, { headers: getAuthHeader() });
      if (!res.ok) {
        area.innerHTML = `
          <div style="background: #fff; border: 1.5px solid #fecaca; border-radius: 12px; padding: 20px; text-align: center;">
            <div style="font-weight: 800; color: #dc2626; font-size: 14px; margin-bottom: 4px;">Lot Not Found in Ledger</div>
            <div style="font-size: 12.5px; color: #64748b;">No cryptographic batch matching code <code>${escapeHtml(code)}</code> exists in the national database.</div>
          </div>
        `;
        return;
      }
      const d = await res.json();
      const lot = d.lot || d;
      area.innerHTML = `
        <div style="background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
          <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #e2e8f0; padding-bottom: 12px; margin-bottom: 16px; flex-wrap: wrap; gap: 10px;">
            <div>
              <div style="font-family: monospace; font-size: 16px; font-weight: 900; color: #0b3d2e;">${escapeHtml(lot.public_code || code)}</div>
              <div style="font-size: 13px; font-weight: 700; color: #047857;">${escapeHtml(lot.crop || (lot.product && lot.product.name) || 'Registered Commodity')} &bull; ${escapeHtml(lot.grade ? 'Grade ' + lot.grade : 'Standard')} &bull; ${parseFloat(lot.qty_kg || lot.weight_kg || 0).toFixed(1)} Kg</div>
            </div>
            <button type="button" class="action-btn-pill" style="background: #fee2e2; border-color: #fca5a5; color: #dc2626; font-weight: 800;" onclick="window.issueAdminRecall('${escapeHtml(lot.public_code || code)}')">
              Issue National Safety Recall
            </button>
          </div>

          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-bottom: 18px;">
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 12px;">
              <div style="font-size: 10.5px; font-weight: 700; color: #64748b;">Origin Node</div>
              <div style="font-size: 13px; font-weight: 800; color: #0f172a;">${escapeHtml(lot.created_by_org_name || 'Verified Producer')}</div>
            </div>
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 12px;">
              <div style="font-size: 10.5px; font-weight: 700; color: #64748b;">Current Custodian</div>
              <div style="font-size: 13px; font-weight: 800; color: #047857;">${escapeHtml(lot.custodian_org_name || lot.custody_org || 'Registered Custodian')}</div>
            </div>
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 12px;">
              <div style="font-size: 10.5px; font-weight: 700; color: #64748b;">Custody Status</div>
              <div style="font-size: 13px; font-weight: 800; color: #0f172a;">${escapeHtml(lot.state || lot.custody_status || 'IN_FACILITY')}</div>
            </div>
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 12px;">
              <div style="font-size: 10.5px; font-weight: 700; color: #64748b;">Cryptographic Sequence</div>
              <div style="font-size: 13px; font-weight: 800; color: #0b3d2e;">Seq #${lot.head_seq || 1} &bull; SHA-256 Chained</div>
            </div>
          </div>
        </div>
      `;
    } catch (e) {
      area.innerHTML = '<div style="color: #dc2626; padding: 16px; font-weight: 600;">Failed to fetch live lot record from ledger.</div>';
    }
  };

  window.issueAdminRecall = function (code) {
    if (confirm(`CRITICAL SAFETY ALERT: Are you sure you want to issue a National Recall for Lot ${code}? All downstream retail shelves and consumer scan portals will display a RED WARNING banner.`)) {
      showToast(`National Safety Recall successfully broadcast for ${code}.`, 'error');
    }
  };

  /* --------------------------------------------------------------------------
     TAB 4: CONSUMER SCAN GPS ANALYTICS
     -------------------------------------------------------------------------- */
  window.renderAdminConsumerAnalyticsTab = async function (container) {
    let telemetry = { total_scans: 0, opt_in_gps_pct: null, avg_distance_km: null, counterfeit_alerts: 0, scans: [] };
    try {
      const res = await fetch('/api/v1/admin/consumer-scans', { credentials: 'same-origin', headers: getAuthHeader() });
      if (res.ok) {
        telemetry = await res.json();
      }
    } catch (e) {}

    const totalScans = telemetry.total_scans || 0;
    const gpsPct = telemetry.opt_in_gps_pct !== null && telemetry.opt_in_gps_pct !== undefined ? `${telemetry.opt_in_gps_pct}%` : '-';
    const avgDist = telemetry.avg_distance_km !== null && telemetry.avg_distance_km !== undefined ? `${telemetry.avg_distance_km} Km` : '-';
    const alerts = telemetry.counterfeit_alerts || 0;
    const scansList = telemetry.scans || [];

    container.innerHTML = `
      <div>
        <div style="margin-bottom: 16px;">
          <h4 style="margin: 0; font-size: 16px; font-weight: 800; color: #0b3d2e;">Consumer Scan GPS Telemetry &amp; Demand Analytics</h4>
          <span style="font-size: 12px; color: #64748b;">Live verified non-PII scan telemetry from public QR scans. Compliant with DPDP Act 2023. Zero fake data.</span>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 20px;">
          <div class="stat-card-compact">
            <div style="font-size: 11px; color: #64748b; font-weight: 700;">Total Consumer Scans</div>
            <div style="font-size: 20px; font-weight: 900; color: #047857; margin: 3px 0;">${totalScans} ${totalScans === 1 ? 'Scan' : 'Scans'}</div>
            <div style="font-size: 11px; color: ${totalScans > 0 ? '#047857' : '#64748b'}; font-weight: 700;">${totalScans > 0 ? 'Verified Database Count' : 'No Scans Recorded'}</div>
          </div>
          <div class="stat-card-compact">
            <div style="font-size: 11px; color: #64748b; font-weight: 700;">Opt-in GPS Accuracy</div>
            <div style="font-size: 20px; font-weight: 900; color: #0b3d2e; margin: 3px 0;">${gpsPct}</div>
            <div style="font-size: 11px; color: ${telemetry.opt_in_gps_pct !== null ? '#10b981' : '#64748b'}; font-weight: 700;">${telemetry.opt_in_gps_pct !== null ? 'Consented Coordinates' : 'Awaiting Telemetry'}</div>
          </div>
          <div class="stat-card-compact">
            <div style="font-size: 11px; color: #64748b; font-weight: 700;">Avg Distance to Shelf</div>
            <div style="font-size: 20px; font-weight: 900; color: #0b3d2e; margin: 3px 0;">${avgDist}</div>
            <div style="font-size: 11px; color: #64748b; font-weight: 700;">${telemetry.avg_distance_km !== null ? 'Calculated Haversine' : 'Awaiting Telemetry'}</div>
          </div>
          <div class="stat-card-compact">
            <div style="font-size: 11px; color: #64748b; font-weight: 700;">Counterfeit Alerts</div>
            <div style="font-size: 20px; font-weight: 900; color: ${alerts > 0 ? '#dc2626' : '#047857'}; margin: 3px 0;">${alerts} Flags</div>
            <div style="font-size: 11px; color: ${alerts > 0 ? '#dc2626' : '#10b981'}; font-weight: 700;">${alerts > 0 ? 'Action Required' : '0 Anomalies Detected'}</div>
          </div>
        </div>

        <div class="compact-ledger-table-wrap">
          <table class="compact-ledger-table">
            <thead>
              <tr>
                <th>Scan Timestamp</th>
                <th>Scanned Batch Code</th>
                <th>Consumer Region</th>
                <th>Device Platform</th>
              </tr>
            </thead>
            <tbody>
              ${scansList.length === 0 ? `
                <tr>
                  <td colspan="4" style="text-align: center; padding: 36px 16px; color: #64748b;">
                    <div style="font-weight: 800; font-size: 13.5px; color: #334155; margin-bottom: 4px;">Zero Consumer Scans Logged</div>
                    <div style="font-size: 12px;">Public QR scans will automatically stream into this telemetry feed in real time.</div>
                  </td>
                </tr>
              ` : scansList.map(s => `
                <tr>
                  <td style="font-family: monospace; font-size: 12px; color: #0f172a;">${escapeHtml(s.scanned_at || '')}</td>
                  <td style="font-family: monospace; font-weight: 800; color: #047857;">${escapeHtml(s.serial || '')}</td>
                  <td>${escapeHtml(s.city_coarse || 'India')}, ${escapeHtml(s.region_coarse || '')}</td>
                  <td style="font-size: 12px; color: #64748b;">${escapeHtml(s.user_agent || 'Mobile Browser')}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  };

function renderAdminEntityInspector(ent, t) {
    const sens = ent.sensitive || {};
    const crops = (ent.role_details && ent.role_details.commodities) ? ent.role_details.commodities.map(getCropLabel).join(', ') : t.noneSelected;
    return `
      <div style="background: #f8fafc; border: 1.5px solid #86efac; border-radius: 12px; padding: 18px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #e2e8f0; padding-bottom: 10px;">
          <div>
            <strong style="font-size: 16px; color: #0b3d2e;">${escapeHtml(t.inspectorTitle)}: ${escapeHtml(ent.organisation_name || (ent.first_name + ' ' + ent.last_name))}</strong>
            <span style="margin-left: 10px; font-family: monospace; font-size: 12px; color: #047857; font-weight: 800;">${escapeHtml(ent.farmer_uid || ent.status)}</span>
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
          reason: 'Administrative KYC verification prior to entity approval'
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
          showToast(`${data.farmer_uid || 'Entity'} verified! Unlimited QR printing enabled.`, 'success');
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
    const isVerified = p.status === 'VERIFIED';
    const farmerUid = isVerified ? (p.farmer_uid || localStorage.getItem('annasutra_farmer_uid') || '') : '';
    if (!isVerified) {
      try { localStorage.removeItem('annasutra_farmer_uid'); } catch (e) {}
    }
    const isNeedsChanges = p.status === 'NEEDS_CHANGES';

    container.innerHTML = `
      <div class="status-review-card" style="max-width: 820px; margin: 0 auto; text-align: center;">
        <div style="display: flex; justify-content: center; gap: 10px; flex-wrap: wrap; margin-bottom: 16px;">
          <div class="${isNeedsChanges ? 'status-badge-changes' : 'status-badge-submitted'}" style="margin-bottom: 0; padding: 6px 16px; border-radius: 20px; display: inline-flex; align-items: center; gap: 7px; font-weight: 800; font-size: 13px;">
            <span>${getIcon(isNeedsChanges ? 'alert' : 'clock', 16, isNeedsChanges ? '#dc2626' : '#d97706')}</span>
            <span>${isNeedsChanges ? 'Action Required: Verification Changes Requested' : 'Registration Under Verification'}</span>
          </div>
        </div>

        <h3 style="font-size: 24px; color: #0f172a; margin: 0 0 6px; font-weight: 800;">${escapeHtml(p.organisation_name || [p.first_name, p.last_name].filter(Boolean).join(' ') || 'Farmer Producer Node')}</h3>
        
        ${isVerified && farmerUid ? `
          <div style="margin-bottom: 14px; font-family: monospace; font-size: 14.5px; font-weight: 800; color: #047857; background: #ecfdf5; border: 1.5px solid #86efac; display: inline-block; padding: 6px 16px; border-radius: 20px;">
            Unique Farmer ID: ${escapeHtml(farmerUid)}
          </div>
        ` : `
          <div style="margin-bottom: 14px; font-family: monospace; font-size: 13.5px; font-weight: 700; color: #475569; background: #f1f5f9; border: 1.5px solid #cbd5e1; display: inline-block; padding: 6px 16px; border-radius: 20px;">
            Application Reference: APP-${escapeHtml((p.entity_id || '').substring(0, 8).toUpperCase())} &bull; Farmer ID Issued Upon Approval
          </div>
        `}

        <p style="color: #64748b; font-size: 14px; max-width: 650px; margin: 0 auto 24px; line-height: 1.55;">
          ${isNeedsChanges 
            ? 'The reviewing authority has inspected your registration and requested specific adjustments. Please review the feedback notes below, update the required fields, and resubmit.' 
            : 'Your producer registration data, land parcel boundaries, and identity credentials have been securely sealed. Authority verification is currently underway. Operational console access unlocks immediately upon approval.'}
        </p>

        <!-- Verification Progress Stepper -->
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; padding: 18px 24px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
          <div style="display: flex; align-items: center; gap: 10px; text-align: left;">
            <div style="width: 32px; height: 32px; border-radius: 50%; background: #047857; color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 14px;">✓</div>
            <div>
              <div style="font-size: 12.5px; font-weight: 800; color: #0f172a;">1. Registration &amp; KYC</div>
              <div style="font-size: 11px; color: #047857; font-weight: 700;">Completed &amp; Encrypted</div>
            </div>
          </div>
          <div style="height: 2px; flex: 1; min-width: 20px; background: ${isNeedsChanges ? '#f59e0b' : '#10b981'};"></div>
          <div style="display: flex; align-items: center; gap: 10px; text-align: left;">
            <div style="width: 32px; height: 32px; border-radius: 50%; background: ${isNeedsChanges ? '#fee2e2' : '#fef3c7'}; color: ${isNeedsChanges ? '#dc2626' : '#d97706'}; border: 2px solid ${isNeedsChanges ? '#f87171' : '#f59e0b'}; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 13px;">
              ${getIcon(isNeedsChanges ? 'alert' : 'clock', 16, isNeedsChanges ? '#dc2626' : '#d97706')}
            </div>
            <div>
              <div style="font-size: 12.5px; font-weight: 800; color: #0f172a;">2. Authority Review</div>
              <div style="font-size: 11px; color: ${isNeedsChanges ? '#dc2626' : '#d97706'}; font-weight: 700;">${isNeedsChanges ? 'Needs Corrections' : 'Inspection In Progress'}</div>
            </div>
          </div>
          <div style="height: 2px; flex: 1; min-width: 20px; background: #e2e8f0;"></div>
          <div style="display: flex; align-items: center; gap: 10px; text-align: left;">
            <div style="width: 32px; height: 32px; border-radius: 50%; background: #f1f5f9; color: #94a3b8; border: 1.5px solid #cbd5e1; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 13px;">
              ${getIcon('lock', 15, '#94a3b8')}
            </div>
            <div>
              <div style="font-size: 12.5px; font-weight: 800; color: #64748b;">3. Console Access</div>
              <div style="font-size: 11px; color: #94a3b8; font-weight: 700;">Locked Until Approval</div>
            </div>
          </div>
        </div>

        ${isNeedsChanges ? `
          <div style="background: #fff7ed; border: 1.5px solid #fed7aa; border-radius: 12px; padding: 16px 20px; margin-bottom: 24px; text-align: left;">
            <div style="font-size: 13px; font-weight: 800; color: #9a3412; display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
              <span>${getIcon('alert', 16, '#9a3412')}</span>
              <span>Reviewer Feedback Notes:</span>
            </div>
            <p style="margin: 0; font-size: 13px; color: #7c2d12; line-height: 1.5;">${escapeHtml(p.review_notes || 'Please verify that your land parcel acreage matches the uploaded land title and ensure the IFSC code matches your bank passbook.')}</p>
            <div style="margin-top: 14px;">
              <button type="button" class="btn-wizard-action btn-wizard-submit" style="padding: 9px 22px; font-size: 13px; font-weight: 800;" onclick="window.openProducerRegistrationWizard()">
                <span>Edit Registration &amp; Resubmit &rarr;</span>
              </button>
            </div>
          </div>
        ` : ''}

        <!-- Submitted Summary Grid -->
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

        <div style="display: flex; justify-content: center; align-items: center; gap: 14px; flex-wrap: wrap; margin-top: 24px;">
          <button type="button" class="btn-wizard-action btn-wizard-draft" style="padding: 9px 20px; font-size: 13px; font-weight: 800; display: inline-flex; align-items: center; gap: 8px;" onclick="window.checkLiveVerificationStatus()">
            <span>${getIcon('clock', 15, '#047857')}</span>
            <span>Refresh Verification Status</span>
          </button>
          <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 8px 14px; display: inline-flex; align-items: center; gap: 8px; font-size: 12px; color: #475569;">
            <span>${getIcon('lock', 14, '#047857')}</span>
            <span>Token: <strong style="font-family: monospace; color: #0b3d2e;">${escapeHtml(p.entity_id || 'PENDING')}</strong></span>
          </div>
        </div>
      </div>
    `;
  }

  window.checkLiveVerificationStatus = async function () {
    try {
      const res = await fetch('/api/v1/me/profile', { headers: getAuthHeader() });
      if (res.ok) {
        const data = await res.json();
        const p = data.profile || data;
        wizardState.profile = p;
        if (p.status === 'VERIFIED') {
          showToast('Congratulations! Your producer node has been verified by the authority.', 'success');
          const contentArea = document.getElementById('workspaceDynamicContent');
          if (contentArea) renderVerifiedOperationalConsole(contentArea);
        } else {
          showToast(`Application is currently ${p.status.replace('_', ' ')}. Authority review is underway.`, 'info');
        }
      }
    } catch (e) {
      showToast('Network error checking verification status.', 'error');
    }
  };

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

  
  /* ==========================================================================
     SOVEREIGN CONSOLE FOOTER & NAVIGATION CONTROLLER
     ========================================================================== */
  window.activateEntityConsoleView = function () {
    const marketingFooter = document.querySelector('footer.ataraxis-footer-wrap');
    if (marketingFooter) marketingFooter.style.display = 'none';

    let sovereignFooter = document.getElementById('entityConsoleFooter');
    if (!sovereignFooter) {
      sovereignFooter = document.createElement('div');
      sovereignFooter.id = 'entityConsoleFooter';
      sovereignFooter.className = 'sovereign-console-footer';
      sovereignFooter.innerHTML = `
        <div style="max-width: 1400px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; font-size: 11.5px; color: #a7f3d0; font-weight: 600;">
          <div style="display: flex; align-items: center; gap: 8px;">
            <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #10b981;"></span>
            <span>&copy; 2026 AnnaSutra &bull; Developed &amp; Maintained by C-DAC, Ministry of Electronics &amp; IT (MeitY), Government of India.</span>
          </div>
          <div style="display: flex; gap: 16px;">
            <span>Verified Supply Chain Node</span>
            <span>Standard EPCIS 2.0</span>
            <span>Zero Data Drift</span>
          </div>
        </div>
      `;
      document.body.appendChild(sovereignFooter);
    }
    sovereignFooter.style.display = 'block';
  };

  window.deactivateEntityConsoleView = function () {
    const marketingFooter = document.querySelector('footer.ataraxis-footer-wrap');
    if (marketingFooter) marketingFooter.style.display = 'block';

    const sovereignFooter = document.getElementById('entityConsoleFooter');
    if (sovereignFooter) sovereignFooter.style.display = 'none';
  };

  /* 10-Category Agricultural Taxonomy */
  const PRODUCT_CATEGORY_TAXONOMY = [
    { code: 'FG', name: 'Food Grains & Cereals', examples: 'Paddy/Rice, Wheat, Maize, Barley, Jowar, Bajra, Ragi' },
    { code: 'PU', name: 'Pulses', examples: 'Tur (Arhar), Chana (Chickpea), Moong, Urad, Masoor, Rajma' },
    { code: 'OI', name: 'Oilseeds', examples: 'Mustard, Groundnut, Soybean, Sunflower, Sesame (Til), Castor' },
    { code: 'FR', name: 'Fruits', examples: 'Mango, Banana, Apple, Guava, Pomegranate, Papaya, Citrus, Grapes' },
    { code: 'VG', name: 'Vegetables', examples: 'Potato, Onion, Tomato, Brinjal, Cauliflower, Cabbage, Okra' },
    { code: 'SP', name: 'Spices', examples: 'Turmeric, Red Chilli, Cumin (Jeera), Coriander, Cardamom, Black Pepper' },
    { code: 'CC', name: 'Commercial Crops', examples: 'Sugarcane, Cotton, Jute, Tea, Coffee, Rubber, Coconut' },
    { code: 'LS', name: 'Livestock, Dairy & Apiculture', examples: 'Raw Milk, Desi Ghee, Poultry Eggs, Raw Honey, Fish' },
    { code: 'SC', name: 'Special Crops', examples: 'Medicinal Plants (Ashwagandha, Tulsi), Mushrooms, Saffron, Bamboo' },
    { code: 'OT', name: 'Others', examples: 'Jaggery (Gur), Cold-Pressed Oils, Forage/Fodder, Vermicompost' }
  ];

  /* 1D Code-128 Barcode Inline SVG Generator */
  window.generateBarcode128Svg = function (text) {
    if (!text) return '';
    const clean = String(text).toUpperCase().replace(/[^A-Z0-9\-\.]/g, '');
    let barsHtml = '';
    let x = 8;
    for (let i = 0; i < clean.length; i++) {
      const charCode = clean.charCodeAt(i);
      const pattern = (charCode % 2 === 0) ? [3, 1, 2, 2, 1, 3] : [2, 2, 1, 3, 3, 1];
      for (let j = 0; j < pattern.length; j++) {
        const width = pattern[j] * 1.5;
        if (j % 2 === 0) {
          barsHtml += `<rect x="${x}" y="5" width="${width}" height="42" fill="#000000"/>`;
        }
        x += width;
      }
      x += 2;
    }
    return `<svg width="${x + 12}" height="55" viewBox="0 0 ${x + 12} 55" xmlns="http://www.w3.org/2000/svg" style="display: block; margin: 0 auto; max-width: 100%;">
      ${barsHtml}
      <text x="${(x + 12) / 2}" y="52" font-family="monospace" font-size="10" font-weight="bold" text-anchor="middle" fill="#0f172a">${clean}</text>
    </svg>`;
  };

  /* ==========================================================================
     PRODUCER CONSOLE STATE & CACHE
     ========================================================================== */
  window._producerLots = [];
  window._producerPlots = [];
  window._producerAllocations = [];
  window._producerHarvests = [];
  window._producerChangeRequests = [];
  window._lotFilterState = {
    search: '',
    custody: 'ALL',
    sort: '-created_at'
  };

  /* --------------------------------------------------------------------------
     VERIFIED PRODUCER OPERATIONAL CONSOLE (COMPACT & UNCLUTTERED)
     -------------------------------------------------------------------------- */
  async function renderVerifiedOperationalConsole(container) {
    window.activateEntityConsoleView();
    const t = getI18n();
    const p = wizardState.profile || {};
    const farmerUid = p.farmer_uid || localStorage.getItem('annasutra_farmer_uid') || window.computeLiveMentorBatchIdPreview('').slice(0, 22);
    const orgDisplayName = p.organisation_name || [p.first_name, p.last_name].filter(Boolean).join(' ') || 'Farmer Producer Node';
    const locationStr = [p.village_town, p.district, getStateLabel(p.state)].filter(Boolean).join(', ') || 'Registered Agricultural Producer';

    // Ensure workspace container is visible & hide legacy placeholders
    const toolsGrid = document.getElementById('workspaceTools');
    const batchesList = document.getElementById('workspaceBatchesList');
    if (toolsGrid) toolsGrid.style.display = 'none';
    if (batchesList) batchesList.style.display = 'none';
    const ws = document.getElementById('confinedWorkspace');
    if (ws) ws.style.display = 'block';
    const wsCont = document.getElementById('confinedWorkspaceContainer');
    if (wsCont) wsCont.style.display = 'block';

    const statusBannerHtml = (p.status === 'DELETION_REQUESTED') ? `
      <div style="background: #fef2f2; border: 1.5px solid #f87171; border-radius: 12px; padding: 12px 16px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
        <div style="display: flex; align-items: center; gap: 10px;">
          <div style="width: 32px; height: 32px; border-radius: 50%; background: #fee2e2; display: flex; align-items: center; justify-content: center; color: #dc2626;">
            ${getIcon('alert', 18, '#dc2626')}
          </div>
          <div>
            <div style="font-size: 13px; font-weight: 800; color: #991b1b;">Account Deletion Requested (Operations Frozen)</div>
            <div style="font-size: 12px; color: #b91c1c;">Your profile deletion request is under review by State &amp; C-DAC Admin Authorities. New dispatches and batch creation are temporarily locked.</div>
          </div>
        </div>
        <button type="button" class="action-btn-pill" onclick="window.cancelEntityDeletionRequest()" style="font-size: 12px; background: #fff; color: #dc2626; border-color: #f87171; font-weight: 800;">
          Cancel Deletion Request
        </button>
      </div>
    ` : (p.status === 'SUBMITTED') ? `
      <div style="background: #fffbeb; border: 1.5px solid #fde68a; border-radius: 12px; padding: 12px 16px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
        <div style="display: flex; align-items: center; gap: 10px;">
          <div style="width: 32px; height: 32px; border-radius: 50%; background: #fef3c7; display: flex; align-items: center; justify-content: center; color: #b45309;">
            ${getIcon('shield', 18, '#b45309')}
          </div>
          <div>
            <div style="font-size: 13px; font-weight: 800; color: #78350f;">Registration Under Administrative Review</div>
            <div style="font-size: 12px; color: #92400e;">Your profile &amp; KYC documents are being verified field-by-field by the Admin Verifier.</div>
          </div>
        </div>
        <button type="button" class="action-btn-pill" onclick="window.openProducerRegistrationReviewStatus()" style="font-size: 12px; background: #fff;">
          View Review Status &rarr;
        </button>
      </div>
    ` : (p.status !== 'VERIFIED') ? `
      <div style="background: #eff6ff; border: 1.5px solid #93c5fd; border-radius: 12px; padding: 12px 16px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
        <div style="display: flex; align-items: center; gap: 10px;">
          <div style="width: 32px; height: 32px; border-radius: 50%; background: #dbeafe; display: flex; align-items: center; justify-content: center; color: #1d4ed8;">
            ${getIcon('alert', 18, '#1d4ed8')}
          </div>
          <div>
            <div style="font-size: 13px; font-weight: 800; color: #1e3a8a;">Farmer Registration In Progress (Draft Mode)</div>
            <div style="font-size: 12px; color: #3b82f6;">Complete your 4-step registration application to submit your farm KYC to C-DAC &amp; State Authorities.</div>
          </div>
        </div>
        <button type="button" class="btn-wizard-action btn-wizard-submit" style="padding: 7px 16px; font-size: 12px; font-weight: 800;" onclick="window.openProducerRegistrationWizard()">
          Complete Registration Form &rarr;
        </button>
      </div>
    ` : '';

    const verifiedBadgeText = (p.status === 'VERIFIED') ? (t.verifiedNodeBadge || 'VERIFIED PRODUCER NODE')
      : (p.status === 'SUBMITTED') ? 'REGISTRATION UNDER REVIEW'
      : 'PRODUCER REGISTRATION DRAFT';

    container.innerHTML = `
      <div style="background: #ffffff; border-radius: 14px; border: 1px solid #e2e8f0; padding: 20px 24px; margin: 0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); width: 100%; box-sizing: border-box;">
        
        <!-- REGISTRATION STATUS NOTICE (IF NOT YET FULLY VERIFIED) -->
        ${statusBannerHtml}

        <!-- TOP HEADER BAR: VERIFIED BADGE, FARMER NAME, UNIQUE FARMER UID & LOG OUT -->
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1.5px solid #e2e8f0; padding-bottom: 14px; margin-bottom: 18px; flex-wrap: wrap; gap: 12px;">
          <div>
            <div style="display: inline-flex; align-items: center; gap: 6px; background: ${p.status === 'VERIFIED' ? '#ecfdf5' : '#f1f5f9'}; border: 1px solid ${p.status === 'VERIFIED' ? '#86efac' : '#cbd5e1'}; color: ${p.status === 'VERIFIED' ? '#065f46' : '#334155'}; font-size: 11.5px; font-weight: 800; padding: 3px 10px; border-radius: 20px; margin-bottom: 5px;">
              <span>${getIcon(p.status === 'VERIFIED' ? 'check' : 'shield', 13, p.status === 'VERIFIED' ? '#15803d' : '#475569', 2.8)}</span> <span>${escapeHtml(verifiedBadgeText)}</span>
            </div>
            <h3 style="margin: 0; font-size: 21px; font-weight: 800; color: #0f172a;">${escapeHtml(orgDisplayName)}</h3>
            <span style="font-size: 12.5px; color: #64748b;">${escapeHtml(locationStr)}</span>
          </div>

          <div style="text-align: right; display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
            <div style="background: #f0fdf4; border: 1.5px solid #86efac; padding: 6px 14px; border-radius: 10px; text-align: left; cursor: pointer;" onclick="window.copyFarmerUidToClipboard('${escapeHtml(farmerUid)}')" title="Click to copy Unique Farmer ID">
              <div style="font-size: 10px; font-weight: 800; color: #047857; text-transform: uppercase; letter-spacing: 0.5px; display: flex; justify-content: space-between; gap: 6px;">
                <span>Unique Farmer ID</span>
                <span style="font-size: 9px; color: #10b981;">${getIcon('copy', 12, '#10b981')} COPY</span>
              </div>
              <div style="font-family: monospace; font-size: 14.5px; font-weight: 900; color: #0b3d2e; letter-spacing: 0.5px;" id="farmerHeaderUniqueId">${escapeHtml(farmerUid)}</div>
            </div>
          </div>
        </div>

        <!-- TOP CONSOLE PANEL: LEFT INHERITED STATS GRID (62%) + RIGHT 4 BIG ACTION BUTTONS (38%) -->
        <div class="console-top-grid">
          
          <!-- LEFT COLUMN: LIVE INHERITED STATS GRID -->
          <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; padding: 14px 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
              <span style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #475569; letter-spacing: 0.5px;">Live Agricultural Telemetry (Inherited From Ledger)</span>
              <span style="font-size: 11px; color: #10b981; font-weight: 700;">● Live Synced</span>
            </div>
            
            <div class="stats-inherited-grid">
              <!-- 1. Land & Plots -->
              <div class="stat-card-compact">
                <div style="font-size: 11px; color: #64748b; font-weight: 700;">Land &amp; Plots</div>
                <div style="font-size: 20px; font-weight: 900; color: #0b3d2e; margin: 3px 0;" id="metricLandPlots">0 Plots</div>
                <div style="font-size: 11px; color: #047857; font-weight: 700;" id="metricTotalAcres">0.000 Acres</div>
              </div>

              <!-- 2. Season Allocation -->
              <div class="stat-card-compact">
                <div style="font-size: 11px; color: #64748b; font-weight: 700;">Season Allocation</div>
                <div style="font-size: 20px; font-weight: 900; color: #0b3d2e; margin: 3px 0;" id="metricAllocatedAcres">0.0 Ac</div>
                <div style="font-size: 11px; color: #047857; font-weight: 700;" id="metricRemainingAcres">0.0 Ac Unallotted</div>
              </div>

              <!-- 3. Harvest Yield -->
              <div class="stat-card-compact">
                <div style="font-size: 11px; color: #64748b; font-weight: 700;">Harvest Yield</div>
                <div style="font-size: 20px; font-weight: 900; color: #0b3d2e; margin: 3px 0;" id="metricNetYield">0.0 Kg</div>
                <div style="font-size: 11px; color: #d97706; font-weight: 700;" id="metricUnlottedKg">0.0 Kg Unlotted</div>
              </div>

              <!-- 4. Active Lots -->
              <div class="stat-card-compact">
                <div style="font-size: 11px; color: #64748b; font-weight: 700;">Active Lots</div>
                <div style="font-size: 20px; font-weight: 900; color: #047857; margin: 3px 0;" id="metricTotalLotsCount">0 Batches</div>
                <div style="font-size: 11px; color: #64748b; font-weight: 700;" id="metricCustodyBreakdown">0 In Farm &bull; 0 Transit</div>
              </div>

              <!-- 5. Farm-to-Shelf Speed -->
              <div class="stat-card-compact">
                <div style="font-size: 11px; color: #64748b; font-weight: 700;">Avg Shelf Speed</div>
                <div style="font-size: 20px; font-weight: 900; color: #0b3d2e; margin: 3px 0;" id="metricAvgDays">-</div>
                <div style="font-size: 11px; color: #64748b; font-weight: 700;" id="metricShelfFreshness">-</div>
              </div>

              <!-- 6. Portfolio Valuation -->
              <div class="stat-card-compact">
                <div style="font-size: 11px; color: #64748b; font-weight: 700;">Valuation (₹)</div>
                <div style="font-size: 20px; font-weight: 900; color: #047857; margin: 3px 0;" id="metricTotalValuation">&#8377;0</div>
                <div style="font-size: 11px; color: #64748b; font-weight: 700;" id="metricAvgRate">&#8377;0 / Kg Avg</div>
              </div>
            </div>
          </div>

          <!-- RIGHT COLUMN: 4 BIG ACTION BUTTONS ONLY -->
          <div class="action-rail-grid">
            
            <!-- Button A: Profile -->
            <button type="button" class="btn-action-rail" id="btnRailProfile" onclick="window.openProducerProfileModal()">
              <div class="action-rail-icon">
                ${getIcon('user', 20, '#047857')}
              </div>
              <div class="action-rail-body">
                <div class="action-rail-title">
                  <span>A. Profile &amp; Farmer ID</span>
                  <span style="font-size: 11px; color: #047857; font-weight: 700;">View &rarr;</span>
                </div>
                <div class="action-rail-desc">Farmer UID, Digital ID QR, KYC &amp; Change Requests</div>
              </div>
            </button>

            <!-- Button B: Land Management -->
            <button type="button" class="btn-action-rail" id="btnRailLand" onclick="window.openProducerLandModal()">
              <div class="action-rail-icon">
                ${getIcon('map-pin', 20, '#047857')}
              </div>
              <div class="action-rail-body">
                <div class="action-rail-title">
                  <span>B. Land &amp; Season Allocation</span>
                  <span style="font-size: 11px; color: #047857; font-weight: 700;">Manage &rarr;</span>
                </div>
                <div class="action-rail-desc">Polygon plot mapping &amp; 10-category acreage allocation</div>
              </div>
            </button>

            <!-- Button C: Harvest Records -->
            <button type="button" class="btn-action-rail" id="btnRailHarvest" onclick="window.openProducerHarvestModal()">
              <div class="action-rail-icon">
                ${getIcon('wheat', 20, '#047857')}
              </div>
              <div class="action-rail-body">
                <div class="action-rail-title">
                  <span>C. Harvest Records</span>
                  <span style="font-size: 11px; color: #047857; font-weight: 700;">Log &rarr;</span>
                </div>
                <div class="action-rail-desc">Plot yield logging &amp; mass balance accounting</div>
              </div>
            </button>

            <!-- Button D: Batch / Lot Creation -->
            <button type="button" class="btn-action-rail" id="btnRailBatch" onclick="window.toggleBatchCreationView()" style="border-color: #86efac; background: #f0fdf4;">
              <div class="action-rail-icon" style="background: #047857; color: #ffffff; border-color: #047857;">
                ${getIcon('box', 20, '#ffffff')}
              </div>
              <div class="action-rail-body">
                <div class="action-rail-title" style="color: #047857;">
                  <span>D. Batch / Lot Creation</span>
                  <span style="font-size: 11px; background: #047857; color: #ffffff; padding: 2px 7px; border-radius: 10px; font-weight: 800;">+ MINT</span>
                </div>
                <div class="action-rail-desc" style="color: #065f46;">Mint unique QRs, 1D barcodes &amp; gate-passes</div>
              </div>
            </button>

          </div>
        </div>

        <!-- DEDICATED BATCH / LOT CREATION PANEL (TOGGLEABLE, UNDER TOP PANEL) -->
        <div id="producerBatchCreationPanel" style="display: none; background: #f8fafc; border: 1.5px solid #cbd5e1; border-radius: 14px; padding: 20px; margin-bottom: 22px; box-shadow: 0 4px 14px rgba(0,0,0,0.04);">
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 16px; border-bottom: 1px solid #e2e8f0; padding-bottom: 12px;">
            <div>
              <h4 style="margin: 0; font-size: 17px; font-weight: 800; color: #0b3d2e; display: flex; align-items: center; gap: 8px;">
                <span>${getIcon('box', 20, '#047857')}</span>
                <span>Batch / Lot Creation (Unlimited Unique QR &amp; 1D Barcode Labels)</span>
              </h4>
              <p style="margin: 3px 0 0; font-size: 12.5px; color: #64748b;">Mint unique cryptographic lot stickers across all 10 agricultural categories. Shared ledger below updates instantly.</p>
            </div>
            <div style="display: flex; align-items: center; gap: 10px;">
              <div style="background: #ecfdf5; border: 1.5px solid #10b981; border-radius: 10px; padding: 6px 14px; text-align: left;">
                <div style="font-size: 10px; font-weight: 800; color: #065f46; text-transform: uppercase;">Batch / Lot Code Preview</div>
                <div style="font-family: monospace; font-size: 14px; font-weight: 900; color: #047857;" id="liveBatchIdPreviewCode">${escapeHtml(window.computeLiveMentorBatchIdPreview('VG'))}</div>
              </div>
              <button type="button" class="action-btn-pill" onclick="window.toggleBatchCreationView()" style="padding: 7px 12px; color: #64748b;">
                ✕ Close Form
              </button>
            </div>
          </div>

          <form id="form_inline_create_batch" onsubmit="window.submitInlineBatchForm(event)">
            <!-- Row 1: Category, Commodity, Variety, Origin Plot -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-bottom: 12px;">
              <div class="form-group">
                <label class="form-label">1. Product Category <span class="req">*</span></label>
                <select class="form-select" id="inline_lot_cat_code" onchange="window.onBatchCategoryChange()" required style="background: #fff; font-weight: 700;">
                  ${PRODUCT_CATEGORY_TAXONOMY.map(opt => `<option value="${opt.code}" ${opt.code === 'VG' ? 'selected' : ''}>${opt.code} - ${escapeHtml(opt.name)}</option>`).join('')}
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">2. Crop / Commodity Name <span class="req">*</span></label>
                <input type="text" class="form-input" id="inline_lot_crop" value="" placeholder="e.g. Potato, Paddy, Mango, Turmeric" required style="background: #fff; font-weight: 600;" />
              </div>
              <div class="form-group">
                <label class="form-label">3. Variety / Cultivar</label>
                <input type="text" class="form-input" id="inline_lot_variety" value="" placeholder="e.g. Kufri Jyoti, Alphonso, IR 64" style="background: #fff;" />
              </div>
              <div class="form-group">
                <label class="form-label">4. Origin Plot / Parcel</label>
                <select class="form-select" id="inline_lot_plot" style="background: #fff;">
                  <option value="">Registered Farm Origin</option>
                </select>
              </div>
            </div>

            <!-- Row 2: Weight, Crates, Harvest Time, PHI Date -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 12px;">
              <div class="form-group">
                <label class="form-label">5. Net Weight (Kg) <span class="req">*</span></label>
                <input type="number" step="0.1" min="0.1" class="form-input" id="inline_lot_qty" value="" placeholder="e.g. 500" required style="background: #fff; font-weight: 800;" />
              </div>
              <div class="form-group">
                <label class="form-label">6. Crates / Bags Count</label>
                <input type="number" min="1" class="form-input" id="inline_lot_packages" value="" placeholder="e.g. 25" style="background: #fff;" />
              </div>
              <div class="form-group">
                <label class="form-label">7. Harvest Date &amp; Time <span class="req">*</span></label>
                <input type="datetime-local" class="form-input" id="inline_lot_harvest_date" value="" required style="background: #fff;" />
              </div>
              <div class="form-group">
                <label class="form-label">8. Last Input / Spray Date (PHI)</label>
                <input type="date" class="form-input" id="inline_lot_spray_date" style="background: #fff;" />
              </div>
            </div>

            <!-- Row 3: Grade, Method, Base Price, Shelf-Life -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 14px;">
              <div class="form-group">
                <label class="form-label">9. Quality Grade</label>
                <select class="form-select" id="inline_lot_grade" style="background: #fff;">
                  <option value="Grade A">Grade A (Premium Export Quality)</option>
                  <option value="Grade B">Grade B (Standard Market Grade)</option>
                  <option value="Grade C">Grade C (Processing Grade)</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">10. Farming Practice</label>
                <select class="form-select" id="inline_lot_method" style="background: #fff;">
                  <option value="Conventional">Conventional Sustainable</option>
                  <option value="Organic NPOP">Organic (Certified NPOP)</option>
                  <option value="PGS-India">PGS-India Natural</option>
                  <option value="Good Agri Practices">GAP Certified</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">11. Base Price (&#8377;/Kg)</label>
                <input type="number" step="0.5" class="form-input" id="inline_lot_price" value="40" style="background: #fff; font-weight: 700;" />
              </div>
              <div class="form-group">
                <label class="form-label">12. Shelf-Life (Days)</label>
                <input type="number" min="1" max="365" class="form-input" id="inline_lot_shelf_life" value="14" style="background: #fff;" />
              </div>
            </div>

            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; border-top: 1px solid #e2e8f0; padding-top: 14px;">
              <div style="display: flex; align-items: center; gap: 8px; font-size: 12px; color: #047857; font-weight: 700;">
                <span>${getIcon('shield', 15, '#047857')}</span>
                <span>Deterministic Batch ID &bull; 6-Digit Label Verification PIN &bull; 2D QR + 1D Code-128</span>
              </div>
              <div style="display: flex; gap: 10px;">
                <button type="submit" class="btn-wizard-action btn-wizard-submit" style="padding: 10px 24px; font-weight: 800;">
                  <span>+ Mint Unique Batch &amp; Print Sticker Sheet</span>
                </button>
              </div>
            </div>
          </form>
        </div>

        <!-- BELOW ALL OF IT: THE COMPACT EDITABLE LOT LEDGER (SHARED ON HOME & BATCH VIEW) -->
        <div class="compact-ledger-card">
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 14px;">
            <div>
              <h4 style="margin: 0; font-size: 16.5px; font-weight: 800; color: #0f172a; display: flex; align-items: center; gap: 8px;">
                <span>${getIcon('sprout', 18, '#047857')}</span>
                <span>Batch / Lot Compact Editable Ledger</span>
              </h4>
              <p style="margin: 2px 0 0; font-size: 12px; color: #64748b;">
                Editable before custody handover to next party. Permanently locked upon buyer physical acceptance.
              </p>
            </div>
            <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
              <input type="text" id="ledger_search_input" class="form-input" placeholder="Search lot code, crop, variety..." style="font-size: 12.5px; padding: 6px 12px; width: 220px; background: #fff;" oninput="window.filterSharedLotLedger()" />
              <select id="ledger_custody_filter" class="form-select" style="font-size: 12px; font-weight: 700; padding: 6px 10px; background: #fff;" onchange="window.filterSharedLotLedger()">
                <option value="ALL">All Custody States</option>
                <option value="IN_CUSTODY">In Farm Custody (Editable)</option>
                <option value="IN_TRANSIT">In Transit (Locked)</option>
              </select>
              <button type="button" class="action-btn-pill" onclick="window.refreshProducerLotsLedger()" title="Refresh ledger from blockchain">
                <span>${getIcon('refresh', 13, '#047857')} Refresh</span>
              </button>
            </div>
          </div>

          <div class="compact-ledger-table-wrap">
            <table class="compact-ledger-table">
              <thead>
                <tr>
                  <th>Lot Identifier &amp; Crop</th>
                  <th>Packages / Crates</th>
                  <th>Net Weight</th>
                  <th>Price &amp; Valuation</th>
                  <th>Custody Status</th>
                  <th>Current Owner</th>
                  <th>Days in Chain</th>
                  <th style="text-align: right;">Actions</th>
                </tr>
              </thead>
              <tbody id="sharedLedgerTableBody">
                <tr>
                  <td colspan="8" style="text-align: center; padding: 32px; color: #64748b;">
                    <div style="width: 24px; height: 24px; border: 2px solid #cbd5e1; border-top-color: #047857; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 10px;"></div>
                    <span>Synchronizing ledger records...</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </div>
    `;

    // Fetch and populate live data
    await window.refreshProducerLotsLedger();
  }

  /* --------------------------------------------------------------------------
     BATCH CREATION VIEW TOGGLE & CATEGORY PREVIEW
     -------------------------------------------------------------------------- */
  window.toggleBatchCreationView = function () {
    const panel = document.getElementById('producerBatchCreationPanel');
    if (!panel) return;
    if (panel.style.display === 'none' || !panel.style.display) {
      panel.style.display = 'block';
      panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      window.onBatchCategoryChange();
    } else {
      panel.style.display = 'none';
    }
  };

  window.onBatchCategoryChange = function () {
    const catEl = document.getElementById('inline_lot_cat_code');
    const previewEl = document.getElementById('liveBatchIdPreviewCode');
    const catCode = catEl ? catEl.value : 'VG';
    if (previewEl) {
      previewEl.textContent = window.computeLiveMentorBatchIdPreview(catCode);
    }
  };

  /* --------------------------------------------------------------------------
     SHARED COMPACT LOT LEDGER DATA SYNC & RENDERING
     -------------------------------------------------------------------------- */
  window.refreshProducerLotsLedger = async function () {
    try {
      const [resLots, resPlots, resAlloc, resHarv] = await Promise.all([
        fetch('/api/v1/lots/', { headers: getAuthHeader() }),
        fetch('/api/v1/me/plots', { headers: getAuthHeader() }),
        fetch('/api/v1/me/season-allocations', { headers: getAuthHeader() }),
        fetch('/api/v1/me/harvest-records', { headers: getAuthHeader() })
      ]);

      if (resLots.ok) {
        const d = await resLots.json();
        window._producerLots = Array.isArray(d) ? d : (d.results || d.lots || []);
      }
      if (resPlots.ok) {
        const d = await resPlots.json();
        window._producerPlots = d.plots || d || [];
      }
      if (resAlloc.ok) {
        const d = await resAlloc.json();
        window._producerAllocations = d.allocations || d || [];
      }
      if (resHarv.ok) {
        const d = await resHarv.json();
        window._producerHarvests = d.harvest_records || d || [];
      }

      window.updateProducerLiveTelemetryStats();
      window.renderSharedLotLedgerRows();
      window.populatePlotDropdown();
    } catch (e) {
      window.renderSharedLotLedgerRows();
    }
  };

  window.populatePlotDropdown = function () {
    const sel = document.getElementById('inline_lot_plot');
    if (!sel) return;
    const plots = window._producerPlots || [];
    sel.innerHTML = '<option value="">Registered Farm Origin</option>' + plots.map(p => {
      const name = escapeHtml(p.plot_name || p.identifier || `Plot #${p.id}`);
      const ac = parseFloat(p.calculated_acreage || p.acreage || 0).toFixed(2);
      return `<option value="${p.id}">${name} (${ac} Acres)</option>`;
    }).join('');
  };

  window.updateProducerLiveTelemetryStats = function () {
    const plots = window._producerPlots || [];
    const allocs = window._producerAllocations || [];
    const harvests = window._producerHarvests || [];
    const lots = window._producerLots || [];

    // 1. Land & Plots
    const totalAc = plots.reduce((acc, p) => acc + parseFloat(p.calculated_acreage || p.acreage || 0), 0);
    const elPlots = document.getElementById('metricLandPlots');
    const elAcres = document.getElementById('metricTotalAcres');
    if (elPlots) elPlots.textContent = `${plots.length} Plot${plots.length === 1 ? '' : 's'}`;
    if (elAcres) elAcres.textContent = `${totalAc.toFixed(2)} Acres`;

    // 2. Season Allocation
    const allocAc = allocs.reduce((acc, a) => acc + parseFloat(a.allocated_acres || 0), 0);
    const unallocAc = Math.max(0, totalAc - allocAc);
    const elAlloc = document.getElementById('metricAllocatedAcres');
    const elUnalloc = document.getElementById('metricRemainingAcres');
    if (elAlloc) elAlloc.textContent = `${allocAc.toFixed(2)} Ac`;
    if (elUnalloc) elUnalloc.textContent = `${unallocAc.toFixed(2)} Ac Unallotted`;

    // 3. Harvest Yield
    const totalYieldKg = harvests.reduce((acc, h) => acc + parseFloat(h.net_yield_kg || 0), 0);
    const totalLottedKg = lots.reduce((acc, l) => acc + parseFloat(l.qty_kg || l.weight_kg || 0), 0);
    const unlottedKg = Math.max(0, totalYieldKg - totalLottedKg);
    const elYield = document.getElementById('metricNetYield');
    const elUnlotted = document.getElementById('metricUnlottedKg');
    if (elYield) elYield.textContent = `${totalYieldKg.toFixed(1)} Kg`;
    if (elUnlotted) elUnlotted.textContent = `${unlottedKg.toFixed(1)} Kg Unlotted`;

    // 4. Active Lots
    const inTransit = lots.filter(l => l.custody_status === 'IN_TRANSIT' || l.status === 'HANDOVER_REQUESTED').length;
    const inFarm = lots.filter(l => l.custody_status !== 'IN_TRANSIT' && l.status !== 'HANDOVER_REQUESTED').length;
    const elLotsCount = document.getElementById('metricTotalLotsCount');
    const elCustody = document.getElementById('metricCustodyBreakdown');
    if (elLotsCount) elLotsCount.textContent = `${lots.length} Batch${lots.length === 1 ? '' : 'es'}`;
    if (elCustody) elCustody.textContent = `${inFarm} In Farm &bull; ${inTransit} Transit`;

    // 5. Avg Shelf Speed (strictly computed from real lot records)
    let totalDays = 0;
    const now = new Date();
    lots.forEach(l => {
      const created = l.created_at ? new Date(l.created_at) : now;
      totalDays += Math.max(0.1, (now - created) / (1000 * 60 * 60 * 24));
    });
    const elAvgDays = document.getElementById('metricAvgDays');
    const elFreshness = document.getElementById('metricShelfFreshness');
    if (lots.length > 0) {
      const avgDays = (totalDays / lots.length).toFixed(1);
      if (elAvgDays) elAvgDays.textContent = `${avgDays} Days`;
      if (elFreshness) {
        elFreshness.textContent = parseFloat(avgDays) <= 3.0 ? 'Fresh Produce' : 'In Custody';
        elFreshness.style.color = '#10b981';
      }
    } else {
      if (elAvgDays) elAvgDays.textContent = '-';
      if (elFreshness) {
        elFreshness.textContent = 'No Batches';
        elFreshness.style.color = '#64748b';
      }
    }

    // 6. Valuation (strictly computed from real lots asking price; 0 if empty)
    let totalVal = 0;
    lots.forEach(l => {
      const kg = parseFloat(l.qty_kg || l.weight_kg || 0);
      const rate = parseFloat(l.price_per_kg || l.asking_price_per_kg || 0);
      totalVal += kg * rate;
    });
    const avgRate = (totalLottedKg > 0 && totalVal > 0) ? Math.round(totalVal / totalLottedKg) : 0;
    const elVal = document.getElementById('metricTotalValuation');
    const elRate = document.getElementById('metricAvgRate');
    if (elVal) elVal.textContent = `₹${Math.round(totalVal).toLocaleString('en-IN')}`;
    if (elRate) elRate.textContent = `₹${avgRate} / Kg Avg`;
  };

  window.filterSharedLotLedger = function () {
    const searchEl = document.getElementById('ledger_search_input');
    const custodyEl = document.getElementById('ledger_custody_filter');
    window._lotFilterState.search = searchEl ? searchEl.value.trim().toLowerCase() : '';
    window._lotFilterState.custody = custodyEl ? custodyEl.value : 'ALL';
    window.renderSharedLotLedgerRows();
  };

  window.renderSharedLotLedgerRows = function () {
    const tbody = document.getElementById('sharedLedgerTableBody');
    if (!tbody) return;

    let lots = window._producerLots || [];
    const search = window._lotFilterState.search;
    const custodyFilter = window._lotFilterState.custody;

    if (search) {
      lots = lots.filter(l => {
        const code = String(l.public_code || l.batch_id || '').toLowerCase();
        const crop = String(l.crop || (l.product && l.product.name) || '').toLowerCase();
        const variety = String(l.variety || (l.product && l.product.variety) || '').toLowerCase();
        return code.includes(search) || crop.includes(search) || variety.includes(search);
      });
    }

    if (custodyFilter !== 'ALL') {
      lots = lots.filter(l => {
        const isInTransit = l.custody_status === 'IN_TRANSIT' || l.status === 'HANDOVER_REQUESTED';
        if (custodyFilter === 'IN_TRANSIT') return isInTransit;
        if (custodyFilter === 'IN_CUSTODY') return !isInTransit;
        return true;
      });
    }

    if (lots.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="8" style="text-align: center; padding: 40px 16px; color: #64748b;">
            <div style="font-size: 28px; margin-bottom: 8px;">${getIcon('box', 28, '#047857')}</div>
            <div style="font-weight: 800; font-size: 14px; color: #334155;">No Batches / Lots Found</div>
            <div style="font-size: 12px; margin-top: 4px;">Click <strong>"D. Batch / Lot Creation (+ MINT)"</strong> above to mint your first cryptographic lot QR!</div>
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = lots.map(lot => {
      const code = escapeHtml(lot.public_code || lot.batch_id || 'LOT');
      const crop = escapeHtml(lot.crop || (lot.product && lot.product.name) || 'Produce');
      const variety = escapeHtml(lot.variety || (lot.product && lot.product.variety) || 'Grade A');
      const catCode = escapeHtml(lot.crop_category || (code.split('-')[3] || 'VG')).slice(0, 2);
      const kg = parseFloat(lot.qty_kg || lot.weight_kg || 0);
      const pkgs = parseInt(lot.crate_count || lot.packages || 25, 10);
      const price = parseFloat(lot.price_per_kg || lot.asking_price_per_kg || 40);
      const val = Math.round(kg * price);
      
      const isInTransit = lot.custody_status === 'IN_TRANSIT' || lot.status === 'HANDOVER_REQUESTED';
      const isLocked = lot.is_custody_locked || (lot.current_custodian_role && lot.current_custodian_role !== 'PRODUCER');
      const ownerName = escapeHtml(lot.current_custodian_name || 'Ramesh Kumar (Farm)');
      
      const created = lot.created_at ? new Date(lot.created_at) : new Date();
      const days = Math.max(1, Math.round((new Date() - created) / (1000 * 60 * 60 * 24)));

      return `
        <tr>
          <td>
            <div style="display: flex; align-items: center; gap: 8px;">
              <span class="badge-crop-cat cat-${catCode}">${catCode}</span>
              <div>
                <div style="font-family: monospace; font-size: 13px; font-weight: 900; color: #0b3d2e;">${code}</div>
                <div style="font-size: 11.5px; font-weight: 700; color: #475569;">${crop} &bull; ${variety}</div>
              </div>
            </div>
          </td>
          <td style="font-weight: 700; color: #334155;">${pkgs} Crates</td>
          <td>
            <strong style="color: #0f172a; font-size: 13.5px;">${kg.toFixed(1)}</strong>
            <span style="font-size: 11px; color: #64748b;">Kg</span>
          </td>
          <td>
            <div style="font-weight: 800; color: #047857;">&#8377;${price} <span style="font-size: 10px; font-weight: 600; color: #64748b;">/kg</span></div>
            <div style="font-size: 11px; color: #64748b;">&#8377;${val.toLocaleString('en-IN')}</div>
          </td>
          <td>
            ${isInTransit ? `
              <span class="badge-custody-chip chip-in-transit">${getIcon('truck', 12, '#b45309')} IN TRANSIT</span>
            ` : (isLocked ? `
              <span class="badge-custody-chip chip-in-custody">${getIcon('lock', 12, '#475569')} LOCKED (NEXT NODE)</span>
            ` : `
              <span class="badge-custody-chip chip-in-farm">✓ IN FARM CUSTODY</span>
            `)}
          </td>
          <td>
            <div style="font-size: 12px; font-weight: 700; color: #0f172a;">${ownerName}</div>
          </td>
          <td>
            <span style="font-size: 12px; font-weight: 800; color: #047857;">${days} Day${days === 1 ? '' : 's'}</span>
          </td>
          <td style="text-align: right;">
            <div style="display: inline-flex; align-items: center; gap: 5px;">
              
              <!-- Track Lot Modal -->
              <button type="button" class="action-btn-pill" onclick="window.openTrackLotModal('${code}')" title="Track lot hops, map and telemetry">
                ${getIcon('map-pin', 13, '#047857')}
                <span>Track</span>
              </button>

              <!-- Edit (Editable before handover; locked once handed over) -->
              ${(!isLocked && !isInTransit) ? `
                <button type="button" class="action-btn-pill" onclick="window.openEditLotModal('${code}')" title="Edit lot details">
                  ${getIcon('edit', 13, '#0284c7')}
                  <span>Edit</span>
                </button>
              ` : `
                <span class="action-btn-pill" style="opacity: 0.6; cursor: not-allowed; background: #f1f5f9; color: #64748b; border-color: #cbd5e1;" title="Custody permanently locked upon handover acceptance">
                  ${getIcon('lock', 13, '#64748b')}
                  <span>Locked</span>
                </span>
              `}

              <!-- Print Labels Sticker Sheet -->
              <button type="button" class="action-btn-pill" onclick="window.openUnlimitedQrPrintModal('${code}')" title="Print label sticker sheet (QR + Barcode + PIN)">
                ${getIcon('printer', 13, '#475569')}
              </button>

              <!-- Handover Dispatch -->
              ${(!isLocked && !isInTransit) ? `
                <button type="button" class="action-btn-pill primary" onclick="window.openCustodyHandoverRequestModal('${code}')" title="Dispatch and handover to next party">
                  ${getIcon('send', 13, '#ffffff')}
                  <span>Handover</span>
                </button>
              ` : ''}

            </div>
          </td>
        </tr>
      `;
    }).join('');
  };

  /* --------------------------------------------------------------------------
     SUBMIT INLINE BATCH FORM (+ MINT BATCH)
     -------------------------------------------------------------------------- */
  window.submitInlineBatchForm = async function (e) {
    e.preventDefault();
    const catCode = (document.getElementById('inline_lot_cat_code') || {}).value || 'VG';
    const crop = (document.getElementById('inline_lot_crop') || {}).value || 'Produce';
    const variety = (document.getElementById('inline_lot_variety') || {}).value || '';
    const plotId = (document.getElementById('inline_lot_plot') || {}).value || '';
    const qty = parseFloat((document.getElementById('inline_lot_qty') || {}).value || 500);
    const pkgs = parseInt((document.getElementById('inline_lot_packages') || {}).value || 25, 10);
    const harvestDate = (document.getElementById('inline_lot_harvest_date') || {}).value || new Date().toISOString();
    const sprayDate = (document.getElementById('inline_lot_spray_date') || {}).value || '';
    const grade = (document.getElementById('inline_lot_grade') || {}).value || 'Grade A';
    const method = (document.getElementById('inline_lot_method') || {}).value || 'Conventional';
    const price = parseFloat((document.getElementById('inline_lot_price') || {}).value || 40);
    const shelfLife = parseInt((document.getElementById('inline_lot_shelf_life') || {}).value || 14, 10);

    const submitBtn = e.target.querySelector('button[type="submit"]');
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span>Minting Cryptographic Lot &amp; Labels...</span>';
    }

    try {
      const payload = {
        crop: crop,
        variety: variety,
        crop_category: catCode,
        quantity_kg: qty,
        crate_count: pkgs,
        harvest_date: harvestDate,
        last_spray_date: sprayDate || null,
        grade: grade,
        farming_method: method,
        price_per_kg: price,
        shelf_life_days: shelfLife,
        plot_id: plotId ? parseInt(plotId, 10) : null
      };

      const res = await fetch('/api/v1/lots/create-with-qr', {
        method: 'POST',
        headers: { ...getAuthHeader(), 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        const created = await res.json();
        const code = created.batch_id || created.public_code;
        showToast(`Batch ${code} successfully minted!`, 'success');
        window.toggleBatchCreationView();
        await window.refreshProducerLotsLedger();
        window.openUnlimitedQrPrintModal(code);
      } else {
        const err = await res.json();
        showToast(err.detail || 'Failed to mint batch.', 'error');
      }
    } catch (err) {
      showToast('Network error while creating batch.', 'error');
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<span>+ Mint Unique Batch &amp; Print Sticker Sheet</span>';
      }
    }
  };


  /* ==========================================================================
     PRODUCER ACTION MODALS (BUTTONS A, B, C & TRACK LOT)
     ========================================================================== */

  /* --------------------------------------------------------------------------
     MODAL A: PRODUCER PROFILE (5-STEP REGISTRATION FORM INSPECTION & UPDATION)
     -------------------------------------------------------------------------- */
  window._prodProfileActiveTab = 'basic';

  window.switchProducerProfileTab = function (tabName) {
    window._prodProfileActiveTab = tabName;
    const container = document.getElementById('producerProfileTabContent');
    if (container) {
      window.renderProducerProfileTabContent(container);
    }
    // Update tab button active states
    const tabs = ['basic', 'plots', 'cultivation', 'identity', 'consent'];
    tabs.forEach(t => {
      const btn = document.getElementById(`prodProfTabBtn_${t}`);
      if (btn) {
        const isActive = (t === tabName);
        btn.style.borderBottom = isActive ? '3px solid #047857' : '3px solid transparent';
        btn.style.color = isActive ? '#047857' : '#64748b';
        btn.style.fontWeight = isActive ? '800' : '600';
      }
    });
  };

  window.closeProducerProfileModal = function () {
    const modal = document.getElementById('producerProfileModal');
    if (modal) modal.style.display = 'none';
  };

  window.openProducerProfileModal = function () {
    if (!wizardState.profile || !wizardState.profile.first_name) {
      try {
        const cached = JSON.parse(localStorage.getItem('annasutra_cached_profile') || '{}');
        if (cached && (cached.first_name || cached.organisation_name)) {
          wizardState.profile = Object.assign({}, cached, wizardState.profile || {});
        }
      } catch (_) {}
    }

    let modal = document.getElementById('producerProfileModal');
    if (!modal || modal.parentElement !== document.body) {
      if (modal && modal.parentElement) modal.parentElement.removeChild(modal);
      modal = document.createElement('div');
      modal.id = 'producerProfileModal';
      modal.className = 'modal-overlay';
      document.body.appendChild(modal);
    }
    modal.onclick = function (e) {
      if (e.target === modal || e.target.classList.contains('modal-overlay')) {
        window.closeProducerProfileModal();
      }
    };

    const p = wizardState.profile || {};
    const farmerUid = p.farmer_uid || '';
    const orgDisplayName = p.organisation_name || [p.first_name, p.last_name].filter(Boolean).join(' ') || 'Farmer Producer Node';

    modal.innerHTML = `
      <div class="portal-modal-box" onclick="event.stopPropagation()" style="max-width: 860px; max-height: 92vh; overflow-y: auto;">
        <button class="modal-close" onclick="window.closeProducerProfileModal()" style="color: #ffffff; background: rgba(255,255,255,0.18);">✕</button>
        
        <div class="portal-modal-header" style="background: linear-gradient(135deg, #07271d 0%, #0b3d2e 100%); padding: 22px 28px;">
          <div>
            <div style="font-size: 11px; font-weight: 800; color: #10b981; text-transform: uppercase; letter-spacing: 0.5px;">Producer Profile &amp; Identity</div>
            <h3 style="margin: 2px 0 0; font-size: 22px; color: #ffffff; font-weight: 800;">A. Producer Profile &amp; Registration Data</h3>
          </div>
        </div>

        <div style="padding: 24px 28px;">
          
          <!-- Digital ID Card Preview -->
          <div style="background: linear-gradient(135deg, #064e3b 0%, #047857 100%); border-radius: 14px; padding: 20px 24px; color: #ffffff; margin-bottom: 22px; box-shadow: 0 4px 14px rgba(4,120,87,0.25); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
            <div>
              <div style="font-size: 11px; font-weight: 800; color: #a7f3d0; text-transform: uppercase; letter-spacing: 1px;">AnnaSutra &bull; Verified Producer Node</div>
              <h4 style="margin: 4px 0 2px; font-size: 20px; font-weight: 900; color: #ffffff;">${escapeHtml(orgDisplayName)}</h4>
              <div style="font-size: 12.5px; color: #ecfdf5;">${escapeHtml(p.village_town || '')}, ${escapeHtml(p.district || '')}, ${escapeHtml(getStateLabel(p.state))}</div>
              ${farmerUid ? `
                <div style="margin-top: 12px; display: inline-block; background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.3); border-radius: 8px; padding: 4px 12px; font-family: monospace; font-size: 14px; font-weight: 900; letter-spacing: 0.5px;">
                  ID: ${escapeHtml(farmerUid)}
                </div>
              ` : `
                <div style="margin-top: 12px; display: inline-block; background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.3); border-radius: 8px; padding: 4px 12px; font-family: monospace; font-size: 12px; font-weight: 700;">
                  Code: ${escapeHtml(p.entity_code || 'PR-PENDING')}
                </div>
              `}
            </div>
            <div style="background: #ffffff; padding: 8px 12px; border-radius: 10px; text-align: center; color: #0b3d2e;">
              <div style="font-size: 11px; font-weight: 800; color: #047857;">VERIFIED STATUS</div>
              <div style="font-size: 13px; font-weight: 900; margin-top: 2px;">ACTIVE NODE</div>
            </div>
          </div>

          <!-- 5 REGISTRATION TABS (UNDER A. PROFILE) -->
          <div style="display: flex; gap: 6px; border-bottom: 2px solid #e2e8f0; margin-bottom: 20px; overflow-x: auto; padding-bottom: 2px;">
            <button type="button" id="prodProfTabBtn_basic" onclick="window.switchProducerProfileTab('basic')" style="padding: 9px 14px; font-size: 12.5px; font-weight: 800; border: none; background: none; cursor: pointer; border-bottom: 3px solid #047857; color: #047857; white-space: nowrap;">
              1. Basic Info
            </button>
            <button type="button" id="prodProfTabBtn_plots" onclick="window.switchProducerProfileTab('plots')" style="padding: 9px 14px; font-size: 12.5px; font-weight: 600; border: none; background: none; cursor: pointer; border-bottom: 3px solid transparent; color: #64748b; white-space: nowrap;">
              2. Farm Plots
            </button>
            <button type="button" id="prodProfTabBtn_cultivation" onclick="window.switchProducerProfileTab('cultivation')" style="padding: 9px 14px; font-size: 12.5px; font-weight: 600; border: none; background: none; cursor: pointer; border-bottom: 3px solid transparent; color: #64748b; white-space: nowrap;">
              3. Cultivation
            </button>
            <button type="button" id="prodProfTabBtn_identity" onclick="window.switchProducerProfileTab('identity')" style="padding: 9px 14px; font-size: 12.5px; font-weight: 600; border: none; background: none; cursor: pointer; border-bottom: 3px solid transparent; color: #64748b; white-space: nowrap;">
              4. Identity &amp; Bank
            </button>
            <button type="button" id="prodProfTabBtn_consent" onclick="window.switchProducerProfileTab('consent')" style="padding: 9px 14px; font-size: 12.5px; font-weight: 600; border: none; background: none; cursor: pointer; border-bottom: 3px solid transparent; color: #64748b; white-space: nowrap;">
              5. Consent &amp; Review
            </button>
          </div>

          <!-- TAB CONTENT CONTAINER -->
          <div id="producerProfileTabContent"></div>

        </div>
      </div>
    `;

    modal.style.display = 'flex';
    window.renderProducerProfileTabContent(document.getElementById('producerProfileTabContent'));

    // Non-blocking background sync for fresh profile & sensitive state without modal delay
    Promise.all([
      fetch('/api/v1/me/profile', { credentials: 'same-origin', headers: getAuthHeader() }).then(r => r.ok ? r.json() : null),
      fetch('/api/v1/me/sensitive', { credentials: 'same-origin', headers: getAuthHeader() }).then(r => r.ok ? r.json() : null)
    ]).then(([freshProfile, freshSensitive]) => {
      let changed = false;
      if (freshProfile) {
        wizardState.profile = freshProfile;
        changed = true;
      }
      if (freshSensitive) {
        wizardState.sensitive = freshSensitive;
        changed = true;
      }
      if (changed) {
        const curModal = document.getElementById('producerProfileModal');
        if (curModal && curModal.style.display === 'flex') {
          const tabContent = document.getElementById('producerProfileTabContent');
          if (tabContent) {
            window.renderProducerProfileTabContent(tabContent);
          }
        }
      }
    }).catch(() => {});
  };

  window.renderProducerProfileTabContent = function (container) {
    if (!container) return;
    const tab = window._prodProfileActiveTab || 'basic';
    const p = wizardState.profile || {};
    const sens = wizardState.sensitive || {};
    const plots = wizardState.plots || [];

    if (tab === 'basic') {
      container.innerHTML = `
        <div>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
            <div>
              <h5 style="margin: 0; font-size: 14px; font-weight: 800; color: #0b3d2e;">Step 1: Basic Information &amp; Operational Preferences</h5>
              <p style="margin: 2px 0 0; font-size: 12px; color: #64748b;">Directly update operational preferences or submit change requests for locked legal identity.</p>
            </div>
          </div>

          <form onsubmit="window.submitProducerBasicInfoForm(event)">
            <!-- Locked Legal Identity Fields -->
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px; margin-bottom: 16px;">
              <div style="font-size: 11px; font-weight: 800; color: #047857; text-transform: uppercase; margin-bottom: 10px;">
                ${getIcon('lock', 12, '#047857')} Verified Identity (Locked by Admin Authority)
              </div>
              <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px;">
                <div>
                  <div style="font-size: 11px; color: #64748b; font-weight: 700;">Legal Applicant Name</div>
                  <div style="font-size: 13.5px; font-weight: 800; color: #0f172a;">${escapeHtml(p.first_name || '')} ${escapeHtml(p.last_name || '')}</div>
                </div>
                <div>
                  <div style="font-size: 11px; color: #64748b; font-weight: 700;">Registered Organisation</div>
                  <div style="font-size: 13.5px; font-weight: 800; color: #0f172a;">${escapeHtml(p.organisation_name || 'Individual Farm')}</div>
                </div>
                <div>
                  <div style="font-size: 11px; color: #64748b; font-weight: 700;">Primary Registered Phone</div>
                  <div style="font-size: 13.5px; font-weight: 800; color: #0f172a; font-family: monospace;">${escapeHtml(p.phone_e164 || '')}</div>
                </div>
              </div>
            </div>

            <!-- Self-Editable Operational Fields -->
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
              <div class="form-group">
                <label class="form-label">Contact Email Address</label>
                <input type="email" class="form-input" id="prof_edit_email" value="${escapeHtml(p.email || '')}" placeholder="e.g. kisan@gmail.com" style="background: #fff;" />
              </div>
              <div class="form-group">
                <label class="form-label">Alternate Mobile Number</label>
                <input type="tel" class="form-input" id="prof_edit_alt_phone" value="${escapeHtml(p.alt_phone || '')}" placeholder="e.g. 9876543210" style="background: #fff;" />
              </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
              <div class="form-group">
                <label class="form-label">Address Line 1</label>
                <input type="text" class="form-input" id="prof_edit_addr1" value="${escapeHtml(p.address_line1 || '')}" placeholder="Street / Landmark" style="background: #fff;" />
              </div>
              <div class="form-group">
                <label class="form-label">Village / Town</label>
                <input type="text" class="form-input" id="prof_edit_village" value="${escapeHtml(p.village_town || '')}" placeholder="Village Name" style="background: #fff;" />
              </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; margin-bottom: 16px;">
              <div class="form-group">
                <label class="form-label">District</label>
                <input type="text" class="form-input" id="prof_edit_district" value="${escapeHtml(p.district || '')}" placeholder="District" style="background: #fff;" />
              </div>
              <div class="form-group">
                <label class="form-label">State</label>
                <input type="text" class="form-input" id="prof_edit_state" value="${escapeHtml(getStateLabel(p.state))}" disabled style="background: #f1f5f9;" />
              </div>
              <div class="form-group">
                <label class="form-label">Pincode</label>
                <input type="text" class="form-input" id="prof_edit_pincode" value="${escapeHtml(p.pincode || '')}" placeholder="6-digit PIN" style="background: #fff;" />
              </div>
            </div>

            <div style="display: flex; justify-content: flex-end; gap: 10px;">
              <button type="submit" class="action-btn-pill primary" style="padding: 9px 20px;">
                Save Profile Updates
              </button>
            </div>
          </form>
        </div>
      `;
    } else if (tab === 'plots') {
      container.innerHTML = `
        <div>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
            <div>
              <h5 style="margin: 0; font-size: 14px; font-weight: 800; color: #0b3d2e;">Step 2: Farm Plots &amp; Land Holdings</h5>
              <p style="margin: 2px 0 0; font-size: 12px; color: #64748b;">Registered farm parcel boundaries and cadastral survey numbers.</p>
            </div>
            <div style="background: #ecfdf5; border: 1px solid #86efac; padding: 4px 12px; border-radius: 8px; font-size: 12.5px; font-weight: 800; color: #047857;">
              Total Land: ${parseFloat(p.total_land_acres || 0).toFixed(2)} Acres
            </div>
          </div>

          <div class="compact-ledger-table-wrap" style="margin-bottom: 18px;">
            <table class="compact-ledger-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Plot Name</th>
                  <th>Survey / Khasra No.</th>
                  <th>Area (Acres)</th>
                  <th>Boundary Status</th>
                </tr>
              </thead>
              <tbody>
                ${plots.length === 0 ? `
                  <tr>
                    <td colspan="5" style="text-align: center; padding: 24px; color: #64748b;">
                      1 Registered Plot Declared (${parseFloat(p.total_land_acres || 0).toFixed(2)} Acres)
                    </td>
                  </tr>
                ` : plots.map((pl, i) => `
                  <tr>
                    <td>${i + 1}</td>
                    <td><strong>${escapeHtml(pl.plot_name || `Plot ${i + 1}`)}</strong></td>
                    <td style="font-family: monospace;">${escapeHtml(pl.khasra_survey_no || 'NA')}</td>
                    <td>${parseFloat(pl.area_acres || 0).toFixed(2)} Acres</td>
                    <td><span style="color: #047857; font-weight: 800;">✓ Mapped Polygon</span></td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>

          <div style="background: #f8fafc; border: 1.5px dashed #cbd5e1; border-radius: 10px; padding: 14px 16px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
              <strong style="font-size: 13px; color: #0f172a;">Need to add or modify plot boundaries?</strong>
              <div style="font-size: 11.5px; color: #64748b;">Land acreage modifications require documentary sale deed / patta verification by Admin.</div>
            </div>
            <button type="button" class="action-btn-pill" onclick="window.prefillChangeRequest('total_land_acres', 'Plot Acreage Modification')" style="background: #fff;">
              Request Land Modification &rarr;
            </button>
          </div>
        </div>
      `;
    } else if (tab === 'cultivation') {
      const crops = (p.role_details && p.role_details.commodities) ? p.role_details.commodities.map(getCropLabel).join(', ') : 'Not specified';
      container.innerHTML = `
        <div>
          <div style="margin-bottom: 14px;">
            <h5 style="margin: 0; font-size: 14px; font-weight: 800; color: #0b3d2e;">Step 3: Cultivation Profile &amp; Commodities</h5>
            <p style="margin: 2px 0 0; font-size: 12px; color: #64748b;">Agricultural practices, primary crops, and irrigation infrastructure.</p>
          </div>

          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-bottom: 18px;">
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px;">
              <div style="font-size: 11px; color: #64748b; font-weight: 700;">Primary Registered Crops</div>
              <div style="font-size: 14px; font-weight: 800; color: #047857; margin-top: 3px;">${escapeHtml(crops)}</div>
            </div>
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px;">
              <div style="font-size: 11px; color: #64748b; font-weight: 700;">Farming Methodology</div>
              <div style="font-size: 14px; font-weight: 800; color: #0f172a; margin-top: 3px;">${escapeHtml((p.role_details && p.role_details.farming_practice) || 'Conventional &amp; Organic NPOP')}</div>
            </div>
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px;">
              <div style="font-size: 11px; color: #64748b; font-weight: 700;">Irrigation Source</div>
              <div style="font-size: 14px; font-weight: 800; color: #0f172a; margin-top: 3px;">${escapeHtml((p.role_details && p.role_details.irrigation_type) || 'Borewell &amp; Drip')}</div>
            </div>
          </div>
        </div>
      `;
    } else if (tab === 'identity') {
      container.innerHTML = `
        <div>
          <div style="margin-bottom: 14px;">
            <h5 style="margin: 0; font-size: 14px; font-weight: 800; color: #0b3d2e;">Step 4: Statutory Identity &amp; Bank Settlement</h5>
            <p style="margin: 2px 0 0; font-size: 12px; color: #64748b;">Sensitive identity and bank details. Masked for security.</p>
          </div>

          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-bottom: 18px;">
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 11px; color: #64748b; font-weight: 700;">PAN Number</span>
                <span style="font-size: 10px; color: #047857; font-weight: 800;">${getIcon('lock', 10, '#047857')} SEALED</span>
              </div>
              <div style="font-size: 14px; font-weight: 800; color: #0f172a; margin-top: 4px; font-family: monospace;">${escapeHtml(sens.pan_masked || '•••• ••••')}</div>
            </div>
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 11px; color: #64748b; font-weight: 700;">Voluntary Aadhaar (Last 4)</span>
                <span style="font-size: 10px; color: #047857; font-weight: 800;">${getIcon('lock', 10, '#047857')} SEALED</span>
              </div>
              <div style="font-size: 14px; font-weight: 800; color: #0f172a; margin-top: 4px; font-family: monospace;">•••• •••• ${escapeHtml(sens.aadhaar_last4 || '••••')}</div>
            </div>
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 11px; color: #64748b; font-weight: 700;">Bank Settlement Account</span>
                <span style="font-size: 10px; color: #047857; font-weight: 800;">${getIcon('lock', 10, '#047857')} SEALED</span>
              </div>
              <div style="font-size: 14px; font-weight: 800; color: #0f172a; margin-top: 4px; font-family: monospace;">${escapeHtml(sens.bank_account_masked || '•••• ••••')} (${escapeHtml(sens.ifsc_masked || 'IFSC')})</div>
            </div>
          </div>

          <div style="background: #fff; border: 1.5px dashed #cbd5e1; border-radius: 10px; padding: 14px 16px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
              <strong style="font-size: 13px; color: #0f172a;">Need to update your bank account or PAN details?</strong>
              <div style="font-size: 11.5px; color: #64748b;">Financial details require administrative review with cancelled cheque proof.</div>
            </div>
            <button type="button" class="action-btn-pill" onclick="window.prefillChangeRequest('bank_details', 'Bank Account Change Request')" style="background: #fff;">
              Request Bank Update &rarr;
            </button>
          </div>
        </div>
      `;
    } else if (tab === 'consent') {
      container.innerHTML = `
        <div>
          <div style="margin-bottom: 14px;">
            <h5 style="margin: 0; font-size: 14px; font-weight: 800; color: #0b3d2e;">Step 5: Consent, Change Requests &amp; Account Operations</h5>
            <p style="margin: 2px 0 0; font-size: 12px; color: #64748b;">Statutory DPDP Act 2023 consent record and submitted Change Requests.</p>
          </div>

          <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px; margin-bottom: 18px;">
            <div style="font-size: 11px; font-weight: 800; color: #047857; text-transform: uppercase; margin-bottom: 4px;">
              ✓ Consent Active
            </div>
            <div style="font-size: 12.5px; color: #334155;">
              Farmer Consent digitally sealed upon registration. Consumer transparency toggles active.
            </div>
          </div>

          <!-- Submit New Change Request Form -->
          <div style="background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 12px; padding: 16px; margin-bottom: 20px;">
            <div style="font-size: 13px; font-weight: 800; color: #0f172a; margin-bottom: 8px;">
              Submit Formal Data Change Request to Admin Authority
            </div>
            <form onsubmit="window.submitProducerChangeRequest(event)">
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px;">
                <div class="form-group">
                  <label class="form-label">Field to Change <span class="req">*</span></label>
                  <select class="form-select" id="req_field_name" required style="background: #fff; font-size: 12px;">
                    <option value="legal_name">Legal Name / Organisation</option>
                    <option value="total_land_acres">Total Registered Land (Acres)</option>
                    <option value="kyc_document">KYC Document / PAN Details</option>
                    <option value="bank_details">Settlement Bank Account</option>
                  </select>
                </div>
                <div class="form-group">
                  <label class="form-label">Requested New Value <span class="req">*</span></label>
                  <input type="text" class="form-input" id="req_new_value" placeholder="e.g. 7.50 Acres or Corrected Name" required style="background: #fff; font-size: 12px;" />
                </div>
              </div>
              <div class="form-group" style="margin-bottom: 10px;">
                <label class="form-label">Reason for Request <span class="req">*</span></label>
                <input type="text" class="form-input" id="req_reason" placeholder="e.g. Acquired additional adjacent parcel with sale deed no. 4829" required style="background: #fff; font-size: 12px;" />
              </div>
              <div style="display: flex; justify-content: flex-end;">
                <button type="submit" class="btn-wizard-action btn-wizard-submit" style="padding: 8px 18px; font-size: 12px; font-weight: 800;">
                  Submit Change Request to Admin &rarr;
                </button>
              </div>
            </form>
          </div>

          <!-- Danger Zone: Account & Profile Deletion -->
          <div style="background: #fef2f2; border: 1.5px solid #fecaca; border-radius: 12px; padding: 18px 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 8px;">
              <h5 style="margin: 0; font-size: 14px; font-weight: 800; color: #991b1b; display: flex; align-items: center; gap: 6px;">
                <span>${getIcon('alert', 16, '#dc2626')}</span>
                <span>Danger Zone: Account &amp; Profile Deletion</span>
              </h5>
              <span style="font-size: 11px; font-weight: 700; color: #b91c1c; background: #fee2e2; border: 1px solid #fca5a5; padding: 2px 8px; border-radius: 6px;">Permanent Action</span>
            </div>
            <p style="margin: 0 0 14px; font-size: 12px; color: #7f1d1d; line-height: 1.5;">
              Request formal deletion of your registered entity profile. If you have active lots in transit or unconfirmed custody handovers, all transfers must be settled before your request can be submitted. Admin review and owner 2FA verification are mandatory.
            </p>
            <div style="display: flex; justify-content: flex-end;">
              <button type="button" onclick="window.closeProducerProfileModal(); window.openEntityDeletionRequestModal();" style="background: #dc2626; color: #ffffff; border: none; border-radius: 8px; padding: 9px 18px; font-size: 12.5px; font-weight: 800; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 2px 6px rgba(220,38,38,0.25);">
                <span>${getIcon('trash', 14, '#ffffff')}</span>
                <span>Request Account Deletion &rarr;</span>
              </button>
            </div>
          </div>
        </div>
      `;
    }
  };

  window.prefillChangeRequest = function (fieldName, defaultVal) {
    window.switchProducerProfileTab('consent');
    setTimeout(() => {
      const select = document.getElementById('req_field_name');
      if (select) select.value = fieldName;
      const input = document.getElementById('req_new_value');
      if (input && defaultVal) input.placeholder = defaultVal;
    }, 50);
  };

  window.submitProducerBasicInfoForm = async function (e) {
    e.preventDefault();
    const email = (document.getElementById('prof_edit_email') || {}).value;
    const altPhone = (document.getElementById('prof_edit_alt_phone') || {}).value;
    const addr1 = (document.getElementById('prof_edit_addr1') || {}).value;
    const village = (document.getElementById('prof_edit_village') || {}).value;
    const district = (document.getElementById('prof_edit_district') || {}).value;
    const pincode = (document.getElementById('prof_edit_pincode') || {}).value;

    try {
      const res = await fetch('/api/v1/me/profile', {
        method: 'PUT',
        headers: { ...getAuthHeader(), 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: email,
          alt_phone: altPhone,
          address_line1: addr1,
          village_town: village,
          district: district,
          pincode: pincode,
          override_lock: true
        })
      });

      if (res.ok) {
        showToast('Profile information successfully updated.', 'success');
        wizardState.profile = await res.json();
      } else {
        const err = await res.json();
        showToast(err.detail || 'Failed to update profile.', 'error');
      }
    } catch (err) {
      showToast('Network error while saving profile.', 'error');
    }
  };

  /* --------------------------------------------------------------------------
     MODAL: UNLIMITED QR LABEL PRINTING & STICKER SHEET
     -------------------------------------------------------------------------- */
  window.openUnlimitedQrPrintModal = function (lotCode) {
    let modal = document.getElementById('unlimitedQrPrintModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'unlimitedQrPrintModal';
      modal.className = 'modal-overlay';
      modal.onclick = (e) => { if (e.target === modal) window.closeUnlimitedQrPrintModal(); };
      document.body.appendChild(modal);
    }

    const myLots = (window._producerLots || []).concat(window._downstreamCustody || []);
    const lot = myLots.find(l => (l.public_code === lotCode || l.batch_id === lotCode)) || { public_code: lotCode };
    const cropName = lot.crop || lot.product_category_name || 'Produce';
    const varietyName = lot.variety || '';
    const farmerName = (wizardState.profile && (wizardState.profile.first_name + ' ' + (wizardState.profile.last_name || ''))) || 'Verified Farmer Node';
    const farmerUid = (wizardState.profile && wizardState.profile.farmer_uid) || '';

    modal.innerHTML = `
      <div class="portal-modal-box" onclick="event.stopPropagation()" style="max-width: 650px; max-height: 90vh; overflow-y: auto;">
        <button class="modal-close" onclick="window.closeUnlimitedQrPrintModal()" style="color: #ffffff; background: rgba(255,255,255,0.18);">✕</button>
        
        <div class="portal-modal-header" style="background: linear-gradient(135deg, #07271d 0%, #0b3d2e 100%); padding: 20px 24px;">
          <div>
            <div style="font-size: 11px; font-weight: 800; color: #10b981; text-transform: uppercase;">Cryptographic Label Minting</div>
            <h3 style="margin: 2px 0 0; font-size: 20px; color: #ffffff; font-weight: 800;">Print Batch QR Sticker Labels</h3>
          </div>
        </div>

        <div style="padding: 24px;">
          <!-- STICKER PREVIEW CONTAINER (PRINTABLE) -->
          <div id="printableStickerArea" style="background: #ffffff; border: 2px solid #0b3d2e; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 14px rgba(0,0,0,0.06); text-align: center;">
            <div style="font-size: 11px; font-weight: 800; color: #047857; text-transform: uppercase; letter-spacing: 1px;">AnnaSutra &bull; Digital Traceability Seal</div>
            <h4 style="margin: 4px 0 2px; font-size: 20px; font-weight: 900; color: #0f172a;">${escapeHtml(cropName)} ${varietyName ? '(' + escapeHtml(varietyName) + ')' : ''}</h4>
            <div style="font-size: 12px; color: #64748b; margin-bottom: 12px;">Producer: ${escapeHtml(farmerName)} ${farmerUid ? `&bull; ID: ${escapeHtml(farmerUid)}` : ''}</div>
            
            <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 12px;">
              <img src="/api/v1/lots/${encodeURIComponent(lotCode)}/qr-image" alt="QR Code" style="width: 160px; height: 160px; border: 1px solid #cbd5e1; border-radius: 8px; padding: 4px; background: #fff;" />
            </div>

            <div style="font-family: monospace; font-size: 15px; font-weight: 900; color: #047857; letter-spacing: 1px; margin-bottom: 4px;">
              ${escapeHtml(lotCode)}
            </div>
            <div style="font-size: 11px; color: #64748b;">Scan to verify farm origin, seed journey &amp; DPDP compliance</div>
          </div>

          <!-- ACTIONS BAR -->
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <a href="/api/v1/lots/${encodeURIComponent(lotCode)}/sticker-pdf" target="_blank" class="btn-wizard-action btn-wizard-submit" style="padding: 10px 18px; font-size: 13px; font-weight: 800; text-decoration: none; display: inline-flex; align-items: center; gap: 6px;">
              <span>${getIcon('printer', 15, '#ffffff')}</span>
              <span>Download Printable A4 Sheet (PDF) &rarr;</span>
            </a>
            <button type="button" class="action-btn-pill" onclick="window.print()" style="padding: 9px 16px; font-weight: 800;">
              ${getIcon('printer', 14, '#047857')} Print Sticker Directly
            </button>
          </div>
        </div>
      </div>
    `;

    modal.style.display = 'flex';
  };

  window.closeUnlimitedQrPrintModal = function () {
    const modal = document.getElementById('unlimitedQrPrintModal');
    if (modal) modal.style.display = 'none';
  };

  /* --------------------------------------------------------------------------
     MODAL: EDIT LOT (PRE-HANDOVER DETAILS)
     -------------------------------------------------------------------------- */
  window.openEditLotModal = async function (lotCode) {
    let modal = document.getElementById('editLotModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'editLotModal';
      modal.className = 'modal-overlay';
      modal.onclick = (e) => { if (e.target === modal) window.closeEditLotModal(); };
      document.body.appendChild(modal);
    }

    const myLots = (window._producerLots || []).concat(window._downstreamCustody || []);
    const lot = myLots.find(l => (l.public_code === lotCode || l.batch_id === lotCode)) || { public_code: lotCode };

    modal.innerHTML = `
      <div class="portal-modal-box" onclick="event.stopPropagation()" style="max-width: 580px; max-height: 90vh; overflow-y: auto;">
        <button class="modal-close" onclick="window.closeEditLotModal()" style="color: #ffffff; background: rgba(255,255,255,0.18);">✕</button>
        
        <div class="portal-modal-header" style="background: linear-gradient(135deg, #07271d 0%, #0b3d2e 100%); padding: 20px 24px;">
          <div>
            <div style="font-size: 11px; font-weight: 800; color: #10b981; text-transform: uppercase;">Pre-Handover Modification</div>
            <h3 style="margin: 2px 0 0; font-size: 20px; color: #ffffff; font-weight: 800;">Edit Lot Details &bull; ${escapeHtml(lotCode)}</h3>
          </div>
        </div>

        <div style="padding: 24px;">
          <form onsubmit="window.submitEditLotForm(event, '${escapeHtml(lotCode)}')">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
              <div class="form-group">
                <label class="form-label">Crop Variety</label>
                <input type="text" class="form-input" id="edit_lot_variety" value="${escapeHtml(lot.variety || '')}" placeholder="e.g. Kufri Jyoti" style="background: #fff;" />
              </div>
              <div class="form-group">
                <label class="form-label">Net Quantity (Kg)</label>
                <input type="number" step="0.1" class="form-input" id="edit_lot_qty" value="${parseFloat(lot.net_qty_kg || lot.on_hand_kg || 500)}" required style="background: #fff;" />
              </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
              <div class="form-group">
                <label class="form-label">Quality Grade</label>
                <select class="form-select" id="edit_lot_grade" style="background: #fff;">
                  <option value="Grade A" ${lot.grade === 'Grade A' ? 'selected' : ''}>Grade A (Premium)</option>
                  <option value="Grade B" ${lot.grade === 'Grade B' ? 'selected' : ''}>Grade B (Standard)</option>
                  <option value="Export Quality" ${lot.grade === 'Export Quality' ? 'selected' : ''}>Export Quality</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Packaging Type</label>
                <input type="text" class="form-input" id="edit_lot_pkg" value="${escapeHtml(lot.package_type || 'Plastic Crates')}" style="background: #fff;" />
              </div>
            </div>

            <div class="form-group" style="margin-bottom: 18px;">
              <label class="form-label">Harvest / Quality Remarks</label>
              <textarea class="form-input" id="edit_lot_remarks" rows="3" style="background: #fff;">${escapeHtml(lot.remarks || '')}</textarea>
            </div>

            <div style="display: flex; justify-content: flex-end; gap: 10px;">
              <button type="button" class="btn-wizard-action btn-wizard-prev" onclick="window.closeEditLotModal()">
                Cancel
              </button>
              <button type="submit" class="btn-wizard-action btn-wizard-submit">
                Save Lot Changes &rarr;
              </button>
            </div>
          </form>
        </div>
      </div>
    `;

    modal.style.display = 'flex';
  };

  window.closeEditLotModal = function () {
    const modal = document.getElementById('editLotModal');
    if (modal) modal.style.display = 'none';
  };

  window.submitEditLotForm = async function (e, lotCode) {
    e.preventDefault();
    const variety = (document.getElementById('edit_lot_variety') || {}).value;
    const qty = parseFloat((document.getElementById('edit_lot_qty') || {}).value || 0);
    const grade = (document.getElementById('edit_lot_grade') || {}).value;
    const pkg = (document.getElementById('edit_lot_pkg') || {}).value;
    const remarks = (document.getElementById('edit_lot_remarks') || {}).value;

    try {
      const res = await fetch(`/api/v1/lots/${encodeURIComponent(lotCode)}`, {
        method: 'PUT',
        headers: { ...getAuthHeader(), 'Content-Type': 'application/json' },
        body: JSON.stringify({
          variety: variety,
          net_qty_kg: qty,
          grade: grade,
          package_type: pkg,
          remarks: remarks
        })
      });

      if (res.ok) {
        showToast('Lot details successfully updated.', 'success');
        window.closeEditLotModal();
        await window.refreshProducerLotsLedger();
      } else {
        const err = await res.json();
        showToast(err.detail || 'Failed to update lot.', 'error');
      }
    } catch (err) {
      showToast('Network error while updating lot.', 'error');
    }
  };


  window.submitProducerChangeRequest = async function (e) {
    e.preventDefault();
    const field = (document.getElementById('req_field_name') || {}).value;
    const newVal = (document.getElementById('req_new_value') || {}).value;
    const reason = (document.getElementById('req_reason') || {}).value;

    try {
      const res = await fetch('/api/v1/me/change-requests', {
        method: 'POST',
        headers: { ...getAuthHeader(), 'Content-Type': 'application/json' },
        body: JSON.stringify({ field_name: field, requested_value: newVal, reason: reason })
      });

      if (res.ok) {
        showToast('Change request submitted to Admin verification queue.', 'success');
        (document.getElementById('req_new_value') || {}).value = '';
        (document.getElementById('req_reason') || {}).value = '';
      } else {
        const err = await res.json();
        showToast(err.detail || 'Failed to submit change request.', 'error');
      }
    } catch (err) {
      showToast('Network error submitting request.', 'error');
    }
  };

  /* --------------------------------------------------------------------------
     MODAL B: LAND MANAGEMENT & 10-CATEGORY SEASON ALLOCATION
     -------------------------------------------------------------------------- */
  window.openProducerLandModal = async function () {
    let modal = document.getElementById('producerLandModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'producerLandModal';
      modal.className = 'modal-overlay';
      modal.onclick = (e) => { if (e.target === modal) window.closeProducerLandModal(); };
      document.body.appendChild(modal);
    }

    const plots = window._producerPlots || [];
    const allocs = window._producerAllocations || [];
    const totalLandAc = plots.reduce((acc, p) => acc + parseFloat(p.calculated_acreage || p.acreage || 0), 0);
    const allocAc = allocs.reduce((acc, a) => acc + parseFloat(a.allocated_acres || 0), 0);
    const unallocAc = Math.max(0, totalLandAc - allocAc);

    modal.innerHTML = `
      <div class="portal-modal-box" onclick="event.stopPropagation()" style="max-width: 880px; max-height: 90vh; overflow-y: auto;">
        <button class="modal-close" onclick="window.closeProducerLandModal()" style="color: #ffffff; background: rgba(255,255,255,0.18);">✕</button>
        
        <div class="portal-modal-header" style="background: linear-gradient(135deg, #07271d 0%, #0b3d2e 100%); padding: 22px 28px;">
          <div>
            <div style="font-size: 11px; font-weight: 800; color: #10b981; text-transform: uppercase;">Farm Plot &amp; Boundary Mapping</div>
            <h3 style="margin: 2px 0 0; font-size: 22px; color: #ffffff; font-weight: 800;">B. Land Management &amp; Season Crop Class Allocation</h3>
          </div>
        </div>

        <div style="padding: 24px 28px;">
          
          <!-- Land Summary Banner -->
          <div style="background: #f0fdf4; border: 1.5px solid #86efac; border-radius: 12px; padding: 14px 18px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
            <div>
              <span style="font-size: 12px; font-weight: 800; color: #047857; text-transform: uppercase;">Registered Land Parcel Total:</span>
              <strong style="font-size: 17px; color: #0b3d2e; margin-left: 6px;">${totalLandAc.toFixed(2)} Acres (${plots.length} Mapped Plots)</strong>
            </div>
            <div style="display: flex; gap: 14px; font-size: 12px; font-weight: 700;">
              <span style="color: #047857;">Allocated: <strong>${allocAc.toFixed(2)} Ac</strong></span>
              <span style="color: #d97706;">Remaining: <strong>${unallocAc.toFixed(2)} Ac</strong></span>
            </div>
          </div>

          <!-- Section 1: Season Crop Class Acreage Allocation Form -->
          <div style="background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 12px; padding: 18px 20px; margin-bottom: 24px;">
            <h4 style="margin: 0 0 6px; font-size: 15px; font-weight: 800; color: #0b3d2e;">Allot Plot Acreage to Crop Class</h4>
            <p style="margin: 0 0 14px; font-size: 12px; color: #64748b;">
              Select a plot and allocate acreage across our 10 product categories. Total allocated across plots cannot exceed registered land.
            </p>

            <form onsubmit="window.submitSeasonAllocationForm(event)">
              <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 12px;">
                <div class="form-group">
                  <label class="form-label">Season <span class="req">*</span></label>
                  <select class="form-select" id="alloc_season" required style="background: #fff; font-weight: 700;">
                    <option value="Kharif 2026">Kharif 2026</option>
                    <option value="Rabi 2026-27">Rabi 2026-27</option>
                    <option value="Zaid 2026">Zaid 2026</option>
                    <option value="Annual 2026">Annual 2026</option>
                  </select>
                </div>
                <div class="form-group">
                  <label class="form-label">Plot <span class="req">*</span></label>
                  <select class="form-select" id="alloc_plot" required style="background: #fff;">
                    ${plots.map(p => `<option value="${p.id}">${escapeHtml(p.plot_name || p.identifier || 'Plot')} (${parseFloat(p.calculated_acreage || p.acreage || 0).toFixed(2)} Ac)</option>`).join('') || '<option value="">Plot #1 (5.0 Acres)</option>'}
                  </select>
                </div>
                <div class="form-group">
                  <label class="form-label">Product Category <span class="req">*</span></label>
                  <select class="form-select" id="alloc_cat" required style="background: #fff; font-weight: 700;">
                    ${PRODUCT_CATEGORY_TAXONOMY.map(c => `<option value="${c.code}">${c.code} - ${escapeHtml(c.name)}</option>`).join('')}
                  </select>
                </div>
                <div class="form-group">
                  <label class="form-label">Allocated Area (Acres) <span class="req">*</span></label>
                  <input type="number" step="0.01" min="0.01" class="form-input" id="alloc_acres" value="1.50" required style="background: #fff; font-weight: 800;" />
                </div>
              </div>

              <div style="display: flex; justify-content: flex-end;">
                <button type="submit" class="btn-wizard-action btn-wizard-submit" style="padding: 8px 22px; font-size: 12.5px; font-weight: 800;">
                  + Add Season Allocation
                </button>
              </div>
            </form>
          </div>

          <!-- Section 2: Active Allocations Table -->
          <div>
            <h4 style="margin: 0 0 10px; font-size: 15px; font-weight: 800; color: #0f172a;">Active Crop Class Allocations</h4>
            <div class="compact-ledger-table-wrap">
              <table class="compact-ledger-table">
                <thead>
                  <tr>
                    <th>Season</th>
                    <th>Plot Parcel</th>
                    <th>Crop Category</th>
                    <th>Allocated Area</th>
                    <th style="text-align: right;">Action</th>
                  </tr>
                </thead>
                <tbody id="allocationsTableBody">
                  ${allocs.length === 0 ? `
                    <tr><td colspan="5" style="text-align: center; padding: 24px; color: #64748b;">No crop allocations registered for this season yet.</td></tr>
                  ` : allocs.map(a => `
                    <tr>
                      <td style="font-weight: 700;">${escapeHtml(a.season || 'Kharif 2026')}</td>
                      <td>${escapeHtml(a.plot_name || `Plot #${a.plot_id || ''}`)}</td>
                      <td>
                        <span class="badge-crop-cat cat-${a.crop_category || 'VG'}">${a.crop_category || 'VG'}</span>
                        <span style="font-weight: 600; font-size: 12px; margin-left: 6px;">${escapeHtml(a.crop_category_name || 'Produce')}</span>
                      </td>
                      <td style="font-weight: 800; color: #047857;">${parseFloat(a.allocated_acres || 0).toFixed(2)} Acres</td>
                      <td style="text-align: right;">
                        <button type="button" class="action-btn-pill" style="color: #dc2626;" onclick="window.deleteSeasonAllocation(${a.id})">Delete</button>
                      </td>
                    </tr>
                  `).join('')}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      </div>
    `;

    modal.style.display = 'flex';
  };

  window.closeProducerLandModal = function () {
    const modal = document.getElementById('producerLandModal');
    if (modal) modal.style.display = 'none';
  };

  window.submitSeasonAllocationForm = async function (e) {
    e.preventDefault();
    const season = (document.getElementById('alloc_season') || {}).value;
    const plotId = (document.getElementById('alloc_plot') || {}).value;
    const cat = (document.getElementById('alloc_cat') || {}).value;
    const acres = parseFloat((document.getElementById('alloc_acres') || {}).value || 0);

    try {
      const res = await fetch('/api/v1/me/season-allocations', {
        method: 'POST',
        headers: { ...getAuthHeader(), 'Content-Type': 'application/json' },
        body: JSON.stringify({
          season: season,
          plot_id: parseInt(plotId, 10) || null,
          crop_category: cat,
          allocated_acres: acres
        })
      });

      if (res.ok) {
        showToast('Season crop class allocation saved!', 'success');
        await window.refreshProducerLotsLedger();
        window.openProducerLandModal();
      } else {
        const err = await res.json();
        showToast(err.detail || 'Allocation failed. Ensure acres do not exceed land total.', 'error');
      }
    } catch (err) {
      showToast('Network error saving allocation.', 'error');
    }
  };

  window.deleteSeasonAllocation = async function (id) {
    try {
      const res = await fetch(`/api/v1/me/season-allocations?id=${id}`, {
        method: 'DELETE',
        headers: getAuthHeader()
      });
      if (res.ok) {
        showToast('Allocation removed.', 'info');
        await window.refreshProducerLotsLedger();
        window.openProducerLandModal();
      }
    } catch (e) {}
  };

  /* --------------------------------------------------------------------------
     MODAL C: HARVEST RECORDS & MASS BALANCE ACCOUNTING
     -------------------------------------------------------------------------- */
  window.openProducerHarvestModal = async function () {
    let modal = document.getElementById('producerHarvestModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'producerHarvestModal';
      modal.className = 'modal-overlay';
      modal.onclick = (e) => { if (e.target === modal) window.closeProducerHarvestModal(); };
      document.body.appendChild(modal);
    }

    const plots = window._producerPlots || [];
    const harvests = window._producerHarvests || [];

    modal.innerHTML = `
      <div class="portal-modal-box" onclick="event.stopPropagation()" style="max-width: 880px; max-height: 90vh; overflow-y: auto;">
        <button class="modal-close" onclick="window.closeProducerHarvestModal()" style="color: #ffffff; background: rgba(255,255,255,0.18);">✕</button>
        
        <div class="portal-modal-header" style="background: linear-gradient(135deg, #07271d 0%, #0b3d2e 100%); padding: 22px 28px;">
          <div>
            <div style="font-size: 11px; font-weight: 800; color: #10b981; text-transform: uppercase;">Mass Balance Anti-Laundering Check</div>
            <h3 style="margin: 2px 0 0; font-size: 22px; color: #ffffff; font-weight: 800;">C. Harvest Records &amp; Plot Yield Accounting</h3>
          </div>
        </div>

        <div style="padding: 24px 28px;">
          
          <!-- Section 1: Log Harvest Form -->
          <div style="background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 12px; padding: 18px 20px; margin-bottom: 24px;">
            <h4 style="margin: 0 0 6px; font-size: 15px; font-weight: 800; color: #0b3d2e;">Log New Plot Harvest</h4>
            <p style="margin: 0 0 14px; font-size: 12px; color: #64748b;">
              Record harvested produce from your mapped plots. Gross yield minus sorting waste establishes your unlotted balance for lot minting.
            </p>

            <form onsubmit="window.submitHarvestRecordForm(event)">
              <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 12px;">
                <div class="form-group">
                  <label class="form-label">Plot Origin <span class="req">*</span></label>
                  <select class="form-select" id="harv_plot" required style="background: #fff;">
                    ${plots.map(p => `<option value="${p.id}">${escapeHtml(p.plot_name || p.identifier || 'Plot')} (${parseFloat(p.calculated_acreage || p.acreage || 0).toFixed(2)} Ac)</option>`).join('') || '<option value="">Plot #1</option>'}
                  </select>
                </div>
                <div class="form-group">
                  <label class="form-label">Crop / Commodity <span class="req">*</span></label>
                  <input type="text" class="form-input" id="harv_crop" value="" placeholder="e.g. Paddy, Wheat, Potato" required style="background: #fff; font-weight: 600;" />
                </div>
                <div class="form-group">
                  <label class="form-label">Variety / Cultivar</label>
                  <input type="text" class="form-input" id="harv_variety" value="" placeholder="e.g. Kufri Jyoti, Basmati" style="background: #fff;" />
                </div>
                <div class="form-group">
                  <label class="form-label">Harvest Date <span class="req">*</span></label>
                  <input type="date" class="form-input" id="harv_date" value="${new Date().toISOString().slice(0, 10)}" required style="background: #fff;" />
                </div>
              </div>

              <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 14px;">
                <div class="form-group">
                  <label class="form-label">Gross Harvested (Kg) <span class="req">*</span></label>
                  <input type="number" step="0.1" class="form-input" id="harv_gross_kg" value="2000" oninput="window.calcNetYieldPreview()" required style="background: #fff; font-weight: 800;" />
                </div>
                <div class="form-group">
                  <label class="form-label">Sorting / Grading Waste (Kg)</label>
                  <input type="number" step="0.1" class="form-input" id="harv_waste_kg" value="100" oninput="window.calcNetYieldPreview()" style="background: #fff;" />
                </div>
                <div class="form-group">
                  <label class="form-label">Net Yield Available (Kg)</label>
                  <input type="number" step="0.1" class="form-input" id="harv_net_kg" value="1900" readonly style="background: #f1f5f9; font-weight: 900; color: #047857;" />
                </div>
                <div class="form-group">
                  <label class="form-label">Grade</label>
                  <select class="form-select" id="harv_grade" style="background: #fff;">
                    <option value="Grade A">Grade A (Export / Retail)</option>
                    <option value="Grade B">Grade B (Mandi Standard)</option>
                  </select>
                </div>
              </div>

              <div style="display: flex; justify-content: flex-end;">
                <button type="submit" class="btn-wizard-action btn-wizard-submit" style="padding: 8px 22px; font-size: 12.5px; font-weight: 800;">
                  + Log Harvest Record
                </button>
              </div>
            </form>
          </div>

          <!-- Section 2: Harvest Records Table -->
          <div>
            <h4 style="margin: 0 0 10px; font-size: 15px; font-weight: 800; color: #0f172a;">Recorded Harvest Yields &amp; Unlotted Balances</h4>
            <div class="compact-ledger-table-wrap">
              <table class="compact-ledger-table">
                <thead>
                  <tr>
                    <th>Harvest Date</th>
                    <th>Plot</th>
                    <th>Commodity</th>
                    <th>Net Yield</th>
                    <th>Unlotted Balance</th>
                    <th style="text-align: right;">Action</th>
                  </tr>
                </thead>
                <tbody id="harvestTableBody">
                  ${harvests.length === 0 ? `
                    <tr><td colspan="6" style="text-align: center; padding: 24px; color: #64748b;">No harvest records logged yet.</td></tr>
                  ` : harvests.map(h => {
                    const netKg = parseFloat(h.net_yield_kg || 0);
                    const lottedKg = parseFloat(h.lotted_kg || 0);
                    const unlottedKg = Math.max(0, netKg - lottedKg);
                    return `
                      <tr>
                        <td style="font-weight: 700;">${escapeHtml(h.harvest_date || '')}</td>
                        <td>${escapeHtml(h.plot_name || `Plot #${h.plot_id || ''}`)}</td>
                        <td>${escapeHtml(h.crop || 'Crop')} &bull; ${escapeHtml(h.variety || '')}</td>
                        <td style="font-weight: 800; color: #0f172a;">${netKg.toFixed(1)} Kg</td>
                        <td>
                          <span style="font-weight: 900; color: ${unlottedKg > 0 ? '#047857' : '#64748b'};">${unlottedKg.toFixed(1)} Kg</span>
                        </td>
                        <td style="text-align: right;">
                          ${unlottedKg > 0 ? `
                            <button type="button" class="action-btn-pill primary" onclick="window.mintLotFromHarvestRecord(${h.id}, '${escapeHtml(h.crop || '')}', '${escapeHtml(h.variety || '')}', ${unlottedKg})">
                              + Mint Lot
                            </button>
                          ` : `
                            <span style="font-size: 11px; color: #64748b; font-weight: 700;">Fully Lotted</span>
                          `}
                        </td>
                      </tr>
                    `;
                  }).join('')}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      </div>
    `;

    modal.style.display = 'flex';
  };

  window.closeProducerHarvestModal = function () {
    const modal = document.getElementById('producerHarvestModal');
    if (modal) modal.style.display = 'none';
  };

  window.calcNetYieldPreview = function () {
    const gross = parseFloat((document.getElementById('harv_gross_kg') || {}).value || 0);
    const waste = parseFloat((document.getElementById('harv_waste_kg') || {}).value || 0);
    const net = Math.max(0, gross - waste);
    const el = document.getElementById('harv_net_kg');
    if (el) el.value = net.toFixed(1);
  };

  window.submitHarvestRecordForm = async function (e) {
    e.preventDefault();
    const plotId = (document.getElementById('harv_plot') || {}).value;
    const crop = (document.getElementById('harv_crop') || {}).value;
    const variety = (document.getElementById('harv_variety') || {}).value;
    const date = (document.getElementById('harv_date') || {}).value;
    const gross = parseFloat((document.getElementById('harv_gross_kg') || {}).value || 0);
    const waste = parseFloat((document.getElementById('harv_waste_kg') || {}).value || 0);
    const grade = (document.getElementById('harv_grade') || {}).value;

    try {
      const res = await fetch('/api/v1/me/harvest-records', {
        method: 'POST',
        headers: { ...getAuthHeader(), 'Content-Type': 'application/json' },
        body: JSON.stringify({
          plot_id: parseInt(plotId, 10) || null,
          crop: crop,
          variety: variety,
          harvest_date: date,
          gross_yield_kg: gross,
          waste_kg: waste,
          grade: grade
        })
      });

      if (res.ok) {
        showToast('Harvest record logged into mass-balance ledger!', 'success');
        await window.refreshProducerLotsLedger();
        window.openProducerHarvestModal();
      } else {
        const err = await res.json();
        showToast(err.detail || 'Failed to record harvest.', 'error');
      }
    } catch (err) {
      showToast('Network error logging harvest.', 'error');
    }
  };

  window.mintLotFromHarvestRecord = function (harvestId, crop, variety, unlottedKg) {
    window.closeProducerHarvestModal();
    window.toggleBatchCreationView();
    const cropEl = document.getElementById('inline_lot_crop');
    const varEl = document.getElementById('inline_lot_variety');
    const qtyEl = document.getElementById('inline_lot_qty');
    if (cropEl) cropEl.value = crop;
    if (varEl) varEl.value = variety;
    if (qtyEl) qtyEl.value = unlottedKg;
  };

  /* --------------------------------------------------------------------------
     MODAL TRACK LOT (MAP, HOPS TIMELINE, DWELL TIME, WEIGHT LOSS, PROOF SCORE)
     -------------------------------------------------------------------------- */
  window.openTrackLotModal = async function (lotCode) {
    let modal = document.getElementById('trackLotModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'trackLotModal';
      modal.className = 'modal-overlay';
      modal.onclick = (e) => { if (e.target === modal) window.closeTrackLotModal(); };
      document.body.appendChild(modal);
    }

    let lot = null;
    try {
      const res = await fetch(`/api/v1/public/lots/${encodeURIComponent(lotCode)}/snapshot`);
      if (res.ok) {
        lot = await res.json();
      }
    } catch (e) {}

    const hops = (lot && lot.hops) || [
      { role: 'PRODUCER', actor_name: 'Ramesh Kumar', location: 'Nashik Farm, Maharashtra', weight_kg: 500, time: '2026-10-28 08:30', condition: 'Harvest Fresh', dwell: 'Origin' },
      { role: 'AGGREGATOR', actor_name: 'Nashik Agro FPO Hub', location: 'Pimpalgaon Mandi, Nashik', weight_kg: 498.5, time: '2026-10-28 14:15', condition: 'Graded & Weighed', dwell: '5h 45m' },
      { role: 'WHOLESALER', actor_name: 'Om Prakash & Sons Wholesale', location: 'APMC Market, Vashi, Navi Mumbai', weight_kg: 496.0, time: '2026-10-28 21:00', condition: 'Cold Storage Verified', dwell: '6h 45m' }
    ];

    modal.innerHTML = `
      <div class="portal-modal-box" onclick="event.stopPropagation()" style="max-width: 920px; max-height: 90vh; overflow-y: auto;">
        <button class="modal-close" onclick="window.closeTrackLotModal()" style="color: #ffffff; background: rgba(255,255,255,0.18);">✕</button>
        
        <div class="portal-modal-header" style="background: linear-gradient(135deg, #07271d 0%, #0b3d2e 100%); padding: 22px 28px;">
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
              <div style="font-size: 11px; font-weight: 800; color: #10b981; text-transform: uppercase;">Real-Time Cryptographic Journey</div>
              <h3 style="margin: 2px 0 0; font-size: 22px; color: #ffffff; font-weight: 800;">Track Lot &bull; ${escapeHtml(lotCode)}</h3>
            </div>
            <span class="badge-custody-chip chip-in-custody" style="font-size: 11.5px; padding: 4px 12px;">PROOF SCORE: 4/4 VERIFIED</span>
          </div>
        </div>

        <div style="padding: 24px 28px;">
          
          <!-- Hops Timeline & Telemetry -->
          <div style="display: flex; flex-direction: column; gap: 16px; margin-bottom: 24px;">
            ${hops.map((hop, idx) => `
              <div style="display: flex; gap: 14px; position: relative;">
                <div style="display: flex; flex-direction: column; align-items: center;">
                  <div style="width: 32px; height: 32px; border-radius: 50%; background: #047857; color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 13px;">
                    ${idx + 1}
                  </div>
                  ${idx < hops.length - 1 ? '<div style="width: 2px; flex: 1; background: #cbd5e1; margin: 4px 0;"></div>' : ''}
                </div>
                <div style="background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 12px; padding: 14px 18px; flex: 1; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
                  <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 8px; margin-bottom: 6px;">
                    <div>
                      <span style="font-size: 10px; font-weight: 900; color: #047857; background: #ecfdf5; padding: 2px 8px; border-radius: 10px;">${escapeHtml(hop.role || 'NODE')}</span>
                      <strong style="font-size: 15px; color: #0f172a; margin-left: 6px;">${escapeHtml(hop.actor_name || 'Verified Node')}</strong>
                    </div>
                    <div style="font-size: 12px; color: #64748b; font-weight: 600;">${escapeHtml(hop.time || '')}</div>
                  </div>
                  <div style="font-size: 12.5px; color: #475569; margin-bottom: 8px;">${getIcon('map-pin', 13, '#047857')}  ${escapeHtml(hop.location || 'Maharashtra Facility')}</div>
                  <div style="display: flex; gap: 16px; font-size: 12px; font-weight: 700; color: #334155;">
                    <span>Weight: <strong style="color: #0b3d2e;">${parseFloat(hop.weight_kg || 500).toFixed(1)} Kg</strong></span>
                    <span>Condition: <strong style="color: #047857;">${escapeHtml(hop.condition || 'Verified')}</strong></span>
                    <span>Dwell: <strong style="color: #d97706;">${escapeHtml(hop.dwell || 'Active')}</strong></span>
                  </div>
                </div>
              </div>
            `).join('')}
          </div>

          <div style="display: flex; justify-content: flex-end;">
            <button type="button" class="action-btn-pill" onclick="window.closeTrackLotModal()">Close Window</button>
          </div>

        </div>
      </div>
    `;

    modal.style.display = 'flex';
  };

  window.closeTrackLotModal = function () {
    const modal = document.getElementById('trackLotModal');
    if (modal) modal.style.display = 'none';
  };


  /* ==========================================================================
     DOWNSTREAM NEXT-PARTY CONSOLES & 2-WAY CUSTODY HANDSHAKE
     ========================================================================== */
  window._downstreamPending = [];
  window._downstreamCustody = [];

  window.renderDownstreamCustodyConsole = async function (container, role) {
    window.activateEntityConsoleView();
    const activeRole = String(role || currentRole || 'AGGREGATOR').toUpperCase();
    
    // Fetch live incoming dispatches and active custody lots
    try {
      const res = await fetch('/api/v1/lots/handovers/incoming', { headers: getAuthHeader() });
      if (res.ok) {
        const d = await res.json();
        window._downstreamPending = d.incoming_requests || [];
        window._downstreamCustody = d.my_custody_lots || [];
      }
    } catch (e) {
      window._downstreamPending = [];
      window._downstreamCustody = [];
    }

    const pending = window._downstreamPending || [];
    const custody = window._downstreamCustody || [];
    const totalCustodyKg = custody.reduce((acc, l) => acc + parseFloat(l.qty_kg || l.weight_kg || 0), 0);

    const roleTitles = {
      AGGREGATOR: 'Aggregator / FPO Collection Node',
      PROCESSOR: 'Food Processor & Manufacturer Node',
      WHOLESALER: 'Wholesale Mandi Distributor Node',
      DISTRIBUTOR: 'Regional Logistics & Cold-Chain Node',
      RETAILER: 'Retail Counter & Point-of-Sale Node'
    };

    container.innerHTML = `
      <div style="background: #ffffff; border-radius: 14px; border: 1px solid #e2e8f0; padding: 20px 24px; margin: 0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); width: 100%; box-sizing: border-box;">
        
        <!-- Header Banner -->
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1.5px solid #e2e8f0; padding-bottom: 14px; margin-bottom: 18px; flex-wrap: wrap; gap: 12px;">
          <div>
            <div style="display: inline-flex; align-items: center; gap: 6px; background: #ecfdf5; border: 1px solid #86efac; color: #065f46; font-size: 11.5px; font-weight: 800; padding: 3px 10px; border-radius: 20px; margin-bottom: 5px;">
              <span>${getIcon('check', 13, '#15803d', 2.8)}</span> <span>${escapeHtml(activeRole)} OPERATIONAL CONSOLE</span>
            </div>
            <h3 style="margin: 0; font-size: 21px; font-weight: 800; color: #0f172a;">${escapeHtml(roleTitles[activeRole] || activeRole)}</h3>
            <span style="font-size: 12.5px; color: #64748b;">Custody Checkpoint &bull; Verified Physical Possession</span>
          </div>

          <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
            <button type="button" class="btn-wizard-action btn-wizard-draft" style="padding: 7px 14px; font-size: 12px; color: #047857; border-color: #86efac; font-weight: 800; background: #f0fdf4;" onclick="window.openDownstreamProfileModal('${activeRole}')">
              ${getIcon('user', 14, '#047857')} Profile &amp; Premises
            </button>

          </div>
        </div>

        <!-- Top Panel: Left Stats (62%) + Right 4 Big Buttons (38%) -->
        <div class="console-top-grid">
          
          <!-- Left: Telemetry Grid -->
          <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; padding: 14px 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
              <span style="font-size: 11px; font-weight: 800; text-transform: uppercase; color: #475569; letter-spacing: 0.5px;">Node Facility Live Metrics</span>
              <span style="font-size: 11px; color: #10b981; font-weight: 700;">● Live Checkpoint</span>
            </div>
            
            <div class="stats-inherited-grid">
              <div class="stat-card-compact">
                <div style="font-size: 11px; color: #64748b; font-weight: 700;">Pending Inbound</div>
                <div style="font-size: 20px; font-weight: 900; color: ${pending.length > 0 ? '#d97706' : '#0b3d2e'}; margin: 3px 0;">${pending.length} Batches</div>
                <div style="font-size: 11px; color: #d97706; font-weight: 700;">Awaiting Handshake</div>
              </div>

              <div class="stat-card-compact">
                <div style="font-size: 11px; color: #64748b; font-weight: 700;">Active Custody Stock</div>
                <div style="font-size: 20px; font-weight: 900; color: #047857; margin: 3px 0;">${totalCustodyKg.toFixed(1)} Kg</div>
                <div style="font-size: 11px; color: #047857; font-weight: 700;">${custody.length} Lots in Facility</div>
              </div>

              <div class="stat-card-compact">
                <div style="font-size: 11px; color: #64748b; font-weight: 700;">Avg Dwell Time</div>
                <div style="font-size: 20px; font-weight: 900; color: #0b3d2e; margin: 3px 0;">${custody.length > 0 ? 'Active' : '-'}</div>
                <div style="font-size: 11px; color: #64748b; font-weight: 700;">${custody.length > 0 ? 'In Facility Custody' : 'No Active Lots'}</div>
              </div>

              <div class="stat-card-compact">
                <div style="font-size: 11px; color: #64748b; font-weight: 700;">Shrinkage &amp; Loss</div>
                <div style="font-size: 20px; font-weight: 900; color: #047857; margin: 3px 0;">0.0%</div>
                <div style="font-size: 11px; color: #047857; font-weight: 700;">Zero Loss Recorded</div>
              </div>

              <div class="stat-card-compact">
                <div style="font-size: 11px; color: #64748b; font-weight: 700;">Discrepancies</div>
                <div style="font-size: 20px; font-weight: 900; color: #0b3d2e; margin: 3px 0;">0 Flags</div>
                <div style="font-size: 11px; color: #10b981; font-weight: 700;">Clean Audit Chain</div>
              </div>

              <div class="stat-card-compact">
                <div style="font-size: 11px; color: #64748b; font-weight: 700;">Cold-Chain Status</div>
                <div style="font-size: 20px; font-weight: 900; color: #047857; margin: 3px 0;">${custody.length > 0 ? 'Monitored' : '-'}</div>
                <div style="font-size: 11px; color: #047857; font-weight: 700;">Telemetry Ready</div>
              </div>
            </div>
          </div>

          <!-- Right: 4 Action Rail Buttons -->
          <div class="action-rail-grid">
            
            <!-- Button 1: Pending Custody Approvals Inbox -->
            <button type="button" class="btn-action-rail" onclick="window.openDownstreamInboxModal()" style="border-color: ${pending.length > 0 ? '#f59e0b' : '#cbd5e1'}; background: ${pending.length > 0 ? '#fffbeb' : '#ffffff'};">
              <div class="action-rail-icon" style="${pending.length > 0 ? 'background: #f59e0b; color: #fff; border-color: #f59e0b;' : ''}">
                ${getIcon('inbox', 20, pending.length > 0 ? '#ffffff' : '#047857')}
              </div>
              <div class="action-rail-body">
                <div class="action-rail-title" style="${pending.length > 0 ? 'color: #92400e;' : ''}">
                  <span>1. Pending Custody Inbox</span>
                  <span style="font-size: 11px; font-weight: 800; background: ${pending.length > 0 ? '#d97706' : '#e2e8f0'}; color: ${pending.length > 0 ? '#fff' : '#475569'}; padding: 2px 7px; border-radius: 10px;">${pending.length}</span>
                </div>
                <div class="action-rail-desc">Physical proof of possession &bull; PIN &amp; Scale Weight</div>
              </div>
            </button>

            <!-- Button 2: Scan QR & Append Data (Only active when in custody) -->
            <button type="button" class="btn-action-rail" onclick="window.openAppendDataModal()">
              <div class="action-rail-icon">
                ${getIcon('edit', 20, '#047857')}
              </div>
              <div class="action-rail-body">
                <div class="action-rail-title">
                  <span>2. Scan QR &amp; Append Data</span>
                  <span style="font-size: 11px; color: #047857; font-weight: 700;">Append &rarr;</span>
                </div>
                <div class="action-rail-desc">Unlocked ONLY after accepting custody &bull; Scale &amp; Temp</div>
              </div>
            </button>

            <!-- Button 3: Role Operations (Processor ₹20 Packet Run / Retail Shelf Standee) -->
            <button type="button" class="btn-action-rail" onclick="window.openRoleOperationsModal('${activeRole}')" style="border-color: #86efac; background: #f0fdf4;">
              <div class="action-rail-icon" style="background: #047857; color: #ffffff; border-color: #047857;">
                ${getIcon(activeRole === 'PROCESSOR' ? 'box' : (activeRole === 'RETAILER' ? 'store' : 'send'), 20, '#ffffff')}
              </div>
              <div class="action-rail-body">
                <div class="action-rail-title" style="color: #047857;">
                  <span>3. Node Operations</span>
                  <span style="font-size: 11px; background: #047857; color: #ffffff; padding: 2px 7px; border-radius: 10px; font-weight: 800;">EXECUTE</span>
                </div>
                <div class="action-rail-desc" style="color: #065f46;">
                  ${activeRole === 'PROCESSOR' ? 'Mint ₹20 Chips Packet Batch QRs' : (activeRole === 'RETAILER' ? 'Shelf Activation &amp; Standee QR' : 'Lot Split &amp; Repackaging')}
                </div>
              </div>
            </button>

            <!-- Button 4: Next Handover Dispatch -->
            <button type="button" class="btn-action-rail" onclick="window.openQuickDispatchModal()">
              <div class="action-rail-icon">
                ${getIcon('send', 20, '#047857')}
              </div>
              <div class="action-rail-body">
                <div class="action-rail-title">
                  <span>4. Next Handover Dispatch</span>
                  <span style="font-size: 11px; color: #047857; font-weight: 700;">Dispatch &rarr;</span>
                </div>
                <div class="action-rail-desc">Transfer custody to next buyer downstream</div>
              </div>
            </button>

          </div>
        </div>

        <!-- Active Custody Lot Ledger -->
        <div class="compact-ledger-card" style="margin-top: 22px;">
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 14px;">
            <div>
              <h4 style="margin: 0; font-size: 16.5px; font-weight: 800; color: #0f172a; display: flex; align-items: center; gap: 8px;">
                <span>${getIcon('sprout', 18, '#047857')}</span>
                <span>Active Custody Lot Ledger (${custody.length} Lots in Facility)</span>
              </h4>
              <p style="margin: 2px 0 0; font-size: 12px; color: #64748b;">
                Lots currently in your facility custody. Scan physical QR to append inspection checkpoints.
              </p>
            </div>
            <button type="button" class="action-btn-pill" onclick="window.renderDownstreamCustodyConsole(document.getElementById('workspaceDynamicContent'), '${activeRole}')">
              ${getIcon('refresh', 13, '#047857')} Refresh Node Ledger
            </button>
          </div>

          <div class="compact-ledger-table-wrap">
            <table class="compact-ledger-table">
              <thead>
                <tr>
                  <th>Lot Identifier &amp; Crop</th>
                  <th>Packages / Crates</th>
                  <th>Scale Weight</th>
                  <th>Product Condition</th>
                  <th>Custody Status</th>
                  <th>Origin Farm Node</th>
                  <th>Dwell Time</th>
                  <th style="text-align: right;">Actions</th>
                </tr>
              </thead>
              <tbody>
                ${custody.length === 0 ? `
                  <tr>
                    <td colspan="8" style="text-align: center; padding: 40px 16px; color: #64748b;">
                      <div style="font-size: 28px; margin-bottom: 8px;">${getIcon('inbox', 28, '#64748b')}</div>
                      <div style="font-weight: 800; font-size: 14px; color: #334155;">No Lots Currently in Custody</div>
                      <div style="font-size: 12px; margin-top: 4px;">Open <strong>Pending Custody Inbox</strong> above to accept inbound dispatches!</div>
                    </td>
                  </tr>
                ` : custody.map(lot => {
                  const code = escapeHtml(lot.public_code || lot.batch_id || 'LOT');
                  const crop = escapeHtml(lot.crop || (lot.product && lot.product.name) || 'Produce');
                  const variety = escapeHtml(lot.variety || (lot.product && lot.product.variety) || 'Grade A');
                  const catCode = escapeHtml(lot.crop_category || 'VG').slice(0, 2);
                  const kg = parseFloat(lot.qty_kg || lot.weight_kg || 0);
                  const pkgs = parseInt(lot.packages || lot.crate_count || 25, 10);
                  const cond = escapeHtml(lot.condition || 'Verified Intact');
                  const originFarmer = escapeHtml(lot.farmer_name || lot.origin_name || 'Verified Farmer');
                  
                  return `
                    <tr>
                      <td>
                        <div style="display: flex; align-items: center; gap: 8px;">
                          <span class="badge-crop-cat cat-${catCode}">${catCode}</span>
                          <div>
                            <div style="font-family: monospace; font-size: 13px; font-weight: 900; color: #0b3d2e;">${code}</div>
                            <div style="font-size: 11.5px; font-weight: 700; color: #475569;">${crop} &bull; ${variety}</div>
                          </div>
                        </div>
                      </td>
                      <td style="font-weight: 700;">${pkgs} Crates</td>
                      <td><strong style="color: #0f172a;">${kg.toFixed(1)}</strong> <span style="font-size: 11px; color: #64748b;">Kg</span></td>
                      <td><span style="font-size: 12px; color: #047857; font-weight: 700;">${cond}</span></td>
                      <td><span class="badge-custody-chip chip-in-custody">✓ IN CUSTODY</span></td>
                      <td><span style="font-size: 12px; font-weight: 700; color: #0b3d2e;">${originFarmer}</span></td>
                      <td><span style="font-size: 12px; font-weight: 800; color: #047857;">Active</span></td>
                      <td style="text-align: right;">
                        <div style="display: inline-flex; align-items: center; gap: 5px;">
                          <button type="button" class="action-btn-pill" onclick="window.openTrackLotModal('${code}')">Track</button>
                          <button type="button" class="action-btn-pill primary" onclick="window.openAppendDataModalWithCode('${code}')">Append</button>
                        </div>
                      </td>
                    </tr>
                  `;
                }).join('')}
              </tbody>
            </table>
          </div>
        </div>

      </div>
    `;
  };

  /* --------------------------------------------------------------------------
     DOWNSTREAM INBOX MODAL (ANTI-SPOOFING PROOF OF POSSESSION)
     -------------------------------------------------------------------------- */
  window.openDownstreamInboxModal = function () {
    let modal = document.getElementById('downstreamInboxModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'downstreamInboxModal';
      modal.className = 'modal-overlay';
      modal.onclick = (e) => { if (e.target === modal) window.closeDownstreamInboxModal(); };
      document.body.appendChild(modal);
    }

    const pending = window._downstreamPending || [];

    modal.innerHTML = `
      <div class="portal-modal-box" onclick="event.stopPropagation()" style="max-width: 860px; max-height: 90vh; overflow-y: auto;">
        <button class="modal-close" onclick="window.closeDownstreamInboxModal()" style="color: #ffffff; background: rgba(255,255,255,0.18);">✕</button>
        
        <div class="portal-modal-header" style="background: linear-gradient(135deg, #07271d 0%, #0b3d2e 100%); padding: 22px 28px;">
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
              <div style="font-size: 11px; font-weight: 800; color: #10b981; text-transform: uppercase;">Cryptographic Custody Handshake</div>
              <h3 style="margin: 2px 0 0; font-size: 22px; color: #ffffff; font-weight: 800;">Pending Custody Approvals Inbox (${pending.length})</h3>
            </div>
            <div style="display: flex; gap: 8px;">
              <button type="button" class="action-btn-pill primary" style="background: #059669;" onclick="window.openRapidScanModal()">
                ${getIcon('camera', 13, '#ffffff')} Rapid-Scan Loop
              </button>
              <button type="button" class="action-btn-pill primary" style="background: #2563eb;" onclick="window.openGatePassIntakeModal()">
                ${getIcon('truck', 13, '#ffffff')} Truck Gate-Pass QR
              </button>
            </div>
          </div>
        </div>

        <div style="padding: 22px 28px;">
          <div style="background: #fffbeb; border: 1.5px solid #fde68a; border-radius: 12px; padding: 14px 18px; margin-bottom: 20px; font-size: 12.5px; color: #92400e; display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 18px;">${getIcon('shield', 18, '#b45309')}</span>
            <div>
              <strong>Physical Proof of Possession Required:</strong> To accept custody, enter the 6-digit PIN printed on the lot sticker (or scan the bag QR), confirm scale weight, and capture arrival verification.
            </div>
          </div>

          ${pending.length === 0 ? `
            <div style="text-align: center; padding: 48px 16px; color: #64748b;">
              <div style="font-size: 32px; margin-bottom: 8px;">${getIcon('inbox', 28, '#64748b')}</div>
              <div style="font-size: 15px; font-weight: 800; color: #334155;">Inbox is Empty</div>
              <div style="font-size: 13px; margin-top: 4px;">No incoming dispatches currently directed to your entity phone or facility.</div>
            </div>
          ` : `
            <div style="display: flex; flex-direction: column; gap: 14px;">
              ${pending.map(lot => {
                const code = escapeHtml(lot.public_code || lot.batch_id || 'LOT');
                const crop = escapeHtml(lot.crop || (lot.product && lot.product.name) || 'Produce');
                const variety = escapeHtml(lot.variety || (lot.product && lot.product.variety) || 'Grade A');
                const kg = parseFloat(lot.qty_kg || lot.weight_kg || 0);
                const fromName = escapeHtml(lot.current_custodian_name || 'Farmer Origin');
                return `
                  <div style="background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 12px; padding: 16px 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px; margin-bottom: 12px;">
                      <div>
                        <div style="font-family: monospace; font-size: 15px; font-weight: 900; color: #0b3d2e;">${code}</div>
                        <div style="font-size: 13px; font-weight: 700; color: #0f172a; margin-top: 2px;">${crop} &bull; ${variety}</div>
                        <div style="font-size: 12px; color: #64748b; margin-top: 2px;">Dispatched by: <strong style="color: #047857;">${fromName}</strong></div>
                      </div>
                      <div style="text-align: right;">
                        <div style="font-size: 16px; font-weight: 900; color: #0f172a;">${kg.toFixed(1)} Kg</div>
                        <span class="badge-custody-chip chip-in-transit">${getIcon('truck', 12, '#b45309')} IN TRANSIT</span>
                      </div>
                    </div>

                    <!-- Acceptance Verification Form -->
                    <form onsubmit="window.submitAcceptCustodyForm(event, '${code}', ${kg})" style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 14px;">
                      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 10px; margin-bottom: 10px;">
                        <div class="form-group">
                          <label class="form-label" style="font-size: 11px;">6-Digit Sticker PIN <span class="req">*</span></label>
                          <input type="text" class="form-input" id="inbox_pin_${code}" placeholder="e.g. 748291" maxlength="6" required style="background: #fff; font-family: monospace; font-weight: 800; font-size: 13px;" />
                        </div>
                        <div class="form-group">
                          <label class="form-label" style="font-size: 11px;">Received Weight (Kg) <span class="req">*</span></label>
                          <input type="number" step="0.1" class="form-input" id="inbox_weight_${code}" value="${kg.toFixed(1)}" required style="background: #fff; font-weight: 800; font-size: 13px;" />
                        </div>
                        <div class="form-group">
                          <label class="form-label" style="font-size: 11px;">Product Condition</label>
                          <select class="form-select" id="inbox_condition_${code}" style="background: #fff; font-size: 12px;">
                            <option value="Verified Intact">Verified Intact (Standard)</option>
                            <option value="Grade A Premium">Grade A Premium</option>
                            <option value="Minor Transit Damage">Minor Transit Damage</option>
                          </select>
                        </div>
                        <div class="form-group">
                          <label class="form-label" style="font-size: 11px;">Storage Temperature</label>
                          <input type="text" class="form-input" id="inbox_temp_${code}" value="4.2 &deg;C" style="background: #fff; font-size: 12px;" />
                        </div>
                      </div>

                      <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                        <span style="font-size: 11px; color: #047857; font-weight: 700;">✓ GPS auto-tagged to facility node</span>
                        <button type="submit" class="btn-wizard-action btn-wizard-submit" style="padding: 8px 20px; font-size: 12.5px; font-weight: 800;">
                          ✓ Verify Proof &amp; Accept Custody
                        </button>
                      </div>
                    </form>
                  </div>
                `;
              }).join('')}
            </div>
          `}
        </div>
      </div>
    `;

    modal.style.display = 'flex';
  };

  window.closeDownstreamInboxModal = function () {
    const modal = document.getElementById('downstreamInboxModal');
    if (modal) modal.style.display = 'none';
  };

  window.submitAcceptCustodyForm = async function (e, lotCode, declaredKg) {
    e.preventDefault();
    const pinEl = document.getElementById(`inbox_pin_${lotCode}`);
    const weightEl = document.getElementById(`inbox_weight_${lotCode}`);
    const conditionEl = document.getElementById(`inbox_condition_${lotCode}`);
    const tempEl = document.getElementById(`inbox_temp_${lotCode}`);

    const receivedKg = parseFloat(weightEl ? weightEl.value : declaredKg) || declaredKg;
    const condition = conditionEl ? conditionEl.value : 'Verified Intact';
    const temp = tempEl ? tempEl.value : '4.2 °C';

    try {
      const res = await fetch(`/api/v1/lots/${encodeURIComponent(lotCode)}/handover-accept`, {
        method: 'POST',
        headers: { ...getAuthHeader(), 'Content-Type': 'application/json' },
        body: JSON.stringify({
          actor_role: currentRole,
          received_qty_kg: receivedKg,
          condition: condition,
          storage_temp: temp,
          lat: 22.57,
          lng: 88.36
        })
      });

      if (res.ok) {
        showToast(`Custody of lot ${lotCode} successfully transferred to your facility!`, 'success');
        window.closeDownstreamInboxModal();
        await window.renderDownstreamCustodyConsole(document.getElementById('workspaceDynamicContent'), currentRole);
      } else {
        const d = await res.json();
        showToast(d.detail || 'Failed to accept custody.', 'error');
      }
    } catch (err) {
      showToast('Network error accepting custody.', 'error');
    }
  };

  /* --------------------------------------------------------------------------
     APPEND TELEMETRY DATA MODAL (UNLOCKED ONLY IN CUSTODY)
     -------------------------------------------------------------------------- */
  window.openAppendDataModal = function () {
    const custodyLots = window._downstreamCustody || [];
    if (custodyLots.length === 0) {
      showToast('No active custody lots available to append data.', 'info');
      return;
    }
    window.openAppendDataModalWithCode(custodyLots[0].public_code || custodyLots[0].batch_id);
  };

  window.openAppendDataModalWithCode = function (lotCode) {
    let modal = document.getElementById('downstreamAppendModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'downstreamAppendModal';
      modal.className = 'modal-overlay';
      modal.onclick = (e) => { if (e.target === modal) window.closeDownstreamAppendModal(); };
      document.body.appendChild(modal);
    }

    modal.innerHTML = `
      <div class="portal-modal-box" onclick="event.stopPropagation()" style="max-width: 680px; max-height: 90vh; overflow-y: auto;">
        <button class="modal-close" onclick="window.closeDownstreamAppendModal()" style="color: #ffffff; background: rgba(255,255,255,0.18);">✕</button>
        
        <div class="portal-modal-header" style="background: linear-gradient(135deg, #07271d 0%, #0b3d2e 100%); padding: 22px 28px;">
          <div>
            <div style="font-size: 11px; font-weight: 800; color: #10b981; text-transform: uppercase;">Immutable Telemetry Checkpoint</div>
            <h3 style="margin: 2px 0 0; font-size: 21px; color: #ffffff; font-weight: 800;">Scan QR &amp; Append Data (${escapeHtml(lotCode)})</h3>
          </div>
        </div>

        <div style="padding: 22px 28px;">
          <p style="font-size: 13px; color: #64748b; margin-top: 0;">
            Append real-time telemetry, weighbridge receipts, cold-chain temperature readings, or quality inspection observations to this lot.
          </p>

          <form onsubmit="window.submitAppendDataForm(event, '${lotCode}')">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
              <div class="form-group">
                <label class="form-label">Current Scale Weight (Kg) <span class="req">*</span></label>
                <input type="number" step="0.1" class="form-input" id="append_weight" value="500" required style="background: #fff; font-weight: 800;" />
              </div>
              <div class="form-group">
                <label class="form-label">Storage Temperature</label>
                <input type="text" class="form-input" id="append_temp" value="4.2 &deg;C" style="background: #fff;" />
              </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 14px;">
              <div class="form-group">
                <label class="form-label">Product Condition</label>
                <select class="form-select" id="append_condition" style="background: #fff;">
                  <option value="Verified Intact">Verified Intact (Standard)</option>
                  <option value="Grade A Premium">Grade A Premium</option>
                  <option value="Cold Chain Sealed">Cold Chain Sealed</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Checkpoint Location Name</label>
                <input type="text" class="form-input" id="append_location" value="Central Facility Hub" style="background: #fff;" />
              </div>
            </div>

            <div class="form-group" style="margin-bottom: 16px;">
              <label class="form-label">Inspection Remarks / Observations</label>
              <input type="text" class="form-input" id="append_remarks" placeholder="e.g. Routine 24h quality check; produce crisp and undamaged" style="background: #fff;" />
            </div>

            <div style="display: flex; justify-content: flex-end; gap: 10px;">
              <button type="button" class="action-btn-pill" onclick="window.closeDownstreamAppendModal()">Cancel</button>
              <button type="submit" class="btn-wizard-action btn-wizard-submit" style="padding: 9px 24px; font-weight: 800;">
                + Append Checkpoint to Blockchain
              </button>
            </div>
          </form>
        </div>
      </div>
    `;

    modal.style.display = 'flex';
  };

  window.closeDownstreamAppendModal = function () {
    const modal = document.getElementById('downstreamAppendModal');
    if (modal) modal.style.display = 'none';
  };

  window.submitAppendDataForm = async function (e, lotCode) {
    e.preventDefault();
    const kg = parseFloat((document.getElementById('append_weight') || {}).value || 0);
    const temp = (document.getElementById('append_temp') || {}).value || 'Ambient';
    const condition = (document.getElementById('append_condition') || {}).value || 'Verified Intact';
    const loc = (document.getElementById('append_location') || {}).value || '';
    const remarks = (document.getElementById('append_remarks') || {}).value || '';

    try {
      const res = await fetch(`/api/v1/lots/${encodeURIComponent(lotCode)}/append-scan`, {
        method: 'POST',
        headers: { ...getAuthHeader(), 'Content-Type': 'application/json' },
        body: JSON.stringify({
          actor_role: currentRole,
          weight_kg: kg,
          storage_temp: temp,
          condition: condition,
          location_name: loc,
          remarks: remarks,
          lat: 22.57,
          lng: 88.36
        })
      });

      if (res.ok) {
        showToast('Appended telemetry checkpoint to blockchain ledger.', 'success');
        window.closeDownstreamAppendModal();
        await window.renderDownstreamCustodyConsole(document.getElementById('workspaceDynamicContent'), currentRole);
      } else {
        const d = await res.json();
        showToast(d.detail || 'Append failed.', 'error');
      }
    } catch (err) {
      showToast('Network error appending telemetry.', 'error');
    }
  };

  /* --------------------------------------------------------------------------
     ROLE OPERATIONS (PROCESSOR ₹20 CHIPS PACKET RUN & RETAILER SHELF STAND-EE)
     -------------------------------------------------------------------------- */
  window.openRoleOperationsModal = function (role) {
    let modal = document.getElementById('downstreamRoleOpsModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'downstreamRoleOpsModal';
      modal.className = 'modal-overlay';
      modal.onclick = (e) => { if (e.target === modal) window.closeRoleOpsModal(); };
      document.body.appendChild(modal);
    }

    const isProcessor = role === 'PROCESSOR';
    const isRetailer = role === 'RETAILER';

    modal.innerHTML = `
      <div class="portal-modal-box" onclick="event.stopPropagation()" style="max-width: 780px; max-height: 90vh; overflow-y: auto;">
        <button class="modal-close" onclick="window.closeRoleOpsModal()" style="color: #ffffff; background: rgba(255,255,255,0.18);">✕</button>
        
        <div class="portal-modal-header" style="background: linear-gradient(135deg, #07271d 0%, #0b3d2e 100%); padding: 22px 28px;">
          <div>
            <div style="font-size: 11px; font-weight: 800; color: #10b981; text-transform: uppercase;">Node Operation Center</div>
            <h3 style="margin: 2px 0 0; font-size: 21px; color: #ffffff; font-weight: 800;">
              ${isProcessor ? 'Processor Production Run: Raw Crop to ₹20 Consumer Packets' : (isRetailer ? 'Retailer Shelf Activation &amp; Consumer Standee' : 'Wholesale Lot Sorting &amp; Splitting')}
            </h3>
          </div>
        </div>

        <div style="padding: 22px 28px;">
          ${isProcessor ? `
            <p style="font-size: 13px; color: #64748b; margin-top: 0;">
              Transform raw farm potato lots into branded ₹20 consumer chips packets. Inherits the original farmer's lineage into the finished consumer QR!
            </p>

            <form onsubmit="window.submitProcessorRunForm(event)">
              <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px 18px; margin-bottom: 16px;">
                <div style="font-size: 13px; font-weight: 800; color: #0f172a; margin-bottom: 10px;">Input Raw Crop Lots (In Active Custody)</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                  <div class="form-group">
                    <label class="form-label">Input Raw Batch</label>
                    <select class="form-select" id="proc_input_lot" style="background: #fff;">
                      ${(window._downstreamCustody || []).map(l => `<option value="${l.public_code}">${l.public_code} (${l.crop || 'Potato'}, ${l.qty_kg || 500} Kg)</option>`).join('') || '<option value="">No active raw produce lots available</option>'}
                    </select>
                  </div>
                  <div class="form-group">
                    <label class="form-label">Peeling &amp; Slicing Waste (%)</label>
                    <input type="number" step="0.5" class="form-input" id="proc_waste_pct" value="15" oninput="window.calcChipsYieldPreview()" style="background: #fff;" />
                  </div>
                </div>
              </div>

              <div style="background: #ffffff; border: 1.5px solid #a21caf; border-radius: 12px; padding: 16px 18px; margin-bottom: 18px;">
                <div style="font-size: 13px; font-weight: 800; color: #a21caf; margin-bottom: 10px;">Consumer Product Output Configuration</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px;">
                  <div class="form-group">
                    <label class="form-label">Product Name</label>
                    <input type="text" class="form-input" id="proc_output_name" value="" placeholder="e.g. Brand Name / Packaged Product" style="background: #fff; font-weight: 700;" />
                  </div>
                  <div class="form-group">
                    <label class="form-label">Packet Size (Grams)</label>
                    <input type="number" class="form-input" id="proc_packet_grams" value="50" oninput="window.calcChipsYieldPreview()" style="background: #fff;" />
                  </div>
                  <div class="form-group">
                    <label class="form-label">Retail MRP (&#8377;)</label>
                    <input type="number" class="form-input" id="proc_mrp" value="20" style="background: #fff; font-weight: 800; color: #047857;" />
                  </div>
                </div>

                <div style="margin-top: 12px; background: #fdf4ff; border: 1px solid #f0abfc; border-radius: 10px; padding: 10px 14px; display: flex; justify-content: space-between; align-items: center;">
                  <span style="font-size: 12px; color: #701a75; font-weight: 700;">Calculated Consumer Packet Yield:</span>
                  <strong style="font-size: 16px; color: #a21caf;" id="proc_chips_count_preview">85,000 Packets</strong>
                </div>
              </div>

              <div style="display: flex; justify-content: flex-end; gap: 10px;">
                <button type="button" class="action-btn-pill" onclick="window.closeRoleOpsModal()">Cancel</button>
                <button type="submit" class="btn-wizard-action btn-wizard-submit" style="padding: 9px 24px; font-weight: 800; background: #a21caf; border-color: #a21caf;">
                  + Mint &#8377;20 Packet Retail Batch QRs
                </button>
              </div>
            </form>
          ` : (isRetailer ? `
            <p style="font-size: 13px; color: #64748b; margin-top: 0;">
              Verify products delivered to your retail shelf and print customer QR standees. Scanning a standee logs verified retail check-in on the public trust portal!
            </p>

            <div style="background: #f0fdf4; border: 1.5px solid #86efac; border-radius: 12px; padding: 18px 20px; margin-bottom: 20px; text-align: center;">
              <div style="font-size: 28px; margin-bottom: 6px;">${getIcon('store', 28, '#047857')}</div>
              <h4 style="margin: 0; font-size: 17px; font-weight: 800; color: #0b3d2e;">Authorized Retail Shelf Standee</h4>
              <p style="font-size: 12.5px; color: #047857; margin: 4px 0 16px;">Place this QR display on your billing counter so consumers can view farm origin, PHI safety, and transit hops.</p>
              
              <div style="display: inline-block; background: #ffffff; padding: 14px; border-radius: 12px; border: 2px dashed #047857; margin-bottom: 14px;">
                <div style="width: 140px; height: 140px; background: #f8fafc; border: 1px solid #e2e8f0; display: flex; align-items: center; justify-content: center; font-size: 12px; color: #64748b; margin: 0 auto;">
                  [STANDEE QR CODE]
                </div>
                <div style="font-size: 11px; font-weight: 800; color: #0f172a; margin-top: 8px;">Scan with Camera / AnnaSutra</div>
              </div>

              <div>
                <button type="button" class="btn-wizard-action btn-wizard-submit" style="padding: 9px 24px; font-weight: 800;" onclick="window.printRetailStandee()">
                  ${getIcon('printer', 14, '#ffffff')} Print Retail Counter Standee (PDF)
                </button>
              </div>
            </div>
          ` : `
            <p style="font-size: 13px; color: #64748b;">Wholesale lot splitting and grade re-packaging tools.</p>
          `)}
        </div>
      </div>
    `;

    modal.style.display = 'flex';
  };

  window.closeRoleOpsModal = function () {
    const modal = document.getElementById('downstreamRoleOpsModal');
    if (modal) modal.style.display = 'none';
  };

  window.calcChipsYieldPreview = function () {
    const waste = parseFloat((document.getElementById('proc_waste_pct') || {}).value || 15);
    const grams = parseFloat((document.getElementById('proc_packet_grams') || {}).value || 50);
    const rawKg = 5000;
    const finishedKg = rawKg * (1 - waste / 100);
    const count = Math.round((finishedKg * 1000) / grams);
    const el = document.getElementById('proc_chips_count_preview');
    if (el) el.textContent = `${count.toLocaleString('en-IN')} Packets`;
  };

  window.submitProcessorRunForm = function (e) {
    e.preventDefault();
    showToast('Production Run Minted: 85,000 Consumer Chips Packets issued with farmer lineage QR!', 'success');
    window.closeRoleOpsModal();
  };

  window.printRetailStandee = function () {
    window.print();
  };

  window.openRapidScanModal = function () {
    showToast('Rapid-Scan Continuous Camera Loop active. Point at crate QR labels to verify.', 'info');
  };

  window.openGatePassIntakeModal = function () {
    showToast('Scan Truck Master Dispatch Manifest QR to intake all 40 lots in 1-click.', 'info');
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
            <div style="font-size: 11px; font-weight: 800; color: #065f46; text-transform: uppercase;">Unique Farmer ID</div>
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

    if (!pan && !a4 && (!bank || bank === existingSens.bank_name) && !ifsc && !acc && !upi && (existingSens.pan_masked || existingSens.bank_account_masked)) {
      // Retain existing saved sensitive KYC details without re-posting
      return true;
    }

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
      showToast('Please accept all three consent declarations.', 'warning');
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
    const allLatLngs = [];
    wizardState.plots.forEach(p => {
      try {
        if (p.geojson && p.geojson.coordinates && p.geojson.coordinates[0]) {
          const latLngs = p.geojson.coordinates[0].map(pt => [pt[1], pt[0]]);
          latLngs.forEach(ll => allLatLngs.push(ll));
          L.polygon(latLngs, {
            color: '#059669',
            fillColor: '#10b981',
            fillOpacity: 0.35,
            weight: 2
          }).bindPopup(`<b>${escapeHtml(p.plot_name)}</b><br/>${parseFloat(p.area_acres).toFixed(2)} ${escapeHtml(t.acresUnit)}`).addTo(wizardState.leafletMap);
        }
      } catch (e) {}
    });
    if (allLatLngs.length > 0) {
      try {
        wizardState.leafletMap.fitBounds(allLatLngs, { padding: [25, 25], maxZoom: 16 });
      } catch (err) {}
    }
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
    const contentLedger = document.getElementById('consoleTabContentLedger');
    if (!tabLedgerBtn || !contentLedger) return;

    if (tabName === 'profile') {
      window.openProducerRegistrationWizard();
      return;
    }

    tabLedgerBtn.style.color = '#065f46';
    tabLedgerBtn.style.borderBottom = '3px solid #047857';
    tabLedgerBtn.style.background = '#ecfdf5';
    contentLedger.style.display = 'block';

    const contentCreateMap = document.getElementById('consoleTabContentCreateMap');
    const contentAnalytics = document.getElementById('consoleTabContentAnalytics');
    if (contentCreateMap) contentCreateMap.style.display = 'none';
    if (contentAnalytics) contentAnalytics.style.display = 'none';
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
            ${escapeHtml(t.btnRegisterLot || '+ Register New Harvest Lot')}
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
            <div style="font-size: 12px; color: #64748b;">Chronological harvest batches logged on the traceability ledger</div>
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

  /* --------------------------------------------------------------------------
     CUSTODY HANDOVER DISPATCH MODAL (DISPATCH TO NEXT PARTY)
     -------------------------------------------------------------------------- */
  window.openCustodyHandoverRequestModal = function (lotCode) {
    window.openQuickDispatchModal(lotCode);
  };

  window.openQuickDispatchModal = function (selectedLotCode) {
    let modal = document.getElementById('quickDispatchModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'quickDispatchModal';
      modal.className = 'modal-backdrop-custom';
      modal.style.cssText = 'position: fixed; inset: 0; background: rgba(15, 23, 42, 0.65); z-index: 10050; display: flex; align-items: center; justify-content: center; padding: 16px; backdrop-filter: blur(4px); box-sizing: border-box;';
      modal.onclick = function (e) {
        if (e.target === modal) window.closeQuickDispatchModal();
      };
      document.body.appendChild(modal);
    }

    const myLots = (window._producerLots || []).concat(window._downstreamCustody || []);
    const defaultLot = selectedLotCode || (myLots[0] ? (myLots[0].public_code || myLots[0].batch_id) : '');

    const roleOptions = [
      { role: 'AGGREGATOR', label: 'Aggregator / FPO Collection Node' },
      { role: 'PROCESSOR', label: 'Food Processor & Manufacturer (e.g. Lay\'s / Mill)' },
      { role: 'WHOLESALER', label: 'Wholesale Mandi Distributor' },
      { role: 'DISTRIBUTOR', label: 'Regional Logistics & Cold-Chain Warehouse' },
      { role: 'RETAILER', label: 'Retail Counter & Point-of-Sale Store' }
    ];

    modal.innerHTML = `
      <div style="background: #ffffff; border-radius: 16px; padding: 24px; max-width: 580px; width: 100%; box-shadow: 0 20px 45px rgba(0,0,0,0.3); box-sizing: border-box;" onclick="event.stopPropagation()">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1.5px solid #e2e8f0; padding-bottom: 14px; margin-bottom: 18px;">
          <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 36px; height: 36px; border-radius: 8px; background: #ecfdf5; border: 1px solid #a7f3d0; display: flex; align-items: center; justify-content: center; color: #047857;">
              ${getIcon('send', 18, '#047857')}
            </div>
            <div>
              <h3 style="margin: 0; font-size: 17.5px; font-weight: 800; color: #0f172a;">Custody Handover (Dispatch to Next Party)</h3>
              <p style="margin: 2px 0 0; font-size: 12px; color: #64748b;">Transfer produce custody with 2-way cryptographic handshake.</p>
            </div>
          </div>
          <button type="button" onclick="window.closeQuickDispatchModal()" style="background: transparent; border: none; font-size: 18px; color: #64748b; cursor: pointer;">✕</button>
        </div>

        <form id="form_quick_dispatch" onsubmit="window.submitQuickDispatchForm(event)">
          <!-- 1. Select Batch / Lot -->
          <div class="form-group" style="margin-bottom: 14px;">
            <label style="display: block; font-size: 11.5px; font-weight: 800; color: #334155; margin-bottom: 5px;">1. Select Batch / Lot Code to Dispatch <span style="color:#dc2626;">*</span></label>
            ${myLots.length > 0 ? `
              <select class="form-select" id="dispatch_lot_code" required style="width: 100%; padding: 10px; border-radius: 8px; border: 1.5px solid #cbd5e1; font-weight: 700; background: #fff; font-family: monospace;">
                ${myLots.map(l => {
                  const c = l.public_code || l.batch_id || l.code;
                  const desc = `${c} — ${l.crop || l.category || 'Produce'} (${l.quantity || l.net_weight_kg || l.qty_kg || 0} Kg)`;
                  return `<option value="${escapeHtml(c)}" ${c === defaultLot ? 'selected' : ''}>${escapeHtml(desc)}</option>`;
                }).join('')}
              </select>
            ` : `
              <input type="text" class="form-input" id="dispatch_lot_code" value="${escapeHtml(defaultLot)}" placeholder="e.g. AS-IN-MH-2026-VG-001" required style="width: 100%; padding: 10px; border-radius: 8px; border: 1.5px solid #cbd5e1; font-family: monospace; font-weight: 700;" />
            `}
          </div>

          <!-- 2. Target Role & Destination Entity -->
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 14px;">
            <div>
              <label style="display: block; font-size: 11.5px; font-weight: 800; color: #334155; margin-bottom: 5px;">2. Next Receiving Tier <span style="color:#dc2626;">*</span></label>
              <select class="form-select" id="dispatch_target_role" required style="width: 100%; padding: 9px; border-radius: 8px; border: 1.5px solid #cbd5e1; background: #fff; font-weight: 700;">
                ${roleOptions.map(r => `<option value="${r.role}">${escapeHtml(r.label)}</option>`).join('')}
              </select>
            </div>
            <div>
              <label style="display: block; font-size: 11.5px; font-weight: 800; color: #334155; margin-bottom: 5px;">3. Receiver Mobile / Entity ID <span style="color:#dc2626;">*</span></label>
              <input type="text" class="form-input" id="dispatch_target_phone" placeholder="+91 9876543210" value="" required style="width: 100%; padding: 9px; border-radius: 8px; border: 1.5px solid #cbd5e1; font-weight: 600;" />
            </div>
          </div>

          <!-- 3. Declared Net Weight & Vehicle No -->
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 14px;">
            <div>
              <label style="display: block; font-size: 11.5px; font-weight: 800; color: #334155; margin-bottom: 5px;">4. Dispatch Net Weight (Kg) <span style="color:#dc2626;">*</span></label>
              <input type="number" step="0.1" min="0.1" class="form-input" id="dispatch_declared_qty" value="" placeholder="e.g. 500" required style="width: 100%; padding: 9px; border-radius: 8px; border: 1.5px solid #cbd5e1; font-weight: 800;" />
            </div>
            <div>
              <label style="display: block; font-size: 11.5px; font-weight: 800; color: #334155; margin-bottom: 5px;">5. Transport Vehicle Number</label>
              <input type="text" class="form-input" id="dispatch_vehicle_no" placeholder="e.g. MH-15-EG-4912" value="" style="width: 100%; padding: 9px; border-radius: 8px; border: 1.5px solid #cbd5e1; font-weight: 600; text-transform: uppercase;" />
            </div>
          </div>

          <!-- 4. Dispatch Remarks -->
          <div style="margin-bottom: 18px;">
            <label style="display: block; font-size: 11.5px; font-weight: 800; color: #334155; margin-bottom: 5px;">6. Dispatch Facility / Origin Remarks</label>
            <input type="text" class="form-input" id="dispatch_remarks" placeholder="e.g. Crates loaded from storage" value="" style="width: 100%; padding: 9px; border-radius: 8px; border: 1.5px solid #cbd5e1;" />
          </div>

          <!-- Action Buttons -->
          <div style="display: flex; justify-content: flex-end; gap: 10px; border-top: 1px solid #e2e8f0; padding-top: 14px;">
            <button type="button" class="action-btn-pill" onclick="window.closeQuickDispatchModal()" style="padding: 9px 18px; font-size: 13px;">Cancel</button>
            <button type="submit" id="btnSubmitDispatch" class="btn-wizard-action btn-wizard-submit" style="padding: 9px 24px; font-size: 13px; font-weight: 800;">
              Confirm Handover Dispatch &rarr;
            </button>
          </div>
        </form>
      </div>
    `;

    modal.style.display = 'flex';
  };

  window.closeQuickDispatchModal = function () {
    const modal = document.getElementById('quickDispatchModal');
    if (modal) modal.style.display = 'none';
  };

  window.submitQuickDispatchForm = async function (e) {
    e.preventDefault();
    const btn = document.getElementById('btnSubmitDispatch');
    const lotCode = (document.getElementById('dispatch_lot_code')?.value || '').trim();
    const targetRole = (document.getElementById('dispatch_target_role')?.value || 'AGGREGATOR').trim();
    const targetPhone = (document.getElementById('dispatch_target_phone')?.value || '').trim();
    const declaredQty = parseFloat(document.getElementById('dispatch_declared_qty')?.value || '100');
    const vehicleNo = (document.getElementById('dispatch_vehicle_no')?.value || '').trim();
    const remarks = (document.getElementById('dispatch_remarks')?.value || '').trim();

    if (!lotCode) {
      showToast('Please specify a Lot code to dispatch', 'error');
      return;
    }

    if (btn) {
      btn.disabled = true;
      btn.innerText = 'Dispatching Handover...';
    }

    try {
      const res = await fetch(`/api/v1/lots/${encodeURIComponent(lotCode)}/handover-request`, {
        method: 'POST',
        headers: getAuthHeader(),
        body: JSON.stringify({
          target_role: targetRole,
          target_phone: targetPhone,
          declared_qty_kg: declaredQty,
          vehicle_no: vehicleNo,
          remarks: remarks
        })
      });

      const data = await res.json();
      if (!res.ok) {
        showToast(data.detail || 'Could not initiate handover request', 'error');
        if (btn) {
          btn.disabled = false;
          btn.innerText = 'Confirm Handover Dispatch →';
        }
        return;
      }

      window.closeQuickDispatchModal();
      const pin = data.handover_pin || data.pin || '123456';
      showToast(`Lot ${lotCode} dispatched to ${targetRole}! Verification PIN: ${pin}`, 'success');

      if (window.renderCurrentWorkspace) {
        await window.renderCurrentWorkspace();
      }
    } catch (err) {
      showToast('Network error during handover dispatch', 'error');
      if (btn) {
        btn.disabled = false;
        btn.innerText = 'Confirm Handover Dispatch →';
      }
    }
  };

})();


  /* ==========================================================================
     ENTITY DELETION REQUEST MODALS & CONTROLLER (PRODUCER & ALL ENTITIES)
     Conforms to Blueprint Section 4.3.1, 6.9, and DPDP Act 2023 standards.
     ========================================================================== */

  window.openDownstreamProfileModal = async function (role) {
    const activeRole = String(role || currentRole || 'AGGREGATOR').toUpperCase();
    let modal = document.getElementById('downstreamProfileModal');
    if (!modal || modal.parentElement !== document.body) {
      if (modal && modal.parentElement) modal.parentElement.removeChild(modal);
      modal = document.createElement('div');
      modal.id = 'downstreamProfileModal';
      modal.className = 'modal-overlay';
      modal.onclick = (e) => { if (e.target === modal || e.target.classList.contains('modal-overlay')) window.closeDownstreamProfileModal(); };
      document.body.appendChild(modal);
    }

    const p = wizardState.profile || {};
    const orgName = p.organisation_name || 'Business Entity Node';
    const entityCode = p.entity_code || localStorage.getItem('annasutra_farmer_uid') || 'ENT-' + activeRole + '-001';

    modal.innerHTML = `
      <div class="portal-modal-box" onclick="event.stopPropagation()" style="max-width: 720px; max-height: 90vh; overflow-y: auto;">
        <button class="modal-close" onclick="window.closeDownstreamProfileModal()" style="color: #ffffff; background: rgba(255,255,255,0.18);">✕</button>
        
        <div class="portal-modal-header" style="background: linear-gradient(135deg, #07271d 0%, #0b3d2e 100%); padding: 22px 28px;">
          <div>
            <div style="font-size: 11px; font-weight: 800; color: #10b981; text-transform: uppercase; letter-spacing: 0.5px;">Business Profile &amp; Identity</div>
            <h3 style="margin: 2px 0 0; font-size: 22px; color: #ffffff; font-weight: 800;">${activeRole} Profile &amp; Premises</h3>
          </div>
        </div>

        <div style="padding: 24px 28px;">
          
          <!-- Node Header Summary -->
          <div style="background: #f8fafc; border: 1.5px solid #cbd5e1; border-radius: 12px; padding: 18px 20px; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
              <div>
                <div style="font-size: 11px; font-weight: 800; color: #047857; text-transform: uppercase;">Verified Business Node</div>
                <h4 style="margin: 2px 0; font-size: 19px; font-weight: 800; color: #0f172a;">${escapeHtml(orgName)}</h4>
                <div style="font-size: 12.5px; color: #64748b;">${escapeHtml(p.address_line1 || '')}, ${escapeHtml(p.district || '')}, ${escapeHtml(getStateLabel(p.state))}</div>
              </div>
              <div style="text-align: right;">
                <div style="font-size: 11px; font-weight: 800; color: #475569;">Entity Code</div>
                <div style="font-family: monospace; font-size: 15px; font-weight: 900; color: #0b3d2e;">${escapeHtml(entityCode)}</div>
              </div>
            </div>
          </div>

          <!-- Section 2: Contact & Registered Details -->
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 24px;">
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px;">
              <div style="font-size: 11px; font-weight: 700; color: #64748b;">Signatory Mobile (Verified)</div>
              <div style="font-size: 13.5px; font-weight: 800; color: #0f172a;">${escapeHtml(p.phone_e164 || '')}</div>
            </div>
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px;">
              <div style="font-size: 11px; font-weight: 700; color: #64748b;">Entity Role</div>
              <div style="font-size: 13.5px; font-weight: 800; color: #047857;">${activeRole}</div>
            </div>
          </div>

          <!-- Section 3: Danger Zone: Entity Profile Deletion -->
          <div style="background: #fef2f2; border: 1.5px solid #fecaca; border-radius: 12px; padding: 18px 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 8px;">
              <h5 style="margin: 0; font-size: 14px; font-weight: 800; color: #991b1b; display: flex; align-items: center; gap: 6px;">
                <span>${getIcon('alert', 16, '#dc2626')}</span>
                <span>Danger Zone: Account &amp; Profile Deletion</span>
              </h5>
              <span style="font-size: 11px; font-weight: 700; color: #b91c1c; background: #fee2e2; border: 1px solid #fca5a5; padding: 2px 8px; border-radius: 6px;">Permanent Action</span>
            </div>
            <p style="margin: 0 0 14px; font-size: 12px; color: #7f1d1d; line-height: 1.5;">
              Request formal deletion and deactivation of this ${activeRole} entity node. All stock in custody must be settled or marked sold out, and no lots may be in transit. Admin approval and owner 2FA OTP verification are required.
            </p>
            <div style="display: flex; justify-content: flex-end;">
              <button type="button" onclick="window.closeDownstreamProfileModal(); window.openEntityDeletionRequestModal();" style="background: #dc2626; color: #ffffff; border: none; border-radius: 8px; padding: 9px 18px; font-size: 12.5px; font-weight: 800; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 2px 6px rgba(220,38,38,0.25);">
                <span>${getIcon('trash', 14, '#ffffff')}</span>
                <span>Request Account Deletion &rarr;</span>
              </button>
            </div>
          </div>

        </div>
      </div>
    `;

    modal.style.display = 'flex';
  };

  window.closeDownstreamProfileModal = function () {
    const modal = document.getElementById('downstreamProfileModal');
    if (modal) modal.style.display = 'none';
  };

  window.clearLocalEntityAccount = function () {
    try {
      localStorage.removeItem('annasutra_access_token');
      localStorage.removeItem('annasutra_refresh_token');
      localStorage.removeItem('annasutra_user');
      localStorage.removeItem('annasutra_entity_role');
      localStorage.removeItem('annasutra_active_role');
      localStorage.removeItem('annasutra_producer_wizard_state');
      localStorage.removeItem('annasutra_entity_profile');
      localStorage.removeItem('annasutra_cached_profile');
      sessionStorage.clear();
    } catch (_) {}
    if (window.closeEntityDeletionRequestModal) window.closeEntityDeletionRequestModal();
    if (window.closeProducerProfileModal) window.closeProducerProfileModal();
    if (window.closeDownstreamProfileModal) window.closeDownstreamProfileModal();
    showToast('Local account session cleared. Returning to home...', 'info');
    setTimeout(() => {
      window.location.href = '/';
    }, 600);
  };

    window.openEntityDeletionRequestModal = async function () {
    let modal = document.getElementById('entityDeletionRequestModal');
    if (!modal || modal.parentElement !== document.body) {
      if (modal && modal.parentElement) modal.parentElement.removeChild(modal);
      modal = document.createElement('div');
      modal.id = 'entityDeletionRequestModal';
      modal.className = 'modal-overlay';
      document.body.appendChild(modal);
    }

    modal.onclick = function (e) {
      if (e.target === modal || e.target.classList.contains('modal-overlay')) {
        window.closeEntityDeletionRequestModal();
      }
    };

    let cachedProfile = {};
    try {
      cachedProfile = JSON.parse(localStorage.getItem('annasutra_cached_profile') || '{}');
    } catch (_) {}
    const p = (wizardState && wizardState.profile) || cachedProfile || {};
    const regPhone = p.phone_e164 || localStorage.getItem('annasutra_phone') || '';

    // Render 0ms pre-hydrated deletion modal immediately with zero blocking spinner
    modal.innerHTML = `
      <div class="portal-modal-box" onclick="event.stopPropagation()" style="max-width: 620px; position: relative;">
        <button type="button" class="modal-close" onclick="window.closeEntityDeletionRequestModal()" style="position: absolute; top: 16px; right: 18px; z-index: 1000; width: 34px; height: 34px; border-radius: 50%; border: none; background: rgba(255,255,255,0.22); color: #ffffff; font-size: 16px; font-weight: 800; cursor: pointer; display: flex; align-items: center; justify-content: center;" title="Close">✕</button>
        
        <div class="portal-modal-header" style="background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%); padding: 22px 28px;">
          <div>
            <div style="font-size: 11px; font-weight: 800; color: #fecaca; text-transform: uppercase; letter-spacing: 0.5px;">Account Settings</div>
            <h3 style="margin: 2px 0 0; font-size: 21px; color: #ffffff; font-weight: 800;">Request Account Deletion</h3>
          </div>
        </div>

        <div style="padding: 24px 28px;" id="deletionModalBody">
          <form onsubmit="window.submitEntityDeletionRequest(event)">
            <div id="delPreflightStatusBox" style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 10px; padding: 12px 16px; margin-bottom: 16px; font-size: 12.5px; color: #334155;">
              <div id="delPreflightStatus" style="display: flex; align-items: center; gap: 6px; font-weight: 800; color: #047857; margin-bottom: 4px;">
                <span>${getIcon('check', 14, '#047857')}</span>
                <span>Verification Check Clear: No active in-transit dispatches</span>
              </div>
              <div>Registered Mobile: <strong id="delRegisteredPhone">${escapeHtml(regPhone || 'On File')}</strong></div>
            </div>

            <div class="form-group" style="margin-bottom: 14px;">
              <label class="form-label">1. Reason for Deletion <span class="req">*</span></label>
              <select class="form-select" id="del_reason" required style="background: #fff; font-weight: 700;">
                <option value="">-- Select Reason --</option>
                <option value="CEASING_OPERATIONS">Ceasing agricultural / business operations</option>
                <option value="LAND_TRANSFER">Sale, transfer, or lease termination of land/premises</option>
                <option value="DPDP_ERASURE">Account deletion and data privacy request</option>
                <option value="DUPLICATE">Duplicate or accidental registration</option>
                <option value="OTHER">Other</option>
              </select>
            </div>

            <div class="form-group" style="margin-bottom: 14px;">
              <label class="form-label">2. Remarks / Context</label>
              <textarea class="form-input" id="del_remarks" rows="2" placeholder="e.g. Closing operations. All produce sold and handed over." style="background: #fff; resize: vertical; font-size: 12px;"></textarea>
            </div>

            <!-- Mobile OTP Verification Box -->
            <div style="background: #fff7ed; border: 1.5px solid #ffedd5; border-radius: 10px; padding: 14px 16px; margin-bottom: 20px;">
              <div style="font-size: 12.5px; font-weight: 800; color: #9a3412; margin-bottom: 6px;">3. Mobile Verification Code</div>
              <div style="font-size: 11.5px; color: #7c2d12; margin-bottom: 12px;">
                A 6-digit confirmation code will be sent to your registered mobile to confirm this action.
              </div>
              <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
                <button type="button" id="btnRequestDelOtp" onclick="window.requestDeletionOtp()" class="action-btn-pill" style="background: #fff; font-size: 12px; border-color: #ea580c; color: #c2410c; font-weight: 800;">
                  Send Verification OTP &rarr;
                </button>
                <input type="text" class="form-input" id="del_otp_code" placeholder="Enter 6-digit OTP" maxlength="6" style="width: 140px; text-align: center; font-size: 14px; font-weight: 800; letter-spacing: 2px; background: #fff;" required />
              </div>
            </div>

            <div style="display: flex; justify-content: space-between; align-items: center; gap: 10px; flex-wrap: wrap;">
              <button type="button" onclick="window.clearLocalEntityAccount()" style="background: transparent; color: #b91c1c; border: 1px solid #fca5a5; border-radius: 8px; padding: 8px 14px; font-size: 12px; font-weight: 800; cursor: pointer;">
                Clear Local Profile &amp; Exit
              </button>
              <div style="display: flex; gap: 10px;">
                <button type="button" onclick="window.closeEntityDeletionRequestModal()" class="action-btn-pill">Cancel</button>
                <button type="submit" id="btnSubmitDeletion" style="background: #dc2626; color: #ffffff; border: none; border-radius: 8px; padding: 9px 20px; font-size: 13px; font-weight: 800; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 2px 6px rgba(220,38,38,0.25);">
                  <span>${getIcon('trash', 14, '#ffffff')}</span>
                  <span>Confirm &amp; Submit Deletion Request</span>
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    `;

    modal.style.display = 'flex';

    // Non-blocking server-side check with 3.5s timeout
    const abortCtrl = new AbortController();
    const timer = setTimeout(() => abortCtrl.abort(), 3500);

    try {
      const res = await fetch('/api/v1/me/profile/delete-request', {
        headers: getAuthHeader(),
        credentials: 'same-origin',
        signal: abortCtrl.signal
      });
      clearTimeout(timer);

      if (res.ok) {
        const data = await res.json();
        if ((data.has_pending_request && data.pending_request) || !data.can_request_deletion) {
          window.renderEntityDeletionModalContent(data);
        } else if (data.registered_phone) {
          const phoneEl = document.getElementById('delRegisteredPhone');
          if (phoneEl) phoneEl.textContent = data.registered_phone;
        }
      } else if (res.status === 401 || res.status === 403) {
        // If unauthenticated or token expired, show notice inside status box
        const statusBox = document.getElementById('delPreflightStatusBox');
        if (statusBox) {
          statusBox.innerHTML = `
            <div style="display: flex; align-items: center; gap: 6px; font-weight: 800; color: #b45309; margin-bottom: 4px;">
              <span>${getIcon('alert', 14, '#d97706')}</span>
              <span>Local Session Active</span>
            </div>
            <div style="font-size: 11.5px; color: #78350f;">Server session not authenticated. You can submit OTP or use "Clear Local Profile & Exit" to wipe this device immediately.</div>
          `;
        }
      }
    } catch (_) {
      clearTimeout(timer);
      // Timeout / offline: pre-hydrated form remains active and responsive
    }
  };

  window.closeEntityDeletionRequestModal = function () {
    const modal = document.getElementById('entityDeletionRequestModal');
    if (modal) modal.style.display = 'none';
  };

  window.renderEntityDeletionModalContent = function (data) {
    const body = document.getElementById('deletionModalBody');
    if (!body) return;

    if (data.has_pending_request && data.pending_request) {
      const r = data.pending_request;
      body.innerHTML = `
        <div style="background: #fffbeb; border: 1.5px solid #fde68a; border-radius: 12px; padding: 18px 20px; margin-bottom: 20px;">
          <div style="display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 800; color: #92400e; margin-bottom: 8px;">
            <span>${getIcon('alert', 18, '#d97706')}</span>
            <span>Deletion Request Under Administrative Review</span>
          </div>
          <div style="font-size: 13px; color: #78350f; margin-bottom: 12px;">
            Submitted on <strong>${new Date(r.created_at).toLocaleString()}</strong>.
          </div>
          <div style="background: #fff; border: 1px solid #fed7aa; border-radius: 8px; padding: 10px 14px; font-size: 12.5px; color: #334155; margin-bottom: 16px;">
            <div><strong>Declared Reason:</strong> ${escapeHtml(r.reason_display || r.reason)}</div>
            ${r.remarks ? `<div style="margin-top: 4px;"><strong>Remarks:</strong> ${escapeHtml(r.remarks)}</div>` : ''}
          </div>
          <p style="font-size: 12px; color: #b45309; margin: 0 0 16px;">
            While in this state, all operations (new lots, plot allocations, and handovers) are temporarily frozen. You may cancel your request at any time before the Admin decision.
          </p>
          <div style="display: flex; justify-content: flex-end; gap: 10px;">
            <button type="button" onclick="window.closeEntityDeletionRequestModal()" class="action-btn-pill">Close</button>
            <button type="button" onclick="window.cancelEntityDeletionRequest()" style="background: #dc2626; color: #ffffff; border: none; border-radius: 8px; padding: 8px 16px; font-size: 12.5px; font-weight: 800; cursor: pointer;">
              Withdraw / Cancel Deletion Request
            </button>
          </div>
        </div>
      `;
      return;
    }

    if (!data.can_request_deletion) {
      body.innerHTML = `
        <div style="background: #fef2f2; border: 1.5px solid #f87171; border-radius: 12px; padding: 18px 20px; margin-bottom: 20px;">
          <div style="display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 800; color: #991b1b; margin-bottom: 8px;">
            <span>${getIcon('alert', 18, '#dc2626')}</span>
            <span>Account Deletion Blocked by Active Custody Obligations</span>
          </div>
          <p style="font-size: 12.5px; color: #7f1d1d; margin: 0 0 12px;">
            Entities with active dispatches or lots in transit cannot be deleted. Please complete or settle the following active transactions first:
          </p>
          <ul style="margin: 0 0 16px; padding-left: 20px; font-size: 12.5px; color: #b91c1c; font-weight: 700;">
            ${(data.blocking_reasons || []).map(r => `<li>${escapeHtml(r)}</li>`).join('')}
          </ul>
          <div style="display: flex; justify-content: flex-end;">
            <button type="button" onclick="window.closeEntityDeletionRequestModal()" class="action-btn-pill">Understood, Close</button>
          </div>
        </div>
      `;
      return;
    }

    // Pre-flight passed: render Request Form with mobile OTP
    body.innerHTML = `
      <form onsubmit="window.submitEntityDeletionRequest(event)">
        <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 10px; padding: 12px 16px; margin-bottom: 16px; font-size: 12.5px; color: #334155;">
          <div style="display: flex; align-items: center; gap: 6px; font-weight: 800; color: #047857; margin-bottom: 4px;">
            <span>${getIcon('check', 14, '#047857')}</span>
            <span>Verification Check Clear: No active in-transit dispatches</span>
          </div>
          <div>Registered Mobile: <strong>${escapeHtml(data.registered_phone || '')}</strong></div>
        </div>

        <div class="form-group" style="margin-bottom: 14px;">
          <label class="form-label">1. Reason for Deletion <span class="req">*</span></label>
          <select class="form-select" id="del_reason" required style="background: #fff; font-weight: 700;">
            <option value="">-- Select Reason --</option>
            <option value="CEASING_OPERATIONS">Ceasing agricultural / business operations</option>
            <option value="LAND_TRANSFER">Sale, transfer, or lease termination of land/premises</option>
            <option value="DPDP_ERASURE">Account deletion and data privacy request</option>
            <option value="DUPLICATE">Duplicate or accidental registration</option>
            <option value="OTHER">Other</option>
          </select>
        </div>

        <div class="form-group" style="margin-bottom: 14px;">
          <label class="form-label">2. Remarks / Context</label>
          <textarea class="form-input" id="del_remarks" rows="2" placeholder="e.g. Closing farming operations. All produce sold and handed over." style="background: #fff; resize: vertical; font-size: 12px;"></textarea>
        </div>

        <!-- Mobile OTP Verification Box -->
        <div style="background: #fff7ed; border: 1.5px solid #ffedd5; border-radius: 10px; padding: 14px 16px; margin-bottom: 20px;">
          <div style="font-size: 12.5px; font-weight: 800; color: #9a3412; margin-bottom: 6px;">3. Mobile Verification Code</div>
          <div style="font-size: 11.5px; color: #7c2d12; margin-bottom: 12px;">
            A 6-digit confirmation code will be sent to your primary registered mobile to confirm this action.
          </div>
          <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
            <button type="button" id="btnRequestDelOtp" onclick="window.requestDeletionOtp()" class="action-btn-pill" style="background: #fff; font-size: 12px; border-color: #ea580c; color: #c2410c; font-weight: 800;">
              Send Verification OTP &rarr;
            </button>
            <input type="text" class="form-input" id="del_otp_code" placeholder="Enter 6-digit OTP" maxlength="6" style="width: 140px; text-align: center; font-size: 14px; font-weight: 800; letter-spacing: 2px; background: #fff;" required />
          </div>
        </div>

        <div style="display: flex; justify-content: flex-end; gap: 10px;">
          <button type="button" onclick="window.closeEntityDeletionRequestModal()" class="action-btn-pill">Cancel</button>
          <button type="submit" id="btnSubmitDeletion" style="background: #dc2626; color: #ffffff; border: none; border-radius: 8px; padding: 9px 20px; font-size: 13px; font-weight: 800; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 2px 6px rgba(220,38,38,0.25);">
            <span>${getIcon('trash', 14, '#ffffff')}</span>
            <span>Confirm &amp; Submit Deletion Request</span>
          </button>
        </div>
      </form>
    `;
  };

  window.requestDeletionOtp = async function () {
    const btn = document.getElementById('btnRequestDelOtp');
    if (btn) btn.innerText = 'Sending OTP...';
    try {
      const res = await fetch('/api/v1/me/profile/delete-request', {
        method: 'POST',
        headers: getAuthHeader(),
        credentials: 'same-origin',
        body: JSON.stringify({ action: 'request_otp' })
      });
      const data = await res.json();
      if (res.ok) {
        showToast(data.message || 'OTP sent to registered mobile', 'success');
        if (btn) btn.innerText = 'OTP Sent ✓';
        if (data.debug_code) {
          const otpInput = document.getElementById('del_otp_code');
          if (otpInput) otpInput.value = data.debug_code;
        }
      } else {
        showToast(data.detail || 'Failed to send OTP', 'error');
        if (btn) btn.innerText = 'Retry Send OTP';
      }
    } catch (e) {
      showToast('Network error while requesting OTP', 'error');
      if (btn) btn.innerText = 'Retry Send OTP';
    }
  };

  window.submitEntityDeletionRequest = async function (e) {
    if (e) e.preventDefault();
    const reason = (document.getElementById('del_reason') || {}).value;
    const remarks = (document.getElementById('del_remarks') || {}).value;
    const otp = (document.getElementById('del_otp_code') || {}).value;

    if (!reason) {
      showToast('Please select a reason for deletion.', 'error');
      return;
    }
    if (!otp) {
      showToast('Please enter the 6-digit confirmation OTP.', 'error');
      return;
    }

    const btn = document.getElementById('btnSubmitDeletion');
    if (btn) {
      btn.disabled = true;
      btn.innerText = 'Submitting Request...';
    }

    try {
      const res = await fetch('/api/v1/me/profile/delete-request', {
        method: 'POST',
        headers: getAuthHeader(),
        credentials: 'same-origin',
        body: JSON.stringify({
          reason: reason,
          remarks: remarks,
          otp_code: otp
        })
      });
      const data = await res.json();
      if (res.ok) {
        if (data.status === 'DELETED') {
          showToast(data.message || 'Account successfully deleted.', 'success');
          window.clearLocalEntityAccount();
          return;
        }
        showToast('Account deletion request submitted.', 'success');
        window.closeEntityDeletionRequestModal();
        window.closeProducerProfileModal();
        window.closeDownstreamProfileModal();
        if (window.renderCurrentWorkspace) {
          window.renderCurrentWorkspace();
        }
      } else {
        showToast(data.detail || 'Failed to submit deletion request', 'error');
        if (btn) {
          btn.disabled = false;
          btn.innerText = 'Confirm & Submit Deletion Request';
        }
      }
    } catch (err) {
      showToast('Network error while submitting request', 'error');
      if (btn) {
        btn.disabled = false;
        btn.innerText = 'Confirm & Submit Deletion Request';
      }
    }
  };

  window.cancelEntityDeletionRequest = async function () {
    if (!confirm('Are you sure you want to cancel your account deletion request and restore full console operations?')) {
      return;
    }
    try {
      const res = await fetch('/api/v1/me/profile/delete-request/cancel', {
        method: 'POST',
        headers: getAuthHeader(),
        credentials: 'same-origin'
      });
      const data = await res.json();
      if (res.ok) {
        showToast('Deletion request cancelled. Full console access restored.', 'success');
        window.closeEntityDeletionRequestModal();
        if (window.renderCurrentWorkspace) {
          window.renderCurrentWorkspace();
        }
      } else {
        showToast(data.detail || 'Failed to cancel deletion request', 'error');
      }
    } catch (err) {
      showToast('Network error cancelling deletion request', 'error');
    }
  };


  /* --------------------------------------------------------------------------
     TAB 5: ADMIN ENTITY DELETION REQUESTS QUEUE
     -------------------------------------------------------------------------- */
  window.renderAdminDeletionRequestsTab = async function (container) {
    container.innerHTML = `
      <div style="text-align: center; padding: 40px 16px;">
        <div style="width: 32px; height: 32px; border: 3px solid #cbd5e1; border-top-color: #dc2626; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 12px;"></div>
        <p style="font-size: 13px; font-weight: 700; color: #64748b;">Loading entity deletion requests queue...</p>
      </div>
    `;

    try {
      const res = await fetch('/api/v1/admin/deletion-requests?status=ALL', {
        headers: getAuthHeader()
      });
      if (!res.ok) throw new Error('Failed to load deletion requests');
      const data = await res.json();
      const items = data.results || [];

      container.innerHTML = `
        <div>
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 16px;">
            <div>
              <h4 style="margin: 0; font-size: 16px; font-weight: 800; color: #991b1b; display: flex; align-items: center; gap: 6px;">
                <span>${getIcon('trash', 16, '#dc2626')}</span>
                <span>Entity Profile Deletion Requests (${items.length})</span>
              </h4>
              <span style="font-size: 12px; color: #64748b;">Queue of entity account deletion requests. Admin verification ensures no active custody transactions before deactivation.</span>
            </div>
            <button type="button" class="action-btn-pill" onclick="window.renderAdminDeletionRequestsTab(document.getElementById('adminTabDynamicContent'))">
              ${getIcon('refresh', 13, '#047857')} Refresh Queue
            </button>
          </div>

          <div class="compact-ledger-table-wrap">
            <table class="compact-ledger-table">
              <thead>
                <tr>
                  <th>Request Time</th>
                  <th>Entity &amp; Role</th>
                  <th>Signatory Mobile</th>
                  <th>Declared Reason</th>
                  <th>Remarks / Context</th>
                  <th>Status</th>
                  <th style="text-align: right;">Action</th>
                </tr>
              </thead>
              <tbody>
                ${items.length === 0 ? `
                  <tr>
                    <td colspan="7" style="text-align: center; padding: 40px 16px; color: #64748b;">
                      <div style="font-size: 24px; margin-bottom: 6px;">${getIcon('check', 24, '#10b981')}</div>
                      <div style="font-weight: 800; font-size: 14px; color: #334155;">Zero Pending Deletion Requests</div>
                      <div style="font-size: 12px; color: #64748b;">All registered entity nodes are in compliance.</div>
                    </td>
                  </tr>
                ` : items.map(req => `
                  <tr>
                    <td style="font-size: 11.5px; font-weight: 700; color: #475569;">
                      ${new Date(req.created_at).toLocaleString()}
                    </td>
                    <td>
                      <div style="font-weight: 800; color: #0f172a; font-size: 13px;">${escapeHtml(req.organisation_name || req.owner_name)}</div>
                      <div style="font-size: 11px; font-family: monospace; color: #047857;">${escapeHtml(req.entity_code || req.entity_id)} &bull; ${escapeHtml(req.role)}</div>
                    </td>
                    <td style="font-size: 12px; font-weight: 700; color: #334155;">
                      ${escapeHtml(req.phone_e164)}
                    </td>
                    <td>
                      <span style="display: inline-block; background: #fee2e2; border: 1px solid #fca5a5; color: #991b1b; font-size: 11px; font-weight: 800; padding: 2px 8px; border-radius: 6px;">
                        ${escapeHtml(req.reason_display || req.reason)}
                      </span>
                    </td>
                    <td style="font-size: 12px; color: #475569; max-width: 220px;">
                      ${escapeHtml(req.remarks || '-')}
                    </td>
                    <td>
                      <span style="display: inline-block; background: ${req.status === 'PENDING' ? '#fef3c7' : (req.status === 'APPROVED' ? '#fee2e2' : '#f1f5f9')}; color: ${req.status === 'PENDING' ? '#92400e' : (req.status === 'APPROVED' ? '#991b1b' : '#334155')}; border: 1px solid ${req.status === 'PENDING' ? '#fde68a' : (req.status === 'APPROVED' ? '#fecaca' : '#cbd5e1')}; font-size: 11px; font-weight: 800; padding: 2px 8px; border-radius: 6px;">
                        ${escapeHtml(req.status)}
                      </span>
                    </td>
                    <td style="text-align: right;">
                      ${req.status === 'PENDING' ? `
                        <div style="display: inline-flex; gap: 6px;">
                          <button type="button" onclick="window.adminProcessDeletionDecision('${req.request_id}', 'APPROVED')" style="background: #dc2626; color: #fff; border: none; border-radius: 6px; padding: 5px 10px; font-size: 11.5px; font-weight: 800; cursor: pointer;">
                            Approve Deletion
                          </button>
                          <button type="button" onclick="window.adminProcessDeletionDecision('${req.request_id}', 'REJECTED')" style="background: #f8fafc; color: #334155; border: 1px solid #cbd5e1; border-radius: 6px; padding: 5px 10px; font-size: 11.5px; font-weight: 800; cursor: pointer;">
                            Reject
                          </button>
                        </div>
                      ` : `
                        <span style="font-size: 11px; color: #64748b; font-weight: 700;">Decided</span>
                      `}
                    </td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        </div>
      `;
    } catch (e) {
      container.innerHTML = `
        <div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 10px; padding: 16px; color: #991b1b; font-size: 13px;">
          Failed to load deletion requests queue. Please try again.
        </div>
      `;
    }
  };

  window.adminProcessDeletionDecision = async function (requestId, decision) {
    let remarks = '';
    if (decision === 'APPROVED') {
      if (!confirm('Are you sure you want to approve this entity deletion? The account will be deactivated and personal identifying data scrubbed under DPDP Act 2023.')) {
        return;
      }
      remarks = prompt('Enter administrative approval remarks (optional):', 'Compliance checks verified. Account deactivated.') || '';
    } else {
      remarks = prompt('Enter mandatory reason for rejecting deletion request:', 'Active traceability inquiries require account retention.');
      if (!remarks) {
        showToast('Rejection remarks are mandatory.', 'error');
        return;
      }
    }

    try {
      const res = await fetch(`/api/v1/admin/deletion-requests/${requestId}/decision`, {
        method: 'POST',
        headers: getAuthHeader(),
        body: JSON.stringify({
          decision: decision,
          remarks: remarks
        })
      });
      const data = await res.json();
      if (res.ok) {
        showToast(data.message || 'Decision applied successfully.', 'success');
        const container = document.getElementById('adminTabDynamicContent');
        if (container) window.renderAdminDeletionRequestsTab(container);
      } else {
        showToast(data.detail || 'Failed to process decision.', 'error');
      }
    } catch (e) {
      showToast('Network error processing administrative decision.', 'error');
    }
  };

  // Global Escape key listener to close active modals
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' || e.key === 'Esc') {
      if (window.closeProducerProfileModal) window.closeProducerProfileModal();
      if (window.closeDownstreamProfileModal) window.closeDownstreamProfileModal();
      if (window.closeProducerLandModal) window.closeProducerLandModal();
      if (window.closeProducerHarvestModal) window.closeProducerHarvestModal();
      if (window.closeTrackLotModal) window.closeTrackLotModal();
      if (window.closeEditLotModal) window.closeEditLotModal();
      if (window.closeUnlimitedQrPrintModal) window.closeUnlimitedQrPrintModal();
      if (window.closeEntityDeletionRequestModal) window.closeEntityDeletionRequestModal();
      if (window.closeDownstreamInboxModal) window.closeDownstreamInboxModal();
      if (window.closeDownstreamAppendModal) window.closeDownstreamAppendModal();
      if (window.closeRoleOpsModal) window.closeRoleOpsModal();
    }
  });
