import 'dart:io' show Platform;
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/harvest_lot.dart';
import 'package:annasutra_mobile/data/platform/platform_providers.dart';
import 'package:annasutra_mobile/domain/platform/local_database.dart';

/// Official 10 Product Category Codes (Mentor's Specification)
const Map<String, String> kProductCategoryCodes = {
  'FG': 'Food grains & cereals (FG)',
  'PU': 'Pulses (PU)',
  'OI': 'Oilseeds (OI)',
  'FR': 'Fruits (FR)',
  'VG': 'Vegetables (VG)',
  'SP': 'Spices (SP)',
  'CC': 'Commercial Crops (CC)',
  'LS': 'Livestock (LS)',
  'SC': 'Special Crops (SC)',
  'OT': 'Others (OT)',
};

final lotsControllerProvider =
    StateNotifierProvider<LotsController, LotsState>((ref) {
  final localDb = ref.watch(localDatabaseProvider);
  return LotsController(localDb: localDb);
});

class LotsState {
  final List<HarvestLot> lots;
  final List<HarvestLot> incomingHandovers;
  final bool isLoading;
  final String searchQuery;
  final String selectedCustody; // 'ALL', 'IN_CUSTODY', 'IN_TRANSIT', 'CLOSED'
  final String selectedCrop; // 'ALL', or crop name
  final String selectedPayment; // 'ALL', 'PENDING', 'ADVANCE', 'SETTLED'
  final String sortOrder; // '-created_at', 'created_at', '-qty', 'qty'
  final String analyticsPeriod; // 'ALL', '30', '90', 'SEASON'

  const LotsState({
    this.lots = const [],
    this.incomingHandovers = const [],
    this.isLoading = false,
    this.searchQuery = '',
    this.selectedCustody = 'ALL',
    this.selectedCrop = 'ALL',
    this.selectedPayment = 'ALL',
    this.sortOrder = '-created_at',
    this.analyticsPeriod = 'ALL',
  });

  LotsState copyWith({
    List<HarvestLot>? lots,
    List<HarvestLot>? incomingHandovers,
    bool? isLoading,
    String? searchQuery,
    String? selectedCustody,
    String? selectedCrop,
    String? selectedPayment,
    String? sortOrder,
    String? analyticsPeriod,
  }) {
    return LotsState(
      lots: lots ?? this.lots,
      incomingHandovers: incomingHandovers ?? this.incomingHandovers,
      isLoading: isLoading ?? this.isLoading,
      searchQuery: searchQuery ?? this.searchQuery,
      selectedCustody: selectedCustody ?? this.selectedCustody,
      selectedCrop: selectedCrop ?? this.selectedCrop,
      selectedPayment: selectedPayment ?? this.selectedPayment,
      sortOrder: sortOrder ?? this.sortOrder,
      analyticsPeriod: analyticsPeriod ?? this.analyticsPeriod,
    );
  }

  // Filtered lots for the UI list
  List<HarvestLot> get filteredLots {
    var result = lots.where((lot) {
      if (searchQuery.isNotEmpty) {
        final query = searchQuery.toLowerCase();
        final text =
            '${lot.publicCode} ${lot.productCategoryCode} ${lot.crop} ${lot.variety} ${lot.originPlotName} ${lot.qualityGrade}'
                .toLowerCase();
        if (!text.contains(query)) {
          return false;
        }
      }
      if (selectedCustody != 'ALL') {
        if (selectedCustody == 'IN_CUSTODY' &&
            !(lot.state == 'IN_CUSTODY' || lot.state == 'CREATED')) {
          return false;
        }
        if (selectedCustody == 'IN_TRANSIT' && lot.state != 'IN_TRANSIT') {
          return false;
        }
        if (selectedCustody == 'CLOSED' &&
            lot.state != 'CLOSED' &&
            !lot.isRetailerVerified) {
          return false;
        }
      }
      if (selectedCrop != 'ALL' &&
          lot.crop.toLowerCase() != selectedCrop.toLowerCase()) {
        return false;
      }
      if (selectedPayment != 'ALL' && lot.paymentStatus != selectedPayment) {
        return false;
      }
      return true;
    }).toList();

    result.sort((a, b) {
      if (sortOrder == 'created_at') {
        return a.createdAt.compareTo(b.createdAt);
      } else if (sortOrder == '-qty') {
        return b.netQtyKg.compareTo(a.netQtyKg);
      } else if (sortOrder == 'qty') {
        return a.netQtyKg.compareTo(b.netQtyKg);
      }
      return b.createdAt.compareTo(a.createdAt);
    });

    return result;
  }

