import 'dart:convert';

/// Domain entity representing a traceable harvest batch in AnnaSutra.
/// Conforms to the 29-field agricultural & custodial ledger schema from the web portal.
class HarvestLot {
  final String publicCode;
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

  // Custody & Dispatch
  final String initialCustodyHolder;
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
    required this.crop,
    this.variety = '',
    required this.netQtyKg,
    this.unit = 'Kg',
    this.packageType = 'Crates',
    this.packagesCount = 0,
    this.originPlotName = 'Plot #1',
    this.originPlotId = 'PLOT-01',
    this.plotAreaAcres = 2.0,
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
    this.fertilizerLog = 'Vermicompost + Neem Cake',
    this.storageFacility = 'Farm Packhouse',
    this.storageTempC = 20.0,
    this.packagingDate = '',
    this.mandiGatepass = '',
    this.initialCustodyHolder = 'Self Producer',
    this.intendedBuyer = 'APMC Mandi',
    this.vehicleNo = '',
    this.driverContact = '',
    this.state = 'IN_CUSTODY',
    this.paymentStatus = 'PENDING',
    this.basePricePerUnit = 30.0,
    this.estimatedValue = 0.0,
    required this.harvestDate,
    required this.createdAt,
  });

  /// Lot is editable ONLY while in farm custody before counterparty handover.
  bool get isEditable => state == 'IN_CUSTODY' || state == 'CREATED';

  HarvestLot copyWith({
    String? publicCode,
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
    final price = (json['base_price_per_unit'] ?? 30.0);
    final val = (json['estimated_value'] ?? (qty is num && price is num ? qty * price : 0.0));

    return HarvestLot(
      publicCode: json['public_code']?.toString() ?? 'AS-UNKNOWN',
      crop: json['crop']?.toString() ?? 'Tomato',
      variety: json['variety']?.toString() ?? '',
      netQtyKg: (qty is num) ? qty.toDouble() : double.tryParse(qty.toString()) ?? 0.0,
      unit: json['unit']?.toString() ?? 'Kg',
      packageType: json['package_type']?.toString() ?? 'Crates',
      packagesCount: (json['packages_count'] is num) ? (json['packages_count'] as num).toInt() : 0,
      originPlotName: json['origin_plot_name']?.toString() ?? 'Plot #1',
      originPlotId: json['origin_plot_id']?.toString() ?? 'PLOT-01',
      plotAreaAcres: (json['plot_area_acres'] is num) ? (json['plot_area_acres'] as num).toDouble() : 2.0,
      surveyNumber: json['survey_number']?.toString() ?? '',
      gpsLat: (json['gps_lat'] is num) ? (json['gps_lat'] as num).toDouble() : null,
      gpsLng: (json['gps_lng'] is num) ? (json['gps_lng'] as num).toDouble() : null,
      qualityGrade: json['quality_grade']?.toString() ?? json['grade']?.toString() ?? 'Grade A (Super)',
      moisturePct: (json['moisture_pct'] is num) ? (json['moisture_pct'] as num).toDouble() : 12.0,
      foreignMatterPct: (json['foreign_matter_pct'] is num) ? (json['foreign_matter_pct'] as num).toDouble() : 0.5,
      grainSize: json['grain_size']?.toString() ?? 'Medium-Large',
      farmingMethod: json['farming_method']?.toString() ?? 'Organic',
      pesticideTested: json['pesticide_tested']?.toString() ?? 'CLEAN',
      seedCertificationNo: json['seed_certification_no']?.toString() ?? '',
      fertilizerLog: json['fertilizer_log']?.toString() ?? 'Vermicompost + Neem Cake',
      storageFacility: json['storage_facility']?.toString() ?? 'Farm Packhouse',
      storageTempC: (json['storage_temp_c'] is num) ? (json['storage_temp_c'] as num).toDouble() : 20.0,
      packagingDate: json['packaging_date']?.toString() ?? '',
      mandiGatepass: json['mandi_gatepass']?.toString() ?? '',
      initialCustodyHolder: json['initial_custody_holder']?.toString() ?? 'Self Producer',
      intendedBuyer: json['intended_buyer']?.toString() ?? 'APMC Mandi',
      vehicleNo: json['vehicle_no']?.toString() ?? '',
      driverContact: json['driver_contact']?.toString() ?? '',
      state: json['state']?.toString() ?? 'IN_CUSTODY',
      paymentStatus: json['payment_status']?.toString() ?? 'PENDING',
      basePricePerUnit: (price is num) ? price.toDouble() : 30.0,
      estimatedValue: (val is num) ? val.toDouble() : 0.0,
      harvestDate: json['harvest_date']?.toString() ?? DateTime.now().toIso8601String(),
      createdAt: json['created_at']?.toString() ?? DateTime.now().toIso8601String(),
    );
  }
}
