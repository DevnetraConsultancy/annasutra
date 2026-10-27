/// Domain entity representing a traceable harvest batch in AnnaSutra.
/// Conforms to the deterministic ID scheme (YYYYDDHHMMSS+CountryCodeMobileNumber+ProductCode+Seq)
/// and the 2-way custody handover + retailer-gated consumer passport ledger.
class HarvestLot {
  final String publicCode;
  final String farmerUid;
  final String productCategoryCode; // FG, PU, OI, FR, VG, SP, CC, LS, SC, OT
  final String productCategoryName;
  final String crop;
  final String variety;
  final double netQtyKg;
  final String unit;
  final String packageType;
  final int packagesCount;

  // Farm & Plot Geo-tagging
  final String originPlotName;
  final String originPlotId;
  final double plotAreaAcres;
  final String surveyNumber;
  final double? gpsLat;
  final double? gpsLng;

  // Quality & Grading
  final String qualityGrade; // 'Grade A (Super)', 'Grade B', 'Grade C', 'FAQ'
  final double moisturePct;
  final double foreignMatterPct;
  final String grainSize;

  // Agri-Inputs & Sustainability
  final String farmingMethod; // 'Organic', 'Natural / ZBNF', 'Conventional'
  final String pesticideTested; // 'CLEAN', 'UNTESTED', 'ORGANIC'
  final String seedCertificationNo;
  final String fertilizerLog;

  // Post-Harvest & Storage
  final String storageFacility;
  final double storageTempC;
  final String packagingDate;
  final String mandiGatepass;

  // Custody & 2-Way Handover
  final String initialCustodyHolder;
  final String
      currentCustodianRole; // 'PRODUCER', 'AGGREGATOR', 'WHOLESALER', 'DISTRIBUTOR', 'RETAILER'
  final String currentCustodianName;
  final bool isRetailerVerified;
  final Map<String, dynamic>? pendingHandover;
  final List<Map<String, dynamic>> journeyCheckpoints;
  final String intendedBuyer;
  final String vehicleNo;
  final String driverContact;

  // Lifecycle & Commercials
  final String state; // 'IN_CUSTODY', 'IN_TRANSIT', 'CLOSED'
  final String paymentStatus; // 'PENDING', 'ADVANCE', 'SETTLED'
  final double basePricePerUnit;
  final double estimatedValue;
  final String harvestDate;
  final String createdAt;

  const HarvestLot({
    required this.publicCode,
    this.farmerUid = '',
    this.productCategoryCode = 'VG',
    this.productCategoryName = 'Vegetables',
    required this.crop,
    this.variety = '',
    required this.netQtyKg,
    this.unit = 'Kg',
    this.packageType = 'Crates',
    this.packagesCount = 0,
    this.originPlotName = '',
    this.originPlotId = '',
    this.plotAreaAcres = 0.0,
    this.surveyNumber = '',
    this.gpsLat,
    this.gpsLng,
    this.qualityGrade = 'Grade A (Super)',
    this.moisturePct = 12.0,
    this.foreignMatterPct = 0.5,
    this.grainSize = 'Medium-Large',
    this.farmingMethod = 'Organic',
    this.pesticideTested = 'CLEAN',
    this.seedCertificationNo = '',
    this.fertilizerLog = '',
    this.storageFacility = 'Farm Packhouse',
    this.storageTempC = 20.0,
    this.packagingDate = '',
    this.mandiGatepass = '',
    this.initialCustodyHolder = 'Producer Farm',
    this.currentCustodianRole = 'PRODUCER',
    this.currentCustodianName = 'Producer Farm',
    this.isRetailerVerified = false,
    this.pendingHandover,
    this.journeyCheckpoints = const [],
    this.intendedBuyer = '',
    this.vehicleNo = '',
    this.driverContact = '',
    this.state = 'IN_CUSTODY',
    this.paymentStatus = 'PENDING',
    this.basePricePerUnit = 30.0,
    this.estimatedValue = 0.0,
    required this.harvestDate,
    required this.createdAt,
  });

  /// Lot is editable ONLY while in initial farm custody before counterparty handover.
  bool get isEditable =>
      (state == 'IN_CUSTODY' || state == 'CREATED') &&
      currentCustodianRole == 'PRODUCER' &&
      pendingHandover == null;

