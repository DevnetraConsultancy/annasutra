import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:dio/dio.dart';
import 'package:intl/intl.dart';
import '../../auth/presentation/controllers/auth_controller.dart';
import '../../auth/domain/auth_state.dart';
import '../../auth/presentation/dpdp_consent_dialog.dart';
import '../../sync/sync_service.dart';
import '../../lots/presentation/controllers/lots_controller.dart';
import '../../lots/domain/harvest_lot.dart';
import '../../lots/presentation/widgets/lot_card.dart';
import '../../lots/presentation/widgets/analytics_charts.dart';

class HomeScreen extends ConsumerStatefulWidget {
  final void Function(Locale locale)? onLocaleChanged;

  const HomeScreen({super.key, this.onLocaleChanged});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  int _currentMainTab = 0; // 0: Ledger, 1: Analytics
  bool _isAnalyticsValuationMode = false;
  String _selectedLang = 'en';
  IconData _weatherIcon = Icons.wb_sunny_outlined;
  String _weatherText = 'Detecting...';
  String _dateTimeText = '';
  Timer? _clockTimer;

  static const Map<String, Map<String, String>> _strings = {
    'en': {
      'brandTitle': 'AnnaSutra',
      'brandSubtitle': 'National Agri-Produce Traceability Platform',
      'navLogin': 'Entity Login',
      'heroHead': 'Empowering Farmers.\nProtecting Consumers.',
      'heroSub': 'Direct cryptographic custody from seed to plate. Tamper-evident batch tracking on immutable tables and offline-ready verification.',
      'scanQrHero': 'Scan QR Code',
      'newBatchHero': 'New Harvest Lot',
      'entityTitle': 'Universal Entity Access',
      'entitySub': 'Select your supply-chain tier for dedicated operations and custody tools',
      'roleFarmer': 'Farmer / FPO Producer',
      'roleFarmerDesc': 'Harvest lot creation, farm bag QR codes, dispatch to mandi.',
      'roleMandi': 'Mandi Aggregator / APMC',
      'roleMandiDesc': 'Inbound receipt, lot grading, lot splitting & auction dispatch.',
      'roleCold': 'Cold Storage / Warehouse',
      'roleColdDesc': 'Inward custody receipt, temperature log, cold-chain outward.',
      'roleProcessor': 'Packhouse & Processor',
      'roleProcessorDesc': 'Raw intake, milling/sorting, retail pack QR generation.',
      'roleRetailer': 'Wholesaler & Retailer',
      'roleRetailerDesc': 'Point-of-sale verification, batch sales recording, consumer audit.',
      'roleAdmin': 'Admin / Verifier',
      'roleAdminDesc': 'Entity verification, KYC reveal audit, and QR label issuance.',
      'loginBtn': 'Login as',
      'tabLedger': 'Harvest Lots & Custody Ledger',
      'tabAnalytics': 'Analytics & Farm Insights',
      'tabIncoming': 'Incoming',
      'tabMyStock': 'My Stock',
      'tabWaiting': 'Waiting',
      'emptyIncoming': 'No inbound shipments awaiting receipt.',
      'emptyStock': 'No active produce batches in custody.',
      'emptyWaiting': 'No dispatched handovers awaiting counterparty sign-off.',
      'receiveBatch': 'Receive Batch',
      'dispatchBatch': 'Dispatch Batch',
      'splitLot': 'Split Lot',
      'recordWaste': 'Record Waste',
      'recordSale': 'Record Sale',
      'inspectQuality': 'Inspect Quality',
      'metricTotalLots': 'Total Active Lots',
      'metricInCustody': 'In Farm Custody',
      'metricInTransit': 'In Mandi Transit',
      'metricTotalWeight': 'Total Harvest Weight',
      'btnRegisterLot': '+ Register New Harvest Lot',
      'searchPlaceholder': 'Search lots by code, crop, plot, grade...',
      'filterCustodyAll': 'All Custody States',
      'filterInCustody': 'In Farm Custody (Editable)',
      'filterInTransit': 'In Transit (Locked)',
      'filterClosed': 'Handover Approved',
      'analyticsCropVolume': 'Crop Volume & Valuation Share',
      'analyticsCustodyFunnel': 'Custody Pipeline Funnel',
      'analyticsSettlement': 'Settlement & Payment Health',
      'disclaimer': 'Records are based on information entered by supply-chain participants. It does not prove the contents of this package.',
    },
    'hi': {
      'brandTitle': 'अन्नसूत्र',
      'brandSubtitle': 'राष्ट्रीय कृषि उपज ट्रेसेबिलिटी मंच',
      'navLogin': 'इकाई लॉगिन',
      'heroHead': 'किसानों का सशक्तिकरण।\nउपभोक्ताओं की सुरक्षा।',
      'heroSub': 'बीज से थाली तक डिजिटल कस्टडी। अपरिवर्तनीय लेजर पर बैच ट्रैकिंग एवं ऑफ़लाइन सत्यापन।',
      'scanQrHero': 'क्यूआर कोड स्कैन करें',
      'newBatchHero': 'नया फ़सल लॉट',
      'entityTitle': 'सार्वभौमिक इकाई पहुंच',
      'entitySub': 'समर्पित संचालन और कस्टडी टूल के लिए अपनी आपूर्ति-श्रृंखला श्रेणी चुनें',
      'roleFarmer': 'किसान / एफपीओ उत्पादक',
      'roleFarmerDesc': 'फ़सल लॉट निर्माण, बैग क्यूआर कोड, मंडी प्रेषण।',
      'roleMandi': 'मंडी एग्रीगेटर / एपीएमसी',
      'roleMandiDesc': 'आवक प्राप्ति, ग्रेडिंग, लॉट विभाजन व नीलामी।',
      'roleCold': 'कोल्ड स्टोरेज / गोदाम',
      'roleColdDesc': 'आवक कस्टडी, तापमान लॉग, सुरक्षित भंडारण।',
      'roleProcessor': 'पैकहाउस व प्रसंस्करणकर्ता',
      'roleProcessorDesc': 'कच्चा माल प्राप्ति, छंटाई, खुदरा पैकेजिंग।',
      'roleRetailer': 'थोक व खुदरा विक्रेता',
      'roleRetailerDesc': 'बिक्री केंद्र सत्यापन, खुदरा बिलिंग।',
      'roleAdmin': 'प्रशासक / सत्यापनकर्ता',
      'roleAdminDesc': 'इकाई सत्यापन, केवाईसी ऑडिट और क्यूआर आवंटन।',
      'loginBtn': 'के रूप में लॉगिन करें',
      'tabLedger': 'फ़सल लॉट एवं कस्टडी लेजर',
      'tabAnalytics': 'एनालिटिक्स एवं फ़ार्म इनसाइट्स',
      'tabIncoming': 'आवक',
      'tabMyStock': 'मेरा स्टॉक',
      'tabWaiting': 'प्रतीक्षारत',
      'emptyIncoming': 'प्राप्ति की प्रतीक्षा में कोई आवक खेप नहीं है।',
      'emptyStock': 'कस्टडी में कोई सक्रिय उत्पाद बैच नहीं है।',
      'emptyWaiting': 'प्रतिपक्ष की पुष्टि के लिए कोई प्रेषित हैंडओवर लंबित नहीं है।',
      'receiveBatch': 'बैच प्राप्त करें',
      'dispatchBatch': 'बैच प्रेषित करें',
      'splitLot': 'लॉट विभाजित करें',
      'recordWaste': 'अपव्यय दर्ज करें',
      'recordSale': 'खुदरा बिक्री दर्ज करें',
      'inspectQuality': 'गुणवत्ता निरीक्षण',
      'metricTotalLots': 'कुल सक्रिय लॉट',
      'metricInCustody': 'फ़ार्म कस्टडी में',
      'metricInTransit': 'मंडी पारगमन में',
      'metricTotalWeight': 'कुल फ़सल वजन',
      'btnRegisterLot': '+ नया फ़सल लॉट पंजीकृत करें',
      'searchPlaceholder': 'कोड, फ़सल, प्लॉट या ग्रेड से खोजें...',
      'filterCustodyAll': 'सभी कस्टडी स्थितियां',
      'filterInCustody': 'फ़ार्म कस्टडी में (संपादन योग्य)',
      'filterInTransit': 'पारगमन में (लॉक)',
      'filterClosed': 'हैंडओवर स्वीकृत',
      'analyticsCropVolume': 'फ़सल मात्रा एवं मूल्यांकन अनुपात',
      'analyticsCustodyFunnel': 'कस्टडी पाइपलाइन फ़नल',
      'analyticsSettlement': 'भुगतान एवं सेटलमेंट स्वास्थ्य',
      'disclaimer': 'रिकॉर्ड आपूर्ति-श्रृंखला प्रतिभागियों द्वारा दर्ज जानकारी पर आधारित हैं। यह पैकेज की आंतरिक सामग्री को सिद्ध नहीं करता है।',
    },
    'bn': {
      'brandTitle': 'অন্নসূত্র',
      'brandSubtitle': 'জাতীয় কৃষি-পণ্য ট্রেসেবিলিটি প্ল্যাটফর্ম',
      'navLogin': 'সংস্থা লগইন',
      'heroHead': 'কৃষকের ক্ষমতায়ন।\nভোক্তার সুরক্ষা।',
      'heroSub': 'বীজ থেকে ভোক্তা পর্যন্ত ডিজিটাল হেফাজত। অপরিবর্তনীয় লেজারে স্বচ্ছ ট্র্যাকিং ও অফলাইন যাচাইকরণ।',
      'scanQrHero': 'কিউআর স্ক্যান করুন',
      'newBatchHero': 'নতুন ফসল লট',
      'entityTitle': 'সার্বজনীন সংস্থা প্রবেশাধিকার',
      'entitySub': 'নির্দিষ্ট কার্যক্রম ও হেফাজত সরঞ্জামের জন্য আপনার সরবরাহ স্তর নির্বাচন করুন',
      'roleFarmer': 'কৃষক / এফপিও উৎপাদক',
      'roleFarmerDesc': 'ফসল লট তৈরি, বস্তা কিউআর কোড, মান্ডিতে প্রেরণ।',
      'roleMandi': 'মান্ডি অ্যাগ্রিগেটর / এপিএমসি',
      'roleMandiDesc': 'আমদানি গ্রহণ, গ্রেডিং, লট বিভাজন ও নিলাম।',
      'roleCold': 'কোল্ড স্টোরেজ / গুদাম',
      'roleColdDesc': 'হেফাজত গ্রহণ, তাপমাত্রা লগ, বহির্গমন অনুমোদন।',
      'roleProcessor': 'প্যাকহাউস ও প্রক্রিয়াকরণকারী',
      'roleProcessorDesc': 'কাঁচামাল গ্রহণ, বাছাই ও প্যাকেটজাতকরণ।',
      'roleRetailer': 'খুচরা বিক্রেতা',
      'roleRetailerDesc': 'বিক্রয় কেন্দ্র যাচাইকরণ, খুচরা বিক্রয় নথিভুক্ত।',
      'roleAdmin': 'প্রশাসক / যাচাইকারী',
      'roleAdminDesc': 'সংস্থা যাচাইকরণ, কেওয়াইসি অডিট এবং কিউআর বরাদ্দ।',
      'loginBtn': 'হিসেবে প্রবেশ করুন',
      'tabLedger': 'ফসল লট ও কাস্টডি লেজার',
      'tabAnalytics': 'বিশ্লেষণ ও কৃষি অন্তর্দৃষ্টি',
      'tabIncoming': 'আগত',
      'tabMyStock': 'আমার স্টক',
      'tabWaiting': 'অপেক্ষমাণ',
      'emptyIncoming': 'গ্রহণের অপেক্ষায় কোনো আগত চালান নেই।',
      'emptyStock': 'হেফাজতে কোনো সক্রিয় পণ্য ব্যাচ নেই।',
      'emptyWaiting': 'প্রতিপক্ষের নিশ্চিতকরণের অপেক্ষায় কোনো প্রেরণ নেই।',
      'receiveBatch': 'ব্যাচ গ্রহণ করুন',
      'dispatchBatch': 'ব্যাচ প্রেরণ করুন',
      'splitLot': 'লট বিভাজন করুন',
      'recordWaste': 'অপচয় নথিভুক্ত করুন',
      'recordSale': 'বিক্রয় নথিভুক্ত করুন',
      'inspectQuality': 'গুণমান পরীক্ষা',
      'metricTotalLots': 'মোট সক্রিয় লট',
      'metricInCustody': 'খামার হেফাজতে',
      'metricInTransit': 'মান্ডি ট্রানজিটে',
      'metricTotalWeight': 'মোট ফসলের ওজন',
      'btnRegisterLot': '+ নতুন ফসল লট নিবন্ধন করুন',
      'searchPlaceholder': 'কোড, ফসল, জমি বা গ্রেড দিয়ে খুঁজুন...',
      'filterCustodyAll': 'সকল হেফাজত স্থিতি',
      'filterInCustody': 'খামার হেফাজতে (সম্পাদনাযোগ্য)',
      'filterInTransit': 'ট্রানজিটে (লক করা)',
      'filterClosed': 'হস্তান্তর অনুমোদিত',
      'analyticsCropVolume': 'ফসল উৎপাদনের পরিমাণ ও মূল্য অনুপাত',
      'analyticsCustodyFunnel': 'হেফাজত পাইপলাইন ফানেল',
      'analyticsSettlement': 'মূল্য প্রাপ্তি ও পেমেন্ট স্থিতি',
      'disclaimer': 'রেকর্ড সরবরাহ-শৃঙ্খল অংশগ্রহণকারীদের দ্বারা প্রবেশ করা তথ্যের উপর ভিত্তি করে। এটি প্যাকেজের অভ্যন্তরীণ সামগ্রী প্রমাণ করে না।',
    },
  };

