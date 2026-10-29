import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../auth/domain/auth_state.dart';
import '../../auth/presentation/controllers/auth_controller.dart';
import '../../auth/presentation/dpdp_consent_dialog.dart';
import '../../lots/domain/harvest_lot.dart';
import '../../lots/presentation/controllers/lots_controller.dart';
import '../../lots/presentation/widgets/lot_card.dart';
import '../../sync/sync_service.dart';

class HomeScreen extends ConsumerStatefulWidget {
  final void Function(Locale locale)? onLocaleChanged;

  const HomeScreen({super.key, this.onLocaleChanged});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  int _currentNavIndex = 0; // 0: Batches, 1: Handover, 2: Insights, 3: Profile
  String _selectedLang = 'en';

  // Search & Filter State
  final TextEditingController _searchController = TextEditingController();
  String _selectedCustodyFilter = 'ALL';

  // Auth form controllers for unauthenticated view
  final TextEditingController _phoneController = TextEditingController(text: '9876543210');
  final TextEditingController _otpController = TextEditingController(text: '123456');
  final TextEditingController _publicLotSearchController = TextEditingController(text: 'LOT-2026-WB-0042');
  String _selectedRole = 'PRODUCER';

  static const List<Map<String, String>> _mandiTickerData = [
    {'crop': 'Paddy (Dhan)', 'rate': '₹2,350/q', 'change': '+2.4%', 'mandi': 'Burdwan'},
    {'crop': 'Mustard Seed', 'rate': '₹5,450/q', 'change': '+1.8%', 'mandi': 'Alwar'},
    {'crop': 'Potato (Jyoti)', 'rate': '₹1,680/q', 'change': '+0.9%', 'mandi': 'Hooghly'},
    {'crop': 'Onion (Nashik)', 'rate': '₹2,800/q', 'change': '-1.2%', 'mandi': 'Lasalgaon'},
    {'crop': 'Wheat (Sharbati)', 'rate': '₹2,420/q', 'change': '+3.1%', 'mandi': 'Indore'},
    {'crop': 'Tomato (Hybrid)', 'rate': '₹2,100/q', 'change': '+4.5%', 'mandi': 'Kolar'},
  ];

  static const List<Map<String, String>> _ecosystemStats = [
    {'num': '1,42,850+ Kg', 'label': 'Produce Tracked', 'sub': 'Cryptographically sealed'},
    {'num': '2,480+', 'label': 'Registered Farmers', 'sub': 'Aadhaar / KYC Verified'},
    {'num': '99.8%', 'label': 'Certified Grade A', 'sub': 'Lab & FSSAI Standards'},
    {'num': '48,900+', 'label': 'Consumer Scans', 'sub': 'Farm-to-fork verified'},
    {'num': '100%', 'label': 'Append-Only Ledger', 'sub': 'EPCIS 2.0 / SHA-256'},
    {'num': '0.0%', 'label': 'DPDP Leakage', 'sub': 'Statutory Consent Compliant'},
  ];

  static const List<Map<String, dynamic>> _supplyChainTiers = [
    {
      'tier': 'Tier 1',
      'title': 'Farm Origin',
      'role': 'Farmer / FPO',
      'desc': 'Harvest attestation, plot GIS & tamper-evident QR crate labels.',
      'icon': Icons.agriculture,
      'color': Color(0xFF047857),
    },
    {
      'tier': 'Tier 2',
      'title': 'Mandi Aggregator',
      'role': 'APMC Market',
      'desc': 'Digital weighbridge gross weight attestation & e-NAM settlement.',
      'icon': Icons.storefront_outlined,
      'color': Color(0xFFD97706),
    },
    {
      'tier': 'Tier 3',
      'title': 'Wholesaler',
      'role': 'Cold Storage',
      'desc': 'Cold chain temperature logs & lot split/merge custody tracking.',
      'icon': Icons.inventory_2_outlined,
      'color': Color(0xFF0284C7),
    },
    {
      'tier': 'Tier 4',
      'title': 'Distributor',
      'role': 'Logistics Fleet',
      'desc': 'GPS waypoint transit handovers & tamper-seal verification.',
      'icon': Icons.local_shipping_outlined,
      'color': Color(0xFF7C3AED),
    },
    {
      'tier': 'Tier 5',
      'title': 'Retailer & Consumer',
      'role': 'Point of Sale',
      'desc': 'Instant QR passport scan revealing harvest-to-shelf provenance.',
      'icon': Icons.verified_user_outlined,
      'color': Color(0xFF059669),
    },
  ];

  static const List<Map<String, dynamic>> _categoryTaxonomy = [
    {'code': 'FG', 'name': 'Food Grains', 'example': 'Paddy, Wheat, Maize', 'icon': Icons.grain},
    {'code': 'PU', 'name': 'Pulses', 'example': 'Gram, Tur, Moong, Urad', 'icon': Icons.spa},
    {'code': 'OI', 'name': 'Oilseeds', 'example': 'Mustard, Soybean, Groundnut', 'icon': Icons.water_drop},
    {'code': 'FR', 'name': 'Fruits', 'example': 'Mango, Apple, Banana, Orange', 'icon': Icons.apple},
    {'code': 'VG', 'name': 'Vegetables', 'example': 'Potato, Onion, Tomato', 'icon': Icons.local_florist},
    {'code': 'SP', 'name': 'Spices', 'example': 'Turmeric, Cardamom, Cumin', 'icon': Icons.flare},
    {'code': 'CC', 'name': 'Commercial Crops', 'example': 'Sugarcane, Cotton, Jute', 'icon': Icons.factory},
    {'code': 'LS', 'name': 'Livestock & Dairy', 'example': 'A2 Cow Milk, Ghee, Honey', 'icon': Icons.pets},
    {'code': 'SC', 'name': 'Seeds & Planting', 'example': 'Certified Organic Seeds', 'icon': Icons.eco},
    {'code': 'OT', 'name': 'Other Specialties', 'example': 'Mushroom, Tea, Coffee', 'icon': Icons.category},
  ];

  static const List<Map<String, dynamic>> _roleOptions = [
    {'code': 'PRODUCER', 'label': 'Farmer / FPO', 'icon': Icons.agriculture},
    {'code': 'AGGREGATOR', 'label': 'Mandi / APMC', 'icon': Icons.storefront_outlined},
    {'code': 'WHOLESALER', 'label': 'Wholesaler', 'icon': Icons.inventory_2_outlined},
    {'code': 'DISTRIBUTOR', 'label': 'Distributor', 'icon': Icons.local_shipping_outlined},
    {'code': 'RETAILER', 'label': 'Retailer Shop', 'icon': Icons.shopping_bag_outlined},
  ];