  HarvestLot copyWith({
    String? publicCode,
    String? farmerUid,
    String? productCategoryCode,
    String? productCategoryName,
    String? crop,
    String? variety,
    double? netQtyKg,
    String? unit,
    String? packageType,
    int? packagesCount,
    String? originPlotName,
    String? originPlotId,
    double? plotAreaAcres,
    String? surveyNumber,
    double? gpsLat,
    double? gpsLng,
    String? qualityGrade,
    double? moisturePct,
    double? foreignMatterPct,
    String? grainSize,
    String? farmingMethod,
    String? pesticideTested,
    String? seedCertificationNo,
    String? fertilizerLog,
    String? storageFacility,
    double? storageTempC,
    String? packagingDate,
    String? mandiGatepass,
    String? initialCustodyHolder,
    String? currentCustodianRole,
    String? currentCustodianName,
    bool? isRetailerVerified,
    Map<String, dynamic>? pendingHandover,
    List<Map<String, dynamic>>? journeyCheckpoints,
    String? intendedBuyer,
    String? vehicleNo,
    String? driverContact,
    String? state,
    String? paymentStatus,
    double? basePricePerUnit,
    double? estimatedValue,
    String? harvestDate,
    String? createdAt,
  }) {
    return HarvestLot(
      publicCode: publicCode ?? this.publicCode,
      farmerUid: farmerUid ?? this.farmerUid,
      productCategoryCode: productCategoryCode ?? this.productCategoryCode,
      productCategoryName: productCategoryName ?? this.productCategoryName,
      crop: crop ?? this.crop,
      variety: variety ?? this.variety,
      netQtyKg: netQtyKg ?? this.netQtyKg,
      unit: unit ?? this.unit,
      packageType: packageType ?? this.packageType,
      packagesCount: packagesCount ?? this.packagesCount,
      originPlotName: originPlotName ?? this.originPlotName,
      originPlotId: originPlotId ?? this.originPlotId,
      plotAreaAcres: plotAreaAcres ?? this.plotAreaAcres,
      surveyNumber: surveyNumber ?? this.surveyNumber,
      gpsLat: gpsLat ?? this.gpsLat,
      gpsLng: gpsLng ?? this.gpsLng,
      qualityGrade: qualityGrade ?? this.qualityGrade,
      moisturePct: moisturePct ?? this.moisturePct,
      foreignMatterPct: foreignMatterPct ?? this.foreignMatterPct,
      grainSize: grainSize ?? this.grainSize,
      farmingMethod: farmingMethod ?? this.farmingMethod,
      pesticideTested: pesticideTested ?? this.pesticideTested,
      seedCertificationNo: seedCertificationNo ?? this.seedCertificationNo,
      fertilizerLog: fertilizerLog ?? this.fertilizerLog,
      storageFacility: storageFacility ?? this.storageFacility,
      storageTempC: storageTempC ?? this.storageTempC,
      packagingDate: packagingDate ?? this.packagingDate,
      mandiGatepass: mandiGatepass ?? this.mandiGatepass,
      initialCustodyHolder: initialCustodyHolder ?? this.initialCustodyHolder,
      currentCustodianRole: currentCustodianRole ?? this.currentCustodianRole,
      currentCustodianName: currentCustodianName ?? this.currentCustodianName,
      isRetailerVerified: isRetailerVerified ?? this.isRetailerVerified,
      pendingHandover: pendingHandover ?? this.pendingHandover,
      journeyCheckpoints: journeyCheckpoints ?? this.journeyCheckpoints,
      intendedBuyer: intendedBuyer ?? this.intendedBuyer,
      vehicleNo: vehicleNo ?? this.vehicleNo,
      driverContact: driverContact ?? this.driverContact,
      state: state ?? this.state,
      paymentStatus: paymentStatus ?? this.paymentStatus,
      basePricePerUnit: basePricePerUnit ?? this.basePricePerUnit,
      estimatedValue: estimatedValue ?? this.estimatedValue,
      harvestDate: harvestDate ?? this.harvestDate,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'public_code': publicCode,
      'farmer_uid': farmerUid,
      'product_category_code': productCategoryCode,
      'product_category_name': productCategoryName,
      'crop': crop,
      'variety': variety,
      'net_qty_kg': netQtyKg,
      'unit': unit,
      'package_type': packageType,
      'packages_count': packagesCount,
      'origin_plot_name': originPlotName,
      'origin_plot_id': originPlotId,
      'plot_area_acres': plotAreaAcres,
      'survey_number': surveyNumber,
      'gps_lat': gpsLat,
      'gps_lng': gpsLng,
      'quality_grade': qualityGrade,
      'moisture_pct': moisturePct,
      'foreign_matter_pct': foreignMatterPct,
      'grain_size': grainSize,
      'farming_method': farmingMethod,
      'pesticide_tested': pesticideTested,
      'seed_certification_no': seedCertificationNo,
      'fertilizer_log': fertilizerLog,
      'storage_facility': storageFacility,
      'storage_temp_c': storageTempC,
      'packaging_date': packagingDate,
      'mandi_gatepass': mandiGatepass,
      'initial_custody_holder': initialCustodyHolder,
      'current_custodian_role': currentCustodianRole,
      'current_custodian_name': currentCustodianName,
      'is_retailer_verified': isRetailerVerified,
      'pending_handover': pendingHandover,
      'journey_checkpoints': journeyCheckpoints,
      'intended_buyer': intendedBuyer,
      'vehicle_no': vehicleNo,
      'driver_contact': driverContact,
      'state': state,
      'payment_status': paymentStatus,
      'base_price_per_unit': basePricePerUnit,
      'estimated_value': estimatedValue,
      'harvest_date': harvestDate,
      'created_at': createdAt,
    };
  }