  // Top KPI Metrics
  int get totalLotsCount => lots.length;
  int get inCustodyCount => lots
      .where((l) =>
          (l.state == 'IN_CUSTODY' || l.state == 'CREATED') &&
          l.currentCustodianRole == 'PRODUCER')
      .length;
  int get inTransitCount => lots.where((l) => l.state == 'IN_TRANSIT').length;
  int get retailerVerifiedCount =>
      lots.where((l) => l.isRetailerVerified).length;
  double get totalWeightKg => lots.fold(0.0, (sum, l) => sum + l.netQtyKg);
  double get totalValuation =>
      lots.fold(0.0, (sum, l) => sum + l.estimatedValue);

  // Analytics Metrics
  Map<String, double> get cropVolumeDistribution {
    final Map<String, double> map = {};
    for (var lot in lots) {
      map[lot.crop] = (map[lot.crop] ?? 0.0) + lot.netQtyKg;
    }
    return map;
  }

  Map<String, double> get cropValuationDistribution {
    final Map<String, double> map = {};
    for (var lot in lots) {
      map[lot.crop] = (map[lot.crop] ?? 0.0) + lot.estimatedValue;
    }
    return map;
  }

  Map<String, double> get custodyFunnel {
    final Map<String, double> map = {
      'In Farm Custody': 0.0,
      'In Transit': 0.0,
      'Supply-Chain Custody': 0.0,
      'Retailer Verified': 0.0,
    };
    for (var lot in lots) {
      if (lot.isRetailerVerified) {
        map['Retailer Verified'] =
            (map['Retailer Verified'] ?? 0) + lot.netQtyKg;
      } else if (lot.state == 'IN_TRANSIT') {
        map['In Transit'] = (map['In Transit'] ?? 0) + lot.netQtyKg;
      } else if (lot.currentCustodianRole == 'PRODUCER') {
        map['In Farm Custody'] = (map['In Farm Custody'] ?? 0) + lot.netQtyKg;
      } else {
        map['Supply-Chain Custody'] =
            (map['Supply-Chain Custody'] ?? 0) + lot.netQtyKg;
      }
    }
    return map;
  }

  Map<String, double> get paymentSettlementStats {
    final Map<String, double> map = {
      'SETTLED': 0.0,
      'ADVANCE': 0.0,
      'PENDING': 0.0,
    };
    for (var lot in lots) {
      final s = lot.paymentStatus;
      if (map.containsKey(s)) {
        map[s] = (map[s] ?? 0.0) + lot.estimatedValue;
      } else {
        map['PENDING'] = (map['PENDING'] ?? 0.0) + lot.estimatedValue;
      }
    }
    return map;
  }
}

class LotsController extends StateNotifier<LotsState> {
  final LocalDatabase _localDb;
  static const String _baseUrl = 'https://annasutra.vercel.app';

  LotsController({required LocalDatabase localDb})
      : _localDb = localDb,
        super(const LotsState());

  bool get _isFlutterTest =>
      !kIsWeb && Platform.environment.containsKey('FLUTTER_TEST');

  /// Fetch real harvest lots and incoming handovers from backend API
  Future<void> fetchRemoteLots({String? accessToken, String? phone}) async {
    if (_isFlutterTest || accessToken == null || accessToken.isEmpty) return;

    state = state.copyWith(isLoading: true);
    try {
      final dio = Dio(BaseOptions(
        baseUrl: _baseUrl,
        connectTimeout: const Duration(seconds: 8),
        receiveTimeout: const Duration(seconds: 8),
        headers: {
          'Authorization': 'Bearer $accessToken',
          if (phone != null && phone.isNotEmpty) 'X-Entity-Phone': phone,
        },
      ));

      final res = await dio.get<dynamic>('/api/v1/lots/');
      List<HarvestLot> loadedLots = [];
      if (res.statusCode == 200 && res.data is Map) {
        final rawList = (res.data as Map)['results'] ??
            (res.data as Map)['lots'] ??
            <dynamic>[];
        if (rawList is List) {
          loadedLots = rawList
              .whereType<Map<dynamic, dynamic>>()
              .map((m) => HarvestLot.fromJson(Map<String, dynamic>.from(m)))
              .toList();
        }
      }

      List<HarvestLot> incomingList = [];
      try {
        final incRes =
            await dio.get<dynamic>('/api/v1/lots/handovers/incoming');
        if (incRes.statusCode == 200 && incRes.data is Map) {
          final rawInc = (incRes.data as Map)['pending_requests'] ??
              (incRes.data as Map)['incoming_requests'] ??
              <dynamic>[];
          if (rawInc is List) {
            incomingList = rawInc
                .whereType<Map<dynamic, dynamic>>()
                .map((m) => HarvestLot.fromJson(Map<String, dynamic>.from(m)))
                .toList();
          }
        }
      } catch (_) {}

      state = state.copyWith(
        lots: loadedLots,
        incomingHandovers: incomingList,
        isLoading: false,
      );
    } catch (_) {
      state = state.copyWith(isLoading: false);
    }
  }

