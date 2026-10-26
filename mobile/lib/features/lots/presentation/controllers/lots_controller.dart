import 'dart:math';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/harvest_lot.dart';
import 'package:annasutra_mobile/data/platform/platform_providers.dart';
import 'package:annasutra_mobile/domain/platform/local_database.dart';

final lotsControllerProvider = StateNotifierProvider<LotsController, LotsState>((ref) {
  final localDb = ref.watch(localDatabaseProvider);
  return LotsController(localDb: localDb);
});

class LotsState {
  final List<HarvestLot> lots;
  final bool isLoading;
  final String searchQuery;
  final String selectedCustody; // 'ALL', 'IN_CUSTODY', 'IN_TRANSIT', 'CLOSED'
  final String selectedCrop; // 'ALL', or crop name
  final String selectedPayment; // 'ALL', 'PENDING', 'ADVANCE', 'SETTLED'
  final String sortOrder; // '-created_at', 'created_at', '-qty', 'qty'
  final String analyticsPeriod; // 'ALL', '30', '90', 'SEASON'

  const LotsState({
    this.lots = const [],
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
        final text = '${lot.publicCode} ${lot.crop} ${lot.variety} ${lot.originPlotName} ${lot.qualityGrade}'.toLowerCase();
        if (!text.contains(query)) {
          return false;
        }
      }
      if (selectedCustody != 'ALL') {
        if (selectedCustody == 'IN_CUSTODY' && !(lot.state == 'IN_CUSTODY' || lot.state == 'CREATED')) {
          return false;
        }
        if (selectedCustody == 'IN_TRANSIT' && lot.state != 'IN_TRANSIT') {
          return false;
        }
        if (selectedCustody == 'CLOSED' && lot.state != 'CLOSED') {
          return false;
        }
      }
      if (selectedCrop != 'ALL' && lot.crop.toLowerCase() != selectedCrop.toLowerCase()) {
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
      // default: -created_at (latest first)
      return b.createdAt.compareTo(a.createdAt);
    });