  static const Map<String, Map<String, String>> _strings = {
    'en': {
      'appTitle': 'AnnaSutra',
      'appSubtitle': 'Producer Operations Console',
      'navBatches': 'Batches',
      'navHandover': 'Handover',
      'navInsights': 'Insights',
      'navProfile': 'Profile',
      'farmerId': 'Unique Farmer ID',
      'activeBatches': 'Active Batches',
      'inCustody': 'In Farm Custody',
      'inTransit': 'In Transit',
      'totalWeight': 'Total Harvest Weight',
      'newBatch': 'New Batch',
      'searchPh': 'Search crop, lot code, or plot...',
      'filterAll': 'All',
      'filterCustody': 'Farm Custody',
      'filterTransit': 'In Transit',
      'filterDelivered': 'Accepted',
      'noBatchesTitle': 'No Harvest Lots Yet',
      'noBatchesSub': 'Register your first produce lot to generate tamper-proof QR crate labels.',
      'btnCreateFirst': '+ Create First Batch',
      'handoverTitle': 'Custody Transfer',
      'handoverSub': 'Hand over produce lot to counterparty with verified QR confirmation.',
      'scanToReceive': 'Scan QR to Receive Custody',
      'scanToReceiveSub': 'Inspect incoming produce crates, verify net weight & append condition telemetry.',
      'btnScanQr': 'Scan Crate QR',
      'manualCodePh': 'Or enter Lot Code manually',
      'btnVerifyAccept': 'Accept & Append Telemetry',
      'dispatchedBatches': 'Dispatched Batches (In Transit)',
      'noDispatched': 'No active outgoing handovers pending counterparty sign-off.',
      'insightsTitle': 'Farm & Harvest Insights',
      'grossValuation': 'Gross Valuation',
      'realizedRevenue': 'Realized Revenue',
      'gradeARatio': 'Grade A Quality Ratio',
      'cropBreakdown': 'Crop Volume Distribution',
      'plotsTitle': 'Mapped Agricultural Plots',
      'profileTitle': 'Producer Digital Node',
      'kycVerified': 'KYC Verified',
      'kycPending': 'KYC Under Review',
      'maskedPan': 'PAN Identity',
      'bankAccount': 'Settlement Bank',
      'statutoryConsent': 'DPDP Act 2023 Consent Active',
      'btnLogout': 'Log Out',
      'loginTitle': 'Farm-to-Fork Traceability',
      'loginSub': 'National Sovereign Agri-Traceability Console',
      'phoneLabel': 'Mobile Number',
      'otpLabel': 'Enter 6-digit OTP',
      'btnSendOtp': 'Get OTP via SMS',
      'btnVerifyOtp': 'Verify & Sign In',
      'btnGoogle': 'Sign in with Google',
      'dpdpNotice': 'Protected under DPDP Act 2023 • C-DAC Sovereign Node',
    },
    'hi': {
      'appTitle': 'अन्नसूत्र',
      'appSubtitle': 'उत्पादक संचालन कंसोल',
      'navBatches': 'फ़सल बैच',
      'navHandover': 'हैंडओवर',
      'navInsights': 'इनसाइट्स',
      'navProfile': 'प्रोफ़ाइल',
      'farmerId': 'किसान विशिष्ट पहचान (ID)',
      'activeBatches': 'सक्रिय बैच',
      'inCustody': 'फ़ार्म कस्टडी में',
      'inTransit': 'पारगमन में',
      'totalWeight': 'कुल फ़सल वजन',
      'newBatch': 'नया बैच',
      'searchPh': 'फ़सल, बैच कोड या खेत से खोजें...',
      'filterAll': 'सभी',
      'filterCustody': 'फ़ार्म कस्टडी',
      'filterTransit': 'पारगमन में',
      'filterDelivered': 'स्वीकृत',
      'noBatchesTitle': 'कोई फ़सल बैच नहीं है',
      'noBatchesSub': 'असीमित क्यूआर क्रेट लेबल उत्पन्न करने के लिए अपना पहला फ़सल लॉट पंजीकृत करें।',
      'btnCreateFirst': '+ पहला बैच बनाएं',
      'handoverTitle': 'कस्टडी हस्तांतरण',
      'handoverSub': 'सत्यापित क्यूआर पुष्टि के साथ प्रतिपक्ष को कस्टडी हस्तांतरित करें।',
      'scanToReceive': 'कस्टडी प्राप्त करने के लिए क्यूआर स्कैन करें',
      'scanToReceiveSub': 'आवक क्रेट्स का निरीक्षण करें, वजन सत्यापित करें व स्थिति दर्ज करें।',
      'btnScanQr': 'क्रेट क्यूआर स्कैन करें',
      'manualCodePh': 'या लॉट कोड दर्ज करें',
      'btnVerifyAccept': 'स्वीकार करें व दर्ज करें',
      'dispatchedBatches': 'प्रेषित बैच (पारगमन में)',
      'noDispatched': 'प्रतिपक्ष की पुष्टि के लिए कोई हैंडओवर लंबित नहीं है।',
      'insightsTitle': 'फ़ार्म एवं फ़सल विश्लेषण',
      'grossValuation': 'सकल मूल्यांकन',
      'realizedRevenue': 'प्राप्त राजस्व',
      'gradeARatio': 'ग्रेड-ए गुणवत्ता अनुपात',
      'cropBreakdown': 'फ़सल मात्रा वितरण',
      'plotsTitle': 'सत्यापित कृषि भूखंड',
      'profileTitle': 'उत्पादक डिजिटल नोड',
      'kycVerified': 'केवाईसी सत्यापित',
      'kycPending': 'केवाईसी समीक्षाधीन',
      'maskedPan': 'पैन पहचान',
      'bankAccount': 'निपटान बैंक',
      'statutoryConsent': 'डीपीडीपी अधिनियम २०२३ सहमति सक्रिय',
      'btnLogout': 'लॉग आउट',
      'loginTitle': 'बीज से थाली तक ट्रेसेबिलिटी',
      'loginSub': 'राष्ट्रीय संप्रभु कृषि-ट्रेसेबिलिटी कंसोल',
      'phoneLabel': 'मोबाइल नंबर',
      'otpLabel': '६-अंकीय ओटीपी दर्ज करें',
      'btnSendOtp': 'ओटीपी प्राप्त करें',
      'btnVerifyOtp': 'सत्यापित करें व प्रवेश करें',
      'btnGoogle': 'गूगल से लॉगिन करें',
      'dpdpNotice': 'डीपीडीपी अधिनियम २०२३ के तहत सुरक्षित • सी-डैक संप्रभु नोड',
    },
    'bn': {
      'appTitle': 'অন্নসূত্র',
      'appSubtitle': 'উৎপাদক অপারেশন কনসোল',
      'navBatches': 'ফসল ব্যাচ',
      'navHandover': 'হস্তান্তর',
      'navInsights': 'বিশ্লেষণ',
      'navProfile': 'প্রোফাইল',
      'farmerId': 'কৃষক ইউনিক আইডি',
      'activeBatches': 'সক্রিয় ব্যাচ',
      'inCustody': 'খামার হেফাজতে',
      'inTransit': 'ট্রানজিটে',
      'totalWeight': 'মোট ফসলের ওজন',
      'newBatch': 'নতুন ব্যাচ',
      'searchPh': 'ফসল, ব্যাচ কোড বা জমি দিয়ে খুঁজুন...',
      'filterAll': 'সকল',
      'filterCustody': 'খামার হেফাজত',
      'filterTransit': 'ট্রানজিটে',
      'filterDelivered': 'গৃহীত',
      'noBatchesTitle': 'কোনো ফসল ব্যাচ নেই',
      'noBatchesSub': 'অফিসিয়াল কিউআর লেবেল পেতে প্রথম ফসল লট নিবন্ধন করুন।',
      'btnCreateFirst': '+ প্রথম ব্যাচ তৈরি করুন',
      'handoverTitle': 'হেফাজত হস্তান্তর',
      'handoverSub': 'যাচাইকৃত কিউআর নিশ্চিতকরণ সহ পরবর্তী পক্ষের কাছে পণ্য হস্তান্তর করুন।',
      'scanToReceive': 'হেফাজত গ্রহণের জন্য কিউআর স্ক্যান করুন',
      'scanToReceiveSub': 'আগত পণ্যের ওজন যাচাই করুন ও অবস্থা নথিভুক্ত করুন।',
      'btnScanQr': 'কিউআর স্ক্যান করুন',
      'manualCodePh': 'বা কোড টাইপ করুন',
      'btnVerifyAccept': 'গ্রহণ করুন ও নথিভুক্ত করুন',
      'dispatchedBatches': 'প্রেরিত ব্যাচ (ট্রানজিটে)',
      'noDispatched': 'নিশ্চিতকরণের জন্য কোনো বহির্গমন অপেক্ষমাণ নেই।',
      'insightsTitle': 'খামার ও ফসল বিশ্লেষণ',
      'grossValuation': 'মোট আনুমানিক মূল্য',
      'realizedRevenue': 'প্রাপ্ত রাজস্ব',
      'gradeARatio': 'গ্রেড-এ গুণমান অনুপাত',
      'cropBreakdown': 'ফসল উৎপাদন বণ্টন',
      'plotsTitle': 'ম্যাপ করা কৃষি জমি',
      'profileTitle': 'উৎপাদক ডিজিটাল নোড',
      'kycVerified': 'কেওয়াইসি যাচাইকৃত',
      'kycPending': 'কেওয়াইসি পর্যালোচনাধীন',
      'maskedPan': 'প্যান পরিচয়',
      'bankAccount': 'ব্যাঙ্ক অ্যাকাউন্ট',
      'statutoryConsent': 'ডিপিডিপি অ্যাক্ট ২০২৩ সম্মতি সক্রিয়',
      'btnLogout': 'লগ আউট',
      'loginTitle': 'বীজ থেকে ভোক্তা পর্যন্ত স্বচ্ছতা',
      'loginSub': 'জাতীয় সার্বভৌম কৃষি ট্রেসেবিলিটি কনসোল',
      'phoneLabel': 'মোবাইল নম্বর',
      'otpLabel': '৬-সংখ্যার ওটিপি লিখুন',
      'btnSendOtp': 'ওটিপি পাঠান',
      'btnVerifyOtp': 'যাচাই করুন ও প্রবেশ করুন',
      'btnGoogle': 'গুগল দিয়ে প্রবেশ করুন',
      'dpdpNotice': 'ডিপিডিপি অ্যাক্ট ২০২৩ দ্বারা সংরক্ষিত • সি-ড্যাক নোড',
    },
  };

  String _t(String key) => _strings[_selectedLang]?[key] ?? _strings['en']?[key] ?? key;

  @override
  void dispose() {
    _searchController.dispose();
    _phoneController.dispose();
    _otpController.dispose();
    _publicLotSearchController.dispose();
    super.dispose();
  }

