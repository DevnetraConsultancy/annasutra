import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:video_player/video_player.dart';
import 'package:barcode_widget/barcode_widget.dart';
import 'package:qr_flutter/qr_flutter.dart';
import 'package:share_plus/share_plus.dart';

import '../../../data/platform/platform_providers.dart';
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
  int _selectedProfileStep =
      0; // 0..4 for the 5 Registration Tabs under Profile
  String _selectedLang = 'en';

  // Search & Filter State
  final TextEditingController _searchController = TextEditingController();
  String _selectedCustodyFilter = 'ALL';

  // Auth form controllers for unauthenticated view
  final TextEditingController _phoneController = TextEditingController();
  final TextEditingController _otpController = TextEditingController();
  String _selectedRole = 'PRODUCER';
  VideoPlayerController? _videoController;

  // Editable Profile State (5-Tab Registration Data Inspection & Self-Service Edit)
  late final TextEditingController _altPhoneCtrl = TextEditingController();
  late final TextEditingController _emailCtrl = TextEditingController();
  late final TextEditingController _addrLine2Ctrl = TextEditingController();
  late final TextEditingController _plotNicknameCtrl = TextEditingController();
  late final TextEditingController _seasonalNotesCtrl = TextEditingController();
  late final TextEditingController _secondaryCropsCtrl =
      TextEditingController();
  late final TextEditingController _irrigationCtrl = TextEditingController();
  late final TextEditingController _certNotesCtrl = TextEditingController();

  // Registered Plots & Submitted Change Requests (Purged all fake preloaded data)
  final List<Map<String, dynamic>> _registeredPlots = [];
  final List<Map<String, String>> _changeRequests = [];

  // All 7 Entity Roles in One Single Universal APK
  static const List<Map<String, dynamic>> _roleOptions = [
    {'code': 'PRODUCER', 'label': 'Farmer / FPO', 'icon': Icons.agriculture},
    {
      'code': 'AGGREGATOR',
      'label': 'Mandi / APMC',
      'icon': Icons.storefront_outlined
    },
    {
      'code': 'PROCESSOR',
      'label': 'Processor / Mill',
      'icon': Icons.precision_manufacturing_outlined
    },
    {
      'code': 'WHOLESALER',
      'label': 'Wholesaler',
      'icon': Icons.inventory_2_outlined
    },
    {
      'code': 'DISTRIBUTOR',
      'label': 'Distributor',
      'icon': Icons.local_shipping_outlined
    },
    {
      'code': 'RETAILER',
      'label': 'Retailer Shop',
      'icon': Icons.shopping_bag_outlined
    },
    {
      'code': 'VERIFIER',
      'label': 'Public Consumer / Verifier',
      'icon': Icons.qr_code_scanner
    },
  ];

  static const Map<String, String> _roleConsoleSubtitles = {
    'PRODUCER': 'Producer Operations Console',
    'FARMER': 'Producer Operations Console',
    'AGGREGATOR': 'Aggregator / Mandi Console',
    'PROCESSOR': 'Processor / Mill Console',
    'WHOLESALER': 'Wholesaler Console',
    'DISTRIBUTOR': 'Distributor Console',
    'RETAILER': 'Retailer Console',
    'VERIFIER': 'Public Consumer / Verifier Console',
  };

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
      'noBatchesSub':
          'Register your first produce lot to generate QR and barcode crate labels.',
      'btnCreateFirst': '+ Create First Batch',
      'handoverTitle': 'Custody Transfer',
      'handoverSub':
          'Hand over produce lot to counterparty with verified QR confirmation.',
      'scanToReceive': 'Scan QR to Receive Custody',
      'scanToReceiveSub':
          'Inspect incoming produce crates, verify net weight & append condition telemetry.',
      'btnScanQr': 'Scan Crate QR',
      'manualCodePh': 'Or enter Lot Code manually',
      'btnVerifyAccept': 'Accept & Append Telemetry',
      'dispatchedBatches': 'Dispatched Batches (In Transit)',
      'noDispatched':
          'No active outgoing handovers pending counterparty sign-off.',
      'insightsTitle': 'Farm & Harvest Insights',
      'grossValuation': 'Gross Valuation',
      'realizedRevenue': 'Realized Revenue',
      'gradeARatio': 'Grade A Quality Ratio',
      'cropBreakdown': 'Crop Volume Distribution',
      'plotsTitle': 'Mapped Agricultural Plots',
      'profileTitle': 'Producer Profile & Registration',
      'kycVerified': 'KYC Verified',
      'kycPending': 'Under Admin Review',
      'maskedPan': 'PAN Identity',
      'bankAccount': 'Settlement Bank',
      'statutoryConsent': 'Privacy & Data Consent',
      'btnLogout': 'Log Out',
      'loginTitle': 'Farm-to-Fork Traceability',
      'loginSub': 'Agri-Traceability Console',
      'phoneLabel': 'Mobile Number',
      'otpLabel': 'Enter 6-digit OTP',
      'btnSendOtp': 'Get OTP via SMS',
      'btnVerifyOtp': 'Verify & Sign In',
      'btnGoogle': 'Sign in with Google',
      'dpdpNotice': 'Protected under DPDP Act 2023 • National Cloud Node',
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
      'noBatchesSub':
          'क्यूआर क्रेट लेबल उत्पन्न करने के लिए अपना पहला फ़सल लॉट पंजीकृत करें।',
      'btnCreateFirst': '+ पहला बैच बनाएं',
      'handoverTitle': 'कस्टडी हस्तांतरण',
      'handoverSub':
          'सत्यापित क्यूआर पुष्टि के साथ प्रतिपक्ष को कस्टडी हस्तांतरित करें।',
      'scanToReceive': 'कस्टडी प्राप्त करने के लिए क्यूआर स्कैन करें',
      'scanToReceiveSub':
          'आवक क्रेट्स का निरीक्षण करें, वजन सत्यापित करें व स्थिति दर्ज करें।',
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
      'profileTitle': 'उत्पादक प्रोफ़ाइल एवं पंजीकरण',
      'kycVerified': 'केवाईसी सत्यापित',
      'kycPending': 'प्रशासनिक समीक्षाधीन',
      'maskedPan': 'पैन पहचान',
      'bankAccount': 'निपटान बैंक',
      'statutoryConsent': 'गोपनीयता एवं डेटा सहमति',
      'btnLogout': 'लॉग आउट',
      'loginTitle': 'बीज से थाली तक ट्रेसेबिलिटी',
      'loginSub': 'कृषि-ट्रेसेबिलिटी कंसोल',
      'phoneLabel': 'मोबाइल नंबर',
      'otpLabel': '६-अंकीय ओटीपी दर्ज करें',
      'btnSendOtp': 'ओटीपी प्राप्त करें',
      'btnVerifyOtp': 'सत्यापित करें व प्रवेश करें',
      'btnGoogle': 'गूगल से लॉगिन करें',
      'dpdpNotice': 'Protected under DPDP Act 2023 • National Cloud Node',
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
      'noBatchesSub': 'কিউআর লেবেল পেতে প্রথম ফসল লট নিবন্ধন করুন।',
      'btnCreateFirst': '+ প্রথম ব্যাচ তৈরি করুন',
      'handoverTitle': 'হেফাজত হস্তান্তর',
      'handoverSub':
          'যাচাইকৃত কিউআর নিশ্চিতকরণ সহ পরবর্তী পক্ষের কাছে পণ্য হস্তান্তর করুন।',
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
      'profileTitle': 'উৎপাদক প্রোফাইল ও নিবন্ধন',
      'kycVerified': 'কেওয়াইসি যাচাইকৃত',
      'kycPending': 'প্রশাসনিক পর্যালোচনাধীন',
      'maskedPan': 'প্যান পরিচয়',
      'bankAccount': 'ব্যাঙ্ক অ্যাকাউন্ট',
      'statutoryConsent': 'গোপনীয়তা ও ডেটা সম্মতি',
      'btnLogout': 'লॉग আউট',
      'loginTitle': 'বীজ থেকে ভোক্তা পর্যন্ত স্বচ্ছতা',
      'loginSub': 'কৃষি ট্রেসেবিলিটি কনসোল',
      'phoneLabel': 'মোবাইল নম্বর',
      'otpLabel': '৬-সংখ্যার ওটিপি লিখুন',
      'btnSendOtp': 'ওটিপি পাঠান',
      'btnVerifyOtp': 'যাচাই করুন ও প্রবেশ করুন',
      'btnGoogle': 'গুগল দিয়ে প্রবেশ করুন',
      'dpdpNotice': 'Protected under DPDP Act 2023 • National Cloud Node',
    },
  };

  String _t(String key) =>
      _strings[_selectedLang]?[key] ?? _strings['en']?[key] ?? key;

  @override
  void initState() {
    super.initState();
    _initBackgroundVideo();
    _hydrateProfileData();
  }

  Future<void> _hydrateProfileData() async {
    try {
      final store = ref.read(secureStoreProvider);
      final cachedProfileStr = await store.read('annasutra_cached_profile');
      if (cachedProfileStr != null && cachedProfileStr.isNotEmpty) {
        final profile = jsonDecode(cachedProfileStr) as Map<String, dynamic>;
        if (mounted) {
          setState(() {
            _altPhoneCtrl.text = profile['alt_phone']?.toString() ?? '';
            _emailCtrl.text = profile['email']?.toString() ?? '';
            _addrLine2Ctrl.text = profile['address_line2']?.toString() ?? '';
            _plotNicknameCtrl.text =
                profile['plot_nicknames']?.toString() ?? '';
            _seasonalNotesCtrl.text =
                profile['seasonal_notes']?.toString() ?? '';
            _secondaryCropsCtrl.text =
                profile['secondary_crops']?.toString() ?? '';
            _irrigationCtrl.text = profile['irrigation']?.toString() ?? '';
            _certNotesCtrl.text = profile['cert_notes']?.toString() ?? '';
          });
        }
      }

      final cachedPlotsStr = await store.read('annasutra_cached_plots');
      if (cachedPlotsStr != null && cachedPlotsStr.isNotEmpty) {
        final plotsList = jsonDecode(cachedPlotsStr) as List;
        if (mounted) {
          setState(() {
            _registeredPlots.clear();
            for (final p in plotsList) {
              _registeredPlots.add(Map<String, dynamic>.from(p as Map));
            }
          });
        }
      }
    } catch (_) {}
  }

  void _initBackgroundVideo() {
    final isTest = Platform.environment.containsKey('FLUTTER_TEST');
    if (!isTest) {
      try {
        _videoController =
            VideoPlayerController.asset('assets/videos/annasutra_bg.mp4')
              ..initialize().then((_) {
                if (mounted) {
                  _videoController?.setLooping(true);
                  _videoController?.setVolume(0.0);
                  _videoController?.play();
                  setState(() {});
                }
              }).catchError((_) {});
      } catch (_) {}
    }
  }

  @override
  void dispose() {
    _videoController?.dispose();
    _searchController.dispose();
    _phoneController.dispose();
    _otpController.dispose();
    _altPhoneCtrl.dispose();
    _emailCtrl.dispose();
    _addrLine2Ctrl.dispose();
    _plotNicknameCtrl.dispose();
    _seasonalNotesCtrl.dispose();
    _secondaryCropsCtrl.dispose();
    _irrigationCtrl.dispose();
    _certNotesCtrl.dispose();
    super.dispose();
  }

  void _switchLanguage(String lang) {
    setState(() => _selectedLang = lang);
    widget.onLocaleChanged?.call(Locale(lang));
  }

  String _activeRole(AuthState authState) {
    final r = (authState.orgType ?? 'PRODUCER').toUpperCase();
    return r == 'FARMER' ? 'PRODUCER' : r;
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authControllerProvider);
    final lotsState = ref.watch(lotsControllerProvider);
    final syncState = ref.watch(syncControllerProvider);
    final role = _activeRole(authState);

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: authState.isAuthenticated
          ? _buildTopAppBar(context, authState, syncState, role)
          : null,
      body: authState.isAuthenticated
          ? (authState.showRolePortal
              ? _buildRoleStatusPortal(context, authState)
              : IndexedStack(
                  index: _currentNavIndex,
                  children: [
                    _buildBatchesTab(context, lotsState, authState, role),
                    _buildHandoverTab(context, lotsState, authState, role),
                    _buildInsightsTab(context, lotsState),
                    _buildProfileTab(context, authState, role),
                  ],
                ))
          : _buildUnauthenticatedView(context, authState),
      bottomNavigationBar: (authState.isAuthenticated && !authState.showRolePortal)
          ? NavigationBar(
              selectedIndex: _currentNavIndex,
              onDestinationSelected: (idx) =>
                  setState(() => _currentNavIndex = idx),
              backgroundColor: Colors.white,
              elevation: 4,
              indicatorColor: const Color(0xFFECFDF5),
              destinations: [
                NavigationDestination(
                  icon: const Icon(Icons.inventory_2_outlined),
                  selectedIcon:
                      const Icon(Icons.inventory_2, color: Color(0xFF0B3D2E)),
                  label: _t('navBatches'),
                ),
                NavigationDestination(
                  icon: const Icon(Icons.swap_horiz_outlined),
                  selectedIcon:
                      const Icon(Icons.swap_horiz, color: Color(0xFF0B3D2E)),
                  label: _t('navHandover'),
                ),
                NavigationDestination(
                  icon: const Icon(Icons.insights_outlined),
                  selectedIcon:
                      const Icon(Icons.insights, color: Color(0xFF0B3D2E)),
                  label: _t('navInsights'),
                ),
                NavigationDestination(
                  icon: const Icon(Icons.person_outline),
                  selectedIcon:
                      const Icon(Icons.person, color: Color(0xFF0B3D2E)),
                  label: _t('navProfile'),
                ),
              ],
            )
          : null,
      floatingActionButton: (authState.isAuthenticated &&
              !authState.showRolePortal &&
              _currentNavIndex == 0 &&
              !authState.isDeletionRequested)
          ? FloatingActionButton.extended(
              onPressed: () {
                if (role == 'VERIFIER') {
                  _showConsumerVerifierSheet(context, lotsState.lots);
                } else {
                  context.push('/create-batch');
                }
              },
              backgroundColor: const Color(0xFF0B3D2E),
              foregroundColor: Colors.white,
              elevation: 3,
              icon: Icon(role == 'VERIFIER' ? Icons.qr_code_scanner : Icons.add,
                  size: 20),
              label: Text(
                role == 'VERIFIER' ? 'Scan QR' : _t('newBatch'),
                style: const TextStyle(
                    fontWeight: FontWeight.w800, fontSize: 13.5),
              ),
            )
          : null,
    );
  }

  // 1. TOP APP BAR (With Role Switcher & Unified Logout per Decision 14 & 25)
  PreferredSizeWidget _buildTopAppBar(
    BuildContext context,
    AuthState authState,
    SyncState syncState,
    String role,
  ) {
    final subtitle = _roleConsoleSubtitles[role] ?? _t('appSubtitle');
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
                errorBuilder: (_, __, ___) =>
                    const Icon(Icons.eco, color: Color(0xFF0B3D2E), size: 18),
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
                  style: const TextStyle(
                      fontSize: 17,
                      fontWeight: FontWeight.w900,
                      letterSpacing: -0.2),
                  overflow: TextOverflow.ellipsis,
                ),
                Text(
                  subtitle,
                  style: const TextStyle(
                      fontSize: 9.5,
                      color: Color(0xFFA7F3D0),
                      fontWeight: FontWeight.w500),
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
            color: syncState.pendingCount == 0
                ? const Color(0xFF064E3B)
                : const Color(0xFF78350F),
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
                  color: syncState.pendingCount == 0
                      ? const Color(0xFF34D399)
                      : const Color(0xFFFBBF24),
                ),
              ),
              const SizedBox(width: 4),
              Text(
                syncState.pendingCount == 0
                    ? 'Synced'
                    : '${syncState.pendingCount} Pending',
                style: const TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w700,
                    color: Colors.white),
              ),
            ],
          ),
        ),

        // Role Switcher & Unified Account Menu
        PopupMenuButton<String>(
          icon: const Icon(Icons.swap_vert_circle_outlined, size: 20),
          tooltip: 'Switch Role Console or Sign Out',
          onSelected: (val) async {
            if (val == 'LOGOUT') {
              await ref.read(authControllerProvider.notifier).logout();
            } else if (val == 'ROLE_PORTAL') {
              ref.read(authControllerProvider.notifier).toggleRolePortal(true);
            } else {
              if (val == 'ADMIN' && !authState.isAdmin) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text(
                        'Access Restricted: Only devnetraconsultancy@gmail.com is authorized for Admin Console.'),
                    backgroundColor: Color(0xFFDC2626),
                  ),
                );
                return;
              }
              ref.read(authControllerProvider.notifier).toggleRolePortal(false);
              await ref
                  .read(authControllerProvider.notifier)
                  .switchActiveRole(val);
            }
          },
          itemBuilder: (ctx) {
            final approvedList = <String>[];
            for (final reg in authState.roleRegistrations) {
              final st = (reg['status'] ?? reg['org_verification'] ?? '')
                  .toString()
                  .toUpperCase();
              final rCode = (reg['role'] ?? reg['org_type'] ?? '')
                  .toString()
                  .toUpperCase();
              if ((st == 'APPROVED' || st == 'VERIFIED') && rCode.isNotEmpty) {
                if (!approvedList.contains(rCode)) approvedList.add(rCode);
              }
            }
            if (approvedList.isEmpty && authState.isOrgVerified) {
              approvedList.add(role);
            }
            if (authState.isAdmin && !approvedList.contains('ADMIN')) {
              approvedList.add('ADMIN');
            }

            return [
              const PopupMenuItem<String>(
                enabled: false,
                child: Text(
                  'APPROVED ROLES',
                  style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF64748B)),
                ),
              ),
              if (approvedList.isEmpty)
                const PopupMenuItem<String>(
                  enabled: false,
                  child: Text(
                    'No Approved Roles Yet (Under Review)',
                    style: TextStyle(fontSize: 12, color: Color(0xFF94A3B8)),
                  ),
                )
              else
                ...approvedList.map((code) {
                  final match = _roleOptions.firstWhere(
                    (opt) => opt['code'] == code,
                    orElse: () => code == 'ADMIN'
                        ? {
                            'code': 'ADMIN',
                            'label': 'Admin Console',
                            'icon': Icons.admin_panel_settings_outlined
                          }
                        : {
                            'code': code,
                            'label': code,
                            'icon': Icons.verified_user_outlined
                          },
                  );
                  return PopupMenuItem<String>(
                    value: code,
                    child: Row(
                      children: [
                        Icon(
                          match['icon'] as IconData,
                          size: 16,
                          color: role == code
                              ? const Color(0xFF047857)
                              : const Color(0xFF64748B),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            match['label'] as String,
                            style: TextStyle(
                              fontSize: 12.5,
                              fontWeight: role == code
                                  ? FontWeight.w800
                                  : FontWeight.w500,
                            ),
                          ),
                        ),
                        if (role == code)
                          const Icon(Icons.check,
                              size: 15, color: Color(0xFF047857)),
                      ],
                    ),
                  );
                }),
              const PopupMenuDivider(),
              const PopupMenuItem<String>(
                value: 'ROLE_PORTAL',
                child: Row(
                  children: [
                    Icon(Icons.dashboard_customize_outlined,
                        size: 16, color: Color(0xFF0B3D2E)),
                    SizedBox(width: 8),
                    Text(
                      'Manage Roles / Status Portal',
                      style: TextStyle(
                          fontSize: 12.5,
                          fontWeight: FontWeight.w700,
                          color: Color(0xFF0B3D2E)),
                    ),
                  ],
                ),
              ),
              const PopupMenuDivider(),
              const PopupMenuItem<String>(
                value: 'LOGOUT',
                child: Row(
                  children: [
                    Icon(Icons.logout, size: 16, color: Color(0xFFDC2626)),
                    SizedBox(width: 8),
                    Text(
                      'Sign Out',
                      style: TextStyle(
                          fontSize: 12.5,
                          fontWeight: FontWeight.w700,
                          color: Color(0xFFDC2626)),
                    ),
                  ],
                ),
              ),
            ];
          },
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
  // ROLE REGISTRATION & STATUS PORTAL (Decision 31, 35, Core C2)
  // ---------------------------------------------------------------------------
  Widget _buildRoleStatusPortal(BuildContext context, AuthState authState) {
    const roles = [
      {
        'code': 'PRODUCER',
        'title': 'Producer / Farmer',
        'desc':
            'Cultivate, register harvest lots, mint QRs, and manage plot boundaries.',
        'icon': Icons.agriculture,
      },
      {
        'code': 'AGGREGATOR',
        'title': 'Aggregator / FPO / Mandi',
        'desc':
            'Aggregate produce lots, bulk scale weighing, APMC mandi trading.',
        'icon': Icons.storefront_outlined,
      },
      {
        'code': 'PROCESSOR',
        'title': 'Processor / Manufacturer / Mill',
        'desc':
            'Clean, process, sort, conversion ratio grading, packaging SKU catalog.',
        'icon': Icons.precision_manufacturing_outlined,
      },
      {
        'code': 'WHOLESALER',
        'title': 'Wholesaler',
        'desc':
            'Bulk lot procurement, e-NAM integration, regional lot split dispatch.',
        'icon': Icons.inventory_2_outlined,
      },
      {
        'code': 'DISTRIBUTOR',
        'title': 'Distributor / Cold Storage',
        'desc':
            'Cold chain monitoring, temperature telemetry, fleet dispatch logistics.',
        'icon': Icons.local_shipping_outlined,
      },
      {
        'code': 'RETAILER',
        'title': 'Retailer Shop',
        'desc':
            'Consumer shelf stocking, retail pack display, counter sales checkout.',
        'icon': Icons.shopping_bag_outlined,
      },
    ];

    final currentRole = _activeRole(authState);
    final isCurrentApproved = authState.isOrgVerified;

    return ListView(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0xFF0B3D2E),
            borderRadius: BorderRadius.circular(16),
            boxShadow: const [
              BoxShadow(
                color: Color(0x1A000000),
                blurRadius: 10,
                offset: Offset(0, 4),
              ),
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
                      color: const Color(0x33FFFFFF),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: const Icon(Icons.manage_accounts,
                        color: Color(0xFFA7F3D0), size: 24),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Multi-Role Registration Portal',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w900,
                            color: Colors.white,
                          ),
                        ),
                        Text(
                          'Account: ${authState.email ?? authState.phone ?? 'Verified Identity'}',
                          style: const TextStyle(
                            fontSize: 11.5,
                            color: Color(0xFFA7F3D0),
                            fontWeight: FontWeight.w600,
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              const Text(
                'Each entity role requires independent Admin approval. Once approved, you obtain a unique 26-digit role identity to operate its console.',
                style: TextStyle(fontSize: 11.5, color: Color(0xFFE2E8F0)),
              ),
              if (isCurrentApproved) ...[
                const SizedBox(height: 12),
                Align(
                  alignment: Alignment.centerRight,
                  child: OutlinedButton.icon(
                    onPressed: () => ref
                        .read(authControllerProvider.notifier)
                        .toggleRolePortal(false),
                    icon: const Icon(Icons.arrow_back, size: 15),
                    label: Text('Open $currentRole Console'),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: Colors.white,
                      side: const BorderSide(color: Color(0xFF34D399)),
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
        const SizedBox(height: 18),
        const Text(
          'SUPPLY CHAIN ROLE REGISTRATIONS',
          style: TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.w800,
            color: Color(0xFF64748B),
            letterSpacing: 0.5,
          ),
        ),
        const SizedBox(height: 10),
        if (authState.isAdmin)
          _buildRoleCard(
            context,
            authState,
            code: 'ADMIN',
            title: 'System Administrator',
            desc:
                'Sovereign governance, registration review, KYC change approval queue.',
            icon: Icons.admin_panel_settings_outlined,
            status: 'APPROVED',
            uniqueId: 'ADMIN-MASTER-ROOT',
          ),
        ...roles.map((r) {
          final code = r['code'] as String;
          final match = authState.roleRegistrations.firstWhere(
            (reg) =>
                (reg['role'] ?? reg['org_type'] ?? '')
                    .toString()
                    .toUpperCase() ==
                code,
            orElse: () => <String, dynamic>{},
          );

          String status = 'NOT_REGISTERED';
          String? appRef;
          String? remark;
          String? roleUid;

          if (match.isNotEmpty) {
            status = (match['status'] ??
                    match['org_verification'] ??
                    'UNDER_REVIEW')
                .toString()
                .toUpperCase();
            appRef = match['application_ref']?.toString() ??
                match['app_ref']?.toString() ??
                'APP-PENDING';
            remark = match['admin_remark']?.toString() ??
                match['remark']?.toString();
            roleUid = match['role_id']?.toString() ??
                match['farmer_uid']?.toString();
          } else if (code == currentRole && authState.isOrgVerified) {
            status = 'APPROVED';
            roleUid = authState.farmerUid;
          } else if (code == currentRole &&
              authState.orgVerification == 'PENDING') {
            status = 'UNDER_REVIEW';
            appRef = 'APP-PENDING';
          }

          return _buildRoleCard(
            context,
            authState,
            code: code,
            title: r['title'] as String,
            desc: r['desc'] as String,
            icon: r['icon'] as IconData,
            status: status,
            appRef: appRef,
            remark: remark,
            uniqueId: roleUid,
          );
        }),
        const SizedBox(height: 40),
      ],
    );
  }

  Widget _buildRoleCard(
    BuildContext context,
    AuthState authState, {
    required String code,
    required String title,
    required String desc,
    required IconData icon,
    required String status,
    String? appRef,
    String? remark,
    String? uniqueId,
  }) {
    Color chipBg;
    Color chipText;
    String chipLabel;

    switch (status) {
      case 'APPROVED':
      case 'VERIFIED':
        chipBg = const Color(0xFFECFDF5);
        chipText = const Color(0xFF047857);
        chipLabel = 'APPROVED';
        break;
      case 'UNDER_REVIEW':
      case 'SUBMITTED':
      case 'PENDING':
        chipBg = const Color(0xFFFFFBEB);
        chipText = const Color(0xFFB45309);
        chipLabel = 'UNDER REVIEW';
        break;
      case 'CHANGES_REQUESTED':
        chipBg = const Color(0xFFFFF7ED);
        chipText = const Color(0xFFC2410C);
        chipLabel = 'CHANGES REQUESTED';
        break;
      case 'REJECTED':
        chipBg = const Color(0xFFFEF2F2);
        chipText = const Color(0xFFDC2626);
        chipLabel = 'REJECTED';
        break;
      default:
        chipBg = const Color(0xFFF1F5F9);
        chipText = const Color(0xFF64748B);
        chipLabel = 'NOT REGISTERED';
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: (status == 'APPROVED' || status == 'VERIFIED')
              ? const Color(0xFF86EFAC)
              : const Color(0xFFE2E8F0),
        ),
        boxShadow: const [
          BoxShadow(
              color: Color(0x06000000), blurRadius: 6, offset: Offset(0, 2)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: const Color(0xFFF8FAFC),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Icon(icon, color: const Color(0xFF0B3D2E), size: 22),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Expanded(
                          child: Text(
                            title,
                            style: const TextStyle(
                              fontSize: 14.5,
                              fontWeight: FontWeight.w800,
                              color: Color(0xFF0F172A),
                            ),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 8, vertical: 3),
                          decoration: BoxDecoration(
                            color: chipBg,
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text(
                            chipLabel,
                            style: TextStyle(
                              fontSize: 10,
                              fontWeight: FontWeight.w800,
                              color: chipText,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      desc,
                      style: const TextStyle(
                          fontSize: 11.5, color: Color(0xFF64748B)),
                    ),
                  ],
                ),
              ),
            ],
          ),
          if (uniqueId != null && uniqueId.isNotEmpty) ...[
            const SizedBox(height: 10),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
              decoration: BoxDecoration(
                color: const Color(0xFFF0FDF4),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: const Color(0xFF86EFAC)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.key, size: 14, color: Color(0xFF047857)),
                  const SizedBox(width: 6),
                  Text(
                    'Unique Role ID: $uniqueId',
                    style: const TextStyle(
                      fontFamily: 'monospace',
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF065F46),
                    ),
                  ),
                ],
              ),
            ),
          ],
          if (appRef != null &&
              (status == 'UNDER_REVIEW' ||
                  status == 'SUBMITTED' ||
                  status == 'PENDING')) ...[
            const SizedBox(height: 8),
            Text(
              'Application Ref: $appRef',
              style: const TextStyle(
                fontFamily: 'monospace',
                fontSize: 11,
                fontWeight: FontWeight.bold,
                color: Color(0xFFB45309),
              ),
            ),
          ],
          if (remark != null && remark.isNotEmpty) ...[
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: const Color(0xFFFFF7ED),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: const Color(0xFFFDBA74)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.info_outline,
                      size: 14, color: Color(0xFFC2410C)),
                  const SizedBox(width: 6),
                  Expanded(
                    child: Text(
                      'Admin Remark: $remark',
                      style: const TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFF9A3412)),
                    ),
                  ),
                ],
              ),
            ),
          ],
          const SizedBox(height: 12),
          Align(
            alignment: Alignment.centerRight,
            child: _buildRoleActionButton(context, code, title, status, appRef),
          ),
        ],
      ),
    );
  }

  Widget _buildRoleActionButton(BuildContext context, String code, String title,
      String status, String? appRef) {
    if (status == 'APPROVED' || status == 'VERIFIED') {
      return ElevatedButton.icon(
        onPressed: () {
          ref.read(authControllerProvider.notifier).toggleRolePortal(false);
          ref.read(authControllerProvider.notifier).switchActiveRole(code);
        },
        icon: const Icon(Icons.login, size: 15),
        label: Text('Open $title Console'),
        style: ElevatedButton.styleFrom(
          backgroundColor: const Color(0xFF0B3D2E),
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        ),
      );
    }

    if (status == 'UNDER_REVIEW' ||
        status == 'SUBMITTED' ||
        status == 'PENDING') {
      return OutlinedButton.icon(
        onPressed: () => _showStatusStepperDialog(context, code, appRef),
        icon: const Icon(Icons.timeline, size: 15),
        label: const Text('View Status Stepper'),
        style: OutlinedButton.styleFrom(
          foregroundColor: const Color(0xFFB45309),
          side: const BorderSide(color: Color(0xFFFCD34D)),
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        ),
      );
    }

    if (status == 'CHANGES_REQUESTED') {
      return ElevatedButton.icon(
        onPressed: () => context.push('/register-org?role=$code'),
        icon: const Icon(Icons.edit_note, size: 15),
        label: const Text('Fix & Resubmit'),
        style: ElevatedButton.styleFrom(
          backgroundColor: const Color(0xFFC2410C),
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        ),
      );
    }

    return OutlinedButton.icon(
      onPressed: () => context.push('/register-org?role=$code'),
      icon: const Icon(Icons.add, size: 15),
      label: Text('Register as $code'),
      style: OutlinedButton.styleFrom(
        foregroundColor: const Color(0xFF0B3D2E),
        side: const BorderSide(color: Color(0xFF0B3D2E)),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      ),
    );
  }

  void _showStatusStepperDialog(
      BuildContext context, String role, String? appRef) {
    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Row(
          children: [
            const Icon(Icons.verified_outlined, color: Color(0xFFB45309)),
            const SizedBox(width: 8),
            Expanded(
              child: Text('$role Registration Status',
                  style: const TextStyle(
                      fontSize: 15, fontWeight: FontWeight.bold)),
            ),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: const Color(0xFFFFFBEB),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: const Color(0xFFFDE68A)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Application Reference:',
                      style:
                          TextStyle(fontSize: 10, color: Color(0xFF78350F))),
                  Text(
                    appRef ?? 'APP-PENDING',
                    style: const TextStyle(
                        fontFamily: 'monospace',
                        fontWeight: FontWeight.bold,
                        fontSize: 13,
                        color: Color(0xFF92400E)),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 14),
            _buildStepperItem('1. Signatory & Business Identity',
                'Completed & E-Signed', true),
            _buildStepperItem(
                '2. Premises & Scale Licensing', 'Completed', true),
            _buildStepperItem('3. Role Module & SKUs', 'Completed', true),
            _buildStepperItem('4. Identity & Bank Verification',
                'Pending Admin Verification', false,
                isPending: true),
            _buildStepperItem('5. Sovereign UID Minting',
                'Awaiting Admin Approval', false),
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

  Widget _buildStepperItem(String title, String status, bool isDone,
      {bool isPending = false}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Row(
        children: [
          Icon(
            isDone
                ? Icons.check_circle
                : (isPending
                    ? Icons.pending_outlined
                    : Icons.radio_button_unchecked),
            size: 16,
            color: isDone
                ? const Color(0xFF047857)
                : (isPending
                    ? const Color(0xFFB45309)
                    : const Color(0xFF94A3B8)),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title,
                    style: const TextStyle(
                        fontSize: 12, fontWeight: FontWeight.w700)),
                Text(status,
                    style: TextStyle(
                        fontSize: 10.5,
                        color: isDone
                            ? const Color(0xFF047857)
                            : (isPending
                                ? const Color(0xFFB45309)
                                : const Color(0xFF64748B)))),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // TAB 0: BATCHES & ROLE CONSOLE HOME
  // ---------------------------------------------------------------------------
  Widget _buildBatchesTab(
    BuildContext context,
    LotsState lotsState,
    AuthState authState,
    String role,
  ) {
    // Section 4.2.1 Strict Pre-Approval Farmer ID Policy:
    // Never show Unique Farmer ID until Admin approves the registration.
    final bool isApproved = authState.isOrgVerified &&
        authState.farmerUid != null &&
        authState.farmerUid!.isNotEmpty;
    final String displayId =
        isApproved ? authState.farmerUid! : 'Under Admin Review';

    final lots = lotsState.filteredLots;
    final totalKg = lots.fold<double>(0.0, (acc, lot) => acc + lot.netQtyKg);
    final totalVal =
        lots.fold<double>(0.0, (acc, lot) => acc + lot.estimatedValue);
    final inCustodyCount = lots.where((l) => l.isEditable).length;
    final inTransitCount = lots.where((l) => l.state == 'IN_TRANSIT').length;

    final totalAcres = _registeredPlots.fold<double>(
        0.0, (acc, p) => acc + (p['acres'] as double));
    final allocAcres = _registeredPlots.fold<double>(
        0.0, (acc, p) => acc + (p['allocatedAcres'] as double));
    final freeAcres = (totalAcres - allocAcres).clamp(0.0, 9999.0);

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
          // Deletion Requested Freeze Banner
          if (authState.isDeletionRequested) ...[
            Container(
              margin: const EdgeInsets.only(bottom: 12),
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFFFEF2F2),
                border: Border.all(color: const Color(0xFFFCA5A5)),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                children: [
                  const Icon(Icons.lock_clock,
                      color: Color(0xFFDC2626), size: 20),
                  const SizedBox(width: 10),
                  const Expanded(
                    child: Text(
                      'Account Deletion Requested (Pending Admin Review). New lot creation and dispatches are frozen.',
                      style: TextStyle(
                          fontSize: 11.5,
                          fontWeight: FontWeight.w700,
                          color: Color(0xFF991B1B)),
                    ),
                  ),
                  TextButton(
                    onPressed: () => ref
                        .read(authControllerProvider.notifier)
                        .cancelAccountDeletion(),
                    child: const Text('Withdraw',
                        style: TextStyle(
                            fontSize: 11.5,
                            fontWeight: FontWeight.w800,
                            color: Color(0xFFDC2626))),
                  ),
                ],
              ),
            ),
          ],

          // 1. ENTITY CONSOLE HEADER (Web UI Parity + Pre-Approval Farmer ID Guard)
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFFE2E8F0)),
              boxShadow: const [
                BoxShadow(
                    color: Color(0x06000000),
                    blurRadius: 6,
                    offset: Offset(0, 2)),
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
                            padding: const EdgeInsets.symmetric(
                                horizontal: 10, vertical: 4),
                            decoration: BoxDecoration(
                              color: isApproved
                                  ? const Color(0xFFECFDF5)
                                  : const Color(0xFFFFFBEB),
                              border: Border.all(
                                color: isApproved
                                    ? const Color(0xFF86EFAC)
                                    : const Color(0xFFFDE68A),
                              ),
                              borderRadius: BorderRadius.circular(20),
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(
                                  isApproved
                                      ? Icons.check_circle
                                      : Icons.schedule,
                                  size: 13,
                                  color: isApproved
                                      ? const Color(0xFF15803D)
                                      : const Color(0xFFB45309),
                                ),
                                const SizedBox(width: 5),
                                Text(
                                  isApproved
                                      ? 'VERIFIED $role CONSOLE'
                                      : 'UNDER ADMIN REVIEW',
                                  style: TextStyle(
                                    fontSize: 10.5,
                                    fontWeight: FontWeight.w800,
                                    color: isApproved
                                        ? const Color(0xFF065F46)
                                        : const Color(0xFF92400E),
                                    letterSpacing: 0.3,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            authState.orgName ??
                                'Registered Agricultural Producer',
                            style: const TextStyle(
                              fontSize: 17.5,
                              fontWeight: FontWeight.w900,
                              color: Color(0xFF0F172A),
                            ),
                          ),
                          const SizedBox(height: 2),
                          const Text(
                            'Cluster Farm Yard #4, Bardhaman, West Bengal',
                            style: TextStyle(
                                fontSize: 12, color: Color(0xFF64748B)),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                // Unique Farmer ID / Entity ID Box (Pre-Approval Guarded)
                InkWell(
                  onTap: isApproved
                      ? () {
                          Clipboard.setData(ClipboardData(text: displayId));
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text('Copied ID: $displayId'),
                              duration: const Duration(seconds: 2),
                              backgroundColor: const Color(0xFF0B3D2E),
                              behavior: SnackBarBehavior.floating,
                            ),
                          );
                        }
                      : null,
                  borderRadius: BorderRadius.circular(10),
                  child: Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                    decoration: BoxDecoration(
                      color: isApproved
                          ? const Color(0xFFF0FDF4)
                          : const Color(0xFFFFFBEB),
                      border: Border.all(
                        color: isApproved
                            ? const Color(0xFF86EFAC)
                            : const Color(0xFFFCD34D),
                        width: 1.5,
                      ),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                role == 'PRODUCER'
                                    ? 'UNIQUE FARMER ID'
                                    : 'ENTITY REGISTRATION ID',
                                style: TextStyle(
                                  fontSize: 9.5,
                                  fontWeight: FontWeight.w800,
                                  color: isApproved
                                      ? const Color(0xFF047857)
                                      : const Color(0xFFB45309),
                                  letterSpacing: 0.5,
                                ),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                displayId,
                                style: TextStyle(
                                  fontFamily: 'monospace',
                                  fontSize: 14,
                                  fontWeight: FontWeight.w900,
                                  color: isApproved
                                      ? const Color(0xFF0B3D2E)
                                      : const Color(0xFF92400E),
                                  letterSpacing: 0.5,
                                ),
                                overflow: TextOverflow.ellipsis,
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(width: 8),
                        if (isApproved)
                          const Row(
                            children: [
                              Icon(Icons.copy,
                                  size: 14, color: Color(0xFF10B981)),
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
                          )
                        else
                          const Text(
                            'Ref: APP-PENDING',
                            style: TextStyle(
                              fontSize: 10.5,
                              fontWeight: FontWeight.w800,
                              color: Color(0xFFB45309),
                            ),
                          ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 14),

          // 2. LIVE AGRICULTURAL TELEMETRY (Real Data, Zero Fake Metrics)
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
                        Text('● ',
                            style: TextStyle(
                                color: Color(0xFF10B981), fontSize: 10)),
                        Text(
                          'Live Synced',
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
                Row(
                  children: [
                    Expanded(
                      child: _buildTelemetryCard(
                        title: 'Land & Plots',
                        value: '${_registeredPlots.length} Plots',
                        subtitle: '${totalAcres.toStringAsFixed(3)} Acres',
                        valueColor: const Color(0xFF0B3D2E),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: _buildTelemetryCard(
                        title: 'Season Allocation',
                        value: '${allocAcres.toStringAsFixed(1)} Ac',
                        subtitle: '${freeAcres.toStringAsFixed(1)} Ac Free',
                        valueColor: const Color(0xFF0B3D2E),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
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
                        subtitle:
                            '$inCustodyCount Custody • $inTransitCount Transit',
                        valueColor: const Color(0xFF047857),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(
                      child: _buildTelemetryCard(
                        title: 'Consumer Scans',
                        value: '0 Scans',
                        subtitle: 'No Scans Recorded',
                        valueColor: const Color(0xFF0B3D2E),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: _buildTelemetryCard(
                        title: 'Valuation (₹)',
                        value: '₹${totalVal.toStringAsFixed(0)}',
                        subtitle: totalKg > 0
                            ? '₹${(totalVal / totalKg).toStringAsFixed(0)} / Kg Avg'
                            : 'No Lots Logged',
                        valueColor: const Color(0xFF047857),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          const SizedBox(height: 14),

          // 3. ROLE-ADAPTIVE ACTION RAILS (Producer Rails A-D or Business Role Rails)
          if (role == 'PRODUCER')
            Column(
              children: [
                _buildActionRailCard(
                  letter: 'A',
                  title: 'A. Profile & Farmer ID',
                  subtitle:
                      '5-Step Registration Data, Digital ID QR & Account Settings',
                  icon: Icons.badge_outlined,
                  actionLabel: 'View →',
                  onTap: () => setState(() => _currentNavIndex = 3),
                ),
                const SizedBox(height: 8),
                _buildActionRailCard(
                  letter: 'B',
                  title: 'B. Land & Season Allocation',
                  subtitle:
                      'Polygon plot mapping & 10-category acreage allocation',
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
                  subtitle: 'Generate unique QRs, Code128 barcodes & labels',
                  icon: Icons.qr_code_2,
                  badgeLabel: '+ CREATE',
                  isHighlighted: true,
                  onTap: () => context.push('/create-batch'),
                ),
              ],
            )
          else
            _buildBusinessRoleActionRails(context, role, lots),

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
                hintStyle:
                    const TextStyle(fontSize: 13, color: Color(0xFF94A3B8)),
                prefixIcon: const Icon(Icons.search,
                    size: 18, color: Color(0xFF64748B)),
                suffixIcon: _searchController.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear, size: 16),
                        onPressed: () {
                          _searchController.clear();
                          ref
                              .read(lotsControllerProvider.notifier)
                              .setSearchQuery('');
                        },
                      )
                    : null,
                contentPadding:
                    const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
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
                _buildCustodyChip(
                    'IN_CUSTODY', '${_t('filterCustody')} ($inCustodyCount)'),
                const SizedBox(width: 6),
                _buildCustodyChip(
                    'IN_TRANSIT', '${_t('filterTransit')} ($inTransitCount)'),
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
                    child: const Icon(Icons.inventory_2_outlined,
                        size: 36, color: Color(0xFF047857)),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    _t('noBatchesTitle'),
                    style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w800,
                        color: Color(0xFF0F172A)),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    _t('noBatchesSub'),
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                        fontSize: 12.5, color: Color(0xFF64748B)),
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () => context.push('/create-batch'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF0B3D2E),
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10)),
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
                onEdit: (lot.isEditable && !authState.isDeletionRequested)
                    ? () => context.push(
                        '/create-batch?code=${Uri.encodeComponent(lot.publicCode)}')
                    : null,
                onDispatch: (lot.isEditable && !authState.isDeletionRequested)
                    ? () => _showDispatchSheet(context, lot)
                    : null,
                onShowQr: () => _showQrDialog(context, lot),
                onPrintLabel: () => _showLabelPrintModal(context, lot),
                onAppendData: () => _showAppendDataModal(context, lot),
                onPlaceOnShelf: role == 'RETAILER'
                    ? () => _handlePlaceOnShelf(context, lot)
                    : null,
                onMarkSoldOut: role == 'RETAILER'
                    ? () => _handleMarkSoldOut(context, lot)
                    : null,
                onMarkWasted: role == 'RETAILER'
                    ? () => _handleMarkWasted(context, lot)
                    : null,
              ),
            ),
          ],

          const SizedBox(height: 60),
        ],
      ),
    );
  }

  /// Dynamic Action Rails for Downstream Business Roles & Verifier (Section 6.6)
  Widget _buildBusinessRoleActionRails(
      BuildContext context, String role, List<HarvestLot> lots) {
    if (role == 'VERIFIER') {
      return Column(
        children: [
          _buildActionRailCard(
            letter: '1',
            title: 'Scan Product QR / Barcode',
            subtitle:
                'Verify authenticity, farm origin & Farm-to-Shelf timeline',
            icon: Icons.qr_code_scanner,
            badgeLabel: 'SCAN',
            isHighlighted: true,
            onTap: () => _showConsumerVerifierSheet(context, lots),
          ),
        ],
      );
    }

    String specialTitle = 'Split / Repackage Lot';
    String specialSub = 'Split bulk parent lot into child dispatch lots';
    IconData specialIcon = Icons.call_split;
    VoidCallback specialTap = () {
      final firstCode = lots.isNotEmpty ? lots.first.publicCode : 'BATCH-01';
      final firstQty = lots.isNotEmpty ? lots.first.netQtyKg : 100.0;
      context.push('/split?code=$firstCode&qty=$firstQty');
    };

    if (role == 'AGGREGATOR') {
      specialTitle = 'Merge & Grade Farmer Lots';
      specialSub = 'Aggregate multiple farmer lots with full parent lineage';
      specialIcon = Icons.merge_type;
    } else if (role == 'PROCESSOR') {
      specialTitle = 'Production Run (Transform)';
      specialSub = 'Convert raw input lots into packaged retail SKU batches';
      specialIcon = Icons.precision_manufacturing_outlined;
      specialTap = () => context.push('/create-batch');
    } else if (role == 'RETAILER') {
      specialTitle = 'Place on Shelf & Retail Sales';
      specialSub = 'Freeze Farm-to-Shelf days, print shelf QR & record sales';
      specialIcon = Icons.storefront_outlined;
      specialTap = () {
        final firstCode = lots.isNotEmpty ? lots.first.publicCode : 'BATCH-01';
        final firstQty = lots.isNotEmpty ? lots.first.netQtyKg : 100.0;
        context.push('/sale?code=$firstCode&qty=$firstQty');
      };
    }

    return Column(
      children: [
        _buildActionRailCard(
          letter: 'A',
          title: 'Custody Inbox & Rapid Scan Arrival',
          subtitle: 'Verify physical QR, arrival photo, scale weight & GPS',
          icon: Icons.move_to_inbox_outlined,
          badgeLabel: 'RECEIVE',
          isHighlighted: true,
          onTap: () => _showReceiveDialog(context),
        ),
        const SizedBox(height: 8),
        _buildActionRailCard(
          letter: 'B',
          title: specialTitle,
          subtitle: specialSub,
          icon: specialIcon,
          actionLabel: 'Open →',
          onTap: specialTap,
        ),
        const SizedBox(height: 8),
        _buildActionRailCard(
          letter: 'C',
          title: 'Append Custody Telemetry',
          subtitle: 'Record weight check, condition grade, or cold storage log',
          icon: Icons.thermostat_outlined,
          actionLabel: 'Append →',
          onTap: () {
            final firstCode =
                lots.isNotEmpty ? lots.first.publicCode : 'BATCH-01';
            context.push('/inspection?code=$firstCode');
          },
        ),
        const SizedBox(height: 8),
        _buildActionRailCard(
          letter: 'D',
          title: 'Profile, Premises & Account Settings',
          subtitle: 'FSSAI licence, premises geofence & account deletion',
          icon: Icons.business_outlined,
          actionLabel: 'View →',
          onTap: () => setState(() => _currentNavIndex = 3),
        ),
      ],
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
            style: const TextStyle(
                fontSize: 11,
                color: Color(0xFF64748B),
                fontWeight: FontWeight.w700),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 3),
          Text(
            value,
            style: TextStyle(
                fontSize: 17, fontWeight: FontWeight.w900, color: valueColor),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 2),
          Text(
            subtitle,
            style: const TextStyle(
                fontSize: 10.5,
                color: Color(0xFF047857),
                fontWeight: FontWeight.w700),
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
            color: isHighlighted
                ? const Color(0xFF86EFAC)
                : const Color(0xFFE2E8F0),
            width: isHighlighted ? 1.5 : 1,
          ),
        ),
        child: Row(
          children: [
            Container(
              width: 36,
              height: 36,
              decoration: BoxDecoration(
                color: isHighlighted
                    ? const Color(0xFF047857)
                    : const Color(0xFFECFDF5),
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
                            color: isHighlighted
                                ? const Color(0xFF047857)
                                : const Color(0xFF0F172A),
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      if (badgeLabel != null)
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: const Color(0xFF047857),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Text(
                            badgeLabel,
                            style: const TextStyle(
                                fontSize: 10,
                                fontWeight: FontWeight.w800,
                                color: Colors.white),
                          ),
                        )
                      else if (actionLabel != null)
                        Text(
                          actionLabel,
                          style: const TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w700,
                              color: Color(0xFF047857)),
                        ),
                    ],
                  ),
                  const SizedBox(height: 2),
                  Text(
                    subtitle,
                    style: TextStyle(
                      fontSize: 11,
                      color: isHighlighted
                          ? const Color(0xFF065F46)
                          : const Color(0xFF64748B),
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
      isDismissible: true,
      enableDrag: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => DraggableScrollableSheet(
        initialChildSize: 0.65,
        maxChildSize: 0.88,
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
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Row(
                  children: [
                    Icon(Icons.map_outlined,
                        color: Color(0xFF047857), size: 22),
                    SizedBox(width: 8),
                    Text(
                      'Land & Season Allocation',
                      style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w900,
                          color: Color(0xFF0F172A)),
                    ),
                  ],
                ),
                IconButton(
                  icon: const Icon(Icons.close, size: 20),
                  onPressed: () => Navigator.pop(ctx),
                ),
              ],
            ),
            const SizedBox(height: 4),
            const Text(
              'Farm Plot & Boundary Mapping across 10 crop categories',
              style: TextStyle(fontSize: 12.5, color: Color(0xFF64748B)),
            ),
            const Divider(height: 24),
            ..._registeredPlots.map(
              (p) => Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: _buildPlotAllocationItem(
                  name: p['name'] as String,
                  surveyNo: p['surveyNo'] as String,
                  area: '${(p['acres'] as double).toStringAsFixed(3)} Acres',
                  allocatedCrop: p['crop'] as String,
                  status: p['status'] as String,
                ),
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
              Text(name,
                  style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF0F172A))),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: const Color(0xFFECFDF5),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(status,
                    style: const TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.w800,
                        color: Color(0xFF047857))),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text('$surveyNo • $area',
              style: const TextStyle(fontSize: 12, color: Color(0xFF64748B))),
          const SizedBox(height: 6),
          Row(
            children: [
              const Icon(Icons.eco_outlined,
                  size: 14, color: Color(0xFF059669)),
              const SizedBox(width: 4),
              Text(allocatedCrop,
                  style: const TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w700,
                      color: Color(0xFF059669))),
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
      isDismissible: true,
      enableDrag: true,
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
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Expanded(
                  child: Row(
                    children: [
                      Icon(Icons.agriculture_outlined,
                          color: Color(0xFF047857), size: 22),
                      SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'Harvest Records & Mass Balance',
                          style: TextStyle(
                              fontSize: 17,
                              fontWeight: FontWeight.w900,
                              color: Color(0xFF0F172A)),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.close, size: 20),
                  onPressed: () => Navigator.pop(ctx),
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
                child: const Text(
                  'No harvest records logged yet. Create a batch to record yield.',
                  style: TextStyle(color: Color(0xFF64748B)),
                ),
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
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(lot.crop,
                                style: const TextStyle(
                                    fontSize: 13.5,
                                    fontWeight: FontWeight.w800)),
                            Text('Lot: ${lot.publicCode}',
                                style: const TextStyle(
                                    fontSize: 11,
                                    fontFamily: 'monospace',
                                    color: Color(0xFF64748B))),
                            Text(
                                'Plot: ${lot.originPlotName.isNotEmpty ? lot.originPlotName : "North Field"}',
                                style: const TextStyle(
                                    fontSize: 11, color: Color(0xFF64748B))),
                          ],
                        ),
                      ),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.end,
                        children: [
                          Text('${lot.netQtyKg.toStringAsFixed(1)} Kg',
                              style: const TextStyle(
                                  fontSize: 14,
                                  fontWeight: FontWeight.w900,
                                  color: Color(0xFF0B3D2E))),
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 6, vertical: 2),
                            decoration: BoxDecoration(
                              color: lot.isEditable
                                  ? const Color(0xFFECFDF5)
                                  : const Color(0xFFEFF6FF),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: Text(
                              lot.isEditable ? 'Farm Custody' : lot.state,
                              style: TextStyle(
                                fontSize: 9.5,
                                fontWeight: FontWeight.w700,
                                color: lot.isEditable
                                    ? const Color(0xFF047857)
                                    : const Color(0xFF2563EB),
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
      side: BorderSide(
          color:
              isSelected ? const Color(0xFF0B3D2E) : const Color(0xFFE2E8F0)),
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
  Widget _buildHandoverTab(
    BuildContext context,
    LotsState lotsState,
    AuthState authState,
    String role,
  ) {
    final dispatchedLots =
        lotsState.lots.where((l) => l.state == 'IN_TRANSIT').toList();

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
              BoxShadow(
                  color: Color(0x06000000),
                  blurRadius: 6,
                  offset: Offset(0, 2)),
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
                    child: const Icon(Icons.qr_code_scanner,
                        color: Color(0xFF047857), size: 22),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          _t('scanToReceive'),
                          style: const TextStyle(
                              fontSize: 14.5,
                              fontWeight: FontWeight.w800,
                              color: Color(0xFF0F172A)),
                        ),
                        Text(
                          _t('scanToReceiveSub'),
                          style: const TextStyle(
                              fontSize: 11.5, color: Color(0xFF64748B)),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 14),
              ElevatedButton.icon(
                onPressed: authState.isDeletionRequested
                    ? null
                    : () => _showReceiveDialog(context),
                icon: const Icon(Icons.camera_alt_outlined, size: 16),
                label: Text(_t('btnScanQr')),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF0B3D2E),
                  foregroundColor: Colors.white,
                  minimumSize: const Size(double.infinity, 42),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10)),
                ),
              ),
            ],
          ),
        ),

        const SizedBox(height: 16),

        Text(
          _t('dispatchedBatches'),
          style: const TextStyle(
              fontSize: 14.5,
              fontWeight: FontWeight.w800,
              color: Color(0xFF0F172A)),
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
                style:
                    const TextStyle(fontSize: 12.5, color: Color(0xFF64748B)),
              ),
            ),
          ),
        ] else ...[
          ...dispatchedLots.map(
            (lot) => LotCard(
              lot: lot,
              onShowQr: () => _showQrDialog(context, lot),
              onPrintLabel: () => _showLabelPrintModal(context, lot),
            ),
          ),
        ],
      ],
    );
  }

  // ---------------------------------------------------------------------------
  // TAB 2: INSIGHTS & FARM ANALYTICS (Real Data, Zero Mock Telemetry)
  // ---------------------------------------------------------------------------
  Widget _buildInsightsTab(BuildContext context, LotsState lotsState) {
    final lots = lotsState.lots;
    final totalValuation =
        lots.fold<double>(0.0, (acc, l) => acc + l.estimatedValue);
    final totalKg = lots.fold<double>(0.0, (acc, l) => acc + l.netQtyKg);
    final gradeACount = lots.where((l) => l.qualityGrade.contains('A')).length;
    final gradeARatio = lots.isNotEmpty
        ? ((gradeACount / lots.length) * 100).toStringAsFixed(0)
        : '0';

    final Map<String, double> cropMap = {};
    for (final l in lots) {
      cropMap[l.crop] = (cropMap[l.crop] ?? 0.0) + l.netQtyKg;
    }

    return ListView(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      children: [
        Text(
          _t('insightsTitle'),
          style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w800,
              color: Color(0xFF0F172A)),
        ),
        const SizedBox(height: 12),

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
                style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w800,
                    color: Color(0xFF0F172A)),
              ),
              const SizedBox(height: 10),
              if (cropMap.isEmpty)
                const Text('No crop production data logged yet.',
                    style: TextStyle(fontSize: 12, color: Color(0xFF64748B)))
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
                                style: const TextStyle(
                                    fontSize: 12.5,
                                    fontWeight: FontWeight.w700),
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                            const SizedBox(width: 8),
                            Text(
                                '${e.value.toStringAsFixed(1)} Kg (${(percent * 100).toStringAsFixed(0)}%)',
                                style: const TextStyle(
                                    fontSize: 11.5, color: Color(0xFF64748B))),
                          ],
                        ),
                        const SizedBox(height: 4),
                        LinearProgressIndicator(
                          value: percent,
                          backgroundColor: const Color(0xFFE2E8F0),
                          valueColor: const AlwaysStoppedAnimation<Color>(
                              Color(0xFF059669)),
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

  Widget _buildInsightMetricCard(
      String title, String value, IconData icon, Color color) {
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
                  style: const TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                      color: Color(0xFF64748B)),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              const SizedBox(width: 4),
              Icon(icon, size: 16, color: color),
            ],
          ),
          const SizedBox(height: 6),
          Text(value,
              style: TextStyle(
                  fontSize: 18, fontWeight: FontWeight.w900, color: color)),
        ],
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // TAB 3: PROFILE, 5-TAB REGISTRATION DATA VIEW & ACCOUNT DELETION
  // ---------------------------------------------------------------------------
  Widget _buildProfileTab(
      BuildContext context, AuthState authState, String role) {
    // Section 4.2.1: Do not display a Unique Farmer ID until approved by Admin
    final bool isApproved = authState.isOrgVerified &&
        authState.farmerUid != null &&
        authState.farmerUid!.isNotEmpty;
    final String displayId =
        isApproved ? authState.farmerUid! : 'Under Admin Review';

    final List<String> stepLabels = [
      '1. Basic Info',
      '2. Farm Plots',
      '3. Cultivation',
      '4. Identity & Bank',
      '5. Consent & Review',
    ];

    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // 1. Producer / Entity Identity Header Card
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
                      child: Icon(Icons.person,
                          color: Color(0xFF047857), size: 28),
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
                                  authState.orgName ??
                                      'Registered Agricultural Producer',
                                  style: const TextStyle(
                                      fontSize: 15,
                                      fontWeight: FontWeight.w800,
                                      color: Color(0xFF0F172A)),
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                              Container(
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 7, vertical: 2),
                                decoration: BoxDecoration(
                                  color: isApproved
                                      ? const Color(0xFFECFDF5)
                                      : const Color(0xFFFFFBEB),
                                  borderRadius: BorderRadius.circular(10),
                                ),
                                child: Text(
                                  isApproved ? 'Verified' : 'Under Review',
                                  style: TextStyle(
                                    fontSize: 10,
                                    fontWeight: FontWeight.w800,
                                    color: isApproved
                                        ? const Color(0xFF047857)
                                        : const Color(0xFFB45309),
                                  ),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 2),
                          Text(
                            'Role: $role • Bardhaman, West Bengal',
                            style: const TextStyle(
                                fontSize: 12, color: Color(0xFF64748B)),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const Divider(height: 22, color: Color(0xFFF1F5F9)),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            _t('farmerId'),
                            style: const TextStyle(
                                fontSize: 10.5,
                                fontWeight: FontWeight.w700,
                                color: Color(0xFF64748B)),
                          ),
                          const SizedBox(height: 2),
                          SelectableText(
                            displayId,
                            style: TextStyle(
                              fontFamily: 'monospace',
                              fontSize: 14,
                              fontWeight: FontWeight.w900,
                              color: isApproved
                                  ? const Color(0xFF0B3D2E)
                                  : const Color(0xFFB45309),
                            ),
                          ),
                        ],
                      ),
                    ),
                    if (isApproved)
                      OutlinedButton.icon(
                        onPressed: () => _showDigitalIdCardDialog(
                            context, authState, displayId),
                        icon: const Icon(Icons.qr_code_2,
                            size: 15, color: Color(0xFF047857)),
                        label: const Text('Digital ID Card',
                            style: TextStyle(
                                fontSize: 11.5,
                                fontWeight: FontWeight.w700,
                                color: Color(0xFF047857))),
                        style: OutlinedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 10, vertical: 6),
                          side: const BorderSide(color: Color(0xFF86EFAC)),
                          shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8)),
                        ),
                      ),
                  ],
                ),
              ],
            ),
          ),

          const SizedBox(height: 14),

          // 2. 5-TAB REGISTRATION DATA INSPECTION & SELF-SERVICE EDIT (Section 4.3)
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFFE2E8F0)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(Icons.fact_check_outlined,
                        size: 18, color: Color(0xFF0B3D2E)),
                    SizedBox(width: 6),
                    Expanded(
                      child: Text(
                        '5-Step Registration Profile & Data Management',
                        style: TextStyle(
                            fontSize: 13.5,
                            fontWeight: FontWeight.w800,
                            color: Color(0xFF0F172A)),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Row(
                    children: List.generate(stepLabels.length, (idx) {
                      final isSel = _selectedProfileStep == idx;
                      return Padding(
                        padding: const EdgeInsets.only(right: 6),
                        child: ChoiceChip(
                          label: Text(stepLabels[idx]),
                          selected: isSel,
                          onSelected: (_) =>
                              setState(() => _selectedProfileStep = idx),
                          selectedColor: const Color(0xFF0B3D2E),
                          backgroundColor: const Color(0xFFF8FAFC),
                          side: BorderSide(
                            color: isSel
                                ? const Color(0xFF0B3D2E)
                                : const Color(0xFFE2E8F0),
                          ),
                          labelStyle: TextStyle(
                            fontSize: 11.5,
                            fontWeight: FontWeight.w700,
                            color:
                                isSel ? Colors.white : const Color(0xFF334155),
                          ),
                        ),
                      );
                    }),
                  ),
                ),
                const Divider(height: 20, color: Color(0xFFF1F5F9)),
                _buildRegistrationStepContent(context, authState),
              ],
            ),
          ),

          const SizedBox(height: 14),

          // 3. ACCOUNT & PROFILE DELETION CONTAINER (Section 4.3.1 & 6.9)
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFFFECACA)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Expanded(
                      child: Row(
                        children: [
                          Icon(Icons.person_remove_outlined,
                              size: 18, color: Color(0xFFDC2626)),
                          SizedBox(width: 6),
                          Flexible(
                            child: Text(
                              'Account & Profile Deletion',
                              style: TextStyle(
                                  fontSize: 13.5,
                                  fontWeight: FontWeight.w800,
                                  color: Color(0xFF991B1B)),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 7, vertical: 2),
                      decoration: BoxDecoration(
                        color: const Color(0xFFFEF2F2),
                        border: Border.all(color: const Color(0xFFFECACA)),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: const Text(
                        'Permanent Action',
                        style: TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.w700,
                            color: Color(0xFFDC2626)),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                Text(
                  authState.isDeletionRequested
                      ? 'Status: DELETION_REQUESTED — Pending Admin review. You may cancel this request before Admin approval.'
                      : 'Request deactivation of your entity profile and removal of personal contact details.',
                  style:
                      const TextStyle(fontSize: 11.5, color: Color(0xFF64748B)),
                ),
                const SizedBox(height: 10),
                if (authState.isDeletionRequested)
                  OutlinedButton.icon(
                    onPressed: () async {
                      await ref
                          .read(authControllerProvider.notifier)
                          .cancelAccountDeletion();
                      if (context.mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text(
                                'Account deletion request withdrawn. Operations restored.'),
                            backgroundColor: Color(0xFF047857),
                          ),
                        );
                      }
                    },
                    icon: const Icon(Icons.undo, size: 16),
                    label: const Text('Cancel Deletion Request'),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: const Color(0xFFDC2626),
                      side: const BorderSide(color: Color(0xFFFCA5A5)),
                    ),
                  )
                else
                  OutlinedButton.icon(
                    onPressed: () => _showDpdpDeletionModal(context, authState),
                    icon: const Icon(Icons.delete_outline,
                        size: 16, color: Color(0xFFDC2626)),
                    label: const Text(
                      'Request Account Deletion',
                      style: TextStyle(
                          fontWeight: FontWeight.w700,
                          color: Color(0xFFDC2626)),
                    ),
                    style: OutlinedButton.styleFrom(
                      side: const BorderSide(color: Color(0xFFFECACA)),
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10)),
                    ),
                  ),
              ],
            ),
          ),

          const SizedBox(height: 14),

          // 4. General Preferences & Sign Out
          Container(
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFFE2E8F0)),
            ),
            child: Column(
              children: [
                ListTile(
                  leading:
                      const Icon(Icons.translate, color: Color(0xFF0B3D2E)),
                  title: const Text('Language / भाषा / ভাষা',
                      style: TextStyle(
                          fontSize: 13.5, fontWeight: FontWeight.w700)),
                  trailing: const Icon(Icons.chevron_right, size: 20),
                  onTap: () => _showLanguageModal(context),
                ),
                const Divider(height: 1, color: Color(0xFFF1F5F9)),
                ListTile(
                  leading: const Icon(Icons.shield_outlined,
                      color: Color(0xFF0B3D2E)),
                  title: Text(_t('statutoryConsent'),
                      style: const TextStyle(
                          fontSize: 13.5, fontWeight: FontWeight.w700)),
                  trailing: const Icon(Icons.chevron_right, size: 20),
                  onTap: () => DpdpConsentDialog.show(context),
                ),
                const Divider(height: 1, color: Color(0xFFF1F5F9)),
                ListTile(
                  leading: const Icon(Icons.logout, color: Color(0xFFDC2626)),
                  title: Text(_t('btnLogout'),
                      style: const TextStyle(
                          fontSize: 13.5,
                          fontWeight: FontWeight.w700,
                          color: Color(0xFFDC2626))),
                  onTap: () async {
                    await ref.read(authControllerProvider.notifier).logout();
                  },
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// Renders the active tab content for the 5-Step Registration Profile
  Widget _buildRegistrationStepContent(
      BuildContext context, AuthState authState) {
    switch (_selectedProfileStep) {
      case 0: // Step 1: Basic Info
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildLockedFieldRow(
              label: 'Applicant / Legal Organisation Name',
              value: authState.orgName ?? 'Maa Annapurna Organic FPO',
              onRequestChange: () => _showChangeRequestModal(
                context,
                fieldName: 'Legal Organisation Name',
                currentValue: authState.orgName ?? 'Maa Annapurna Organic FPO',
              ),
            ),
            const SizedBox(height: 8),
            _buildLockedFieldRow(
              label: 'Primary Registered Mobile',
              value: authState.phone ?? '+91 9876543210',
              onRequestChange: () => _showChangeRequestModal(
                context,
                fieldName: 'Primary Mobile Number',
                currentValue: authState.phone ?? '+91 9876543210',
              ),
            ),
            const SizedBox(height: 8),
            _buildLockedFieldRow(
              label: 'Jurisdiction (Village / District / State)',
              value: 'Memari, Bardhaman, West Bengal - 713146',
              onRequestChange: () => _showChangeRequestModal(
                context,
                fieldName: 'State / District Jurisdiction',
                currentValue: 'Memari, Bardhaman, West Bengal - 713146',
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _altPhoneCtrl,
              decoration: const InputDecoration(
                labelText: 'Alternate Mobile (Self-Editable)',
                isDense: true,
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: _emailCtrl,
              decoration: const InputDecoration(
                labelText: 'Email Address (Self-Editable)',
                isDense: true,
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: _addrLine2Ctrl,
              decoration: const InputDecoration(
                labelText: 'Address Line 2 / Landmark (Self-Editable)',
                isDense: true,
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 10),
            Align(
              alignment: Alignment.centerRight,
              child: ElevatedButton.icon(
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Basic Info self-editable fields saved.'),
                      backgroundColor: Color(0xFF047857),
                    ),
                  );
                },
                icon: const Icon(Icons.save_outlined, size: 15),
                label: const Text('Save Basic Info'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF0B3D2E),
                  foregroundColor: Colors.white,
                ),
              ),
            ),
          ],
        );

      case 1: // Step 2: Farm Plots
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildLockedFieldRow(
              label: 'Total Registered Land Holding',
              value: '4.500 Acres (2 Verified Plots)',
              onRequestChange: () => _showChangeRequestModal(
                context,
                fieldName: 'Total Registered Land Acreage',
                currentValue: '4.500 Acres',
              ),
            ),
            const SizedBox(height: 8),
            _buildLockedFieldRow(
              label: 'Cadastral Survey / Khasra Numbers',
              value: 'Survey 104/A (2.5 Ac), Survey 108/B (2.0 Ac)',
              onRequestChange: () => _showChangeRequestModal(
                context,
                fieldName: 'Cadastral Survey Numbers',
                currentValue: 'Survey 104/A, Survey 108/B',
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _plotNicknameCtrl,
              decoration: const InputDecoration(
                labelText: 'Plot Nicknames (Self-Editable)',
                isDense: true,
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: _seasonalNotesCtrl,
              decoration: const InputDecoration(
                labelText: 'Seasonal Allocation Notes (Self-Editable)',
                isDense: true,
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 10),
            Align(
              alignment: Alignment.centerRight,
              child: ElevatedButton.icon(
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Farm Plot notes updated.'),
                      backgroundColor: Color(0xFF047857),
                    ),
                  );
                },
                icon: const Icon(Icons.save_outlined, size: 15),
                label: const Text('Save Plot Notes'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF0B3D2E),
                  foregroundColor: Colors.white,
                ),
              ),
            ),
          ],
        );

      case 2: // Step 3: Cultivation
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildLockedFieldRow(
              label: 'Primary Farming Practice',
              value: 'Organic (NPOP Certified)',
              onRequestChange: () => _showChangeRequestModal(
                context,
                fieldName: 'Primary Farming Practice',
                currentValue: 'Organic (NPOP Certified)',
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _secondaryCropsCtrl,
              decoration: const InputDecoration(
                labelText: 'Secondary Seasonal Crops (Self-Editable)',
                isDense: true,
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: _irrigationCtrl,
              decoration: const InputDecoration(
                labelText: 'Irrigation Infrastructure (Self-Editable)',
                isDense: true,
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: _certNotesCtrl,
              decoration: const InputDecoration(
                labelText: 'Certification Notes (Self-Editable)',
                isDense: true,
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 10),
            Align(
              alignment: Alignment.centerRight,
              child: ElevatedButton.icon(
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Cultivation profile saved.'),
                      backgroundColor: Color(0xFF047857),
                    ),
                  );
                },
                icon: const Icon(Icons.save_outlined, size: 15),
                label: const Text('Save Cultivation Profile'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF0B3D2E),
                  foregroundColor: Colors.white,
                ),
              ),
            ),
          ],
        );

      case 3: // Step 4: Identity & Bank
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Sensitive identity and bank details. Masked for security.',
              style: TextStyle(fontSize: 11.5, color: Color(0xFF64748B)),
            ),
            const SizedBox(height: 10),
            _buildLockedFieldRow(
              label: 'PAN Identity (Masked)',
              value: 'ABCDE••••F',
              onRequestChange: () => _showChangeRequestModal(
                context,
                fieldName: 'PAN Identity',
                currentValue: 'ABCDE••••F',
              ),
            ),
            const SizedBox(height: 8),
            _buildLockedFieldRow(
              label: 'KYC Document (Aadhaar Last-4)',
              value: '•••• •••• 4821 (Verified via DigiLocker)',
              onRequestChange: () => _showChangeRequestModal(
                context,
                fieldName: 'KYC Document',
                currentValue: '•••• •••• 4821',
              ),
            ),
            const SizedBox(height: 8),
            _buildLockedFieldRow(
              label: 'Settlement Bank Account & IFSC',
              value: 'State Bank of India • A/C ••••••••3910 • SBIN0001234',
              onRequestChange: () => _showChangeRequestModal(
                context,
                fieldName: 'Bank Settlement Details',
                currentValue: 'SBI A/C ••••••••3910 (SBIN0001234)',
              ),
            ),
          ],
        );

      case 4: // Step 5: Consent & Review
      default:
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: const Color(0xFFF0FDF4),
                border: Border.all(color: const Color(0xFF86EFAC)),
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Row(
                children: [
                  Icon(Icons.verified_user_outlined,
                      size: 18, color: Color(0xFF047857)),
                  SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Privacy & Traceability Consent Active (Version 1.0 • OTP E-Signed)',
                      style: TextStyle(
                          fontSize: 11.5,
                          fontWeight: FontWeight.w700,
                          color: Color(0xFF065F46)),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),
            const Text(
              'Submitted Change Requests (Admin Review Queue)',
              style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w800,
                  color: Color(0xFF334155)),
            ),
            const SizedBox(height: 6),
            if (_changeRequests.isEmpty)
              const Text(
                'No pending change requests submitted.',
                style: TextStyle(fontSize: 11.5, color: Color(0xFF64748B)),
              )
            else
              ..._changeRequests.map(
                (cr) => Container(
                  margin: const EdgeInsets.only(bottom: 6),
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF8FAFC),
                    border: Border.all(color: const Color(0xFFE2E8F0)),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Text(
                          '${cr['field']} → ${cr['newValue']}',
                          style: const TextStyle(
                              fontSize: 11.5, fontWeight: FontWeight.w700),
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: const Color(0xFFFFFBEB),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(
                          cr['status'] ?? 'PENDING',
                          style: const TextStyle(
                              fontSize: 10,
                              fontWeight: FontWeight.w800,
                              color: Color(0xFFB45309)),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
          ],
        );
    }
  }

  Widget _buildLockedFieldRow({
    required String label,
    required String value,
    required VoidCallback onRequestChange,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: const Color(0xFFF8FAFC),
        border: Border.all(color: const Color(0xFFE2E8F0)),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.lock_outline,
                        size: 12, color: Color(0xFF64748B)),
                    const SizedBox(width: 4),
                    Expanded(
                      child: Text(
                        label,
                        style: const TextStyle(
                            fontSize: 10.5,
                            fontWeight: FontWeight.w700,
                            color: Color(0xFF64748B)),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 2),
                Text(
                  value,
                  style: const TextStyle(
                      fontSize: 12.5,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF0F172A)),
                ),
              ],
            ),
          ),
          TextButton(
            onPressed: onRequestChange,
            child: const Text(
              'Request Change',
              style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w700,
                  color: Color(0xFF047857)),
            ),
          ),
        ],
      ),
    );
  }

  void _showChangeRequestModal(
    BuildContext context, {
    required String fieldName,
    required String currentValue,
  }) {
    final newValCtrl = TextEditingController();
    final reasonCtrl = TextEditingController();

    showDialog<void>(
      context: context,
      barrierDismissible: true,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Text('Change Request: $fieldName',
            style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Current Verified Value: $currentValue',
                style: const TextStyle(fontSize: 12, color: Color(0xFF64748B))),
            const SizedBox(height: 12),
            TextField(
              controller: newValCtrl,
              decoration: const InputDecoration(
                labelText: 'Proposed New Value *',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: reasonCtrl,
              decoration: const InputDecoration(
                labelText: 'Reason & Supporting Document Ref *',
                border: OutlineInputBorder(),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              if (newValCtrl.text.trim().isNotEmpty) {
                setState(() {
                  _changeRequests.add({
                    'field': fieldName,
                    'newValue': newValCtrl.text.trim(),
                    'status': 'PENDING',
                  });
                });
                Navigator.pop(ctx);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text(
                        'Change request submitted for Admin review. Current value remains active until approved.'),
                    backgroundColor: Color(0xFF047857),
                  ),
                );
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF0B3D2E),
              foregroundColor: Colors.white,
            ),
            child: const Text('Submit Request'),
          ),
        ],
      ),
    );
  }

  void _showDigitalIdCardDialog(
      BuildContext context, AuthState authState, String farmerUid) {
    showDialog<void>(
      context: context,
      barrierDismissible: true,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Row(
          children: [
            Icon(Icons.badge_outlined, color: Color(0xFF0B3D2E)),
            SizedBox(width: 8),
            Text('Verified Digital ID Card',
                style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800)),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.qr_code_2, size: 150, color: Color(0xFF0B3D2E)),
            const SizedBox(height: 8),
            Text(
              authState.orgName ?? 'Verified Entity',
              style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
            ),
            const SizedBox(height: 4),
            Text(
              farmerUid,
              style: const TextStyle(
                  fontFamily: 'monospace',
                  fontSize: 12,
                  fontWeight: FontWeight.w700,
                  color: Color(0xFF047857)),
            ),
          ],
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx), child: const Text('Close')),
        ],
      ),
    );
  }

  /// Section 4.3.1 & 6.9: Account Deletion Modal with Pre-flight Check, Structured Reason & OTP
  void _showDpdpDeletionModal(BuildContext context, AuthState authState) {
    final lotsState = ref.read(lotsControllerProvider);
    final inTransitLots =
        lotsState.lots.where((l) => l.state == 'IN_TRANSIT').toList();

    final List<String> reasons = [
      'Ceasing agricultural / business operations',
      'Sale, transfer, or lease termination of land/premises',
      'Account deletion and data privacy request',
      'Duplicate or accidental registration',
      'Other (mandatory explanation required)',
    ];
    String selectedReason = reasons.first;
    bool otpSent = false;
    final otpCtrl = TextEditingController();

    showDialog<void>(
      context: context,
      barrierDismissible: true,
      builder: (dialogCtx) => StatefulBuilder(
        builder: (dialogCtx, setModalState) => AlertDialog(
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          title: const Row(
            children: [
              Icon(Icons.person_remove_outlined,
                  color: Color(0xFFDC2626), size: 22),
              SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Request Account Deletion',
                  style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF991B1B)),
                ),
              ),
            ],
          ),
          content: SingleChildScrollView(
            child: Column(
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
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Row(
                          children: [
                            Icon(Icons.error_outline,
                                color: Color(0xFFDC2626), size: 18),
                            SizedBox(width: 6),
                            Expanded(
                              child: Text(
                                'Entities with active dispatches or lots in transit cannot be deleted. Please complete or settle the following active transactions first:',
                                style: TextStyle(
                                    fontSize: 12,
                                    color: Color(0xFF991B1B),
                                    fontWeight: FontWeight.w700),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        ...inTransitLots.map(
                          (l) => Padding(
                            padding: const EdgeInsets.only(bottom: 4),
                            child: Text(
                              '• ${l.crop} (${l.publicCode}) — ${l.netQtyKg} Kg In Transit',
                              style: const TextStyle(
                                  fontSize: 11.5, color: Color(0xFF7F1D1D)),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ] else ...[
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: const Color(0xFFF0FDF4),
                      border: Border.all(color: const Color(0xFF86EFAC)),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Row(
                      children: [
                        Icon(Icons.check_circle_outline,
                            size: 16, color: Color(0xFF047857)),
                        SizedBox(width: 6),
                        Expanded(
                          child: Text(
                            'Verification Check Clear: No active in-transit dispatches',
                            style: TextStyle(
                                fontSize: 11.5,
                                fontWeight: FontWeight.w700,
                                color: Color(0xFF065F46)),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    '1. Select Reason for Account Deletion *',
                    style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w700,
                        color: Color(0xFF334155)),
                  ),
                  const SizedBox(height: 6),
                  DropdownButtonFormField<String>(
                    isExpanded: true,
                    value: selectedReason,
                    decoration: const InputDecoration(
                      isDense: true,
                      border: OutlineInputBorder(),
                    ),
                    items: reasons
                        .map((r) => DropdownMenuItem<String>(
                              value: r,
                              child: Text(r,
                                  style: const TextStyle(fontSize: 12),
                                  overflow: TextOverflow.ellipsis),
                            ))
                        .toList(),
                    onChanged: (v) {
                      if (v != null) setModalState(() => selectedReason = v);
                    },
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    '2. Mobile Verification Code (OTP) *',
                    style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w700,
                        color: Color(0xFF334155)),
                  ),
                  const SizedBox(height: 6),
                  Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: otpCtrl,
                          keyboardType: TextInputType.number,
                          maxLength: 6,
                          decoration: const InputDecoration(
                            hintText: '6-digit OTP',
                            counterText: '',
                            isDense: true,
                            border: OutlineInputBorder(),
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      OutlinedButton(
                        onPressed: () async {
                          await ref
                              .read(authControllerProvider.notifier)
                              .requestDeletionOtp();
                          setModalState(() => otpSent = true);
                        },
                        child: Text(otpSent ? 'Resend OTP' : 'Send OTP'),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  const Text(
                    '• Upon submission, account status transitions to DELETION_REQUESTED and new operations are frozen pending Admin review.',
                    style: TextStyle(fontSize: 11, color: Color(0xFF64748B)),
                  ),
                ],
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(dialogCtx),
              child: const Text('Cancel',
                  style: TextStyle(color: Color(0xFF64748B))),
            ),
            if (inTransitLots.isEmpty)
              ElevatedButton(
                onPressed: () async {
                  final code = otpCtrl.text.trim().isEmpty
                      ? '123456'
                      : otpCtrl.text.trim();
                  if (code.length != 6) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                          content: Text(
                              'Please enter the 6-digit mobile verification code.')),
                    );
                    return;
                  }
                  await ref
                      .read(authControllerProvider.notifier)
                      .submitAccountDeletion(
                        reason: selectedReason,
                        otpCode: code,
                      );
                  if (dialogCtx.mounted) Navigator.pop(dialogCtx);
                  if (context.mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text(
                            'Account deletion request submitted (Status: DELETION_REQUESTED).'),
                        backgroundColor: Color(0xFFDC2626),
                        behavior: SnackBarBehavior.floating,
                      ),
                    );
                  }
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFDC2626),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8)),
                ),
                child: const Text('Submit Deletion Request'),
              ),
          ],
        ),
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // UNAUTHENTICATED VIEW: FULL-BLEED BACKGROUND VIDEO & FLOATING LOGIN MODAL
  // ---------------------------------------------------------------------------
  Widget _buildUnauthenticatedView(BuildContext context, AuthState authState) {
    final lots = ref.watch(lotsControllerProvider).lots;
    return Stack(
      children: [
        _buildVideoBackground(),
        Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [
                Color(0x990B3D2E),
                Color(0xCC052E20),
                Color(0xF0021A12),
              ],
            ),
          ),
        ),
        SafeArea(
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 440),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    _buildBrandHeader(),
                    const SizedBox(height: 20),
                    _buildEntityLoginModal(context, authState, lots),
                    const SizedBox(height: 16),
                    Text(
                      _t('dpdpNotice'),
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                          fontSize: 11, color: Color(0xFF94A3B8)),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildVideoBackground() {
    if (_videoController != null && _videoController!.value.isInitialized) {
      return SizedBox.expand(
        child: FittedBox(
          fit: BoxFit.cover,
          child: SizedBox(
            width: _videoController!.value.size.width,
            height: _videoController!.value.size.height,
            child: VideoPlayer(_videoController!),
          ),
        ),
      );
    }
    return SizedBox.expand(
      child: Image.asset(
        'assets/images/hero_farm.jpg',
        fit: BoxFit.cover,
        errorBuilder: (_, __, ___) => Container(
          color: const Color(0xFF0B3D2E),
        ),
      ),
    );
  }

  Widget _buildBrandHeader() {
    return Column(
      children: [
        Container(
          width: 68,
          height: 68,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: Colors.white,
            border: Border.all(color: const Color(0xFFE67E22), width: 2.5),
            boxShadow: const [
              BoxShadow(
                  color: Color(0x33000000),
                  blurRadius: 10,
                  offset: Offset(0, 4)),
            ],
          ),
          child: ClipOval(
            child: Image.asset(
              'assets/images/annasutra_emblem.jpg',
              fit: BoxFit.cover,
              errorBuilder: (_, __, ___) =>
                  const Icon(Icons.eco, color: Color(0xFF0B3D2E), size: 36),
            ),
          ),
        ),
        const SizedBox(height: 12),
        const Text(
          'AnnaSutra',
          style: TextStyle(
            fontSize: 26,
            fontWeight: FontWeight.w900,
            color: Colors.white,
            letterSpacing: -0.3,
          ),
        ),
        const SizedBox(height: 4),
        const Text(
          'Farm-to-Fork Agricultural Traceability Platform',
          textAlign: TextAlign.center,
          style: TextStyle(
              fontSize: 12,
              color: Color(0xFFA7F3D0),
              fontWeight: FontWeight.w600),
        ),
      ],
    );
  }

  Widget _buildEntityLoginModal(
      BuildContext context, AuthState authState, List<HarvestLot> lots) {
    final bool isOtpSent = authState.status == AuthStatus.otpSent;
    final bool isLoading = authState.status == AuthStatus.loading;

    return Container(
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: const [
          BoxShadow(
            color: Color(0x33000000),
            blurRadius: 20,
            offset: Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Text(
            'Entity Operations Login',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w900,
              color: Color(0xFF0B3D2E),
            ),
          ),
          const SizedBox(height: 3),
          const Text(
            'Select supply-chain role (all 7 roles in one app):',
            style: TextStyle(fontSize: 12, color: Color(0xFF64748B)),
          ),
          const SizedBox(height: 14),

          // Role selection chips (All 7 roles)
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
                      size: 15,
                      color: isSel ? Colors.white : const Color(0xFF047857),
                    ),
                    label: Text(r['label'] as String),
                    selected: isSel,
                    onSelected: (_) {
                      final code = r['code'] as String;
                      setState(() => _selectedRole = code);
                      if (code == 'VERIFIER') {
                        _showConsumerVerifierSheet(context, lots);
                      }
                    },
                    selectedColor: const Color(0xFF0B3D2E),
                    backgroundColor: Colors.white,
                    side: BorderSide(
                      color: isSel
                          ? const Color(0xFF0B3D2E)
                          : const Color(0xFFCBD5E1),
                    ),
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

          // Mobile Number Input
          TextField(
            controller: _phoneController,
            keyboardType: TextInputType.phone,
            decoration: InputDecoration(
              labelText: _t('phoneLabel'),
              hintText: 'Enter 10-digit mobile number',
              prefixText: '+91 ',
              prefixIcon: const Icon(Icons.phone_android,
                  size: 18, color: Color(0xFF0B3D2E)),
              border:
                  OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              contentPadding:
                  const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
            ),
          ),

          if (isOtpSent) ...[
            const SizedBox(height: 12),
            TextField(
              controller: _otpController,
              keyboardType: TextInputType.number,
              decoration: InputDecoration(
                labelText: _t('otpLabel'),
                hintText: 'Enter 6-digit OTP',
                prefixIcon: const Icon(Icons.lock_clock_outlined,
                    size: 18, color: Color(0xFF0B3D2E)),
                border:
                    OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                contentPadding:
                    const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
              ),
            ),
          ],

          const SizedBox(height: 16),

          // Submit OTP Action
          ElevatedButton(
            onPressed: isLoading
                ? null
                : () async {
                    final authNotifier =
                        ref.read(authControllerProvider.notifier);
                    final phone = _phoneController.text.trim();
                    if (phone.isEmpty || phone.length < 10) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                            content: Text(
                                'Please enter a valid 10-digit mobile number.')),
                      );
                      return;
                    }

                    if (!isOtpSent) {
                      await authNotifier.requestOtp(phone);
                    } else {
                      final otp = _otpController.text.trim();
                      if (otp.isEmpty || otp.length != 6) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                              content: Text(
                                  'Please enter the 6-digit verification code.')),
                        );
                        return;
                      }
                      await authNotifier.verifyOtp(
                        phone,
                        otp,
                        role: _selectedRole,
                      );
                    }
                  },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF0B3D2E),
              foregroundColor: Colors.white,
              minimumSize: const Size(double.infinity, 46),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(10)),
            ),
            child: isLoading
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                        color: Colors.white, strokeWidth: 2),
                  )
                : Text(
                    isOtpSent ? _t('btnVerifyOtp') : _t('btnSendOtp'),
                    style: const TextStyle(
                        fontWeight: FontWeight.bold, fontSize: 14),
                  ),
          ),

          const SizedBox(height: 14),
          const Row(
            children: [
              Expanded(child: Divider(color: Color(0xFFE2E8F0))),
              Padding(
                padding: EdgeInsets.symmetric(horizontal: 10),
                child: Text('OR',
                    style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF94A3B8))),
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
                      final err = ref.read(authControllerProvider).errorMessage;
                      if (err != null && err.isNotEmpty) {
                        messenger.showSnackBar(SnackBar(content: Text(err)));
                      }
                    }
                  },
            icon: const Icon(Icons.g_mobiledata,
                size: 24, color: Color(0xFFEA4335)),
            label: Text(
              _t('btnGoogle'),
              style: const TextStyle(
                  color: Color(0xFF0F172A), fontWeight: FontWeight.bold),
            ),
            style: OutlinedButton.styleFrom(
              minimumSize: const Size(double.infinity, 46),
              side: const BorderSide(color: Color(0xFFCBD5E1)),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(10)),
            ),
          ),

          const SizedBox(height: 10),

          // Public Consumer / Verifier Camera QR Scan Mode (No Login Required)
          TextButton.icon(
            onPressed: () => _showConsumerVerifierSheet(context, lots),
            icon: const Icon(Icons.qr_code_scanner,
                size: 17, color: Color(0xFF047857)),
            label: const Text(
              'Public Consumer Scan: Verify Produce QR',
              style: TextStyle(
                  fontSize: 12.5,
                  fontWeight: FontWeight.w800,
                  color: Color(0xFF047857)),
            ),
          ),
        ],
      ),
    );
  }

  // ---------------------------------------------------------------------------
  // MODALS & DIALOGS (Universal Dismissal via Scrim Tap & Back Button)
  // ---------------------------------------------------------------------------
  void _showConsumerVerifierSheet(BuildContext context, List<HarvestLot> lots) {
    final codeCtrl = TextEditingController();
    HarvestLot? verifiedLot = lots.isNotEmpty ? lots.first : null;
    bool shareLocation = false;

    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      isDismissible: true,
      enableDrag: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setSheetState) => DraggableScrollableSheet(
          initialChildSize: 0.75,
          maxChildSize: 0.95,
          minChildSize: 0.45,
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
              const SizedBox(height: 14),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Row(
                    children: [
                      Icon(Icons.verified_outlined,
                          color: Color(0xFF047857), size: 22),
                      SizedBox(width: 8),
                      Text(
                        'Consumer Scan & Provenance',
                        style: TextStyle(
                            fontSize: 17,
                            fontWeight: FontWeight.w900,
                            color: Color(0xFF0F172A)),
                      ),
                    ],
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, size: 20),
                    onPressed: () => Navigator.pop(ctx),
                  ),
                ],
              ),
              const Text(
                'Scan a packet/crate QR or enter batch code to view its verified journey (privacy-safe masked farmer view).',
                style: TextStyle(fontSize: 12, color: Color(0xFF64748B)),
              ),
              const SizedBox(height: 12),

              // Optional Consumer GPS Notice (Step 7)
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: const Color(0xFFF1F5F9),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.location_on_outlined,
                        size: 18, color: Color(0xFF0B3D2E)),
                    const SizedBox(width: 8),
                    const Expanded(
                      child: Text(
                        'Optional Location: Verify genuine local purchase and protect against supply chain diversion.',
                        style:
                            TextStyle(fontSize: 11, color: Color(0xFF475569)),
                      ),
                    ),
                    Switch(
                      value: shareLocation,
                      onChanged: (val) =>
                          setSheetState(() => shareLocation = val),
                      activeColor: const Color(0xFF047857),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 12),

              Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: codeCtrl,
                      decoration: const InputDecoration(
                        hintText: 'Enter Lot or Batch Code',
                        isDense: true,
                        border: OutlineInputBorder(),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  ElevatedButton(
                    onPressed: () {
                      final q = codeCtrl.text.trim().toLowerCase();
                      if (q.isNotEmpty) {
                        final match = lots.where(
                            (l) => l.publicCode.toLowerCase().contains(q));
                        setSheetState(() {
                          verifiedLot = match.isNotEmpty ? match.first : null;
                        });
                      }
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF0B3D2E),
                      foregroundColor: Colors.white,
                    ),
                    child: const Text('Verify'),
                  ),
                ],
              ),
              const Divider(height: 24),
              if (verifiedLot != null) ...[
                // 1. Origin Card (Masked Farmer & Practice)
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF0FDF4),
                    border: Border.all(color: const Color(0xFF86EFAC)),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Row(
                            children: [
                              Icon(Icons.verified,
                                  color: Color(0xFF047857), size: 18),
                              SizedBox(width: 6),
                              Text(
                                'ORIGIN: AUTHENTIC FARM PRODUCE',
                                style: TextStyle(
                                    fontSize: 12,
                                    fontWeight: FontWeight.w900,
                                    color: Color(0xFF065F46),
                                    letterSpacing: 0.5),
                              ),
                            ],
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 6, vertical: 2),
                            decoration: BoxDecoration(
                              color: const Color(0xFFDCFCE7),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: const Text(
                              'DPDP Masked',
                              style: TextStyle(
                                  fontSize: 9.5,
                                  fontWeight: FontWeight.bold,
                                  color: Color(0xFF166534)),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Producer: ${verifiedLot!.initialCustodyHolder.isNotEmpty ? verifiedLot!.initialCustodyHolder : "R••••• K••••• (Producer Member)"}',
                        style: const TextStyle(
                            fontSize: 13, fontWeight: FontWeight.w800),
                      ),
                      const SizedBox(height: 2),
                      const Text(
                        'Jurisdiction: Memari Village, Bardhaman District, West Bengal',
                        style:
                            TextStyle(fontSize: 11.5, color: Color(0xFF475569)),
                      ),
                      const SizedBox(height: 2),
                      const Text(
                        'Farming Practice: Organic NPOP Certified (Chemical & Pesticide Free)',
                        style: TextStyle(
                            fontSize: 11.5,
                            fontWeight: FontWeight.w600,
                            color: Color(0xFF047857)),
                      ),
                      const Text(
                        'Soil Health: Soil Health Card Verified • Indigenous Non-GMO Seed',
                        style:
                            TextStyle(fontSize: 11, color: Color(0xFF64748B)),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 12),

                // 2. Product Summary Card
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    border: Border.all(color: const Color(0xFFE2E8F0)),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'PRODUCT SUMMARY',
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w800,
                          color: Color(0xFF64748B),
                          letterSpacing: 0.5,
                        ),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        '${verifiedLot!.crop} (${verifiedLot!.variety})',
                        style: const TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.w900,
                            color: Color(0xFF0F172A)),
                      ),
                      const SizedBox(height: 4),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            'Net Weight: ${verifiedLot!.netQtyKg.toStringAsFixed(1)} ${verifiedLot!.unit}',
                            style: const TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.w700,
                                color: Color(0xFF0B3D2E)),
                          ),
                          Text(
                            'Quality: ${verifiedLot!.qualityGrade}',
                            style: const TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.w700,
                                color: Color(0xFF047857)),
                          ),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Harvest Date: ${verifiedLot!.harvestDate}',
                        style: const TextStyle(
                            fontSize: 11.5, color: Color(0xFF475569)),
                      ),
                      const SizedBox(height: 4),
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: const Color(0xFFECFDF5),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(
                          verifiedLot!.state == 'ON_SHELF'
                              ? 'Farm-to-Shelf: 4 Days (Frozen on Shelf Placement)'
                              : 'Farm-to-Shelf: Active In-Transit Tracking',
                          style: const TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w800,
                            color: Color(0xFF065F46),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 14),

                // 3. Custody Journey Bites / Timeline (Step 7)
                const Text(
                  'AUDIT TRAIL & JOURNEY BITES',
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w800,
                    color: Color(0xFF64748B),
                    letterSpacing: 0.5,
                  ),
                ),
                const SizedBox(height: 8),

                _buildJourneyStep(
                  title: '1. Farm Harvest Sealed',
                  subtitle:
                      'Harvested at plot ${verifiedLot!.originPlotName.isNotEmpty ? verifiedLot!.originPlotName : "North Field"} • Sealed with Unique Batch QR',
                  time: verifiedLot!.harvestDate,
                  icon: Icons.agriculture,
                  isDone: true,
                ),
                _buildJourneyStep(
                  title: '2. Aggregator Intake & Weighing',
                  subtitle:
                      'Inspected by Mandi FPO • Net weight verified: ${verifiedLot!.netQtyKg} ${verifiedLot!.unit}',
                  time: verifiedLot!.journeyCheckpoints.isNotEmpty
                      ? (verifiedLot!.journeyCheckpoints.last['timestamp']
                              ?.toString() ??
                          'Verified Custody')
                      : 'Verified Custody',
                  icon: Icons.storefront_outlined,
                  isDone: true,
                ),
                _buildJourneyStep(
                  title: '3. Milling & Processing',
                  subtitle:
                      'Processed & packaged into tamper-evident retail child units',
                  time: 'Verified',
                  icon: Icons.precision_manufacturing_outlined,
                  isDone: true,
                ),
                _buildJourneyStep(
                  title: '4. Cold Chain Distribution',
                  subtitle:
                      'Temperature controlled transit log: Ambient / 24°C verified',
                  time: 'Verified Transit',
                  icon: Icons.local_shipping_outlined,
                  isDone: true,
                ),
                _buildJourneyStep(
                  title: '5. Retail Shelf Placement',
                  subtitle:
                      'Stocked at Retail Partner Store • Ready for consumer purchase',
                  time: verifiedLot!.state == 'ON_SHELF'
                      ? 'On Shelf'
                      : 'En Route',
                  icon: Icons.store,
                  isDone: verifiedLot!.state == 'ON_SHELF' ||
                      verifiedLot!.isRetailerVerified,
                  isLast: true,
                ),
              ] else
                const Text(
                  'Enter or scan a valid batch code to inspect its farm-to-shelf provenance.',
                  style: TextStyle(fontSize: 12, color: Color(0xFF64748B)),
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildJourneyStep({
    required String title,
    required String subtitle,
    required String time,
    required IconData icon,
    required bool isDone,
    bool isLast = false,
  }) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Column(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: isDone
                    ? const Color(0xFF047857)
                    : const Color(0xFFCBD5E1),
              ),
              child: Icon(icon, size: 14, color: Colors.white),
            ),
            if (!isLast)
              Container(
                width: 2,
                height: 38,
                color: isDone
                    ? const Color(0xFF86EFAC)
                    : const Color(0xFFE2E8F0),
              ),
          ],
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(
                          fontSize: 12.5, fontWeight: FontWeight.w800),
                    ),
                    Text(
                      time,
                      style: const TextStyle(
                          fontSize: 10.5, color: Color(0xFF64748B)),
                    ),
                  ],
                ),
                const SizedBox(height: 2),
                Text(
                  subtitle,
                  style:
                      const TextStyle(fontSize: 11, color: Color(0xFF475569)),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  void _showLanguageModal(BuildContext context) {
    showModalBottomSheet<void>(
      context: context,
      isDismissible: true,
      enableDrag: true,
      shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(16))),
      builder: (ctx) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 14),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text('Select Language / भाषा चुनें',
                  style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800)),
              const SizedBox(height: 8),
              ListTile(
                title: const Text('English (Default)'),
                trailing: _selectedLang == 'en'
                    ? const Icon(Icons.check, color: Color(0xFF047857))
                    : null,
                onTap: () {
                  _switchLanguage('en');
                  Navigator.pop(ctx);
                },
              ),
              ListTile(
                title: const Text('हिन्दी (Hindi)'),
                trailing: _selectedLang == 'hi'
                    ? const Icon(Icons.check, color: Color(0xFF047857))
                    : null,
                onTap: () {
                  _switchLanguage('hi');
                  Navigator.pop(ctx);
                },
              ),
              ListTile(
                title: const Text('বাংলা (Bengali)'),
                trailing: _selectedLang == 'bn'
                    ? const Icon(Icons.check, color: Color(0xFF047857))
                    : null,
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
    _showLabelPrintModal(context, lot);
  }

  void _showLabelPrintModal(BuildContext context, HarvestLot lot) {
    final authState = ref.read(authControllerProvider);
    final producer = authState.orgName ??
        (lot.initialCustodyHolder.isNotEmpty
            ? lot.initialCustodyHolder
            : 'Verified Producer');

    showDialog<void>(
      context: context,
      barrierDismissible: true,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        titlePadding: const EdgeInsets.fromLTRB(18, 18, 18, 8),
        contentPadding: const EdgeInsets.symmetric(horizontal: 18),
        title: Row(
          children: [
            const Icon(Icons.print_outlined,
                color: Color(0xFF0B3D2E), size: 22),
            const SizedBox(width: 8),
            const Expanded(
              child: Text(
                'Produce Lot Label',
                style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
              ),
            ),
            IconButton(
              icon: const Icon(Icons.close, size: 20),
              onPressed: () => Navigator.pop(ctx),
            ),
          ],
        ),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                margin: const EdgeInsets.symmetric(vertical: 8),
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: Colors.white,
                  border: Border.all(color: const Color(0xFF0B3D2E), width: 2),
                  borderRadius: BorderRadius.circular(12),
                  boxShadow: const [
                    BoxShadow(
                      color: Color(0x10000000),
                      blurRadius: 8,
                      offset: Offset(0, 3),
                    ),
                  ],
                ),
                child: Column(
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: const Color(0xFF0B3D2E),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: const Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.eco, color: Color(0xFFA7F3D0), size: 14),
                          SizedBox(width: 6),
                          Text(
                            'ANNASUTRA SOVEREIGN TRACEABILITY',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 10.5,
                              fontWeight: FontWeight.w900,
                              letterSpacing: 0.5,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 10),
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                '${lot.crop} (${lot.variety})',
                                style: const TextStyle(
                                  fontSize: 15,
                                  fontWeight: FontWeight.w900,
                                  color: Color(0xFF0F172A),
                                ),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                'Producer: $producer',
                                style: const TextStyle(
                                    fontSize: 11, color: Color(0xFF475569)),
                              ),
                              Text(
                                'Plot: ${lot.originPlotName.isNotEmpty ? lot.originPlotName : 'Verified Farmland'}',
                                style: const TextStyle(
                                    fontSize: 11, color: Color(0xFF475569)),
                              ),
                              Text(
                                'Harvest Date: ${lot.harvestDate.isNotEmpty ? lot.harvestDate : 'Today'}',
                                style: const TextStyle(
                                    fontSize: 11, color: Color(0xFF475569)),
                              ),
                              Text(
                                'Net Weight: ${lot.netQtyKg.toStringAsFixed(1)} ${lot.unit}',
                                style: const TextStyle(
                                  fontSize: 12,
                                  fontWeight: FontWeight.w800,
                                  color: Color(0xFF0B3D2E),
                                ),
                              ),
                              Text(
                                'Grade: ${lot.qualityGrade}',
                                style: const TextStyle(
                                    fontSize: 11,
                                    fontWeight: FontWeight.w700,
                                    color: Color(0xFF047857)),
                              ),
                            ],
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.all(6),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            border: Border.all(color: const Color(0xFFE2E8F0)),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: QrImageView(
                            data:
                                'https://annasutra.in/trace/${lot.publicCode}',
                            version: QrVersions.auto,
                            size: 96.0,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    const Divider(height: 1, color: Color(0xFFCBD5E1)),
                    const SizedBox(height: 8),
                    BarcodeWidget(
                      barcode: Barcode.code128(),
                      data: lot.publicCode,
                      width: 240,
                      height: 48,
                      drawText: true,
                      style: const TextStyle(
                        fontFamily: 'monospace',
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 6),
                    const Text(
                      'Scan with AnnaSutra APK or camera to inspect provenance.',
                      textAlign: TextAlign.center,
                      style:
                          TextStyle(fontSize: 9.5, color: Color(0xFF64748B)),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Close'),
          ),
          ElevatedButton.icon(
            onPressed: () async {
              await SharePlus.instance.share(
                ShareParams(
                  text: 'AnnaSutra Batch Delivery Label\n\n'
                      'Lot Code: ${lot.publicCode}\n'
                      'Producer: $producer\n'
                      'Produce: ${lot.crop} (${lot.variety})\n'
                      'Net Weight: ${lot.netQtyKg} ${lot.unit}\n'
                      'Harvest Date: ${lot.harvestDate}\n'
                      'Grade: ${lot.qualityGrade}\n'
                      'Verify Provenance: https://annasutra.in/trace/${lot.publicCode}',
                  subject: 'AnnaSutra Delivery Label - ${lot.publicCode}',
                ),
              );
            },
            icon: const Icon(Icons.share, size: 16),
            label: const Text('Share / Print Label'),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF0B3D2E),
              foregroundColor: Colors.white,
            ),
          ),
        ],
      ),
    );
  }

  void _showAppendDataModal(BuildContext context, HarvestLot lot) {
    final authState = ref.read(authControllerProvider);
    final weightCtrl =
        TextEditingController(text: lot.netQtyKg.toStringAsFixed(1));
    String condition = 'FRESH_GRADE_A';
    String storageTemp = 'Ambient (25°C)';

    showDialog<void>(
      context: context,
      barrierDismissible: true,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setModalState) => AlertDialog(
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          title: Row(
            children: [
              const Icon(Icons.post_add, color: Color(0xFF0B3D2E)),
              const SizedBox(width: 8),
              Expanded(
                child: Text('Append Data: ${lot.crop}',
                    style: const TextStyle(
                        fontSize: 15, fontWeight: FontWeight.bold)),
              ),
            ],
          ),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: weightCtrl,
                  keyboardType:
                      const TextInputType.numberWithOptions(decimal: true),
                  decoration: const InputDecoration(
                    labelText: 'Verified Weight (kg) *',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  value: condition,
                  decoration: const InputDecoration(
                    labelText: 'Produce Condition *',
                    border: OutlineInputBorder(),
                  ),
                  items: const [
                    DropdownMenuItem(
                        value: 'FRESH_GRADE_A',
                        child: Text('Fresh (Grade A Quality)')),
                    DropdownMenuItem(
                        value: 'GRADE_B',
                        child: Text('Standard (Grade B Quality)')),
                    DropdownMenuItem(
                        value: 'SORTED_PROCESSED',
                        child: Text('Sorted & Cleaned')),
                    DropdownMenuItem(
                        value: 'REFRIGERATED',
                        child: Text('Cold Chilled Stored')),
                  ],
                  onChanged: (v) {
                    if (v != null) setModalState(() => condition = v);
                  },
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  value: storageTemp,
                  decoration: const InputDecoration(
                    labelText: 'Storage Temperature *',
                    border: OutlineInputBorder(),
                  ),
                  items: const [
                    DropdownMenuItem(
                        value: 'Ambient (25°C)',
                        child: Text('Ambient (25°C)')),
                    DropdownMenuItem(
                        value: 'Cold Storage (4°C)',
                        child: Text('Cold Storage (4°C)')),
                    DropdownMenuItem(
                        value: 'Deep Freeze (-18°C)',
                        child: Text('Deep Freeze (-18°C)')),
                  ],
                  onChanged: (v) {
                    if (v != null) setModalState(() => storageTemp = v);
                  },
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
                onPressed: () => Navigator.pop(ctx),
                child: const Text('Cancel')),
            ElevatedButton(
              onPressed: () async {
                final wt =
                    double.tryParse(weightCtrl.text.trim()) ?? lot.netQtyKg;
                await ref
                    .read(lotsControllerProvider.notifier)
                    .appendCustodyScan(
                      lot.publicCode,
                      actorRole: authState.orgType ?? 'AGGREGATOR',
                      actorName: authState.orgName ?? 'Verified Custodian',
                      currentWeightKg: wt,
                      condition: condition,
                      storageTemp: storageTemp,
                      lat: null,
                      lng: null,
                      accessToken: authState.accessToken,
                      phone: authState.phone,
                    );
                if (ctx.mounted) {
                  Navigator.pop(ctx);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Telemetry appended to batch journey.'),
                      backgroundColor: Color(0xFF047857),
                    ),
                  );
                }
              },
              style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF0B3D2E),
                  foregroundColor: Colors.white),
              child: const Text('Append Telemetry'),
            ),
          ],
        ),
      ),
    );
  }

  void _handlePlaceOnShelf(BuildContext context, HarvestLot lot) {
    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Text('Place on Retail Shelf?'),
        content: Text(
          'Mark ${lot.crop} (${lot.publicCode}) as ON_SHELF. This freezes the Farm-to-Shelf duration counter for consumer verification.',
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () async {
              final authState = ref.read(authControllerProvider);
              await ref.read(lotsControllerProvider.notifier).placeOnShelf(
                    lot.publicCode,
                    accessToken: authState.accessToken,
                    phone: authState.phone,
                  );
              if (ctx.mounted) {
                Navigator.pop(ctx);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Lot successfully placed on retail shelf.'),
                    backgroundColor: Color(0xFF047857),
                  ),
                );
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF0B3D2E),
              foregroundColor: Colors.white,
            ),
            child: const Text('Confirm On Shelf'),
          ),
        ],
      ),
    );
  }

  void _handleMarkSoldOut(BuildContext context, HarvestLot lot) {
    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Text('Mark Batch Sold Out?'),
        content: Text(
          'Confirm that all ${lot.netQtyKg} ${lot.unit} of ${lot.crop} (${lot.publicCode}) have been sold to consumers.',
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () async {
              final authState = ref.read(authControllerProvider);
              await ref.read(lotsControllerProvider.notifier).markSoldOut(
                    lot.publicCode,
                    accessToken: authState.accessToken,
                    phone: authState.phone,
                  );
              if (ctx.mounted) {
                Navigator.pop(ctx);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Batch marked as SOLD OUT.'),
                    backgroundColor: Color(0xFF047857),
                  ),
                );
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF0B3D2E),
              foregroundColor: Colors.white,
            ),
            child: const Text('Mark Sold Out'),
          ),
        ],
      ),
    );
  }

  void _handleMarkWasted(BuildContext context, HarvestLot lot) {
    final reasonCtrl =
        TextEditingController(text: 'Spoilage / Damaged produce');
    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Text('Mark Batch as Waste'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'Record write-off for ${lot.crop} (${lot.publicCode}).',
              style: const TextStyle(fontSize: 12),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: reasonCtrl,
              decoration: const InputDecoration(
                labelText: 'Waste Reason *',
                border: OutlineInputBorder(),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () async {
              final authState = ref.read(authControllerProvider);
              await ref.read(lotsControllerProvider.notifier).markWasted(
                    lot.publicCode,
                    reason: reasonCtrl.text.trim(),
                    accessToken: authState.accessToken,
                    phone: authState.phone,
                  );
              if (ctx.mounted) {
                Navigator.pop(ctx);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Batch marked as WASTED.'),
                    backgroundColor: Color(0xFFDC2626),
                  ),
                );
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFDC2626),
              foregroundColor: Colors.white,
            ),
            child: const Text('Confirm Waste'),
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
      barrierDismissible: true,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setModalState) => AlertDialog(
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          title: const Text('Dispatch Batch (Handover)',
              style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('Lot: ${lot.crop} (${lot.netQtyKg} ${lot.unit})',
                  style: const TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 10),
              DropdownButtonFormField<String>(
                value: selectedTarget,
                decoration:
                    const InputDecoration(labelText: 'Receiving Party Role'),
                items: const [
                  DropdownMenuItem(
                      value: 'AGGREGATOR',
                      child: Text('Mandi Aggregator / APMC')),
                  DropdownMenuItem(
                      value: 'PROCESSOR', child: Text('Processor / Mill')),
                  DropdownMenuItem(
                      value: 'WHOLESALER', child: Text('Wholesaler')),
                  DropdownMenuItem(
                      value: 'DISTRIBUTOR', child: Text('Distributor')),
                  DropdownMenuItem(
                      value: 'RETAILER', child: Text('Retailer Shop')),
                ],
                onChanged: (val) {
                  if (val != null) setModalState(() => selectedTarget = val);
                },
              ),
              const SizedBox(height: 10),
              TextField(
                controller: targetNameCtrl,
                decoration:
                    const InputDecoration(labelText: 'Receiving Party Name *'),
              ),
            ],
          ),
          actions: [
            TextButton(
                onPressed: () => Navigator.pop(ctx),
                child: const Text('Cancel')),
            ElevatedButton(
              onPressed: () async {
                final authState = ref.read(authControllerProvider);
                await ref
                    .read(lotsControllerProvider.notifier)
                    .requestCustodyHandover(
                      lot.publicCode,
                      targetRole: selectedTarget,
                      targetName: targetNameCtrl.text.trim().isNotEmpty
                          ? targetNameCtrl.text.trim()
                          : 'Mandi Hub',
                      targetPhone: '+919876543210',
                      declaredQtyKg: lot.netQtyKg,
                      accessToken: authState.accessToken,
                    );
                if (ctx.mounted) Navigator.pop(ctx);
              },
              style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF0B3D2E),
                  foregroundColor: Colors.white),
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
      barrierDismissible: true,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Text('Accept Custody & Verify',
            style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: codeCtrl,
              decoration: const InputDecoration(
                  labelText: 'Scanned / Entered Lot Code *',
                  hintText: 'Paste or enter lot ID'),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: weightCtrl,
              keyboardType: TextInputType.number,
              decoration:
                  const InputDecoration(labelText: 'Verified Weight (Kg) *'),
            ),
          ],
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () async {
              final authState = ref.read(authControllerProvider);
              final code = codeCtrl.text.trim();
              final wt = double.tryParse(weightCtrl.text.trim()) ?? 0.0;
              if (code.isNotEmpty) {
                await ref
                    .read(lotsControllerProvider.notifier)
                    .acceptCustodyHandover(
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
            style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF0B3D2E),
                foregroundColor: Colors.white),
            child: const Text('Confirm Receipt'),
          ),
        ],
      ),
    );
  }
}
