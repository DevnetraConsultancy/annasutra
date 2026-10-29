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
  final TextEditingController _phoneController = TextEditingController();
  final TextEditingController _otpController = TextEditingController();
  String _selectedRole = 'PRODUCER';

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
  // UNAUTHENTICATED VIEW: GOLD STANDARD MOBILE SIGN-IN
  // ---------------------------------------------------------------------------
  Widget _buildUnauthenticatedView(BuildContext context, AuthState authState) {
    final bool isOtpSent = authState.status == AuthStatus.otpSent;
    final bool isLoading = authState.status == AuthStatus.loading;

    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 440),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Hero Brand Header
              Center(
                child: Column(
                  children: [
                    Container(
                      width: 64,
                      height: 64,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: Colors.white,
                        border: Border.all(color: const Color(0xFFE67E22), width: 2),
                        boxShadow: const [
                          BoxShadow(color: Color(0x14000000), blurRadius: 8, offset: Offset(0, 3)),
                        ],
                      ),
                      child: ClipOval(
                        child: Image.asset(
                          'assets/images/annasutra_emblem.jpg',
                          fit: BoxFit.cover,
                          errorBuilder: (_, __, ___) => const Icon(Icons.eco, color: Color(0xFF0B3D2E), size: 32),
                        ),
                      ),
                    ),
                    const SizedBox(height: 10),
                    Text(
                      _t('loginTitle'),
                      style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w900, color: Color(0xFF0B3D2E)),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      _t('loginSub'),
                      textAlign: TextAlign.center,
                      style: const TextStyle(fontSize: 12.5, color: Color(0xFF64748B)),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 18),

              // Role Selection Chips
              const Text('Select Supply-Chain Role:', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Color(0xFF475569))),
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

              const SizedBox(height: 16),

              // Authentication Card
              Container(
                padding: const EdgeInsets.all(18),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                  boxShadow: const [
                    BoxShadow(color: Color(0x08000000), blurRadius: 8, offset: Offset(0, 2)),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // Phone Number Input
                    TextField(
                      controller: _phoneController,
                      keyboardType: TextInputType.phone,
                      decoration: InputDecoration(
                        labelText: _t('phoneLabel'),
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
                              if (!isOtpSent) {
                                final phone = _phoneController.text.trim();
                                if (phone.isNotEmpty) {
                                  await authNotifier.requestOtp(phone);
                                }
                              } else {
                                final otp = _otpController.text.trim();
                                final phone = _phoneController.text.trim();
                                if (otp.isNotEmpty && phone.isNotEmpty) {
                                  await authNotifier.verifyOtp(phone, otp);
                                }
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
                              if (!success) {
                                final err =
                                    ref.read(authControllerProvider).errorMessage;
                                if (err != null && err.isNotEmpty) {
                                  messenger.showSnackBar(
                                    SnackBar(content: Text(err)),
                                  );
                                }
                              }
                            },
                      icon: const Icon(Icons.g_mobiledata, size: 22, color: Color(0xFFEA4335)),
                      label: Text(_t('btnGoogle'), style: const TextStyle(color: Color(0xFF0F172A))),
                      style: OutlinedButton.styleFrom(
                        minimumSize: const Size(double.infinity, 44),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 16),
              Text(
                _t('dpdpNotice'),
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 10.5, color: Color(0xFF94A3B8)),
              ),
            ],
          ),
        ),
      ),
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