  factory HarvestLot.fromJson(Map<String, dynamic> json) {
    final qty = (json['net_qty_kg'] ?? json['on_hand_kg'] ?? 0.0);
    final price =
        (json['base_price_per_unit'] ?? json['price_per_unit'] ?? 30.0);
    final val = (json['estimated_value'] ??
        json['total_value'] ??
        (qty is num && price is num ? qty * price : 0.0));

    final rawCheckpoints = json['journey_checkpoints'];
    final List<Map<String, dynamic>> checkpoints = [];
    if (rawCheckpoints is List) {
      for (final item in rawCheckpoints) {
        if (item is Map) {
          checkpoints.add(Map<String, dynamic>.from(item));
        }
      }
    }

    Map<String, dynamic>? pendingHo;
    if (json['pending_handover'] is Map) {
      pendingHo = Map<String, dynamic>.from(json['pending_handover'] as Map);
    }

    return HarvestLot(
      publicCode: json['public_code']?.toString() ?? '',
      farmerUid: json['farmer_uid']?.toString() ?? '',
      productCategoryCode: json['product_category_code']?.toString() ?? 'VG',
      productCategoryName:
          json['product_category_name']?.toString() ?? 'Vegetables',
      crop: json['crop']?.toString() ?? '',
      variety: json['variety']?.toString() ?? '',
      netQtyKg: (qty is num)
          ? qty.toDouble()
          : double.tryParse(qty.toString()) ?? 0.0,
      unit: json['unit']?.toString() ?? 'Kg',
      packageType: json['package_type']?.toString() ?? 'Crates',
      packagesCount: (json['packages_count'] is num)
          ? (json['packages_count'] as num).toInt()
          : 0,
      originPlotName: json['origin_plot_name']?.toString() ?? '',
      originPlotId: json['origin_plot_id']?.toString() ?? '',
      plotAreaAcres: (json['plot_area_acres'] is num)
          ? (json['plot_area_acres'] as num).toDouble()
          : 0.0,
      surveyNumber: json['survey_number']?.toString() ?? '',
      gpsLat: (json['gps_lat'] is num)
          ? (json['gps_lat'] as num).toDouble()
          : (json['origin_lat'] is num
              ? (json['origin_lat'] as num).toDouble()
              : null),
      gpsLng: (json['gps_lng'] is num)
          ? (json['gps_lng'] as num).toDouble()
          : (json['origin_lng'] is num
              ? (json['origin_lng'] as num).toDouble()
              : null),
      qualityGrade: json['quality_grade']?.toString() ??
          json['grade']?.toString() ??
          'Grade A',
      moisturePct: (json['moisture_pct'] is num)
          ? (json['moisture_pct'] as num).toDouble()
          : 12.0,
      foreignMatterPct: (json['foreign_matter_pct'] is num)
          ? (json['foreign_matter_pct'] as num).toDouble()
          : 0.5,
      grainSize: json['grain_size']?.toString() ?? 'Standard',
      farmingMethod: json['farming_method']?.toString() ?? 'Organic',
      pesticideTested: json['pesticide_tested']?.toString() ?? 'CLEAN',
      seedCertificationNo: json['seed_certification_no']?.toString() ?? '',
      fertilizerLog: json['fertilizer_log']?.toString() ?? '',
      storageFacility: json['storage_facility']?.toString() ?? 'Farm Packhouse',
      storageTempC: (json['storage_temp_c'] is num)
          ? (json['storage_temp_c'] as num).toDouble()
          : 20.0,
      packagingDate: json['packaging_date']?.toString() ?? '',
      mandiGatepass: json['mandi_gatepass']?.toString() ?? '',
      initialCustodyHolder:
          json['initial_custody_holder']?.toString() ?? 'Producer Farm',
      currentCustodianRole:
          json['current_custodian_role']?.toString() ?? 'PRODUCER',
      currentCustodianName:
          json['current_custodian_name']?.toString() ?? 'Producer Farm',
      isRetailerVerified: json['is_retailer_verified'] == true,
      pendingHandover: pendingHo,
      journeyCheckpoints: checkpoints,
      intendedBuyer: json['intended_buyer']?.toString() ?? '',
      vehicleNo: json['vehicle_no']?.toString() ?? '',
      driverContact: json['driver_contact']?.toString() ?? '',
      state: json['state']?.toString() ?? 'IN_CUSTODY',
      paymentStatus: json['payment_status']?.toString() ?? 'PENDING',
      basePricePerUnit: (price is num) ? price.toDouble() : 30.0,
      estimatedValue: (val is num) ? val.toDouble() : 0.0,
      harvestDate:
          json['harvest_date']?.toString() ?? DateTime.now().toIso8601String(),
      createdAt:
          json['created_at']?.toString() ?? DateTime.now().toIso8601String(),
    );
  }
}