  void _switchLanguage(String lang) {
    setState(() => _selectedLang = lang);
    widget.onLocaleChanged?.call(Locale(lang));
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authControllerProvider);
    final lotsState = ref.watch(lotsControllerProvider);
    final syncState = ref.watch(syncControllerProvider);

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: _buildTopAppBar(context, authState, syncState),
      body: authState.isAuthenticated
          ? IndexedStack(
              index: _currentNavIndex,
              children: [
                _buildBatchesTab(context, lotsState, authState),
                _buildHandoverTab(context, lotsState, authState),
                _buildInsightsTab(context, lotsState),
                _buildProfileTab(context, authState),
              ],
            )
          : _buildUnauthenticatedView(context, authState),
      bottomNavigationBar: authState.isAuthenticated
          ? NavigationBar(
              selectedIndex: _currentNavIndex,
              onDestinationSelected: (idx) => setState(() => _currentNavIndex = idx),
              backgroundColor: Colors.white,
              elevation: 4,
              indicatorColor: const Color(0xFFECFDF5),
              destinations: [
                NavigationDestination(
                  icon: const Icon(Icons.inventory_2_outlined),
                  selectedIcon: const Icon(Icons.inventory_2, color: Color(0xFF0B3D2E)),
                  label: _t('navBatches'),
                ),
                NavigationDestination(
                  icon: const Icon(Icons.swap_horiz_outlined),
                  selectedIcon: const Icon(Icons.swap_horiz, color: Color(0xFF0B3D2E)),
                  label: _t('navHandover'),
                ),
                NavigationDestination(
                  icon: const Icon(Icons.insights_outlined),
                  selectedIcon: const Icon(Icons.insights, color: Color(0xFF0B3D2E)),
                  label: _t('navInsights'),
                ),
                NavigationDestination(
                  icon: const Icon(Icons.person_outline),
                  selectedIcon: const Icon(Icons.person, color: Color(0xFF0B3D2E)),
                  label: _t('navProfile'),
                ),
              ],
            )
          : null,
      floatingActionButton: (authState.isAuthenticated && _currentNavIndex == 0)
          ? FloatingActionButton.extended(
              onPressed: () => context.push('/create-batch'),
              backgroundColor: const Color(0xFF0B3D2E),
              foregroundColor: Colors.white,
              elevation: 3,
              icon: const Icon(Icons.add, size: 20),
              label: Text(
                _t('newBatch'),
                style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 13.5),
              ),
            )
          : null,
    );
  }

  // 1. TOP APP BAR
  PreferredSizeWidget _buildTopAppBar(BuildContext context, AuthState authState, SyncState syncState) {
    return AppBar(
      backgroundColor: const Color(0xFF0B3D2E),
      foregroundColor: Colors.white,
      elevation: 0,
      titleSpacing: 16,
      title: Row(
        children: [
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: Colors.white,
              border: Border.all(color: const Color(0xFFE67E22), width: 1.5),
            ),
            child: ClipOval(
              child: Image.asset(
                'assets/images/annasutra_emblem.jpg',
                fit: BoxFit.cover,
                errorBuilder: (_, __, ___) => const Icon(Icons.eco, color: Color(0xFF0B3D2E), size: 18),
              ),
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  _t('appTitle'),
                  style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w900, letterSpacing: -0.2),
                  overflow: TextOverflow.ellipsis,
                ),
                Text(
                  _t('appSubtitle'),
                  style: const TextStyle(fontSize: 9.5, color: Color(0xFFA7F3D0), fontWeight: FontWeight.w500),
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
        ],
      ),
      actions: [
        // Sync status badge
        Container(
          margin: const EdgeInsets.symmetric(vertical: 16),
          padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
          decoration: BoxDecoration(
            color: syncState.pendingCount == 0 ? const Color(0xFF064E3B) : const Color(0xFF78350F),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 7,
                height: 7,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: syncState.pendingCount == 0 ? const Color(0xFF34D399) : const Color(0xFFFBBF24),
                ),
              ),
              const SizedBox(width: 4),
              Text(
                syncState.pendingCount == 0 ? 'Synced' : '${syncState.pendingCount} Pending',
                style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w700, color: Colors.white),
              ),
            ],
          ),
        ),

        // Language Switcher Chip
        IconButton(
          icon: const Icon(Icons.translate, size: 20),
          tooltip: 'Change Language',
          onPressed: () => _showLanguageModal(context),
        ),

        // DPDP Privacy Info
        IconButton(
          icon: const Icon(Icons.shield_outlined, size: 20),
          tooltip: 'Data Privacy Consent',
          onPressed: () => DpdpConsentDialog.show(context),
        ),
      ],
    );
  }

  // ---------------------------------------------------------------------------
  // TAB 0: BATCHES (HARVEST LOTS)
  // ---------------------------------------------------------------------------
  Widget _buildBatchesTab(BuildContext context, LotsState lotsState, AuthState authState) {
    final farmerUid = authState.farmerUid ??
        (authState.phone != null && authState.phone!.isNotEmpty
            ? LotsController.generateFarmerUid(phone: authState.phone)
            : 'REGISTERED');

    final lots = lotsState.filteredLots;
    final totalKg = lots.fold<double>(0.0, (acc, lot) => acc + lot.netQtyKg);
    final inCustodyCount = lots.where((l) => l.isEditable).length;
    final inTransitCount = lots.where((l) => l.state == 'IN_TRANSIT').length;

    return RefreshIndicator(
      onRefresh: () async {
        await ref.read(lotsControllerProvider.notifier).fetchRemoteLots(
              accessToken: authState.accessToken,
              phone: authState.phone,
            );
      },
      child: ListView(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
        children: [
          // 1. VERIFIED PRODUCER NODE HEADER (Web UI Parity)
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFFE2E8F0)),
              boxShadow: const [
                BoxShadow(color: Color(0x06000000), blurRadius: 6, offset: Offset(0, 2)),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                            decoration: BoxDecoration(
                              color: const Color(0xFFECFDF5),
                              border: Border.all(color: const Color(0xFF86EFAC)),
                              borderRadius: BorderRadius.circular(20),
                            ),
                            child: const Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(Icons.check_circle, size: 13, color: Color(0xFF15803D)),
                                SizedBox(width: 5),
                                Text(
                                  'VERIFIED PRODUCER NODE',
                                  style: TextStyle(
                                    fontSize: 10.5,
                                    fontWeight: FontWeight.w800,
                                    color: Color(0xFF065F46),
                                    letterSpacing: 0.3,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            authState.orgName ?? 'Registered Agricultural Producer',
                            style: const TextStyle(
                              fontSize: 17.5,
                              fontWeight: FontWeight.w900,
                              color: Color(0xFF0F172A),
                            ),
                          ),
                          const SizedBox(height: 2),
                          const Text(
                            'Cluster Farm Yard #4, Bardhaman, West Bengal',
                            style: TextStyle(fontSize: 12, color: Color(0xFF64748B)),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                // Unique Farmer ID Box with 1-tap copy
                InkWell(
                  onTap: () {
                    Clipboard.setData(ClipboardData(text: farmerUid));
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('Copied Farmer ID: $farmerUid'),
                        duration: const Duration(seconds: 2),
                        backgroundColor: const Color(0xFF0B3D2E),
                        behavior: SnackBarBehavior.floating,
                      ),
                    );
                  },
                  borderRadius: BorderRadius.circular(10),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                    decoration: BoxDecoration(
                      color: const Color(0xFFF0FDF4),
                      border: Border.all(color: const Color(0xFF86EFAC), width: 1.5),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text(
                                'UNIQUE FARMER ID',
                                style: TextStyle(
                                  fontSize: 9.5,
                                  fontWeight: FontWeight.w800,
                                  color: Color(0xFF047857),
                                  letterSpacing: 0.5,
                                ),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                farmerUid,
                                style: const TextStyle(
                                  fontFamily: 'monospace',
                                  fontSize: 14,
                                  fontWeight: FontWeight.w900,
                                  color: Color(0xFF0B3D2E),
                                  letterSpacing: 0.5,
                                ),
                                overflow: TextOverflow.ellipsis,
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(width: 8),
                        const Row(
                          children: [
                            Icon(Icons.copy, size: 14, color: Color(0xFF10B981)),
                            SizedBox(width: 4),
                            Text(
                              'COPY',
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w800,
                                color: Color(0xFF10B981),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 14),

          // 2. LIVE AGRICULTURAL TELEMETRY (6 Inherited Metrics Grid)
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: const Color(0xFFF8FAFC),
              border: Border.all(color: const Color(0xFFE2E8F0)),
              borderRadius: BorderRadius.circular(14),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Text(
                        'LIVE AGRICULTURAL TELEMETRY',
                        style: TextStyle(
                          fontSize: 10.5,
                          fontWeight: FontWeight.w800,
                          color: Color(0xFF475569),
                          letterSpacing: 0.5,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    SizedBox(width: 6),
                    Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text('● ', style: TextStyle(color: Color(0xFF10B981), fontSize: 10)),
                        Text(
                          'Sovereign Synced',
                          style: TextStyle(
                            fontSize: 10.5,
                            fontWeight: FontWeight.w700,
                            color: Color(0xFF10B981),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                // Row 1: Land & Plots | Season Allocation
                Row(
                  children: [
                    Expanded(
                      child: _buildTelemetryCard(
                        title: 'Land & Plots',
                        value: '2 Plots',
                        subtitle: '4.500 Acres',
                        valueColor: const Color(0xFF0B3D2E),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: _buildTelemetryCard(
                        title: 'Season Allocation',
                        value: '3.0 Ac',
                        subtitle: '1.5 Ac Free',
                        valueColor: const Color(0xFF0B3D2E),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                // Row 2: Harvest Yield | Active Lots
                Row(
                  children: [
                    Expanded(
                      child: _buildTelemetryCard(
                        title: 'Harvest Yield',
                        value: '${totalKg.toStringAsFixed(0)} Kg',
                        subtitle: 'Net Yield',
                        valueColor: const Color(0xFF0B3D2E),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: _buildTelemetryCard(
                        title: 'Active Lots',
                        value: '${lots.length} Batches',
                        subtitle: '$inCustodyCount Farm • $inTransitCount Transit',
                        valueColor: const Color(0xFF047857),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                // Row 3: Avg Shelf Speed | Portfolio Valuation
                Row(
                  children: [
                    Expanded(
                      child: _buildTelemetryCard(
                        title: 'Avg Shelf Speed',
                        value: '2.4 Days',
                        subtitle: 'Fresh Status',
                        valueColor: const Color(0xFF0B3D2E),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: _buildTelemetryCard(
                        title: 'Valuation (₹)',
                        value: '₹${(totalKg > 0 ? (totalKg * 42).toStringAsFixed(0) : "0")}',
                        subtitle: '₹42 / Kg Avg',
                        valueColor: const Color(0xFF047857),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          const SizedBox(height: 14),

          // 3. FOUR ACTION RAILS (Matching Web UI Rails A-D)
          Column(
            children: [
              _buildActionRailCard(
                letter: 'A',
                title: 'A. Profile & Farmer ID',
                subtitle: 'Farmer UID, Digital ID QR, KYC & Change Requests',
                icon: Icons.badge_outlined,
                actionLabel: 'View →',
                onTap: () => setState(() => _currentNavIndex = 3),
              ),
              const SizedBox(height: 8),
              _buildActionRailCard(
                letter: 'B',
                title: 'B. Land & Season Allocation',
                subtitle: 'Polygon plot mapping & 10-category acreage allocation',
                icon: Icons.map_outlined,
                actionLabel: 'Manage →',
                onTap: () => _showLandAllocationSheet(context),
              ),
              const SizedBox(height: 8),
              _buildActionRailCard(
                letter: 'C',
                title: 'C. Harvest Records',
                subtitle: 'Plot yield logging & mass balance accounting',
                icon: Icons.agriculture_outlined,
                actionLabel: 'Log →',
                onTap: () => _showHarvestRecordsSheet(context, lots),
              ),
              const SizedBox(height: 8),
              _buildActionRailCard(
                letter: 'D',
                title: 'D. Batch / Lot Creation',
                subtitle: 'Mint unique QRs, 1D barcodes & gate-passes',
                icon: Icons.qr_code_2,
                badgeLabel: '+ MINT',
                isHighlighted: true,
                onTap: () => context.push('/create-batch'),
              ),
            ],
          ),

          const SizedBox(height: 16),

          // 4. SEARCH & FILTER CONTROLS
          Container(
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: const Color(0xFFE2E8F0)),
            ),
            child: TextField(
              controller: _searchController,
              onChanged: (val) {
                ref.read(lotsControllerProvider.notifier).setSearchQuery(val);
              },
              decoration: InputDecoration(
                hintText: _t('searchPh'),
                hintStyle: const TextStyle(fontSize: 13, color: Color(0xFF94A3B8)),
                prefixIcon: const Icon(Icons.search, size: 18, color: Color(0xFF64748B)),
                suffixIcon: _searchController.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear, size: 16),
                        onPressed: () {
                          _searchController.clear();
                          ref.read(lotsControllerProvider.notifier).setSearchQuery('');
                        },
                      )
                    : null,
                contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                border: InputBorder.none,
              ),
            ),
          ),

          const SizedBox(height: 8),

          // Filter Chips Row
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                _buildCustodyChip('ALL', '${_t('filterAll')} (${lots.length})'),
                const SizedBox(width: 6),
                _buildCustodyChip('IN_CUSTODY', '${_t('filterCustody')} ($inCustodyCount)'),
                const SizedBox(width: 6),
                _buildCustodyChip('IN_TRANSIT', '${_t('filterTransit')} ($inTransitCount)'),
              ],
            ),
          ),

          const SizedBox(height: 12),

          // 5. LOTS LIST OR EMPTY STATE
          if (lots.isEmpty) ...[
            Container(
              padding: const EdgeInsets.symmetric(vertical: 40, horizontal: 20),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFFE2E8F0)),
              ),
              child: Column(
                children: [
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: const BoxDecoration(
                      shape: BoxShape.circle,
                      color: Color(0xFFECFDF5),
                    ),
                    child: const Icon(Icons.inventory_2_outlined, size: 36, color: Color(0xFF047857)),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    _t('noBatchesTitle'),
                    style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    _t('noBatchesSub'),
                    textAlign: TextAlign.center,
                    style: const TextStyle(fontSize: 12.5, color: Color(0xFF64748B)),
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () => context.push('/create-batch'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF0B3D2E),
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                    child: Text(_t('btnCreateFirst')),
                  ),
                ],
              ),
            ),
          ] else ...[
            ...lots.map(
              (lot) => LotCard(
                lot: lot,
                onEdit: lot.isEditable
                    ? () => context.push('/create-batch?code=${Uri.encodeComponent(lot.publicCode)}')
                    : null,
                onDispatch: lot.isEditable ? () => _showDispatchSheet(context, lot) : null,
                onShowQr: () => _showQrDialog(context, lot),
              ),
            ),
          ],

          const SizedBox(height: 60), // Room for FAB
        ],
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // TELEMETRY & ACTION RAIL HELPERS
  // ---------------------------------------------------------------------------
  Widget _buildTelemetryCard({
    required String title,
    required String value,
    required String subtitle,
    required Color valueColor,
  }) {
    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(fontSize: 11, color: Color(0xFF64748B), fontWeight: FontWeight.w700),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 3),
          Text(
            value,
            style: TextStyle(fontSize: 17, fontWeight: FontWeight.w900, color: valueColor),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 2),
          Text(
            subtitle,
            style: const TextStyle(fontSize: 10.5, color: Color(0xFF047857), fontWeight: FontWeight.w700),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }

  Widget _buildActionRailCard({
    required String letter,
    required String title,
    required String subtitle,
    required IconData icon,
    String? actionLabel,
    String? badgeLabel,
    bool isHighlighted = false,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
        decoration: BoxDecoration(
          color: isHighlighted ? const Color(0xFFF0FDF4) : Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isHighlighted ? const Color(0xFF86EFAC) : const Color(0xFFE2E8F0),
            width: isHighlighted ? 1.5 : 1,
          ),
        ),
        child: Row(
          children: [
            Container(
              width: 36,
              height: 36,
              decoration: BoxDecoration(
                color: isHighlighted ? const Color(0xFF047857) : const Color(0xFFECFDF5),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(
                icon,
                size: 20,
                color: isHighlighted ? Colors.white : const Color(0xFF047857),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          title,
                          style: TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w800,
                            color: isHighlighted ? const Color(0xFF047857) : const Color(0xFF0F172A),
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      if (badgeLabel != null)
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: const Color(0xFF047857),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Text(
                            badgeLabel,
                            style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: Colors.white),
                          ),
                        )
                      else if (actionLabel != null)
                        Text(
                          actionLabel,
                          style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: Color(0xFF047857)),
                        ),
                    ],
                  ),
                  const SizedBox(height: 2),
                  Text(
                    subtitle,
                    style: TextStyle(
                      fontSize: 11,
                      color: isHighlighted ? const Color(0xFF065F46) : const Color(0xFF64748B),
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showLandAllocationSheet(BuildContext context) {
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => DraggableScrollableSheet(
        initialChildSize: 0.6,
        maxChildSize: 0.85,
        minChildSize: 0.4,
        expand: false,
        builder: (_, scrollController) => ListView(
          controller: scrollController,
          padding: const EdgeInsets.all(20),
          children: [
            Center(
              child: Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: const Color(0xFFCBD5E1),
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: 16),
            const Row(
              children: [
                Icon(Icons.map_outlined, color: Color(0xFF047857), size: 22),
                SizedBox(width: 8),
                Text(
                  'Land & Season Allocation',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: Color(0xFF0F172A)),
                ),
              ],
            ),
            const SizedBox(height: 4),
            const Text(
              'Polygon plot mapping & 10-category acreage allocation',
              style: TextStyle(fontSize: 12.5, color: Color(0xFF64748B)),
            ),
            const Divider(height: 24),
            _buildPlotAllocationItem(
              name: 'Plot #1 - North Field',
              surveyNo: 'Survey 104/A',
              area: '2.500 Acres',
              allocatedCrop: 'Paddy / Rice (FG)',
              status: 'Cultivated',
            ),
            const SizedBox(height: 12),
            _buildPlotAllocationItem(
              name: 'Plot #2 - Riverbank South',
              surveyNo: 'Survey 108/B',
              area: '2.000 Acres',
              allocatedCrop: 'Mustard (OI) / Seasonal',
              status: 'Cultivated',
            ),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFFF0FDF4),
                border: Border.all(color: const Color(0xFF86EFAC)),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Total Registered Land', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: Color(0xFF047857))),
                      SizedBox(height: 2),
                      Text('4.500 Acres', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w900, color: Color(0xFF0B3D2E))),
                    ],
                  ),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text('Season Allocated / Free', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: Color(0xFF047857))),
                      SizedBox(height: 2),
                      Text('3.0 Ac / 1.5 Ac Free', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF047857))),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPlotAllocationItem({
    required String name,
    required String surveyNo,
    required String area,
    required String allocatedCrop,
    required String status,
  }) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border.all(color: const Color(0xFFE2E8F0)),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(name, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: const Color(0xFFECFDF5),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(status, style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: Color(0xFF047857))),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text('$surveyNo • $area', style: const TextStyle(fontSize: 12, color: Color(0xFF64748B))),
          const SizedBox(height: 6),
          Row(
            children: [
              const Icon(Icons.eco_outlined, size: 14, color: Color(0xFF059669)),
              const SizedBox(width: 4),
              Text(allocatedCrop, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Color(0xFF059669))),
            ],
          ),
        ],
      ),
    );
  }

  void _showHarvestRecordsSheet(BuildContext context, List<HarvestLot> lots) {
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => DraggableScrollableSheet(
        initialChildSize: 0.6,
        maxChildSize: 0.85,
        minChildSize: 0.4,
        expand: false,
        builder: (_, scrollController) => ListView(
          controller: scrollController,
          padding: const EdgeInsets.all(20),
          children: [
            Center(
              child: Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: const Color(0xFFCBD5E1),
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: 16),
            const Row(
              children: [
                Icon(Icons.agriculture_outlined, color: Color(0xFF047857), size: 22),
                SizedBox(width: 8),
                Text(
                  'Harvest Records & Mass Balance',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: Color(0xFF0F172A)),
                ),
              ],
            ),
            const SizedBox(height: 4),
            const Text(
              'Plot yield logging & mass balance accounting across harvest cycles',
              style: TextStyle(fontSize: 12.5, color: Color(0xFF64748B)),
            ),
            const Divider(height: 24),
            if (lots.isEmpty)
              Container(
                padding: const EdgeInsets.all(24),
                alignment: Alignment.center,
                child: const Text('No harvest records logged yet. Mint a batch to record yield.', style: TextStyle(color: Color(0xFF64748B))),
              )
            else
              ...lots.map(
                (lot) => Container(
                  margin: const EdgeInsets.only(bottom: 10),
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    border: Border.all(color: const Color(0xFFE2E8F0)),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(lot.crop, style: const TextStyle(fontSize: 13.5, fontWeight: FontWeight.w800)),
                          Text('Lot: ${lot.publicCode}', style: const TextStyle(fontSize: 11, fontFamily: 'monospace', color: Color(0xFF64748B))),
                          Text('Plot: ${lot.originPlotName.isNotEmpty ? lot.originPlotName : "North Field"}', style: const TextStyle(fontSize: 11, color: Color(0xFF64748B))),
                        ],
                      ),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.end,
                        children: [
                          Text('${lot.netQtyKg.toStringAsFixed(1)} Kg', style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w900, color: Color(0xFF0B3D2E))),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                            decoration: BoxDecoration(
                              color: lot.isEditable ? const Color(0xFFECFDF5) : const Color(0xFFEFF6FF),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: Text(
                              lot.isEditable ? 'Farm Custody' : lot.state,
                              style: TextStyle(
                                fontSize: 9.5,
                                fontWeight: FontWeight.w700,
                                color: lot.isEditable ? const Color(0xFF047857) : const Color(0xFF2563EB),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildCustodyChip(String filterVal, String label) {
    final isSelected = _selectedCustodyFilter == filterVal;
    return ChoiceChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (_) {
        setState(() => _selectedCustodyFilter = filterVal);
        ref.read(lotsControllerProvider.notifier).setCustodyFilter(filterVal);
      },
      selectedColor: const Color(0xFF0B3D2E),
      backgroundColor: Colors.white,
      side: BorderSide(color: isSelected ? const Color(0xFF0B3D2E) : const Color(0xFFE2E8F0)),
      labelStyle: TextStyle(
        fontSize: 11.5,
        fontWeight: FontWeight.w700,
        color: isSelected ? Colors.white : const Color(0xFF475569),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 0),
    );
  }

  // ---------------------------------------------------------------------------
  // TAB 1: HANDOVER & CUSTODY HUB
  // ---------------------------------------------------------------------------
  Widget _buildHandoverTab(BuildContext context, LotsState lotsState, AuthState authState) {
    final dispatchedLots = lotsState.lots.where((l) => l.state == 'IN_TRANSIT').toList();

    return ListView(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      children: [
        // Receive Custody Action Card
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFFE2E8F0)),
            boxShadow: const [
              BoxShadow(color: Color(0x06000000), blurRadius: 6, offset: Offset(0, 2)),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: const Color(0xFFECFDF5),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: const Icon(Icons.qr_code_scanner, color: Color(0xFF047857), size: 22),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          _t('scanToReceive'),
                          style: const TextStyle(fontSize: 14.5, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                        ),
                        Text(
                          _t('scanToReceiveSub'),
                          style: const TextStyle(fontSize: 11.5, color: Color(0xFF64748B)),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 14),
              ElevatedButton.icon(
                onPressed: () => _showReceiveDialog(context),
                icon: const Icon(Icons.camera_alt_outlined, size: 16),
                label: Text(_t('btnScanQr')),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF0B3D2E),
                  foregroundColor: Colors.white,
                  minimumSize: const Size(double.infinity, 42),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
              ),
            ],
          ),
        ),

        const SizedBox(height: 16),

        // Dispatched Batches Section
        Text(
          _t('dispatchedBatches'),
          style: const TextStyle(fontSize: 14.5, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        const SizedBox(height: 8),

        if (dispatchedLots.isEmpty) ...[
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: const Color(0xFFE2E8F0)),
            ),
            child: Center(
              child: Text(
                _t('noDispatched'),
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 12.5, color: Color(0xFF64748B)),
              ),
            ),
          ),
        ] else ...[
          ...dispatchedLots.map(
            (lot) => LotCard(
              lot: lot,
              onShowQr: () => _showQrDialog(context, lot),
            ),
          ),
        ],
      ],
    );
  }

  // ---------------------------------------------------------------------------
  // TAB 2: INSIGHTS & FARM ANALYTICS
  // ---------------------------------------------------------------------------
  Widget _buildInsightsTab(BuildContext context, LotsState lotsState) {
    final lots = lotsState.lots;
    final totalValuation = lots.fold<double>(0.0, (acc, l) => acc + l.estimatedValue);
    final totalKg = lots.fold<double>(0.0, (acc, l) => acc + l.netQtyKg);
    final gradeACount = lots.where((l) => l.qualityGrade.contains('A')).length;
    final gradeARatio = lots.isNotEmpty ? ((gradeACount / lots.length) * 100).toStringAsFixed(0) : '0';

    // Crop distribution map
    final Map<String, double> cropMap = {};
    for (final l in lots) {
      cropMap[l.crop] = (cropMap[l.crop] ?? 0.0) + l.netQtyKg;
    }

    return ListView(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      children: [
        Text(
          _t('insightsTitle'),
          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        const SizedBox(height: 12),

        // KPI Stats Row
        Row(
          children: [
            Expanded(
              child: _buildInsightMetricCard(
                _t('grossValuation'),
                '₹${totalValuation.toStringAsFixed(0)}',
                Icons.currency_rupee,
                const Color(0xFF047857),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _buildInsightMetricCard(
                _t('gradeARatio'),
                '$gradeARatio%',
                Icons.verified_outlined,
                const Color(0xFF1E40AF),
              ),
            ),
          ],
        ),

        const SizedBox(height: 8),

        Row(
          children: [
            Expanded(
              child: _buildInsightMetricCard(
                'Total Harvested',
                '${totalKg.toStringAsFixed(0)} Kg',
                Icons.scale_outlined,
                const Color(0xFF0B3D2E),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _buildInsightMetricCard(
                'Total Batches',
                '${lots.length}',
                Icons.layers_outlined,
                const Color(0xFFD97706),
              ),
            ),
          ],
        ),

        const SizedBox(height: 16),

        // Crop Distribution Breakdown
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFFE2E8F0)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                _t('cropBreakdown'),
                style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
              ),
              const SizedBox(height: 10),
              if (cropMap.isEmpty)
                const Text('No crop production data logged yet.', style: TextStyle(fontSize: 12, color: Color(0xFF64748B)))
              else
                ...cropMap.entries.map((e) {
                  final percent = totalKg > 0 ? (e.value / totalKg) : 0.0;
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 10),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Expanded(
                              child: Text(
                                e.key,
                                style: const TextStyle(fontSize: 12.5, fontWeight: FontWeight.w700),
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                            const SizedBox(width: 8),
                            Text('${e.value.toStringAsFixed(1)} Kg (${(percent * 100).toStringAsFixed(0)}%)',
                                style: const TextStyle(fontSize: 11.5, color: Color(0xFF64748B))),
                          ],
                        ),
                        const SizedBox(height: 4),
                        LinearProgressIndicator(
                          value: percent,
                          backgroundColor: const Color(0xFFE2E8F0),
                          valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF059669)),
                          borderRadius: BorderRadius.circular(4),
                          minHeight: 6,
                        ),
                      ],
                    ),
                  );
                }),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildInsightMetricCard(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text(
                  title,
                  style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: Color(0xFF64748B)),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              const SizedBox(width: 4),
              Icon(icon, size: 16, color: color),
            ],
          ),
          const SizedBox(height: 6),
          Text(value, style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: color)),
        ],
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // TAB 3: PROFILE & ACCOUNT
  // ---------------------------------------------------------------------------
  Widget _buildProfileTab(BuildContext context, AuthState authState) {
    final farmerUid = authState.farmerUid ??
        (authState.phone != null && authState.phone!.isNotEmpty
            ? LotsController.generateFarmerUid(phone: authState.phone)
            : 'REGISTERED');

    return ListView(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      children: [
        // Producer Card
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFFE2E8F0)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const CircleAvatar(
                    radius: 24,
                    backgroundColor: Color(0xFFECFDF5),
                    child: Icon(Icons.person, color: Color(0xFF047857), size: 28),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          authState.orgName ?? 'Registered Agricultural Producer',
                          style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                        ),
                        Text(
                          'Role: ${authState.orgType ?? "PRODUCER"}',
                          style: const TextStyle(fontSize: 12, color: Color(0xFF64748B)),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const Divider(height: 22, color: Color(0xFFF1F5F9)),
              Text(
                _t('farmerId'),
                style: const TextStyle(fontSize: 10.5, fontWeight: FontWeight.w700, color: Color(0xFF64748B)),
              ),
              const SizedBox(height: 2),
              SelectableText(
                farmerUid,
                style: const TextStyle(
                  fontFamily: 'monospace',
                  fontSize: 14,
                  fontWeight: FontWeight.w900,
                  color: Color(0xFF0B3D2E),
                ),
              ),
            ],
          ),
        ),

        const SizedBox(height: 12),

        // Compliance & Legal Settings
        Container(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFFE2E8F0)),
          ),
          child: Column(
            children: [
              ListTile(
                leading: const Icon(Icons.translate, color: Color(0xFF0B3D2E)),
                title: const Text('Language / भाषा / ভাষা', style: TextStyle(fontSize: 13.5, fontWeight: FontWeight.w700)),
                trailing: const Icon(Icons.chevron_right, size: 20),
                onTap: () => _showLanguageModal(context),
              ),
              const Divider(height: 1, color: Color(0xFFF1F5F9)),
              ListTile(
                leading: const Icon(Icons.shield_outlined, color: Color(0xFF0B3D2E)),
                title: Text(_t('statutoryConsent'), style: const TextStyle(fontSize: 13.5, fontWeight: FontWeight.w700)),
                trailing: const Icon(Icons.chevron_right, size: 20),
                onTap: () => DpdpConsentDialog.show(context),
              ),
              const Divider(height: 1, color: Color(0xFFF1F5F9)),
              ListTile(
                leading: const Icon(Icons.delete_outline, color: Color(0xFFDC2626)),
                title: const Text('Request Account Deletion (DPDP Act § 12(3))', style: TextStyle(fontSize: 13.5, fontWeight: FontWeight.w700, color: Color(0xFFDC2626))),
                subtitle: const Text('Statutory right to erasure of personal data and profile node', style: TextStyle(fontSize: 11, color: Color(0xFF64748B))),
                trailing: const Icon(Icons.chevron_right, size: 20, color: Color(0xFFDC2626)),
                onTap: () => _showDpdpDeletionModal(context, authState),
              ),
              const Divider(height: 1, color: Color(0xFFF1F5F9)),
              ListTile(
                leading: const Icon(Icons.logout, color: Color(0xFFDC2626)),
                title: Text(_t('btnLogout'), style: const TextStyle(fontSize: 13.5, fontWeight: FontWeight.w700, color: Color(0xFFDC2626))),
                onTap: () async {
                  await ref.read(authControllerProvider.notifier).logout();
                },
              ),
            ],
          ),
        ),
      ],
    );
  }

  void _showDpdpDeletionModal(BuildContext context, AuthState authState) {
    final lotsState = ref.read(lotsControllerProvider);
    final inTransitLots = lotsState.lots.where((l) => l.state == 'IN_TRANSIT').toList();

    showDialog<void>(
      context: context,
      builder: (dialogCtx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Row(
          children: [
            Icon(Icons.shield_outlined, color: Color(0xFFDC2626), size: 24),
            SizedBox(width: 8),
            Expanded(
              child: Text(
                'DPDP Act 2023 § 12(3)\nRight to Erasure Request',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF991B1B)),
              ),
            ),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (inTransitLots.isNotEmpty) ...[
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: const Color(0xFFFEF2F2),
                  border: Border.all(color: const Color(0xFFF87171)),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.error_outline, color: Color(0xFFDC2626), size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Cannot request deletion while ${inTransitLots.length} lot(s) are in transit. Active custody transfers must be settled or accepted by counterparties before deletion can be processed.',
                        style: const TextStyle(fontSize: 12, color: Color(0xFF991B1B), fontWeight: FontWeight.w600),
                      ),
                    ),
                  ],
                ),
              ),
            ] else ...[
              const Text(
                'Under Section 12(3) of the Digital Personal Data Protection Act, 2023, you have the statutory right to request erasure of your personal data and entity node registration.',
                style: TextStyle(fontSize: 13, color: Color(0xFF334155)),
              ),
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: const Color(0xFFF8FAFC),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('• Operations & dispatch will be frozen pending review.', style: TextStyle(fontSize: 11.5, color: Color(0xFF64748B))),
                    SizedBox(height: 4),
                    Text('• C-DAC & State Verifiers review requests within statutory timelines.', style: TextStyle(fontSize: 11.5, color: Color(0xFF64748B))),
                    SizedBox(height: 4),
                    Text('• Immutable past cryptographic hashes remain on EPCIS ledger.', style: TextStyle(fontSize: 11.5, color: Color(0xFF64748B))),
                  ],
                ),
              ),
            ],
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogCtx),
            child: const Text('Cancel', style: TextStyle(color: Color(0xFF64748B))),
          ),
          if (inTransitLots.isEmpty)
            ElevatedButton(
              onPressed: () {
                Navigator.pop(dialogCtx);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Account deletion request submitted under DPDP Act 2023.'),
                    backgroundColor: Color(0xFFDC2626),
                    behavior: SnackBarBehavior.floating,
                  ),
                );
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFFDC2626),
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
              ),
              child: const Text('Submit Deletion Request'),
            ),
        ],
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // UNAUTHENTICATED VIEW: VAST WEB UI PRODUCT HOME PORTAL
  // ---------------------------------------------------------------------------
  Widget _buildUnauthenticatedView(BuildContext context, AuthState authState) {
    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 580),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // 1. Hero Billboard Showcase
              _buildHeroBillboard(),
              const SizedBox(height: 14),

              // 2. One-Tap Quick Access (Zero Friction)
              _buildInstantAccessCard(context),
              const SizedBox(height: 16),

              // 3. Live Mandi & Custody Telemetry Ticker
              _buildMandiTicker(),
              const SizedBox(height: 16),

              // 4. Public Produce Lot Verification & QR Scanner
              _buildLotVerificationCard(context),
              const SizedBox(height: 16),

              // 5. National Trust & Ecosystem Stats Grid
              _buildEcosystemStatsGrid(),
              const SizedBox(height: 16),

              // 6. 5-Tier Supply-Chain Architecture Flow
              _buildSupplyChainSection(),
              const SizedBox(height: 16),

              // 7. Operations Console Sign-In Card
              _buildAuthCard(context, authState),
              const SizedBox(height: 18),

              // 8. 10 Agricultural Taxonomy Categories Showcase
              _buildTaxonomyShowcase(),
              const SizedBox(height: 20),

              // 9. Sovereign Footer & Statutory Notice
              _buildSovereignFooter(),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeroBillboard() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF0B3D2E), Color(0xFF064E3B)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: const [
          BoxShadow(color: Color(0x200B3D2E), blurRadius: 16, offset: Offset(0, 6)),
        ],
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 56,
                height: 56,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: Colors.white,
                  border: Border.all(color: const Color(0xFFE67E22), width: 2.5),
                  boxShadow: const [
                    BoxShadow(color: Color(0x30000000), blurRadius: 8, offset: Offset(0, 3)),
                  ],
                ),
                child: ClipOval(
                  child: Image.asset(
                    'assets/images/annasutra_emblem.jpg',
                    fit: BoxFit.cover,
                    errorBuilder: (_, __, ___) => const Icon(Icons.eco, color: Color(0xFF0B3D2E), size: 30),
                  ),
                ),
              ),
              const SizedBox(width: 14),
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Farm-to-Fork Traceability',
                      style: TextStyle(
                        fontSize: 21,
                        fontWeight: FontWeight.w900,
                        color: Colors.white,
                        letterSpacing: -0.3,
                      ),
                    ),
                    Text(
                      'National Sovereign Agri-Produce Traceability Platform',
                      style: TextStyle(fontSize: 11, color: Color(0xFFA7F3D0), fontWeight: FontWeight.w600),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          const Text(
            'From Soil to Shelf, Every Grain Accounted For.\nFarm-to-Fork Traceability Across Bharat.',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 13.5,
              fontWeight: FontWeight.w600,
              color: Color(0xFFECFDF5),
              height: 1.35,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInstantAccessCard(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF10B981), width: 1.5),
        boxShadow: const [
          BoxShadow(color: Color(0x1210B981), blurRadius: 10, offset: Offset(0, 3)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: const Color(0xFFECFDF5),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(Icons.bolt, color: Color(0xFF047857), size: 22),
              ),
              const SizedBox(width: 10),
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '⚡ Instant Producer Console Access',
                      style: TextStyle(fontSize: 14.5, fontWeight: FontWeight.w800, color: Color(0xFF0B3D2E)),
                    ),
                    Text(
                      'Explore batches, QR labels & cold chain telemetry in 1 tap',
                      style: TextStyle(fontSize: 11.5, color: Color(0xFF64748B)),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ElevatedButton.icon(
            onPressed: () async {
              await ref.read(authControllerProvider.notifier).signInAsVerifiedDemo(role: _selectedRole);
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Welcome! Verified Producer Console Active.'),
                    backgroundColor: Color(0xFF047857),
                  ),
                );
              }
            },
            icon: const Icon(Icons.touch_app, size: 18),
            label: const Text(
              '⚡ Explore Verified Producer Console',
              style: TextStyle(fontWeight: FontWeight.w800, fontSize: 13.5),
            ),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF047857),
              foregroundColor: Colors.white,
              minimumSize: const Size(double.infinity, 44),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMandiTicker() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Container(
              width: 8,
              height: 8,
              decoration: const BoxDecoration(
                color: Color(0xFF10B981),
                shape: BoxShape.circle,
              ),
            ),
            const SizedBox(width: 6),
            const Expanded(
              child: Text(
                'LIVE MANDI & CUSTODY TELEMETRY',
                style: TextStyle(fontSize: 11.5, fontWeight: FontWeight.w800, color: Color(0xFF475569), letterSpacing: 0.4),
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        SizedBox(
          height: 76,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: _mandiTickerData.length,
            separatorBuilder: (_, __) => const SizedBox(width: 8),
            itemBuilder: (ctx, i) {
              final item = _mandiTickerData[i];
              final isPos = item['change']!.startsWith('+');
              return Container(
                width: 160,
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      item['crop']!,
                      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Color(0xFF1E293B)),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Expanded(
                          child: Text(
                            item['rate']!,
                            style: const TextStyle(fontSize: 12.5, fontWeight: FontWeight.w800, color: Color(0xFF0B3D2E)),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        const SizedBox(width: 4),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 2),
                          decoration: BoxDecoration(
                            color: isPos ? const Color(0xFFECFDF5) : const Color(0xFFFEF2F2),
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            item['change']!,
                            style: TextStyle(
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
                              color: isPos ? const Color(0xFF047857) : const Color(0xFFDC2626),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildLotVerificationCard(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE2E8F0)),
        boxShadow: const [
          BoxShadow(color: Color(0x06000000), blurRadius: 8, offset: Offset(0, 2)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.qr_code_scanner, color: Color(0xFF0B3D2E), size: 20),
              SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Public Lot Verification',
                  style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          const Text(
            'Enter any batch code or scan crate QR to verify farm origin and integrity.',
            style: TextStyle(fontSize: 12, color: Color(0xFF64748B)),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _publicLotSearchController,
            decoration: InputDecoration(
              hintText: 'e.g. LOT-2026-WB-0042',
              contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
              prefixIcon: const Icon(Icons.tag, size: 18, color: Color(0xFF64748B)),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
            ),
          ),
          const SizedBox(height: 10),
          Row(
            children: [
              Expanded(
                flex: 3,
                child: ElevatedButton.icon(
                  onPressed: () => _showLotVerificationModal(context, _publicLotSearchController.text),
                  icon: const Icon(Icons.search, size: 16),
                  label: const Text('Verify Lot'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF0B3D2E),
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                flex: 2,
                child: OutlinedButton.icon(
                  onPressed: () => _showLotVerificationModal(context, 'LOT-2026-WB-0042'),
                  icon: const Icon(Icons.qr_code, size: 16, color: Color(0xFF047857)),
                  label: const Text('Scan QR', style: TextStyle(color: Color(0xFF047857))),
                  style: OutlinedButton.styleFrom(
                    side: const BorderSide(color: Color(0xFF047857)),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildEcosystemStatsGrid() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'NATIONAL TRUST & ECOSYSTEM METRICS',
          style: TextStyle(fontSize: 11.5, fontWeight: FontWeight.w800, color: Color(0xFF475569), letterSpacing: 0.4),
        ),
        const SizedBox(height: 8),
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: _ecosystemStats.length,
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            crossAxisSpacing: 10,
            mainAxisSpacing: 10,
            childAspectRatio: 2.1,
          ),
          itemBuilder: (ctx, i) {
            final s = _ecosystemStats[i];
            return Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFFE2E8F0)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  FittedBox(
                    fit: BoxFit.scaleDown,
                    alignment: Alignment.centerLeft,
                    child: Text(
                      s['num']!,
                      style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w900, color: Color(0xFF047857)),
                    ),
                  ),
                  Text(
                    s['label']!,
                    style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: Color(0xFF1E293B)),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  Text(
                    s['sub']!,
                    style: const TextStyle(fontSize: 9.5, color: Color(0xFF94A3B8)),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            );
          },
        ),
      ],
    );
  }

  Widget _buildSupplyChainSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '5-TIER SUPPLY-CHAIN ARCHITECTURE',
          style: TextStyle(fontSize: 11.5, fontWeight: FontWeight.w800, color: Color(0xFF475569), letterSpacing: 0.4),
        ),
        const SizedBox(height: 8),
        SizedBox(
          height: 130,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: _supplyChainTiers.length,
            separatorBuilder: (_, __) => const SizedBox(width: 10),
            itemBuilder: (ctx, i) {
              final t = _supplyChainTiers[i];
              return Container(
                width: 220,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(6),
                          decoration: BoxDecoration(
                            color: (t['color'] as Color).withOpacity(0.12),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Icon(t['icon'] as IconData, size: 16, color: t['color'] as Color),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(t['tier'] as String, style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: t['color'] as Color)),
                              Text(t['title'] as String, style: const TextStyle(fontSize: 12.5, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Expanded(
                      child: Text(
                        t['desc'] as String,
                        style: const TextStyle(fontSize: 10.5, color: Color(0xFF64748B), height: 1.2),
                        maxLines: 3,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildAuthCard(BuildContext context, AuthState authState) {
    final bool isOtpSent = authState.status == AuthStatus.otpSent;
    final bool isLoading = authState.status == AuthStatus.loading;

    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: const Color(0xFFCBD5E1)),
        boxShadow: const [
          BoxShadow(color: Color(0x0C000000), blurRadius: 10, offset: Offset(0, 3)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Text(
            'Producer Operations Sign-In',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0B3D2E)),
          ),
          const SizedBox(height: 2),
          const Text(
            'Authenticate with your mobile OTP or registered Google ID.',
            style: TextStyle(fontSize: 11.5, color: Color(0xFF64748B)),
          ),
          const SizedBox(height: 12),

          // Role selection chips (Farmer / FPO, etc.)
          const Text('Select Supply-Chain Role:', style: TextStyle(fontSize: 11.5, fontWeight: FontWeight.w700, color: Color(0xFF475569))),
          const SizedBox(height: 6),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: _roleOptions.map((r) {
                final isSel = _selectedRole == r['code'];
                return Padding(
                  padding: const EdgeInsets.only(right: 6),
                  child: ChoiceChip(
                    avatar: Icon(
                      r['icon'] as IconData,
                      size: 14,
                      color: isSel ? Colors.white : const Color(0xFF047857),
                    ),
                    label: Text(r['label'] as String),
                    selected: isSel,
                    onSelected: (_) => setState(() => _selectedRole = r['code'] as String),
                    selectedColor: const Color(0xFF0B3D2E),
                    backgroundColor: Colors.white,
                    side: BorderSide(color: isSel ? const Color(0xFF0B3D2E) : const Color(0xFFE2E8F0)),
                    labelStyle: TextStyle(
                      fontSize: 11.5,
                      fontWeight: FontWeight.w700,
                      color: isSel ? Colors.white : const Color(0xFF334155),
                    ),
                  ),
                );
              }).toList(),
            ),
          ),
          const SizedBox(height: 14),

          // Phone Number Input
          TextField(
            controller: _phoneController,
            keyboardType: TextInputType.phone,
            decoration: InputDecoration(
              labelText: _t('phoneLabel'),
              hintText: '9876543210 (Demo)',
              prefixText: '+91 ',
              prefixIcon: const Icon(Icons.phone_android, size: 18, color: Color(0xFF0B3D2E)),
            ),
          ),

          if (isOtpSent) ...[
            const SizedBox(height: 12),
            TextField(
              controller: _otpController,
              keyboardType: TextInputType.number,
              decoration: InputDecoration(
                labelText: _t('otpLabel'),
                hintText: '123456',
                prefixIcon: const Icon(Icons.lock_clock_outlined, size: 18, color: Color(0xFF0B3D2E)),
              ),
            ),
          ],

          const SizedBox(height: 14),

          // Submit OTP Action
          ElevatedButton(
            onPressed: isLoading
                ? null
                : () async {
                    final authNotifier = ref.read(authControllerProvider.notifier);
                    var phone = _phoneController.text.trim();
                    if (phone.isEmpty) {
                      phone = '9876543210';
                      _phoneController.text = phone;
                    }

                    if (!isOtpSent) {
                      await authNotifier.requestOtp(phone);
                      if (context.mounted) {
                        _otpController.text = '123456';
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('OTP sent! Use demo code 123456 to verify.'),
                            backgroundColor: Color(0xFF047857),
                          ),
                        );
                      }
                    } else {
                      var otp = _otpController.text.trim();
                      if (otp.isEmpty) {
                        otp = '123456';
                        _otpController.text = otp;
                      }
                      await authNotifier.verifyOtp(phone, otp);
                    }
                  },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF0B3D2E),
              foregroundColor: Colors.white,
              minimumSize: const Size(double.infinity, 44),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
            child: isLoading
                ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                : Text(isOtpSent ? _t('btnVerifyOtp') : _t('btnSendOtp')),
          ),

          const SizedBox(height: 14),
          const Row(
            children: [
              Expanded(child: Divider(color: Color(0xFFE2E8F0))),
              Padding(
                padding: EdgeInsets.symmetric(horizontal: 10),
                child: Text('OR', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF94A3B8))),
              ),
              Expanded(child: Divider(color: Color(0xFFE2E8F0))),
            ],
          ),
          const SizedBox(height: 14),

          // Google Sign-In Button
          OutlinedButton.icon(
            onPressed: isLoading
                ? null
                : () async {
                    final messenger = ScaffoldMessenger.of(context);
                    final success = await ref
                        .read(authControllerProvider.notifier)
                        .signInWithNativeGoogle(role: _selectedRole);
                    if (!mounted) return;
                    if (success) {
                      messenger.showSnackBar(
                        const SnackBar(
                          content: Text('Signed in with Google (Verified Producer)'),
                          backgroundColor: Color(0xFF047857),
                        ),
                      );
                    } else {
                      final err = ref.read(authControllerProvider).errorMessage;
                      if (err != null && err.isNotEmpty) {
                        messenger.showSnackBar(SnackBar(content: Text(err)));
                      }
                    }
                  },
            icon: const Icon(Icons.g_mobiledata, size: 22, color: Color(0xFFEA4335)),
            label: Text(_t('btnGoogle'), style: const TextStyle(color: Color(0xFF0F172A), fontWeight: FontWeight.bold)),
            style: OutlinedButton.styleFrom(
              minimumSize: const Size(double.infinity, 44),
              side: const BorderSide(color: Color(0xFFCBD5E1)),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTaxonomyShowcase() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '10-CATEGORY AGRICULTURAL TAXONOMY',
          style: TextStyle(fontSize: 11.5, fontWeight: FontWeight.w800, color: Color(0xFF475569), letterSpacing: 0.4),
        ),
        const SizedBox(height: 8),
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: _categoryTaxonomy.length,
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            crossAxisSpacing: 10,
            mainAxisSpacing: 10,
            childAspectRatio: 2.3,
          ),
          itemBuilder: (ctx, i) {
            final cat = _categoryTaxonomy[i];
            return Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFFE2E8F0)),
              ),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(6),
                    decoration: BoxDecoration(
                      color: const Color(0xFFECFDF5),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Icon(cat['icon'] as IconData, size: 16, color: const Color(0xFF047857)),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                              decoration: BoxDecoration(
                                color: const Color(0xFF0B3D2E),
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: Text(
                                cat['code'] as String,
                                style: const TextStyle(color: Colors.white, fontSize: 8.5, fontWeight: FontWeight.bold),
                              ),
                            ),
                            const SizedBox(width: 4),
                            Expanded(
                              child: Text(
                                cat['name'] as String,
                                style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: Color(0xFF1E293B)),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ],
                        ),
                        Text(
                          cat['example'] as String,
                          style: const TextStyle(fontSize: 9.5, color: Color(0xFF64748B)),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            );
          },
        ),
      ],
    );
  }

  Widget _buildSovereignFooter() {
    return Column(
      children: [
        Text(
          _t('dpdpNotice'),
          textAlign: TextAlign.center,
          style: const TextStyle(fontSize: 11, color: Color(0xFF64748B), fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 4),
        const Text(
          'GS1 Digital Link • EPCIS 2.0 Standard • Ministry-Aligned Open Sovereign Agri-Stack',
          textAlign: TextAlign.center,
          style: TextStyle(fontSize: 9.5, color: Color(0xFF94A3B8)),
        ),
      ],
    );
  }

  void _showLotVerificationModal(BuildContext context, String code) {
    final lotCode = code.trim().isEmpty ? 'LOT-2026-WB-0042' : code.trim();
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => Container(
        height: MediaQuery.of(ctx).size.height * 0.85,
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        ),
        child: Column(
          children: [
            Container(
              margin: const EdgeInsets.only(top: 12, bottom: 8),
              width: 44,
              height: 4,
              decoration: BoxDecoration(
                color: const Color(0xFFCBD5E1),
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: const Color(0xFFECFDF5),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: const Icon(Icons.verified, color: Color(0xFF047857), size: 24),
                  ),
                  const SizedBox(width: 12),
                  const Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'EPCIS 2.0 Digital Passport',
                          style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0B3D2E)),
                        ),
                        Text(
                          'Sovereign C-DAC Node Verification • Cryptographically Signed',
                          style: TextStyle(fontSize: 11, color: Color(0xFF64748B)),
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    onPressed: () => Navigator.pop(ctx),
                    icon: const Icon(Icons.close, color: Color(0xFF64748B)),
                  ),
                ],
              ),
            ),
            const Divider(height: 1, color: Color(0xFFE2E8F0)),
            Expanded(
              child: ListView(
                padding: const EdgeInsets.all(20),
                children: [
                  // Lot identification badge
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: const Color(0xFF0B3D2E),
                      borderRadius: BorderRadius.circular(14),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                              decoration: BoxDecoration(
                                color: const Color(0xFF10B981),
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: const Text(
                                'AUTHENTIC & SEALED',
                                style: TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold),
                              ),
                            ),
                            const Text(
                              'GS1 Digital Link',
                              style: TextStyle(color: Color(0xFFA7F3D0), fontSize: 11, fontWeight: FontWeight.w600),
                            ),
                          ],
                        ),
                        const SizedBox(height: 10),
                        Text(
                          lotCode,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 19,
                            fontWeight: FontWeight.w900,
                            letterSpacing: 0.5,
                          ),
                        ),
                        const SizedBox(height: 4),
                        const Text(
                          'Organic Govindobhog Premium Rice (Paddy)',
                          style: TextStyle(color: Color(0xFFD1FAE5), fontSize: 13, fontWeight: FontWeight.w600),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Origin & Agronomic Profile
                  const Text('Origin & Agronomic Metadata', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Color(0xFF1E293B))),
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: const Color(0xFFF8FAFC),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: const Color(0xFFE2E8F0)),
                    ),
                    child: Column(
                      children: [
                        _buildModalRow('FPO / Farmer', 'Maa Annapurna Organic FPO'),
                        const Divider(height: 14),
                        _buildModalRow('Farmer UID', '202628120000919876543210'),
                        const Divider(height: 14),
                        _buildModalRow('Geo Coordinates', '23.2324° N, 87.8615° E (Burdwan, WB)'),
                        const Divider(height: 14),
                        _buildModalRow('Harvest Net Weight', '1,500 Kg (Grade A Certified)'),
                        const Divider(height: 14),
                        _buildModalRow('Soil Health Metric', 'Organic Carbon 0.82% • pH 6.8'),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),

                  // 5-Tier Custody Chain Timeline
                  const Text('EPCIS 2.0 Custody Timeline', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Color(0xFF1E293B))),
                  const SizedBox(height: 8),
                  _buildTimelineItem(
                    step: '1',
                    title: 'Farm Origin Registration',
                    subtitle: '12 Oct 2026, 08:30 IST • Crate QR 202628-001 sealed at farm',
                    status: 'ATTESTED',
                    statusColor: const Color(0xFF047857),
                    isLast: false,
                  ),
                  _buildTimelineItem(
                    step: '2',
                    title: 'APMC Mandi Weighbridge Sign-Off',
                    subtitle: '13 Oct 2026, 11:15 IST • Gross 1,520 Kg, e-NAM settlement',
                    status: 'VERIFIED',
                    statusColor: const Color(0xFF047857),
                    isLast: false,
                  ),
                  _buildTimelineItem(
                    step: '3',
                    title: 'Cold Storage Transit Telemetry',
                    subtitle: '14 Oct 2026, 04:00 IST • 4.2°C temperature sensor logged',
                    status: 'LOGGED',
                    statusColor: const Color(0xFF0284C7),
                    isLast: false,
                  ),
                  _buildTimelineItem(
                    step: '4',
                    title: 'Retail Distribution Hub Receipt',
                    subtitle: '15 Oct 2026, 09:20 IST • Tamper seal intact & verified',
                    status: 'DELIVERED',
                    statusColor: const Color(0xFF059669),
                    isLast: true,
                  ),
                  const SizedBox(height: 16),

                  // Cryptographic Proof Strip
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: const Color(0xFFECFDF5),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: const Color(0xFFA7F3D0)),
                    ),
                    child: const Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Icon(Icons.shield_outlined, color: Color(0xFF047857), size: 20),
                        SizedBox(width: 8),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'SHA-256 Tamper-Proof Cryptographic Hash',
                                style: TextStyle(fontSize: 11.5, fontWeight: FontWeight.bold, color: Color(0xFF065F46)),
                              ),
                              SizedBox(height: 2),
                              Text(
                                'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                style: TextStyle(fontSize: 10, fontFamily: 'monospace', color: Color(0xFF047857)),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildModalRow(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: const TextStyle(fontSize: 12, color: Color(0xFF64748B))),
        Text(value, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF1E293B))),
      ],
    );
  }

  Widget _buildTimelineItem({
    required String step,
    required String title,
    required String subtitle,
    required String status,
    required Color statusColor,
    required bool isLast,
  }) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Column(
          children: [
            Container(
              width: 24,
              height: 24,
              decoration: BoxDecoration(
                color: statusColor,
                shape: BoxShape.circle,
              ),
              child: Center(
                child: Text(step, style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
              ),
            ),
            if (!isLast)
              Container(
                width: 2,
                height: 36,
                color: const Color(0xFFCBD5E1),
              ),
          ],
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Padding(
            padding: EdgeInsets.only(bottom: isLast ? 0 : 12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(title, style: const TextStyle(fontSize: 12.5, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: statusColor.withOpacity(0.12),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        status,
                        style: TextStyle(color: statusColor, fontSize: 9.5, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 2),
                Text(subtitle, style: const TextStyle(fontSize: 11, color: Color(0xFF64748B))),
              ],
            ),
          ),
        ),
      ],
    );
  }

  // ---------------------------------------------------------------------------
  // MODALS & DIALOGS
  // ---------------------------------------------------------------------------
  void _showLanguageModal(BuildContext context) {
    showModalBottomSheet<void>(
      context: context,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(16))),
      builder: (ctx) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 14),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text('Select Language / भाषा चुनें', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800)),
              const SizedBox(height: 8),
              ListTile(
                title: const Text('English (Default)'),
                trailing: _selectedLang == 'en' ? const Icon(Icons.check, color: Color(0xFF047857)) : null,
                onTap: () {
                  _switchLanguage('en');
                  Navigator.pop(ctx);
                },
              ),
              ListTile(
                title: const Text('हिन्दी (Hindi)'),
                trailing: _selectedLang == 'hi' ? const Icon(Icons.check, color: Color(0xFF047857)) : null,
                onTap: () {
                  _switchLanguage('hi');
                  Navigator.pop(ctx);
                },
              ),
              ListTile(
                title: const Text('বাংলা (Bengali)'),
                trailing: _selectedLang == 'bn' ? const Icon(Icons.check, color: Color(0xFF047857)) : null,
                onTap: () {
                  _switchLanguage('bn');
                  Navigator.pop(ctx);
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showQrDialog(BuildContext context, HarvestLot lot) {
    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Row(
          children: [
            const Icon(Icons.qr_code_2, color: Color(0xFF0B3D2E)),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                '${lot.crop} QR Code',
                style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFFE2E8F0)),
              ),
              child: const Icon(Icons.qr_code_2, size: 160, color: Color(0xFF0B3D2E)),
            ),
            const SizedBox(height: 8),
            Text(
              lot.publicCode,
              style: const TextStyle(fontFamily: 'monospace', fontSize: 11, fontWeight: FontWeight.w700),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  void _showDispatchSheet(BuildContext context, HarvestLot lot) {
    String selectedTarget = 'AGGREGATOR';
    final targetNameCtrl = TextEditingController();

    showDialog<void>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setModalState) => AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          title: const Text('Dispatch Batch (Handover)', style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('Lot: ${lot.crop} (${lot.netQtyKg} ${lot.unit})', style: const TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 10),
              DropdownButtonFormField<String>(
                value: selectedTarget,
                decoration: const InputDecoration(labelText: 'Receiving Party Role'),
                items: const [
                  DropdownMenuItem(value: 'AGGREGATOR', child: Text('Mandi Aggregator / APMC')),
                  DropdownMenuItem(value: 'WHOLESALER', child: Text('Wholesaler')),
                  DropdownMenuItem(value: 'DISTRIBUTOR', child: Text('Distributor')),
                  DropdownMenuItem(value: 'RETAILER', child: Text('Retailer Shop')),
                ],
                onChanged: (val) {
                  if (val != null) setModalState(() => selectedTarget = val);
                },
              ),
              const SizedBox(height: 10),
              TextField(
                controller: targetNameCtrl,
                decoration: const InputDecoration(labelText: 'Receiving Party Name *'),
              ),
            ],
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
            ElevatedButton(
              onPressed: () async {
                final authState = ref.read(authControllerProvider);
                await ref.read(lotsControllerProvider.notifier).requestCustodyHandover(
                      lot.publicCode,
                      targetRole: selectedTarget,
                      targetName: targetNameCtrl.text.trim().isNotEmpty ? targetNameCtrl.text.trim() : 'Mandi Hub',
                      targetPhone: '+919876543210',
                      declaredQtyKg: lot.netQtyKg,
                      accessToken: authState.accessToken,
                    );
                if (ctx.mounted) Navigator.pop(ctx);
              },
              style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF0B3D2E), foregroundColor: Colors.white),
              child: const Text('Confirm Dispatch'),
            ),
          ],
        ),
      ),
    );
  }

  void _showReceiveDialog(BuildContext context) {
    final codeCtrl = TextEditingController();
    final weightCtrl = TextEditingController();

    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Text('Accept Custody & Verify', style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: codeCtrl,
              decoration: const InputDecoration(labelText: 'Scanned / Entered Lot Code *', hintText: 'Paste or enter lot ID'),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: weightCtrl,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'Verified Weight (Kg) *'),
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () async {
              final authState = ref.read(authControllerProvider);
              final code = codeCtrl.text.trim();
              final wt = double.tryParse(weightCtrl.text.trim()) ?? 0.0;
              if (code.isNotEmpty) {
                await ref.read(lotsControllerProvider.notifier).acceptCustodyHandover(
                      code,
                      actorRole: authState.orgType ?? 'AGGREGATOR',
                      actorName: authState.orgName ?? 'Verified Custodian',
                      receivedQtyKg: wt,
                      condition: 'FRESH_GRADE_A',
                      accessToken: authState.accessToken,
                    );
                if (ctx.mounted) Navigator.pop(ctx);
              }
            },
            style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF0B3D2E), foregroundColor: Colors.white),
            child: const Text('Confirm Receipt'),
          ),
        ],
      ),
    );
  }
}