  void addLot(HarvestLot newLot) {
    state = state.copyWith(lots: [newLot, ...state.lots]);
    _localDb.saveQueuedEvent({
      'event_type': 'LOT_CREATED',
      'public_code': newLot.publicCode,
      'payload': newLot.toJson(),
      'timestamp': DateTime.now().toIso8601String(),
    });
  }

  void updateLot(HarvestLot updatedLot) {
    final list = state.lots.map((l) {
      if (l.publicCode == updatedLot.publicCode) {
        return updatedLot;
      }
      return l;
    }).toList();
    state = state.copyWith(lots: list);
    _localDb.saveQueuedEvent({
      'event_type': 'LOT_UPDATED',
      'public_code': updatedLot.publicCode,
      'payload': updatedLot.toJson(),
      'timestamp': DateTime.now().toIso8601String(),
    });
  }

  /// Request 2-Way Custody Handover to Next Party (Aggregator, Wholesaler, Distributor, Retailer)
  Future<void> requestCustodyHandover(
    String publicCode, {
    required String targetRole,
    required String targetName,
    required String targetPhone,
    String vehicleNo = '',
    double? declaredQtyKg,
    String? accessToken,
    String? senderPhone,
  }) async {
    final pin =
        (100000 + (DateTime.now().microsecondsSinceEpoch % 900000)).toString();
    final pendingMap = <String, dynamic>{
      'status': 'PENDING_ACCEPTANCE',
      'target_role': targetRole,
      'target_name': targetName,
      'target_phone': targetPhone,
      'vehicle_no': vehicleNo,
      'handover_pin': pin,
      'requested_at': DateTime.now().toIso8601String(),
    };

    if (!_isFlutterTest && accessToken != null && accessToken.isNotEmpty) {
      try {
        final dio = Dio(BaseOptions(
          baseUrl: _baseUrl,
          headers: {
            'Authorization': 'Bearer $accessToken',
            if (senderPhone != null) 'X-Entity-Phone': senderPhone,
          },
        ));
        final res = await dio.post<dynamic>(
          '/api/v1/lots/$publicCode/handover-request',
          data: {
            'target_role': targetRole,
            'target_name': targetName,
            'target_phone': targetPhone,
            'vehicle_no': vehicleNo,
            if (declaredQtyKg != null) 'declared_qty_kg': declaredQtyKg,
          },
        );
        if ((res.statusCode == 200 || res.statusCode == 201) &&
            res.data is Map) {
          final updated =
              HarvestLot.fromJson(Map<String, dynamic>.from(res.data as Map));
          updateLot(updated);
          return;
        }
      } catch (_) {}
    }

    final list = state.lots.map((l) {
      if (l.publicCode == publicCode) {
        return l.copyWith(
          state: 'IN_TRANSIT',
          vehicleNo: vehicleNo.isNotEmpty ? vehicleNo : l.vehicleNo,
          driverContact: targetPhone.isNotEmpty ? targetPhone : l.driverContact,
          pendingHandover: pendingMap,
        );
      }
      return l;
    }).toList();
    state = state.copyWith(lots: list);
    _localDb.saveQueuedEvent({
      'event_type': 'HANDOVER_REQUEST',
      'public_code': publicCode,
      'payload': pendingMap,
      'timestamp': DateTime.now().toIso8601String(),
    });
  }