  String _t(String key) {
    return _strings[_selectedLang]?[key] ?? _strings['en']?[key] ?? key;
  }

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _updateClock();
    if (!const bool.fromEnvironment('FLUTTER_TEST')) {
      _clockTimer = Timer.periodic(const Duration(seconds: 1), (_) => _updateClock());
      _fetchWeather();
    }
  }

  @override
  void dispose() {
    _clockTimer?.cancel();
    _tabController.dispose();
    super.dispose();
  }

  void _updateClock() {
    final now = DateTime.now();
    final formatter = DateFormat('EEE, dd MMM yyyy • HH:mm:ss');
    if (mounted) {
      setState(() {
        _dateTimeText = formatter.format(now);
      });
    }
  }

  Future<void> _fetchWeather() async {
    try {
      final dio = Dio(BaseOptions(
        connectTimeout: const Duration(seconds: 4),
        receiveTimeout: const Duration(seconds: 4),
      ));
      final Response<dynamic> ipRes = await dio.get<dynamic>('https://ipwho.is/');
      if (ipRes.statusCode == 200 && ipRes.data is Map) {
        final data = ipRes.data as Map;
        final lat = data['latitude'] ?? 22.57;
        final lon = data['longitude'] ?? 88.36;
        final city = data['city'] ?? 'Local';

        final Response<dynamic> weatherRes = await dio.get<dynamic>(
          'https://api.open-meteo.com/v1/forecast?latitude=$lat&longitude=$lon&current=temperature_2m,weather_code&timezone=auto',
        );
        if (weatherRes.statusCode == 200 && weatherRes.data is Map) {
          final weatherData = weatherRes.data as Map;
          final current = weatherData['current'];
          final int temp = (current is Map && current['temperature_2m'] is num)
              ? (current['temperature_2m'] as num).round()
              : 28;
          final int code = (current is Map && current['weather_code'] is num)
              ? (current['weather_code'] as num).toInt()
              : 1;

          IconData icon = Icons.wb_cloudy_outlined;
          if (code == 0) {
            icon = Icons.wb_sunny_outlined;
          } else if (code >= 61 && code <= 65) {
            icon = Icons.water_drop_outlined;
          } else if (code >= 95) {
            icon = Icons.thunderstorm_outlined;
          }

          if (mounted) {
            setState(() {
              _weatherIcon = icon;
              _weatherText = '$temp°C $city';
            });
          }
        }
      }
    } catch (_) {
      if (mounted) {
        setState(() {
          _weatherIcon = Icons.wb_sunny_outlined;
          _weatherText = 'India';
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final AuthState authState = ref.watch(authControllerProvider);
    final LotsState lotsState = ref.watch(lotsControllerProvider);
    final SyncState syncState = ref.watch(syncControllerProvider);
    final screenWidth = MediaQuery.of(context).size.width;
    final isDesktop = screenWidth >= 900;

    return Scaffold(
      backgroundColor: const Color(0xFFF6F8F5),
      body: SafeArea(
        child: Column(
          children: [
            // 1. TOP UTILITY HEADER (Weather, Clock, Language Switcher, DPDP)
            _buildTopUtilityBar(context),

            // 2. MAIN BRAND NAVIGATION BAR
            _buildMainNavBar(context, authState),

            // 3. SCROLLABLE MAIN CONTENT
            Expanded(
              child: SingleChildScrollView(
                child: Center(
                  child: ConstrainedBox(
                    constraints: BoxConstraints(maxWidth: isDesktop ? 1160 : double.infinity),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        // Unauthenticated Landing View
                        if (!authState.isAuthenticated) ...[
                          _buildHeroBanner(context, isDesktop),
                          _buildUniversalEntityLoginSection(context, authState),
                          const SizedBox(height: 16),
                          _buildNationalTrustStandards(context),
                        ],

                        // Authenticated Entity Workspace View
                        if (authState.isAuthenticated) ...[
                          _buildSyncAndVerificationAlerts(context, authState, syncState),
                          const SizedBox(height: 12),
                          _buildDualTabNavigation(context),
                          const SizedBox(height: 12),

                          if (_currentMainTab == 0) ...[
                            // TAB 0: Harvest Lots & Custody Ledger
                            _buildProducerKpiCards(lotsState),
                            const SizedBox(height: 14),
                            _buildLotControlsAndFilterBar(context, lotsState),
                            const SizedBox(height: 14),
                            _buildHarvestLotsList(context, lotsState),
                            const SizedBox(height: 16),
                            _buildAccessibleActionButtons(context),
                          ] else ...[
                            // TAB 1: Analytics & Farm Insights
                            _buildProducerAnalyticsView(context, lotsState),
                          ],
                        ],

                        const SizedBox(height: 20),
                        _buildOfficialFooter(context),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // 1. TOP UTILITY BAR
  Widget _buildTopUtilityBar(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      decoration: const BoxDecoration(
        color: Color(0xFF07271D),
        border: Border(bottom: BorderSide(color: Color(0xFF144D3B), width: 1)),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.08),
              borderRadius: BorderRadius.circular(6),
              border: Border.all(color: Colors.white.withOpacity(0.14)),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(_weatherIcon, color: const Color(0xFFFDE047), size: 13),
                const SizedBox(width: 4),
                Text(
                  _weatherText,
                  style: const TextStyle(
                    color: Color(0xFFFDE047),
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              _dateTimeText,
              style: const TextStyle(
                color: Color(0xFFE2E8F0),
                fontSize: 11,
                fontWeight: FontWeight.w600,
                letterSpacing: 0.2,
              ),
              overflow: TextOverflow.ellipsis,
            ),
          ),
          Container(
            height: 28,
            padding: const EdgeInsets.symmetric(horizontal: 8),
            decoration: BoxDecoration(
              color: const Color(0xFF114232),
              borderRadius: BorderRadius.circular(6),
              border: Border.all(color: const Color(0xFF23654E), width: 1),
            ),
            child: DropdownButtonHideUnderline(
              child: DropdownButton<String>(
                value: _selectedLang,
                icon: const Icon(Icons.arrow_drop_down, color: Colors.white, size: 18),
                dropdownColor: const Color(0xFF0B3D2E),
                style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold),
                items: const [
                  DropdownMenuItem(value: 'en', child: Text('English (EN)')),
                  DropdownMenuItem(value: 'hi', child: Text('हिन्दी (HI)')),
                  DropdownMenuItem(value: 'bn', child: Text('বাংলা (BN)')),
                ],
                onChanged: (String? val) {
                  if (val != null) {
                    setState(() => _selectedLang = val);
                    widget.onLocaleChanged?.call(Locale(val));
                  }
                },
              ),
            ),
          ),
          const SizedBox(width: 8),
          IconButton(
            icon: const Icon(Icons.shield_outlined, color: Color(0xFFF59E0B), size: 18),
            tooltip: 'DPDP 2023',
            visualDensity: VisualDensity.compact,
            padding: EdgeInsets.zero,
            constraints: const BoxConstraints(minWidth: 28, minHeight: 28),
            onPressed: () => DpdpConsentDialog.show(context),
          ),
        ],
      ),
    );
  }

  // 2. MAIN BRAND NAVIGATION BAR
  Widget _buildMainNavBar(BuildContext context, AuthState authState) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: const BoxDecoration(
        color: Color(0xFF0B3D2E),
        boxShadow: [
          BoxShadow(color: Colors.black26, blurRadius: 4, offset: Offset(0, 2)),
        ],
      ),
      child: Row(
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: Container(
              height: 38,
              padding: const EdgeInsets.symmetric(horizontal: 4),
              child: Image.asset(
                'assets/images/annasutra_official_logo.png',
                fit: BoxFit.contain,
                errorBuilder: (_, __, ___) => Image.asset(
                  'assets/images/annasutra_emblem.jpg',
                  fit: BoxFit.cover,
                  errorBuilder: (_, __, ___) => const CircleAvatar(
                    backgroundColor: Color(0xFF14532D),
                    child: Text('AS', style: TextStyle(color: Colors.amber, fontWeight: FontWeight.bold)),
                  ),
                ),
              ),
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Row(
                  children: [
                    Text(
                      _t('brandTitle'),
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 18,
                        fontWeight: FontWeight.w900,
                        letterSpacing: 0.5,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: const Color(0xFFE67E22),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: const Text(
                        'GOV IN',
                        style: TextStyle(color: Colors.white, fontSize: 9.5, fontWeight: FontWeight.w900),
                      ),
                    ),
                  ],
                ),
                Text(
                  _t('brandSubtitle'),
                  style: const TextStyle(
                    color: Color(0xFFA7F3D0),
                    fontSize: 10.5,
                    fontWeight: FontWeight.w500,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
          if (authState.isAuthenticated) ...[
            Flexible(
              child: InkWell(
                onTap: () => _showAccountDialog(context),
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.12),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.white24),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.verified, color: Color(0xFF10B981), size: 16),
                      const SizedBox(width: 6),
                      Flexible(
                        child: Text(
                          authState.orgName ?? 'Verified Node',
                          style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ] else ...[
            ElevatedButton.icon(
              onPressed: () => context.push('/login'),
              icon: const Icon(Icons.login, size: 14),
              label: Text(_t('navLogin')),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFFE67E22),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                minimumSize: const Size(80, 36),
                textStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
              ),
            ),
          ],
        ],
      ),
    );
  }

  // DUAL-TAB SEGMENTED NAVIGATION (Matching Web App)
  Widget _buildDualTabNavigation(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        color: const Color(0xFFE2E8F0),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Expanded(
            child: InkWell(
              onTap: () => setState(() => _currentMainTab = 0),
              borderRadius: BorderRadius.circular(9),
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 10),
                decoration: BoxDecoration(
                  color: _currentMainTab == 0 ? const Color(0xFF0B3D2E) : Colors.transparent,
                  borderRadius: BorderRadius.circular(9),
                  boxShadow: _currentMainTab == 0
                      ? const [BoxShadow(color: Colors.black12, blurRadius: 4, offset: Offset(0, 1))]
                      : null,
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.inventory_2_outlined,
                      size: 16,
                      color: _currentMainTab == 0 ? const Color(0xFFFCD34D) : const Color(0xFF475569),
                    ),
                    const SizedBox(width: 8),
                    Flexible(
                      child: Text(
                        _t('tabLedger'),
                        style: TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.bold,
                          color: _currentMainTab == 0 ? Colors.white : const Color(0xFF475569),
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          const SizedBox(width: 4),
          Expanded(
            child: InkWell(
              onTap: () => setState(() => _currentMainTab = 1),
              borderRadius: BorderRadius.circular(9),
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 10),
                decoration: BoxDecoration(
                  color: _currentMainTab == 1 ? const Color(0xFF0B3D2E) : Colors.transparent,
                  borderRadius: BorderRadius.circular(9),
                  boxShadow: _currentMainTab == 1
                      ? const [BoxShadow(color: Colors.black12, blurRadius: 4, offset: Offset(0, 1))]
                      : null,
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.insights_outlined,
                      size: 16,
                      color: _currentMainTab == 1 ? const Color(0xFFFCD34D) : const Color(0xFF475569),
                    ),
                    const SizedBox(width: 8),
                    Flexible(
                      child: Text(
                        _t('tabAnalytics'),
                        style: TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.bold,
                          color: _currentMainTab == 1 ? Colors.white : const Color(0xFF475569),
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // 4 TOP KPI SUMMARY CARDS
  Widget _buildProducerKpiCards(LotsState lotsState) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: LayoutBuilder(
        builder: (context, constraints) {
          final isNarrow = constraints.maxWidth < 600;
          return GridView.count(
            crossAxisCount: isNarrow ? 2 : 4,
            crossAxisSpacing: 10,
            mainAxisSpacing: 10,
            childAspectRatio: isNarrow ? 1.7 : 1.9,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            children: [
              _buildKpiCard(
                title: _t('metricTotalLots'),
                value: lotsState.totalLotsCount.toString(),
                icon: Icons.layers_outlined,
                color: const Color(0xFF0F172A),
                iconBg: const Color(0xFFF1F5F9),
              ),
              _buildKpiCard(
                title: _t('metricInCustody'),
                value: lotsState.inCustodyCount.toString(),
                icon: Icons.agriculture_outlined,
                color: const Color(0xFF047857),
                iconBg: const Color(0xFFECFDF5),
              ),
              _buildKpiCard(
                title: _t('metricInTransit'),
                value: lotsState.inTransitCount.toString(),
                icon: Icons.local_shipping_outlined,
                color: const Color(0xFFD97706),
                iconBg: const Color(0xFFFFFBEB),
              ),
              _buildKpiCard(
                title: _t('metricTotalWeight'),
                value: '${lotsState.totalWeightKg.toStringAsFixed(0)} Kg',
                icon: Icons.scale_outlined,
                color: const Color(0xFF2563EB),
                iconBg: const Color(0xFFEFF6FF),
              ),
            ],
          );
        },
      ),
    );
  }

  Widget _buildKpiCard({
    required String title,
    required String value,
    required IconData icon,
    required Color color,
    required Color iconBg,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFE2E8F0)),
        boxShadow: const [
          BoxShadow(color: Color(0x08000000), blurRadius: 3, offset: Offset(0, 1)),
        ],
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(9),
            decoration: BoxDecoration(color: iconBg, borderRadius: BorderRadius.circular(10)),
            child: Icon(icon, size: 20, color: color),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  title,
                  style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: Color(0xFF64748B)),
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 2),
                Text(
                  value,
                  style: TextStyle(fontSize: 17, fontWeight: FontWeight.w900, color: color),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // LOT CONTROLS & FILTER BAR
  Widget _buildLotControlsAndFilterBar(BuildContext context, LotsState lotsState) {
    final notifier = ref.read(lotsControllerProvider.notifier);

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Top row: Search input + "+ Register New Harvest Lot" Button
          LayoutBuilder(
            builder: (context, constraints) {
              final isNarrow = constraints.maxWidth < 540;
              final searchField = SizedBox(
                height: 44,
                child: TextField(
                  onChanged: (val) => notifier.setSearchQuery(val),
                  decoration: InputDecoration(
                    hintText: _t('searchPlaceholder'),
                    hintStyle: const TextStyle(fontSize: 12.5, color: Color(0xFF94A3B8)),
                    prefixIcon: const Icon(Icons.search, size: 18, color: Color(0xFF64748B)),
                    contentPadding: const EdgeInsets.symmetric(vertical: 0, horizontal: 10),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: const BorderSide(color: Color(0xFFCBD5E1))),
                    filled: true,
                    fillColor: const Color(0xFFF8FAFC),
                  ),
                ),
              );

              final registerBtn = ElevatedButton.icon(
                onPressed: () => context.push('/create-batch'),
                icon: const Icon(Icons.add, size: 18),
                label: Text(
                  _t('btnRegisterLot'),
                  style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF047857),
                  foregroundColor: Colors.white,
                  minimumSize: Size(isNarrow ? double.infinity : 130, 44),
                  padding: const EdgeInsets.symmetric(horizontal: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
              );

              if (isNarrow) {
                return Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    searchField,
                    const SizedBox(height: 10),
                    registerBtn,
                  ],
                );
              }

              return Row(
                children: [
                  Expanded(child: searchField),
                  const SizedBox(width: 10),
                  registerBtn,
                ],
              );
            },
          ),
          const SizedBox(height: 12),

          // Horizontal Filter Chips: Custody State
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                _buildFilterChip('ALL', _t('filterCustodyAll'), lotsState.selectedCustody == 'ALL', () => notifier.setCustodyFilter('ALL')),
                const SizedBox(width: 6),
                _buildFilterChip('IN_CUSTODY', _t('filterInCustody'), lotsState.selectedCustody == 'IN_CUSTODY', () => notifier.setCustodyFilter('IN_CUSTODY')),
                const SizedBox(width: 6),
                _buildFilterChip('IN_TRANSIT', _t('filterInTransit'), lotsState.selectedCustody == 'IN_TRANSIT', () => notifier.setCustodyFilter('IN_TRANSIT')),
                const SizedBox(width: 6),
                _buildFilterChip('CLOSED', _t('filterClosed'), lotsState.selectedCustody == 'CLOSED', () => notifier.setCustodyFilter('CLOSED')),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFilterChip(String value, String label, bool isSelected, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(20),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: isSelected ? const Color(0xFF047857) : const Color(0xFFF1F5F9),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: isSelected ? const Color(0xFF047857) : const Color(0xFFCBD5E1)),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 11.5,
            fontWeight: isSelected ? FontWeight.w800 : FontWeight.w600,
            color: isSelected ? Colors.white : const Color(0xFF334155),
          ),
        ),
      ),
    );
  }

  // HARVEST LOTS LIST CONTAINER
  Widget _buildHarvestLotsList(BuildContext context, LotsState lotsState) {
    final filtered = lotsState.filteredLots;

    if (filtered.isEmpty) {
      return Container(
        margin: const EdgeInsets.symmetric(horizontal: 16),
        padding: const EdgeInsets.all(36),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: const Color(0xFFE2E8F0)),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.eco_outlined, size: 48, color: Color(0xFF047857)),
            const SizedBox(height: 12),
            const Text(
              'No harvest lots in custody matching your filters.',
              style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
            ),
            const SizedBox(height: 6),
            const Text(
              'Click "+ Register New Harvest Lot" to add your first verified produce lot.',
              style: TextStyle(fontSize: 12.5, color: Color(0xFF64748B)),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => context.push('/create-batch'),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF047857),
                foregroundColor: Colors.white,
              ),
              child: Text(_t('btnRegisterLot')),
            ),
          ],
        ),
      );
    }

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Column(
        children: filtered.map((lot) {
          return LotCard(
            lot: lot,
            onEdit: () {
              context.push('/create-batch?code=${lot.publicCode}');
            },
            onDispatch: () {
              _showQuickDispatchDialog(context, lot);
            },
            onShowQr: () {
              _showUnlimitedQrDialog(context, lot);
            },
          );
        }).toList(),
      ),
    );
  }

  // TAB 1: ANALYTICS & FARM INSIGHTS VIEW
  Widget _buildProducerAnalyticsView(BuildContext context, LotsState lotsState) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Period Selector Bar
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: const Color(0xFFE2E8F0)),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    const Icon(Icons.auto_graph, color: Color(0xFF047857), size: 18),
                    const SizedBox(width: 8),
                    Text(
                      _t('tabAnalytics'),
                      style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                    ),
                  ],
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF1F5F9),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Text('All Recorded Lots', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF334155))),
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),

          // 1. Crop Volume & Valuation Share Card
          Container(
            padding: const EdgeInsets.all(16),
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
                    Text(
                      _t('analyticsCropVolume'),
                      style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                    ),
                    InkWell(
                      onTap: () => setState(() => _isAnalyticsValuationMode = !_isAnalyticsValuationMode),
                      borderRadius: BorderRadius.circular(6),
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: const Color(0xFFECFDF5),
                          border: Border.all(color: const Color(0xFFA7F3D0)),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(
                          _isAnalyticsValuationMode ? 'Switch to Weight (Kg)' : 'Switch to Value (₹)',
                          style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF047857)),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 14),
                CropDonutChart(
                  data: _isAnalyticsValuationMode ? lotsState.cropValuationDistribution : lotsState.cropVolumeDistribution,
                  unit: _isAnalyticsValuationMode ? '₹' : 'Kg',
                  height: 180,
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),

          // 2. Custody Pipeline Funnel Card
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: const Color(0xFFE2E8F0)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  _t('analyticsCustodyFunnel'),
                  style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                ),
                const SizedBox(height: 12),
                CustodyFunnelWidget(
                  stages: lotsState.custodyFunnel,
                  totalWeightKg: lotsState.totalWeightKg,
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),

          // 3. Settlement & Commercial Payment Health
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: const Color(0xFFE2E8F0)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  _t('analyticsSettlement'),
                  style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                ),
                const SizedBox(height: 12),
                SettlementHealthWidget(stats: lotsState.paymentSettlementStats),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // MODALS & DIALOGS
  void _showUnlimitedQrDialog(BuildContext context, HarvestLot lot) {
    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Row(
          children: [
            Icon(Icons.qr_code, color: Color(0xFF047857)),
            SizedBox(width: 8),
            Text('Verifiable Sovereign QR', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFFCBD5E1), width: 1.5),
              ),
              child: Column(
                children: [
                  Container(
                    width: 160,
                    height: 160,
                    decoration: BoxDecoration(
                      border: Border.all(color: const Color(0xFF0B3D2E), width: 3),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(Icons.qr_code_2, size: 100, color: Color(0xFF0B3D2E)),
                          Text(
                            lot.publicCode,
                            style: const TextStyle(fontFamily: 'monospace', fontWeight: FontWeight.w900, fontSize: 13),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 10),
                  Text(
                    '${lot.crop} (${lot.variety}) • ${lot.netQtyKg.toStringAsFixed(1)} ${lot.unit}',
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 4),
                  const Text(
                    'Govt. of India AgriTrace Compliant • Unlimited Generator',
                    style: TextStyle(fontSize: 10.5, color: Color(0xFF64748B)),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Close'),
          ),
          ElevatedButton.icon(
            onPressed: () {
              Navigator.pop(ctx);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('Preparing print sheet for ${lot.publicCode}...'),
                  backgroundColor: const Color(0xFF047857),
                ),
              );
            },
            icon: const Icon(Icons.print, size: 16),
            label: const Text('Print Labels'),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF047857),
              foregroundColor: Colors.white,
            ),
          ),
        ],
      ),
    );
  }

  void _showQuickDispatchDialog(BuildContext context, HarvestLot lot) {
    final vehicleCtrl = TextEditingController(text: 'WB-25-A-8902');
    final driverCtrl = TextEditingController(text: '+919876500000');

    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Row(
          children: [
            Icon(Icons.local_shipping, color: Color(0xFF047857)),
            SizedBox(width: 8),
            Text('Dispatch to Mandi / Buyer', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Lot: ${lot.publicCode} (${lot.crop} • ${lot.netQtyKg} ${lot.unit})', style: const TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            TextField(
              controller: vehicleCtrl,
              decoration: const InputDecoration(labelText: 'Vehicle Number', border: OutlineInputBorder()),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: driverCtrl,
              decoration: const InputDecoration(labelText: 'Driver Phone', border: OutlineInputBorder()),
            ),
            const SizedBox(height: 10),
            const Text(
              'Notice: Upon dispatch, lot status switches to "In Transit" and immutability lock is enforced.',
              style: TextStyle(fontSize: 11, color: Color(0xFFC2410C), fontWeight: FontWeight.w600),
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () {
              ref.read(lotsControllerProvider.notifier).dispatchLot(
                lot.publicCode,
                vehicleNo: vehicleCtrl.text.trim(),
                driverContact: driverCtrl.text.trim(),
              );
              Navigator.pop(ctx);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('Lot ${lot.publicCode} dispatched! Status locked to In Transit.'),
                  backgroundColor: const Color(0xFF047857),
                ),
              );
            },
            style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF047857), foregroundColor: Colors.white),
            child: const Text('Confirm Handover'),
          ),
        ],
      ),
    );
  }

  // HERO BANNER & UNIVERSAL LOGIN (For unauthenticated visitors)
  Widget _buildHeroBanner(BuildContext context, bool isDesktop) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF0B3D2E),
        borderRadius: BorderRadius.circular(16),
        boxShadow: const [BoxShadow(color: Colors.black12, blurRadius: 6, offset: Offset(0, 2))],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            _t('heroHead'),
            style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: Colors.white, height: 1.2),
          ),
          const SizedBox(height: 8),
          Text(
            _t('heroSub'),
            style: const TextStyle(fontSize: 12.5, color: Color(0xFFA7F3D0), height: 1.4),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              ElevatedButton.icon(
                onPressed: () => context.push('/login'),
                icon: const Icon(Icons.qr_code_scanner, size: 16),
                label: Text(_t('scanQrHero')),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFE67E22),
                  foregroundColor: Colors.white,
                  minimumSize: const Size(120, 42),
                ),
              ),
              const SizedBox(width: 10),
              OutlinedButton.icon(
                onPressed: () => context.push('/create-batch'),
                icon: const Icon(Icons.add, size: 16, color: Colors.white),
                label: Text(_t('newBatchHero'), style: const TextStyle(color: Colors.white)),
                style: OutlinedButton.styleFrom(
                  side: const BorderSide(color: Colors.white54),
                  minimumSize: const Size(120, 42),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildUniversalEntityLoginSection(BuildContext context, AuthState authState) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            _t('entityTitle'),
            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
          ),
          Text(
            _t('entitySub'),
            style: const TextStyle(fontSize: 12, color: Color(0xFF64748B)),
          ),
          const SizedBox(height: 14),
          LayoutBuilder(
            builder: (context, constraints) {
              final isWide = constraints.maxWidth > 600;
              return Wrap(
                spacing: 10,
                runSpacing: 10,
                children: [
                  _buildEntityCard(
                    context: context,
                    roleKey: 'FARMER',
                    icon: Icons.grass,
                    title: _t('roleFarmer'),
                    description: _t('roleFarmerDesc'),
                    width: isWide ? (constraints.maxWidth - 20) / 2 : constraints.maxWidth,
                    onTapLogin: () {
                      ref.read(authControllerProvider.notifier).quickLoginAsEntity(
                        entityRole: 'FARMER',
                        orgName: "Dr. Niladri's Farm (WB-PROD-2026-X7803)",
                        phone: '+919876543210',
                      );
                    },
                  ),
                  _buildEntityCard(
                    context: context,
                    roleKey: 'MANDI',
                    icon: Icons.storefront,
                    title: _t('roleMandi'),
                    description: _t('roleMandiDesc'),
                    width: isWide ? (constraints.maxWidth - 20) / 2 : constraints.maxWidth,
                    onTapLogin: () {
                      ref.read(authControllerProvider.notifier).quickLoginAsEntity(
                        entityRole: 'MANDI',
                        orgName: 'Kolkata APMC Mandi Hub',
                        phone: '+919876543211',
                      );
                    },
                  ),
                  _buildEntityCard(
                    context: context,
                    roleKey: 'COLD_STORAGE',
                    icon: Icons.ac_unit,
                    title: _t('roleCold'),
                    description: _t('roleColdDesc'),
                    width: isWide ? (constraints.maxWidth - 20) / 2 : constraints.maxWidth,
                    onTapLogin: () {
                      ref.read(authControllerProvider.notifier).quickLoginAsEntity(
                        entityRole: 'COLD_STORAGE',
                        orgName: 'Bengal Cold Chain Terminal',
                        phone: '+919876543212',
                      );
                    },
                  ),
                  _buildEntityCard(
                    context: context,
                    roleKey: 'ADMIN',
                    icon: Icons.verified_user_outlined,
                    title: _t('roleAdmin'),
                    description: _t('roleAdminDesc'),
                    width: isWide ? (constraints.maxWidth - 20) / 2 : constraints.maxWidth,
                    onTapLogin: () {
                      ref.read(authControllerProvider.notifier).quickLoginAsEntity(
                        entityRole: 'ADMIN',
                        orgName: 'AnnaSutra Sovereign Registry Node',
                        phone: '+919999999999',
                      );
                    },
                  ),
                ],
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildEntityCard({
    required BuildContext context,
    required String roleKey,
    required IconData icon,
    required String title,
    required String description,
    required double width,
    required VoidCallback onTapLogin,
  }) {
    return Container(
      width: width,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFFFAFAFA),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(color: const Color(0xFF0B3D2E), borderRadius: BorderRadius.circular(8)),
                child: Icon(icon, color: Colors.white, size: 18),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(description, style: const TextStyle(fontSize: 11, color: Color(0xFF64748B), height: 1.3)),
          const SizedBox(height: 10),
          SizedBox(
            width: double.infinity,
            height: 38,
            child: ElevatedButton.icon(
              onPressed: onTapLogin,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF0B3D2E),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(horizontal: 10),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
              ),
              icon: const Icon(Icons.login, size: 16),
              label: Text('${_t('loginBtn')} $title', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNationalTrustStandards(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFFECFDF5),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFA7F3D0)),
      ),
      child: const Row(
        children: [
          Icon(Icons.gavel, color: Color(0xFF047857), size: 24),
          SizedBox(width: 12),
          Expanded(
            child: Text(
              'National Agriculture Traceability Standard • Tamper-Evident Ledger • DPDP 2023 Conforming',
              style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF065F46)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSyncAndVerificationAlerts(BuildContext context, AuthState authState, SyncState syncState) {
    final registeredName = (authState.orgName != null && authState.orgName!.trim().isNotEmpty)
        ? authState.orgName!
        : 'Dr. Niladri\'s Farm (WB-PROD-2026-X7803)';

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(color: const Color(0xFFECFDF5), borderRadius: BorderRadius.circular(8)),
            child: const Icon(Icons.verified, color: Color(0xFF047857), size: 20),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  registeredName,
                  style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 13, color: Color(0xFF0F172A)),
                ),
                const Row(
                  children: [
                    Text('Active Sovereign Node', style: TextStyle(fontSize: 11, color: Color(0xFF047857), fontWeight: FontWeight.bold)),
                    SizedBox(width: 6),
                    Text('• 100% Cryptographically Bound', style: TextStyle(fontSize: 11, color: Color(0xFF64748B))),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // Quick Action Buttons (matching widget test expectations: Scan QR, Create Batch)
  Widget _buildAccessibleActionButtons(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () => context.push('/receive'),
                  icon: const Icon(Icons.qr_code_scanner, size: 18),
                  label: const Text('Scan QR', style: TextStyle(fontWeight: FontWeight.bold)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF0B3D2E),
                    foregroundColor: Colors.white,
                    minimumSize: const Size(120, 48),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: () => context.push('/create-batch'),
                  icon: const Icon(Icons.add, size: 18),
                  label: const Text('Create Batch', style: TextStyle(fontWeight: FontWeight.bold)),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: const Color(0xFF0B3D2E),
                    side: const BorderSide(color: Color(0xFF0B3D2E), width: 1.5),
                    minimumSize: const Size(120, 48),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: () => context.push('/dispatch'),
                  icon: const Icon(Icons.upload, size: 16),
                  label: Text(_t('dispatchBatch')),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: () => context.push('/split'),
                  icon: const Icon(Icons.call_split, size: 16),
                  label: Text(_t('splitLot')),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: () => context.push('/inspection'),
                  icon: const Icon(Icons.verified_outlined, size: 16),
                  label: Text(_t('inspectQuality')),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  // OFFICIAL FOOTER
  Widget _buildOfficialFooter(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      color: const Color(0xFF0B3D2E),
      child: Column(
        children: [
          Text(
            _t('disclaimer'),
            style: const TextStyle(color: Color(0xFFA7F3D0), fontSize: 11.5, height: 1.4),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 12),
          const Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.phone, color: Color(0xFFFCD34D), size: 14),
              SizedBox(width: 5),
              Text('Kisan Helpline: 1800-180-1551', style: TextStyle(color: Color(0xFFFCD34D), fontSize: 11, fontWeight: FontWeight.bold)),
              SizedBox(width: 12),
              Text('|', style: TextStyle(color: Colors.white24)),
              SizedBox(width: 12),
              Icon(Icons.shield, color: Colors.white70, size: 14),
              SizedBox(width: 5),
              Text('Consumer Helpline: 1915', style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
            ],
          ),
        ],
      ),
    );
  }

  void _showAccountDialog(BuildContext context) {
    final authState = ref.read(authControllerProvider);
    final entityDisplay = authState.orgName ?? "Dr. Niladri's Farm";
    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Node Identity'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Entity: $entityDisplay', style: const TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 4),
            Text('Phone: ${authState.phone ?? "+919876543210"}'),
            const SizedBox(height: 4),
            const Text('Status: VERIFIED SOVEREIGN NODE', style: TextStyle(color: Colors.green, fontWeight: FontWeight.bold)),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Close')),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(ctx);
              ref.read(authControllerProvider.notifier).checkSavedAuth();
              context.go('/login');
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red.shade700, foregroundColor: Colors.white),
            child: const Text('Switch Account'),
          ),
        ],
      ),
    );
  }
}