    return result;
  }

  // 4 Top Metrics
  int get totalLotsCount => lots.length;
  int get inCustodyCount => lots.where((l) => l.state == 'IN_CUSTODY' || l.state == 'CREATED').length;
  int get inTransitCount => lots.where((l) => l.state == 'IN_TRANSIT').length;
  double get totalWeightKg => lots.fold(0.0, (sum, l) => sum + l.netQtyKg);
  double get totalValuation => lots.fold(0.0, (sum, l) => sum + l.estimatedValue);

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
      'Delivered / Mandi': 0.0,
      'Custody Closed': 0.0,
    };
    for (var lot in lots) {
      if (lot.state == 'IN_CUSTODY' || lot.state == 'CREATED') {
        map['In Farm Custody'] = (map['In Farm Custody'] ?? 0) + lot.netQtyKg;
      } else if (lot.state == 'IN_TRANSIT') {
        map['In Transit'] = (map['In Transit'] ?? 0) + lot.netQtyKg;
      } else if (lot.state == 'DELIVERED') {
        map['Delivered / Mandi'] = (map['Delivered / Mandi'] ?? 0) + lot.netQtyKg;
      } else {
        map['Custody Closed'] = (map['Custody Closed'] ?? 0) + lot.netQtyKg;
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

  LotsController({required LocalDatabase localDb})
      : _localDb = localDb,
        super(const LotsState()) {
    _initSampleLots();
  }

  void _initSampleLots() {
    // Verified Producer (X7803) live recorded lots
    final now = DateTime.now();
    final lots = [
      HarvestLot(
        publicCode: 'AS-9K2M4P7L8Q1R',
        crop: 'Tomato',
        variety: 'Hybrid Red (Abhinav)',
        netQtyKg: 750.0,
        unit: 'Kg',
        packageType: 'Crates',
        packagesCount: 30,
        originPlotName: 'Plot #1 (North Yard)',
        originPlotId: 'PLOT-01',
        plotAreaAcres: 2.5,
        qualityGrade: 'Grade A (Super)',
        moisturePct: 11.5,
        foreignMatterPct: 0.2,
        farmingMethod: 'Organic',
        pesticideTested: 'CLEAN',
        fertilizerLog: 'Vermicompost + Trichoderma',
        storageFacility: 'Farm Packhouse',
        storageTempC: 18.0,
        state: 'IN_CUSTODY',
        paymentStatus: 'ADVANCE',
        basePricePerUnit: 34.0,
        estimatedValue: 25500.0,
        harvestDate: now.subtract(const Duration(hours: 18)).toIso8601String(),
        createdAt: now.subtract(const Duration(hours: 18)).toIso8601String(),
      ),
      HarvestLot(
        publicCode: 'AS-4X8T2N1M9L5K',
        crop: 'Potato',
        variety: 'Jyoti Premium',
        netQtyKg: 1200.0,
        unit: 'Kg',
        packageType: 'Gunny Bags',
        packagesCount: 24,
        originPlotName: 'Plot #2 (Canal Basin)',
        originPlotId: 'PLOT-02',
        plotAreaAcres: 3.0,
        qualityGrade: 'Grade A (Super)',
        moisturePct: 14.0,
        foreignMatterPct: 0.5,
        farmingMethod: 'Natural / ZBNF',
        pesticideTested: 'ORGANIC',
        fertilizerLog: 'Jeevamrit + Neem Extract',
        storageFacility: 'Cold Storage Ambient Bay',
        storageTempC: 12.0,
        state: 'IN_TRANSIT',
        paymentStatus: 'PENDING',
        basePricePerUnit: 22.0,
        estimatedValue: 26400.0,
        harvestDate: now.subtract(const Duration(days: 2)).toIso8601String(),
        createdAt: now.subtract(const Duration(days: 2)).toIso8601String(),
      ),
      HarvestLot(
        publicCode: 'AS-7H3V6B9Q2R4C',
        crop: 'Cauliflower',
        variety: 'Snowball White',
        netQtyKg: 480.0,
        unit: 'Kg',
        packageType: 'Crates',
        packagesCount: 20,
        originPlotName: 'Plot #1 (North Yard)',
        originPlotId: 'PLOT-01',
        plotAreaAcres: 2.5,
        qualityGrade: 'Grade B',
        moisturePct: 10.0,
        foreignMatterPct: 0.8,
        farmingMethod: 'Organic',
        pesticideTested: 'CLEAN',
        fertilizerLog: 'Cow dung compost + Bio-N',
        storageFacility: 'Farm Packhouse',
        storageTempC: 16.0,
        state: 'IN_CUSTODY',
        paymentStatus: 'SETTLED',
        basePricePerUnit: 28.0,
        estimatedValue: 13440.0,
        harvestDate: now.subtract(const Duration(days: 4)).toIso8601String(),
        createdAt: now.subtract(const Duration(days: 4)).toIso8601String(),
      ),
    ];

    state = state.copyWith(lots: lots);
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

  void dispatchLot(String publicCode, {String vehicleNo = '', String driverContact = ''}) {
    final list = state.lots.map((l) {
      if (l.publicCode == publicCode) {
        return l.copyWith(
          state: 'IN_TRANSIT',
          vehicleNo: vehicleNo.isNotEmpty ? vehicleNo : l.vehicleNo,
          driverContact: driverContact.isNotEmpty ? driverContact : l.driverContact,
        );
      }
      return l;
    }).toList();
    state = state.copyWith(lots: list);
    _localDb.saveQueuedEvent({
      'event_type': 'LOT_DISPATCHED',
      'public_code': publicCode,
      'timestamp': DateTime.now().toIso8601String(),
    });
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

  void setAnalyticsPeriod(String period) {
    state = state.copyWith(analyticsPeriod: period);
  }

  /// Generate a unique 12-character sovereign code matching web standard
  static String generateSovereignCode() {
    const chars = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ';
    final rand = Random.secure();
    final p1 = List.generate(4, (_) => chars[rand.nextInt(chars.length)]).join();
    final p2 = List.generate(4, (_) => chars[rand.nextInt(chars.length)]).join();
    final p3 = List.generate(4, (_) => chars[rand.nextInt(chars.length)]).join();
    return 'AS-$p1$p2$p3';
  }
}