  /// Next party confirms custody acceptance via QR scan
  Future<void> acceptCustodyHandover(
    String publicCode, {
    required String actorRole,
    required String actorName,
    required double receivedQtyKg,
    required String condition,
    String storageTemp = 'Ambient',
    double? lat,
    double? lng,
    String? accessToken,
    String? phone,
  }) async {
    if (!_isFlutterTest && accessToken != null && accessToken.isNotEmpty) {
      try {
        final dio = Dio(BaseOptions(
          baseUrl: _baseUrl,
          headers: {
            'Authorization': 'Bearer $accessToken',
            if (phone != null) 'X-Entity-Phone': phone,
          },
        ));
        final res = await dio.post<dynamic>(
          '/api/v1/lots/$publicCode/handover-accept',
          data: {
            'actor_role': actorRole,
            'actor_name': actorName,
            'received_qty_kg': receivedQtyKg,
            'condition': condition,
            'storage_temp': storageTemp,
            if (lat != null) 'lat': lat,
            if (lng != null) 'lng': lng,
          },
        );
        if (res.statusCode == 200 && res.data is Map) {
          final updated =
              HarvestLot.fromJson(Map<String, dynamic>.from(res.data as Map));
          updateLot(updated);
          return;
        }
      } catch (_) {}
    }

    final list = state.lots.map((l) {
      if (l.publicCode == publicCode) {
        final nextCheckpoints = [
          ...l.journeyCheckpoints,
          {
            'step': l.journeyCheckpoints.length + 1,
            'event_type': 'HANDOVER_ACCEPT',
            'role': actorRole,
            'actor_name': actorName,
            'weight_kg': receivedQtyKg,
            'condition': condition,
            'storage_temp': storageTemp,
            'lat': lat,
            'lng': lng,
            'timestamp': DateTime.now().toIso8601String(),
          },
        ];
        return l.copyWith(
          state: 'IN_CUSTODY',
          netQtyKg: receivedQtyKg,
          currentCustodianRole: actorRole,
          currentCustodianName: actorName,
          isRetailerVerified: l.isRetailerVerified || actorRole == 'RETAILER',
          pendingHandover: null,
          journeyCheckpoints: nextCheckpoints,
        );
      }
      return l;
    }).toList();
    state = state.copyWith(lots: list);
  }

  /// Downstream party appends QR scan telemetry (weight, condition, temp, GPS)
  Future<void> appendCustodyScan(
    String publicCode, {
    required String actorRole,
    required String actorName,
    required double currentWeightKg,
    required String condition,
    String storageTemp = 'Ambient',
    double? lat,
    double? lng,
    String? accessToken,
    String? phone,
  }) async {
    if (!_isFlutterTest && accessToken != null && accessToken.isNotEmpty) {
      try {
        final dio = Dio(BaseOptions(
          baseUrl: _baseUrl,
          headers: {
            'Authorization': 'Bearer $accessToken',
            if (phone != null) 'X-Entity-Phone': phone,
          },
        ));
        final res = await dio.post<dynamic>(
          '/api/v1/lots/$publicCode/append-scan',
          data: {
            'actor_role': actorRole,
            'actor_name': actorName,
            'current_weight_kg': currentWeightKg,
            'condition': condition,
            'storage_temp': storageTemp,
            if (lat != null) 'lat': lat,
            if (lng != null) 'lng': lng,
          },
        );
        if ((res.statusCode == 200 || res.statusCode == 201) &&
            res.data is Map) {
          final updated =
              HarvestLot.fromJson(Map<String, dynamic>.from(res.data as Map));
          updateLot(updated);
          return;
        }
      } catch (_) {}
    }

    final list = state.lots.map((l) {
      if (l.publicCode == publicCode) {
        final nextCheckpoints = [
          ...l.journeyCheckpoints,
          {
            'step': l.journeyCheckpoints.length + 1,
            'event_type': 'CUSTODY_APPEND',
            'role': actorRole,
            'actor_name': actorName,
            'weight_kg': currentWeightKg,
            'condition': condition,
            'storage_temp': storageTemp,
            'lat': lat,
            'lng': lng,
            'timestamp': DateTime.now().toIso8601String(),
          },
        ];
        return l.copyWith(
          netQtyKg: currentWeightKg,
          isRetailerVerified: l.isRetailerVerified || actorRole == 'RETAILER',
          journeyCheckpoints: nextCheckpoints,
        );
      }
      return l;
    }).toList();
    state = state.copyWith(lots: list);
  }

  void dispatchLot(String publicCode,
      {String vehicleNo = '', String driverContact = ''}) {
    requestCustodyHandover(
      publicCode,
      targetRole: 'AGGREGATOR',
      targetName: 'Receiving Partner',
      targetPhone: driverContact,
      vehicleNo: vehicleNo,
    );
  }

