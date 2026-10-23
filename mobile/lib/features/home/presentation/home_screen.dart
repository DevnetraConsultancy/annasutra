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

class HomeScreen extends ConsumerStatefulWidget {
  final void Function(Locale locale)? onLocaleChanged;

  const HomeScreen({super.key, this.onLocaleChanged});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
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
      'tabIncoming': 'Incoming',
      'tabMyStock': 'My Stock',
      'tabWaiting': 'Waiting',
      'emptyIncoming': 'No inbound shipments awaiting receipt.',
      'emptyStock': 'No active produce batches in custody.',
      'emptyWaiting': 'No dispatched handovers awaiting counterparty sign-off.',
      'receiveBatch': 'Receive Batch',
      'dispatchBatch': 'Dispatch Batch',
      'splitLot': 'Split Lot',
      'inspectQuality': 'Inspect Quality',
      'recordWaste': 'Record Waste',
      'recordSale': 'Record Retail Sale',
      'scanQr': 'Scan QR',
      'createBatch': 'Create Batch',
      'trustTitle': 'National Trust & Verification Standards',
      'trust1Title': 'Cryptographic Append-Only Ledger',
      'trust1Desc': 'Every harvest, dispatch, and quality inspection is secured with SHA-256 hash chains and immutable database triggers.',
      'trust2Title': 'Zero Personal Data Leakage',
      'trust2Desc': 'Farmer personal identity, precise farm GPS coordinates, and commercial pricing are strictly protected under the DPDP Act 2023.',
      'trust3Title': 'Mutual Custody Confirmation',
      'trust3Desc': 'Produce ownership transfers require verified sign-off between both dispatching and receiving operators.',
      'footerDev': 'Developed by Centre for Development of Advanced Computing (C-DAC)',
      'footerGov': 'Ministry of Electronics & Information Technology, Government of India',
      'disclaimer': 'Notice: Records are based on information entered by supply-chain participants. They do not prove physical package contents.',
      'dpdpLink': 'DPDP Act 2023 Compliance & Grievance Redressal Officer: grievance@annasutra.in',
    },
    'hi': {
      'brandTitle': 'अन्नसूत्र',
      'brandSubtitle': 'राष्ट्रीय कृषि-उत्पाद ट्रैसेबिलिटी प्लेटफॉर्म',
      'navLogin': 'संस्थागत प्रवेश',
      'heroHead': 'किसानों का सशक्तिकरण।\nउपभोक्ताओं की सुरक्षा।',
      'heroSub': 'खेत से थाली तक संपूर्ण डिजिटल कस्टडी। अपरिवर्तनीय डेटाबेस द्वारा सुरक्षित बैच ट्रैकिंग।',
      'scanQrHero': 'क्यूआर कोड स्कैन करें',
      'newBatchHero': 'नया फसल लॉट बनाएं',
      'entityTitle': 'यूनिवर्सल संस्थागत पहुंच',
      'entitySub': 'समर्पित संचालन और कस्टडी टूल के लिए अपनी आपूर्ति-श्रृंखला श्रेणी चुनें',
      'roleFarmer': 'किसान / एफपीओ',
      'roleFarmerDesc': 'फसल लॉट निर्माण, क्रेट टैग, मंडी प्रेषण।',
      'roleMandi': 'मंडी आढ़ती / एपीएमसी',
      'roleMandiDesc': 'आवक प्राप्ति, गुणवत्ता ग्रेडिंग, लॉट विभाजन व नीलामी।',
      'roleCold': 'शीत गृह / गोदाम',
      'roleColdDesc': 'कस्टडी रसीद, तापमान निगरानी, शीत-श्रृंखला प्रेषण।',
      'roleProcessor': 'प्रसंस्करण इकाई',
      'roleProcessorDesc': 'कच्चा माल प्राप्ति, छंटाई, खुदरा पैकेजिंग।',
      'roleRetailer': 'थोक व खुदरा विक्रेता',
      'roleRetailerDesc': 'बिक्री केंद्र सत्यापन, खुदरा बिलिंग।',
      'roleAdmin': 'प्रशासक / सत्यापनकर्ता',
      'roleAdminDesc': 'इकाई सत्यापन, केवाईसी ऑडिट और क्यूआर आवंटन।',
      'loginBtn': 'के रूप में लॉगिन करें',
      'tabIncoming': 'आवक',
      'tabMyStock': 'मेरा स्टॉक',
      'tabWaiting': 'प्रतीक्षारत',
      'emptyIncoming': 'प्राप्ति की प्रतीक्षा में कोई आवक खेप नहीं है।',
      'emptyStock': 'कस्टडी में कोई सक्रिय उत्पाद बैच नहीं है।',
      'emptyWaiting': 'प्रतिपक्ष की पुष्टि के लिए कोई प्रेषित हैंडओवर लंबित नहीं है।',
      'receiveBatch': 'बैच प्राप्त करें',
      'dispatchBatch': 'बैच प्रेषित करें',
      'splitLot': 'लॉट विभाजित करें',
      'inspectQuality': 'गुणवत्ता जांचें',
      'recordWaste': 'नुकसान दर्ज करें',
      'recordSale': 'बिक्री दर्ज करें',
      'scanQr': 'क्यूआर स्कैन',
      'createBatch': 'बैच बनाएं',
      'trustTitle': 'राष्ट्रीय विश्वास एवं सत्यापन मानक',
      'trust1Title': 'क्रिप्टोग्राफ़िक केवल-जोड़ लेज़र',
      'trust1Desc': 'प्रत्येक फसल, प्रेषण और गुणवत्ता निरीक्षण SHA-256 हैश श्रृंखला और अपरिवर्तनीय डेटाबेस ट्रिगर्स द्वारा सुरक्षित है।',
      'trust2Title': 'शून्य व्यक्तिगत डेटा रिसाव',
      'trust2Desc': 'किसान की व्यक्तिगत पहचान, सटीक जीपीएस निर्देशांक और वाणिज्यिक मूल्य निर्धारण DPDP अधिनियम 2023 के तहत सुरक्षित हैं।',
      'trust3Title': 'पारस्परिक कस्टडी पुष्टि',
      'trust3Desc': 'उत्पाद स्वामित्व हस्तांतरण के लिए प्रेषक और प्राप्तकर्ता दोनों संचालकों के सत्यापन की आवश्यकता होती है।',
      'footerDev': 'प्रगत संगणन विकास केंद्र (सी-डैक / C-DAC) द्वारा विकसित',
      'footerGov': 'इलेक्ट्रॉनिकी एवं सूचना प्रौद्योगिकी मंत्रालय, भारत सरकार',
      'disclaimer': 'सूचना: रिकॉर्ड आपूर्ति-श्रृंखला प्रतिभागियों द्वारा दर्ज की गई जानकारी पर आधारित हैं। वे भौतिक पैकेज सामग्री को साबित नहीं करते हैं।',
      'dpdpLink': 'DPDP अधिनियम 2023 अनुपालन एवं शिकायत निवारण अधिकारी: grievance@annasutra.in',
    },
    'bn': {
      'brandTitle': 'অন্নসূত্র',
      'brandSubtitle': 'জাতীয় কৃষি-পণ্য ট্রেসেবিলিটি প্ল্যাটফর্ম',
      'navLogin': 'সংস্থা প্রবেশ',
      'heroHead': 'কৃষকের ক্ষমতায়ন।\nভোক্তার সুরক্ষা।',
      'heroSub': 'মাটি থেকে থালা পর্যন্ত ক্রিপ্টোগ্রাফিক সুরক্ষা। অপরিবর্তনীয় ডাটাবেসে ব্যাচ ট্র্যাকিং।',
      'scanQrHero': 'কিউআর কোড স্ক্যান',
      'newBatchHero': 'নতুন ফসল লট',
      'entityTitle': 'সার্বজনীন সংস্থা প্রবেশাধিকার',
      'entitySub': 'কাস্টডি কার্যক্রমের জন্য আপনার সরবরাহ-শৃঙ্খল স্তরটি নির্বাচন করুন',
      'roleFarmer': 'কৃষক / সমবায়',
      'roleFarmerDesc': 'ফসল লট তৈরি, ক্রেট ট্যাগ, মাণ্ডিতে প্রেরণ।',
      'roleMandi': 'মাণ্ডি ব্যবসায়ী',
      'roleMandiDesc': 'পণ্য গ্রহণ, গুণমান পরীক্ষা, লট ভাগ ও নিলাম।',
      'roleCold': 'হিমাগার / গুদাম',
      'roleColdDesc': 'সংরক্ষণ রসিদ, তাপমাত্রা নজরদারি, প্রেরণ।',
      'roleProcessor': 'খাদ্য প্রক্রিয়াকরণ',
      'roleProcessorDesc': 'কাঁচামাল গ্রহণ, বাছাই ও প্যাকেটজাতকরণ।',
      'roleRetailer': 'খুচরা বিক্রেতা',
      'roleRetailerDesc': 'বিক্রয় কেন্দ্র যাচাইকরণ, খুচরা বিক্রয় নথিভুক্ত।',
      'roleAdmin': 'প্রশাসক / যাচাইকারী',
      'roleAdminDesc': 'সংস্থা যাচাইকরণ, কেওয়াইসি অডিট এবং কিউআর বরাদ্দ।',
      'loginBtn': 'হিসেবে প্রবেশ করুন',
      'tabIncoming': 'আগত',
      'tabMyStock': 'আমার স্টক',
      'tabWaiting': 'অপেক্ষমাণ',
      'emptyIncoming': 'গ্রহণের অপেক্ষায় কোনো আগত চালান নেই।',
      'emptyStock': 'হেফাজতে কোনো সক্রিয় পণ্য ব্যাচ নেই।',
      'emptyWaiting': 'প্রতিপক্ষের নিশ্চিতকরণের অপেক্ষায় কোনো প্রেরণ নেই।',
      'receiveBatch': 'ব্যাচ গ্রহণ করুন',
      'dispatchBatch': 'ব্যাচ প্রেরণ করুন',
      'splitLot': 'লট ভাগ করুন',
      'inspectQuality': 'গুণমান পরীক্ষা করুন',
      'recordWaste': 'ক্ষতি নথিভুক্ত করুন',
      'recordSale': 'বিক্রি নথিভুক্ত করুন',
      'scanQr': 'কিউআর স্ক্যান',
      'createBatch': 'ব্যাচ তৈরি',
      'trustTitle': 'জাতীয় আস্থা ও যাচাইকরণ মানদণ্ড',
      'trust1Title': 'ক্রিপ্টোগ্রাফিক কেবল-সংযোজন খতিয়ান',
      'trust1Desc': 'প্রতিটি ফসল তোলা, প্রেরণ এবং মান পরিদর্শন SHA-256 হ্যাশ চেইন এবং অপরিবর্তনীয় ডাটাবেস ট্রিগার দ্বারা সুরক্ষিত।',
      'trust2Title': 'শূন্য ব্যক্তিগত তথ্য প্রকাশ',
      'trust2Desc': 'কৃষকের ব্যক্তিগত পরিচয়, খামারের সুনির্দিষ্ট জিপিএস স্থানাঙ্ক এবং বাণিজ্যিক মূল্য ডিপিডিপি আইন ২০২৩ এর অধীনে সুরক্ষিত।',
      'trust3Title': 'পারস্পরিক হেফাজত নিশ্চিতকরণ',
      'trust3Desc': 'পণ্য মালিকানা হস্তান্তরের জন্য প্রেরণকারী এবং গ্রহণকারী উভয় পরিচালকের যাচাইকৃত সম্মতির প্রয়োজন।',
      'footerDev': 'সেন্টার ফর ডেভেলপমেন্ট অব অ্যাডভান্সড কম্পিউটিং (C-DAC) দ্বারা তৈরি',
      'footerGov': 'ইলেকট্রনিক্স ও তথ্য প্রযুক্তি মন্ত্রক, ভারত সরকার',
      'disclaimer': 'বিজ্ঞপ্তি: রেকর্ডগুলি সরবরাহ-শৃঙ্খল অংশগ্রহণকারীদের দেওয়া তথ্যের উপর ভিত্তি করে তৈরি। এটি প্যাকেজের সামগ্রী প্রমাণ করে না।',
      'dpdpLink': 'DPDP আইন ২০২৩ অনুপালন ও অভিযোগ নিষ্পত্তি কর্মকর্তা: grievance@annasutra.in',
    },
  };

  String _t(String key) {
    return _strings[_selectedLang]?[key] ?? _strings['en']![key] ?? key;
  }

  String _roleDisplayName(String? orgType) {
    final code = (orgType ?? 'PRODUCER').toUpperCase();
    if (_selectedLang == 'hi') {
      switch (code) {
        case 'FARMER':
        case 'PRODUCER':
          return 'किसान';
        case 'MANDI':
        case 'AGGREGATOR':
          return 'मंडी';
        case 'COLD_STORAGE':
          return 'शीत गृह';
        case 'PROCESSOR':
          return 'प्रसंस्करण';
        case 'RETAILER':
          return 'खुदरा विक्रेता';
        case 'ADMIN':
          return 'प्रशासक';
        default:
          return code;
      }
    } else if (_selectedLang == 'bn') {
      switch (code) {
        case 'FARMER':
        case 'PRODUCER':
          return 'কৃষক';
        case 'MANDI':
        case 'AGGREGATOR':
          return 'মাণ্ডি';
        case 'COLD_STORAGE':
          return 'হিমাগার';
        case 'PROCESSOR':
          return 'প্রক্রিয়াকরণ';
        case 'RETAILER':
          return 'খুচরা বিক্রেতা';
        case 'ADMIN':
          return 'প্রশাসক';
        default:
          return code;
      }
    }
    switch (code) {
      case 'FARMER':
      case 'PRODUCER':
        return 'Producer';
      case 'MANDI':
      case 'AGGREGATOR':
        return 'Mandi';
      case 'COLD_STORAGE':
        return 'Cold Storage';
      case 'PROCESSOR':
        return 'Processor';
      case 'RETAILER':
        return 'Retailer';
      case 'ADMIN':
        return 'Admin';
      default:
        return 'Producer';
    }
  }

  String _formatUserBadge(AuthState authState) {
    final roleLabel = _roleDisplayName(authState.orgType);
    final rawPhone = (authState.phone ?? '').replaceAll(RegExp(r'\D'), '');
    if (rawPhone.length >= 4) {
      final last4 = rawPhone.substring(rawPhone.length - 4);
      return '$roleLabel (X$last4)';
    }
    return roleLabel;
  }

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _updateClock();
    _clockTimer = Timer.periodic(const Duration(seconds: 1), (_) => _updateClock());
    _fetchWeather();
  }

  @override
  void dispose() {
    _clockTimer?.cancel();
    _tabController.dispose();
    super.dispose();
  }

  void _updateClock() {
    final now = DateTime.now();
    final timeStr = DateFormat('hh:mm a').format(now);
    final dateStr = DateFormat('EEE, dd MMM').format(now);
    if (mounted) {
      setState(() {
        _dateTimeText = '$timeStr • $dateStr';
      });
    }
  }

  Future<void> _fetchWeather() async {
    try {
      final dio = Dio(BaseOptions(
        connectTimeout: const Duration(seconds: 4),
        receiveTimeout: const Duration(seconds: 4),
      ));
      final ipRes = await dio.get('https://ipwho.is/');
      if (ipRes.statusCode == 200 && ipRes.data is Map) {
        final data = ipRes.data as Map;
        final lat = data['latitude'] ?? 22.57;
        final lon = data['longitude'] ?? 88.36;
        final city = data['city'] ?? 'Local';

        final weatherRes = await dio.get(
          'https://api.open-meteo.com/v1/forecast?latitude=$lat&longitude=$lon&current=temperature_2m,weather_code&timezone=auto',
        );
        if (weatherRes.statusCode == 200 && weatherRes.data is Map) {
          final weatherData = weatherRes.data as Map;
          final current = weatherData['current'];
          final temp = current?['temperature_2m']?.round() ?? 28;
          final code = current?['weather_code'] ?? 1;

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
    final SyncState syncState = ref.watch(syncControllerProvider);
    final theme = Theme.of(context);
    final screenWidth = MediaQuery.of(context).size.width;
    final isDesktop = screenWidth >= 900;

    return Scaffold(
      backgroundColor: const Color(0xFFF6F8F5),
      body: SafeArea(
        child: Column(
          children: [
            // 1. TOP UTILITY HEADER
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
                        if (!authState.isAuthenticated) ...[
                          _buildHeroBanner(context, isDesktop),
                          _buildUniversalEntityLoginSection(context, authState),
                          const SizedBox(height: 16),
                          _buildNationalTrustStandards(context),
                        ],
                        if (authState.isAuthenticated) ...[
                          _buildSyncAndVerificationAlerts(context, authState, syncState),
                          _buildOperationalConsole(context, theme),
                          const SizedBox(height: 16),
                          _buildAccessibleActionButtons(context),
                        ],
                        const SizedBox(height: 16),
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
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  _t('brandTitle'),
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.w900,
                    letterSpacing: -0.3,
                  ),
                ),
                Text(
                  _t('brandSubtitle'),
                  style: const TextStyle(
                    color: Color(0xFFCBD5E1),
                    fontSize: 11,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
          if (authState.isAuthenticated) ...[
            InkWell(
              onTap: () => _showAccountDialog(context),
              borderRadius: BorderRadius.circular(8),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: const Color(0xFF14532D),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: const Color(0xFF22C55E), width: 1),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.verified_user, color: Color(0xFF86EFAC), size: 16),
                    const SizedBox(width: 6),
                    Text(
                      _formatUserBadge(authState),
                      style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
              ),
            ),
          ] else ...[
            ElevatedButton.icon(
              onPressed: () => context.push('/login'),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFFE67E22),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                minimumSize: const Size(80, 36),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
              ),
              icon: const Icon(Icons.login, size: 16),
              label: Text(_t('navLogin'), style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildHeroBanner(BuildContext context, bool isDesktop) {
    return Container(
      margin: EdgeInsets.all(isDesktop ? 16.0 : 12.0),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        boxShadow: const [
          BoxShadow(color: Colors.black12, blurRadius: 10, offset: Offset(0, 4)),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: Stack(
          children: [
            Positioned.fill(
              child: Image.asset(
                'assets/images/hero_farm.jpg',
                fit: BoxFit.cover,
                alignment: Alignment.centerRight,
                errorBuilder: (_, __, ___) => Container(color: const Color(0xFF0B3D2E)),
              ),
            ),
            Positioned.fill(
              child: DecoratedBox(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.centerLeft,
                    end: Alignment.centerRight,
                    colors: [
                      const Color(0xFF07271D).withOpacity(0.96),
                      const Color(0xFF0B3D2E).withOpacity(0.90),
                      const Color(0xFF0B3D2E).withOpacity(0.60),
                      Colors.black.withOpacity(0.35),
                    ],
                    stops: const [0.0, 0.45, 0.75, 1.0],
                  ),
                ),
              ),
            ),
            Padding(
              padding: EdgeInsets.symmetric(
                horizontal: isDesktop ? 32.0 : 20.0,
                vertical: isDesktop ? 32.0 : 24.0,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    _t('heroHead'),
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: isDesktop ? 32 : 24,
                      fontWeight: FontWeight.w900,
                      height: 1.15,
                      letterSpacing: -0.5,
                    ),
                  ),
                  const SizedBox(height: 8),
                  ConstrainedBox(
                    constraints: BoxConstraints(maxWidth: isDesktop ? 600 : double.infinity),
                    child: Text(
                      _t('heroSub'),
                      style: const TextStyle(
                        color: Color(0xFFE2E8F0),
                        fontSize: 13,
                        fontWeight: FontWeight.w400,
                        height: 1.4,
                      ),
                    ),
                  ),
                  const SizedBox(height: 18),
                  Wrap(
                    spacing: 12,
                    runSpacing: 10,
                    children: [
                      ElevatedButton.icon(
                        onPressed: () {
                          context.push('/receive');
                        },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFFE67E22),
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
                          elevation: 2,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                        ),
                        icon: const Icon(Icons.qr_code_scanner, size: 18),
                        label: Text(_t('scanQrHero'), style: const TextStyle(fontWeight: FontWeight.bold)),
                      ),
                      OutlinedButton.icon(
                        onPressed: () {
                          context.push('/create-batch');
                        },
                        style: OutlinedButton.styleFrom(
                          foregroundColor: Colors.white,
                          side: const BorderSide(color: Colors.white, width: 1.5),
                          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                        ),
                        icon: const Icon(Icons.add_box, size: 18),
                        label: Text(_t('newBatchHero'), style: const TextStyle(fontWeight: FontWeight.bold)),
                      ),
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

  Widget _buildNationalTrustStandards(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFE2E8F0)),
        boxShadow: const [
          BoxShadow(
            color: Color(0x0A000000),
            blurRadius: 8,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.verified_user, color: Color(0xFF0B3D2E), size: 22),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  _t('trustTitle'),
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w900,
                    color: Color(0xFF0F172A),
                    letterSpacing: -0.3,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          _buildTrustItem(Icons.verified_user_outlined, _t('trust1Title'), _t('trust1Desc')),
          const Divider(height: 24, thickness: 1, color: Color(0xFFF1F5F9)),
          _buildTrustItem(Icons.lock_outline, _t('trust2Title'), _t('trust2Desc')),
          const Divider(height: 24, thickness: 1, color: Color(0xFFF1F5F9)),
          _buildTrustItem(Icons.balance_outlined, _t('trust3Title'), _t('trust3Desc')),
        ],
      ),
    );
  }

  Widget _buildTrustItem(IconData iconData, String title, String description) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: const Color(0xFFF0FDF4),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: const Color(0xFFBBF7D0)),
          ),
          child: Icon(iconData, color: const Color(0xFF0B3D2E), size: 20),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: RichText(
            text: TextSpan(
              style: const TextStyle(
                fontSize: 13,
                color: Color(0xFF475569),
                height: 1.45,
              ),
              children: [
                TextSpan(
                  text: '$title: ',
                  style: const TextStyle(
                    fontWeight: FontWeight.w800,
                    color: Color(0xFF0F172A),
                  ),
                ),
                TextSpan(text: description),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildSyncAndVerificationAlerts(BuildContext context, AuthState authState, SyncState syncState) {
    final registeredName = (authState.orgName != null && authState.orgName!.trim().isNotEmpty)
        ? authState.orgName!
        : _roleDisplayName(authState.orgType);
    return Column(
      children: [
        Container(
          margin: const EdgeInsets.fromLTRB(16, 12, 16, 4),
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
          decoration: BoxDecoration(
            color: const Color(0xFFF0FDF4),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: const Color(0xFF86EFAC)),
          ),
          child: Row(
            children: [
              const Icon(Icons.verified_user_outlined, color: Color(0xFF15803D), size: 18),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  registeredName,
                  style: const TextStyle(
                    color: Color(0xFF14532D),
                    fontWeight: FontWeight.w800,
                    fontSize: 13,
                  ),
                ),
              ),
              Text(
                _formatUserBadge(authState),
                style: const TextStyle(
                  color: Color(0xFF15803D),
                  fontWeight: FontWeight.w700,
                  fontSize: 11,
                ),
              ),
            ],
          ),
        ),
        if (authState.isAuthenticated && authState.orgVerification == 'PENDING')
          Container(
            margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            decoration: BoxDecoration(
              color: Colors.amber.shade100,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.amber.shade400),
            ),
            child: Row(
              children: [
                Icon(Icons.warning_amber_rounded, color: Colors.amber.shade900, size: 22),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'Organisation Pending Verification: Batch operations are disabled until approved.',
                    style: TextStyle(
                      color: Colors.amber.shade900,
                      fontWeight: FontWeight.w600,
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
          ),
        Container(
          margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
          decoration: BoxDecoration(
            color: syncState.pendingCount > 0 ? const Color(0xFFFFFBEB) : const Color(0xFFF0FDF4),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(
              color: syncState.pendingCount > 0 ? const Color(0xFFFCD34D) : const Color(0xFFBBF7D0),
            ),
          ),
          child: Row(
            children: [
              Icon(
                syncState.pendingCount > 0 ? Icons.cloud_queue : Icons.cloud_done,
                color: syncState.pendingCount > 0 ? Colors.amber.shade800 : Colors.green.shade800,
                size: 18,
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  syncState.pendingCount > 0
                      ? 'Offline Queue: ${syncState.pendingCount} events waiting to sync'
                      : 'Sync Status: All events synced',
                  style: TextStyle(
                    color: syncState.pendingCount > 0 ? Colors.amber.shade900 : Colors.green.shade900,
                    fontWeight: FontWeight.w600,
                    fontSize: 12,
                  ),
                ),
              ),
              TextButton.icon(
                onPressed: syncState.isSyncing
                    ? null
                    : () => ref.read(syncControllerProvider.notifier).syncNow(),
                icon: syncState.isSyncing
                    ? const SizedBox(
                        width: 12,
                        height: 12,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.sync, size: 14),
                label: Text(
                  syncState.isSyncing ? 'Syncing...' : 'Sync Now',
                  style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildUniversalEntityLoginSection(BuildContext context, AuthState authState) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFE2E8F0)),
        boxShadow: const [
          BoxShadow(color: Colors.black12, blurRadius: 4, offset: Offset(0, 1)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(6),
                decoration: BoxDecoration(
                  color: const Color(0xFF0B3D2E).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(Icons.hub_outlined, color: Color(0xFF0B3D2E), size: 20),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      _t('entityTitle'),
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w800,
                        color: Color(0xFF0F172A),
                      ),
                    ),
                    Text(
                      _t('entitySub'),
                      style: const TextStyle(
                        fontSize: 12,
                        color: Color(0xFF64748B),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          LayoutBuilder(
            builder: (context, constraints) {
              final isWide = constraints.maxWidth > 700;
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
                    width: isWide ? (constraints.maxWidth - 20) / 3 : constraints.maxWidth,
                    currentRole: authState.orgType,
                  ),
                  _buildEntityCard(
                    context: context,
                    roleKey: 'MANDI',
                    icon: Icons.storefront,
                    title: _t('roleMandi'),
                    description: _t('roleMandiDesc'),
                    width: isWide ? (constraints.maxWidth - 20) / 3 : constraints.maxWidth,
                    currentRole: authState.orgType,
                  ),
                  _buildEntityCard(
                    context: context,
                    roleKey: 'COLD_STORAGE',
                    icon: Icons.ac_unit,
                    title: _t('roleCold'),
                    description: _t('roleColdDesc'),
                    width: isWide ? (constraints.maxWidth - 20) / 3 : constraints.maxWidth,
                    currentRole: authState.orgType,
                  ),
                  _buildEntityCard(
                    context: context,
                    roleKey: 'PROCESSOR',
                    icon: Icons.precision_manufacturing,
                    title: _t('roleProcessor'),
                    description: _t('roleProcessorDesc'),
                    width: isWide ? (constraints.maxWidth - 20) / 3 : constraints.maxWidth,
                    currentRole: authState.orgType,
                  ),
                  _buildEntityCard(
                    context: context,
                    roleKey: 'RETAILER',
                    icon: Icons.shopping_basket,
                    title: _t('roleRetailer'),
                    description: _t('roleRetailerDesc'),
                    width: isWide ? (constraints.maxWidth - 20) / 3 : constraints.maxWidth,
                    currentRole: authState.orgType,
                  ),
                  _buildEntityCard(
                    context: context,
                    roleKey: 'ADMIN',
                    icon: Icons.verified_user_outlined,
                    title: _t('roleAdmin'),
                    description: _t('roleAdminDesc'),
                    width: isWide ? (constraints.maxWidth - 20) / 3 : constraints.maxWidth,
                    currentRole: authState.orgType,
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
    required String? currentRole,
  }) {
    final bool isActive = currentRole == roleKey;

    return Container(
      width: width,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isActive ? const Color(0xFFF0FDF4) : const Color(0xFFFAFAFA),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(
          color: isActive ? const Color(0xFF22C55E) : const Color(0xFFE2E8F0),
          width: isActive ? 1.5 : 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: isActive ? const Color(0xFF16A34A) : const Color(0xFF0B3D2E),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(icon, color: Colors.white, size: 18),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  title,
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            description,
            style: const TextStyle(fontSize: 11, color: Color(0xFF64748B), height: 1.3),
          ),
          const SizedBox(height: 10),
          SizedBox(
            width: double.infinity,
            height: 38,
            child: ElevatedButton.icon(
              onPressed: () {
                context.push('/login');
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: isActive ? const Color(0xFF15803D) : const Color(0xFF0B3D2E),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(horizontal: 10),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
              ),
              icon: Icon(isActive ? Icons.check_circle : Icons.login, size: 16),
              label: Text(
                '${_t('loginBtn')} $title',
                style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildOperationalConsole(BuildContext context, ThemeData theme) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFE2E8F0)),
        boxShadow: const [
          BoxShadow(color: Colors.black12, blurRadius: 4, offset: Offset(0, 1)),
        ],
      ),
      child: Column(
        children: [
          Container(
            decoration: const BoxDecoration(
              color: Color(0xFF0B3D2E),
              borderRadius: BorderRadius.vertical(top: Radius.circular(13)),
            ),
            child: TabBar(
              controller: _tabController,
              labelColor: const Color(0xFFFCD34D),
              unselectedLabelColor: Colors.white70,
              indicatorColor: const Color(0xFFE67E22),
              indicatorWeight: 3.5,
              labelStyle: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
              tabs: [
                Tab(text: _t('tabIncoming')),
                Tab(text: _t('tabMyStock')),
                Tab(text: _t('tabWaiting')),
              ],
            ),
          ),
          SizedBox(
            height: 300,
            child: TabBarView(
              controller: _tabController,
              children: [
                _buildIncomingTabContent(context),
                _buildMyStockTabContent(context),
                _buildWaitingTabContent(context),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildIncomingTabContent(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.move_to_inbox_outlined, size: 42, color: Color(0xFF64748B)),
            const SizedBox(height: 12),
            Text(
              _t('emptyIncoming'),
              style: const TextStyle(fontSize: 14, color: Color(0xFF475569), fontWeight: FontWeight.w600),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: () => context.push('/receive'),
              icon: const Icon(Icons.download_done, size: 18),
              label: Text(_t('receiveBatch')),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF0B3D2E),
                foregroundColor: Colors.white,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMyStockTabContent(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.inventory_2_outlined, size: 42, color: Color(0xFF64748B)),
            const SizedBox(height: 12),
            Text(
              _t('emptyStock'),
              style: const TextStyle(fontSize: 14, color: Color(0xFF475569), fontWeight: FontWeight.w600),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              alignment: WrapAlignment.center,
              children: [
                ElevatedButton.icon(
                  onPressed: () => context.push('/create-batch'),
                  icon: const Icon(Icons.add_box_outlined, size: 16),
                  label: Text(_t('createBatch')),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF0B3D2E),
                    foregroundColor: Colors.white,
                  ),
                ),
                OutlinedButton.icon(
                  onPressed: () => context.push('/dispatch'),
                  icon: const Icon(Icons.upload, size: 16),
                  label: Text(_t('dispatchBatch')),
                ),
                OutlinedButton.icon(
                  onPressed: () => context.push('/split'),
                  icon: const Icon(Icons.call_split, size: 16),
                  label: Text(_t('splitLot')),
                ),
                OutlinedButton.icon(
                  onPressed: () => context.push('/inspection'),
                  icon: const Icon(Icons.verified_outlined, size: 16),
                  label: Text(_t('inspectQuality')),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildWaitingTabContent(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.hourglass_empty_rounded, size: 42, color: Color(0xFF64748B)),
            const SizedBox(height: 12),
            Text(
              _t('emptyWaiting'),
              style: const TextStyle(fontSize: 14, color: Color(0xFF475569), fontWeight: FontWeight.w600),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAccessibleActionButtons(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16.0),
      child: Row(
        children: [
          Expanded(
            child: ElevatedButton.icon(
              onPressed: () {
                context.push('/receive');
              },
              style: ElevatedButton.styleFrom(
                minimumSize: const Size(120, 52),
                backgroundColor: const Color(0xFF0B3D2E),
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              icon: const Icon(Icons.qr_code_scanner, size: 22),
              label: Text(_t('scanQr'), style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: OutlinedButton.icon(
              onPressed: () {
                context.push('/create-batch');
              },
              style: OutlinedButton.styleFrom(
                minimumSize: const Size(120, 52),
                foregroundColor: const Color(0xFF0B3D2E),
                side: const BorderSide(color: Color(0xFF0B3D2E), width: 1.8),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              icon: const Icon(Icons.add_box, size: 22),
              label: Text(_t('createBatch'), style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildOfficialFooter(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(top: 16),
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
      decoration: const BoxDecoration(
        color: Color(0xFF07271D),
        border: Border(top: BorderSide(color: Color(0xFF144D3B), width: 1.5)),
      ),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            margin: const EdgeInsets.only(bottom: 14),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.06),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.white12),
            ),
            child: const Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.phone_in_talk_outlined, color: Color(0xFFFCD34D), size: 13),
                    SizedBox(width: 5),
                    Text('Kisan Helpline: 1800-180-1551', style: TextStyle(color: Color(0xFFFCD34D), fontSize: 10.5, fontWeight: FontWeight.bold)),
                  ],
                ),
                Text('|', style: TextStyle(color: Colors.white30)),
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.shield_outlined, color: Color(0xFFE2E8F0), size: 13),
                    SizedBox(width: 5),
                    Text('Consumer Helpline: 1915', style: TextStyle(color: Color(0xFFE2E8F0), fontSize: 10.5, fontWeight: FontWeight.bold)),
                  ],
                ),
              ],
            ),
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              ClipRRect(
                borderRadius: BorderRadius.circular(16),
                child: Image.asset(
                  'assets/images/annasutra_emblem.jpg',
                  width: 32,
                  height: 32,
                  errorBuilder: (_, __, ___) => const Icon(Icons.grain, color: Colors.amber),
                ),
              ),
              const SizedBox(width: 12),
              Text(
                _t('brandTitle'),
                style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16),
              ),
              const SizedBox(width: 20),
              Container(width: 1, height: 24, color: Colors.white24),
              const SizedBox(width: 20),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Image.asset(
                  'assets/images/cdac_logo.png',
                  height: 22,
                  errorBuilder: (_, __, ___) => const Icon(Icons.memory, color: Color(0xFF002080)),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            _t('footerDev'),
            style: const TextStyle(color: Color(0xFFE2E8F0), fontSize: 12, fontWeight: FontWeight.w600),
            textAlign: TextAlign.center,
          ),
          Text(
            _t('footerGov'),
            style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 11),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 14),
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: Colors.black.withOpacity(0.25),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.white12),
            ),
            child: Text(
              _t('disclaimer'),
              style: const TextStyle(fontSize: 11, color: Color(0xFFCBD5E1), height: 1.3),
              textAlign: TextAlign.center,
            ),
          ),
          const SizedBox(height: 10),
          TextButton(
            onPressed: () => DpdpConsentDialog.show(context),
            child: Text(
              _t('dpdpLink'),
              style: const TextStyle(color: Color(0xFFFCD34D), fontSize: 11),
              textAlign: TextAlign.center,
            ),
          ),
        ],
      ),
    );
  }

  void _showAccountDialog(BuildContext context) {
    final authState = ref.read(authControllerProvider);
    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('User Account'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Entity: ${authState.orgName ?? authState.orgType ?? "Authenticated Operator"}', style: const TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 4),
            Text('Phone: ${authState.phone ?? "-"}'),
            const SizedBox(height: 4),
            Text('Status: ${authState.orgVerification ?? "VERIFIED"}', style: const TextStyle(color: Colors.green, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            const Text('Authenticated with cryptographic key-pair.', style: TextStyle(fontSize: 12, color: Colors.black54)),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(ctx);
              ref.read(authControllerProvider.notifier).logout();
            },
            child: const Text('Log Out', style: TextStyle(color: Colors.red)),
          ),
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }
}