  Future<void> placeOnShelf(String publicCode,
      {String? accessToken, String? phone}) async {
    final nowIso = DateTime.now().toIso8601String();
    final list = state.lots.map((l) {
      if (l.publicCode == publicCode) {
        final checkpoints = [
          ...l.journeyCheckpoints,
          {
            'step': l.journeyCheckpoints.length + 1,
            'event_type': 'ON_SHELF',
            'role': 'RETAILER',
            'actor_name': 'Retailer Store',
            'timestamp': nowIso,
            'notes': 'Placed on retail shelf for consumer purchase.',
          },
        ];
        return l.copyWith(
          state: 'ON_SHELF',
          isRetailerVerified: true,
          journeyCheckpoints: checkpoints,
        );
      }
      return l;
    }).toList();
    state = state.copyWith(lots: list);
  }

  Future<void> markSoldOut(String publicCode,
      {String? accessToken, String? phone}) async {
    final nowIso = DateTime.now().toIso8601String();
    final list = state.lots.map((l) {
      if (l.publicCode == publicCode) {
        final checkpoints = [
          ...l.journeyCheckpoints,
          {
            'step': l.journeyCheckpoints.length + 1,
            'event_type': 'SOLD_OUT',
            'role': 'RETAILER',
            'actor_name': 'Retailer Store',
            'timestamp': nowIso,
            'notes': 'Produce batch sold out.',
          },
        ];
        return l.copyWith(
          state: 'SOLD_OUT',
          journeyCheckpoints: checkpoints,
        );
      }
      return l;
    }).toList();
    state = state.copyWith(lots: list);
  }

  Future<void> markWasted(String publicCode,
      {String? accessToken, String? phone, String reason = 'Spoiled / Discarded'}) async {
    final nowIso = DateTime.now().toIso8601String();
    final list = state.lots.map((l) {
      if (l.publicCode == publicCode) {
        final checkpoints = [
          ...l.journeyCheckpoints,
          {
            'step': l.journeyCheckpoints.length + 1,
            'event_type': 'WASTED',
            'role': 'RETAILER',
            'actor_name': 'Retailer Store',
            'timestamp': nowIso,
            'notes': 'Produce batch marked as waste: $reason',
          },
        ];
        return l.copyWith(
          state: 'WASTED',
          journeyCheckpoints: checkpoints,
        );
      }
      return l;
    }).toList();
    state = state.copyWith(lots: list);
  }

  void setSearchQuery(String query) {
    state = state.copyWith(searchQuery: query);
  }

  void setCustodyFilter(String filter) {
    state = state.copyWith(selectedCustody: filter);
  }

  void setCropFilter(String crop) {
    state = state.copyWith(selectedCrop: crop);
  }

  void setPaymentFilter(String payment) {
    state = state.copyWith(selectedPayment: payment);
  }

  void setSortOrder(String order) {
    state = state.copyWith(sortOrder: order);
  }

  /// Normalize phone number to CountryCode + Mobile digits (e.g. 919876543210)
  static String normalizePhoneDigits(String? rawPhone) {
    final digits = (rawPhone ?? '').replaceAll(RegExp(r'\D'), '');
    if (digits.length == 10) {
      return '91$digits';
    }
    if (digits.length >= 11) {
      return digits;
    }
    return '910000000000';
  }

  /// Format: YYYYDDHHMMSS+CountryCodeMobileNumber (Mentor's Specification A)
  static String generateFarmerUid({String? phone, DateTime? timestamp}) {
    final dt = (timestamp ?? DateTime.now()).toUtc();
    final yyyy = dt.year.toString().padLeft(4, '0');
    final dd = dt.day.toString().padLeft(2, '0');
    final hh = dt.hour.toString().padLeft(2, '0');
    final mm = dt.minute.toString().padLeft(2, '0');
    final ss = dt.second.toString().padLeft(2, '0');
    final phoneDigits = normalizePhoneDigits(phone);
    return '$yyyy$dd$hh$mm$ss$phoneDigits';
  }

  /// Format: YYYYDDHHMMSS+CountryCodeMobileNumber + ProductCode + 4-Digit Sequence (Mentor's Specification B)
  static String generateSovereignCode({
    String? phone,
    String categoryCode = 'VG',
    int seq = 1,
    DateTime? timestamp,
  }) {
    final cat = kProductCategoryCodes.containsKey(categoryCode.toUpperCase())
        ? categoryCode.toUpperCase()
        : 'OT';
    final baseUid = generateFarmerUid(phone: phone, timestamp: timestamp);
    final seqStr =
        (seq % 10000 == 0 ? 1 : seq % 10000).toString().padLeft(4, '0');
    return '$baseUid$cat$seqStr';
  }
}
