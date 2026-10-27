import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import 'package:uuid/uuid.dart';

import 'package:annasutra_mobile/data/platform/platform_providers.dart';
import '../../auth/presentation/controllers/auth_controller.dart';
import 'controllers/lots_controller.dart';
import '../domain/harvest_lot.dart';

class BatchCreateScreen extends ConsumerStatefulWidget {
  final String? lotCode; // If provided, edit mode

  const BatchCreateScreen({super.key, this.lotCode});

  @override
  ConsumerState<BatchCreateScreen> createState() => _BatchCreateScreenState();
}

class _BatchCreateScreenState extends ConsumerState<BatchCreateScreen> {
  final _formKey = GlobalKey<FormState>();

  late TextEditingController _serialController;
  late TextEditingController _productController;
  late TextEditingController _varietyController;
  late TextEditingController _qtyController;
  late TextEditingController _cratesController;

  late TextEditingController _plotNameController;
  late TextEditingController _plotAreaController;
  late TextEditingController _surveyNoController;
  late TextEditingController _moistureController;
  late TextEditingController _foreignMatterController;
  late TextEditingController _fertilizerController;
  late TextEditingController _storageTempController;
  late TextEditingController _mandiGatepassController;
  late TextEditingController _intendedBuyerController;
  late TextEditingController _basePriceController;

  // 10 Official Product Category Codes (Mentor Specification)
  String _selectedCategoryCode = 'VG';
  String _selectedUnit = 'Kg';
  String _selectedPackageType = 'Crates';
  String _selectedGrade = 'Grade A (Super)';
  String _selectedFarmingMethod = 'Organic';
  String _selectedPesticideStatus = 'CLEAN';
  String _selectedStorageFacility = 'Farm Packhouse';
  String _selectedPaymentStatus = 'PENDING';

  DateTime _harvestDate = DateTime.now();
  bool _isSubmitting = false;
  bool _isEdit = false;

  @override
  void initState() {
    super.initState();
    _isEdit = widget.lotCode != null && widget.lotCode!.isNotEmpty;

    // Clean empty controllers — NO prebuilt template strings
    _serialController = TextEditingController();
    _productController = TextEditingController();
    _varietyController = TextEditingController();
    _qtyController = TextEditingController();
    _cratesController = TextEditingController();

    _plotNameController = TextEditingController();
    _plotAreaController = TextEditingController();
    _surveyNoController = TextEditingController();
    _moistureController = TextEditingController();
    _foreignMatterController = TextEditingController();
    _fertilizerController = TextEditingController();
    _storageTempController = TextEditingController();
    _mandiGatepassController = TextEditingController();
    _intendedBuyerController = TextEditingController();
    _basePriceController = TextEditingController();

    if (!_isEdit) {
      _serialController.text = LotsController.generateSovereignCode(
        categoryCode: _selectedCategoryCode,
        seq: 1,
      );
    }
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final authState = ref.read(authControllerProvider);
    final lotsState = ref.read(lotsControllerProvider);

    if (!_isEdit &&
        _serialController.text.contains('910000000000') &&
        authState.phone != null) {
      _serialController.text = LotsController.generateSovereignCode(
        phone: authState.phone,
        categoryCode: _selectedCategoryCode,
        seq: lotsState.lots.length + 1,
      );
    }

    if (_isEdit) {
      final existing = lotsState.lots.firstWhere(
        (l) => l.publicCode == widget.lotCode,
        orElse: () => HarvestLot(
          publicCode: widget.lotCode!,
          crop: '',
          netQtyKg: 0.0,
          harvestDate: DateTime.now().toIso8601String(),
          createdAt: DateTime.now().toIso8601String(),
        ),
      );

      _serialController.text = existing.publicCode;
      _selectedCategoryCode =
          kProductCategoryCodes.containsKey(existing.productCategoryCode)
              ? existing.productCategoryCode
              : 'VG';
      _productController.text = existing.crop;
      _varietyController.text = existing.variety;
      _qtyController.text =
          existing.netQtyKg > 0 ? existing.netQtyKg.toString() : '';
      _cratesController.text =
          existing.packagesCount > 0 ? existing.packagesCount.toString() : '';
      _plotNameController.text = existing.originPlotName;
      _plotAreaController.text =
          existing.plotAreaAcres > 0 ? existing.plotAreaAcres.toString() : '';
      _surveyNoController.text = existing.surveyNumber;
      _moistureController.text = existing.moisturePct.toString();
      _foreignMatterController.text = existing.foreignMatterPct.toString();
      _fertilizerController.text = existing.fertilizerLog;
      _storageTempController.text = existing.storageTempC.toString();
      _mandiGatepassController.text = existing.mandiGatepass;
      _intendedBuyerController.text = existing.intendedBuyer;
      _basePriceController.text = existing.basePricePerUnit.toString();

      _selectedUnit = existing.unit;
      _selectedPackageType = existing.packageType;
      _selectedGrade = existing.qualityGrade;
      _selectedFarmingMethod = existing.farmingMethod;
      _selectedPesticideStatus = existing.pesticideTested;
      _selectedStorageFacility = existing.storageFacility;
      _selectedPaymentStatus = existing.paymentStatus;
      try {
        _harvestDate = DateTime.parse(existing.harvestDate);
      } catch (_) {}
    }
  }

  @override
  void dispose() {
    _serialController.dispose();
    _productController.dispose();
    _varietyController.dispose();
    _qtyController.dispose();
    _cratesController.dispose();
    _plotNameController.dispose();
    _plotAreaController.dispose();
    _surveyNoController.dispose();
    _moistureController.dispose();
    _foreignMatterController.dispose();
    _fertilizerController.dispose();
    _storageTempController.dispose();
    _mandiGatepassController.dispose();
    _intendedBuyerController.dispose();
    _basePriceController.dispose();
    super.dispose();
  }

  void _regenerateDeterministicBatchId() {
    final authState = ref.read(authControllerProvider);
    final lotsState = ref.read(lotsControllerProvider);
    setState(() {
      _serialController.text = LotsController.generateSovereignCode(
        phone: authState.phone,
        categoryCode: _selectedCategoryCode,
        seq: lotsState.lots.length + 1,
      );
    });
  }

  Future<void> _submitBatch() async {
    if (!(_formKey.currentState?.validate() ?? false)) {
      return;
    }

    setState(() {
      _isSubmitting = true;
    });

    try {
      final authState = ref.read(authControllerProvider);
      final signer = ref.read(signerProvider);
      final localDb = ref.read(localDatabaseProvider);
      final serial = _serialController.text.trim().toUpperCase();
      final netQty = double.tryParse(_qtyController.text.trim()) ?? 0.0;
      final price = double.tryParse(_basePriceController.text.trim()) ?? 30.0;
      final estVal = netQty * price;
      final farmerUid = authState.farmerUid ??
          LotsController.generateFarmerUid(phone: authState.phone);

      final lot = HarvestLot(
        publicCode: serial,
        farmerUid: farmerUid,
        productCategoryCode: _selectedCategoryCode,
        productCategoryName:
            kProductCategoryCodes[_selectedCategoryCode] ?? 'Vegetables (VG)',
        crop: _productController.text.trim(),
        variety: _varietyController.text.trim(),
        netQtyKg: netQty,
        unit: _selectedUnit,
        packageType: _selectedPackageType,
        packagesCount: int.tryParse(_cratesController.text.trim()) ?? 0,
        originPlotName: _plotNameController.text.trim(),
        originPlotId: _surveyNoController.text.trim().isNotEmpty
            ? _surveyNoController.text.trim()
            : 'PLOT-01',
        plotAreaAcres: double.tryParse(_plotAreaController.text.trim()) ?? 0.0,
        surveyNumber: _surveyNoController.text.trim(),
        qualityGrade: _selectedGrade,
        moisturePct: double.tryParse(_moistureController.text.trim()) ?? 12.0,
        foreignMatterPct:
            double.tryParse(_foreignMatterController.text.trim()) ?? 0.5,
        farmingMethod: _selectedFarmingMethod,
        pesticideTested: _selectedPesticideStatus,
        fertilizerLog: _fertilizerController.text.trim(),
        storageFacility: _selectedStorageFacility,
        storageTempC:
            double.tryParse(_storageTempController.text.trim()) ?? 18.0,
        mandiGatepass: _mandiGatepassController.text.trim(),
        intendedBuyer: _intendedBuyerController.text.trim(),
        basePricePerUnit: price,
        estimatedValue: estVal,
        paymentStatus: _selectedPaymentStatus,
        harvestDate: _harvestDate.toIso8601String(),
        createdAt: DateTime.now().toIso8601String(),
        journeyCheckpoints: [
          {
            'step': 1,
            'event_type': 'HARVEST_CREATE',
            'role': 'PRODUCER',
            'actor_name': authState.orgName ?? 'Producer Farm',
            'location_name': _plotNameController.text.trim().isNotEmpty
                ? _plotNameController.text.trim()
                : 'Origin Farm Plot',
            'weight_kg': netQty,
            'condition': 'Fresh Harvest ($_selectedGrade)',
            'storage_temp': _storageTempController.text.trim().isNotEmpty
                ? '${_storageTempController.text.trim()}°C'
                : 'Ambient',
            'timestamp': DateTime.now().toIso8601String(),
          },
        ],
      );

      final canonicalJson = jsonEncode(lot.toJson());
      final payloadBytes = Uint8List.fromList(utf8.encode(canonicalJson));
      final deviceSignature = await signer.sign(payloadBytes);

      await localDb.saveQueuedEvent({
        'event_id': const Uuid().v4(),
        'public_code': serial,
        'payload': canonicalJson,
        'signature': deviceSignature,
        'status': 'PENDING_SYNC',
        'created_at': DateTime.now().toIso8601String(),
      });

      final lotsNotifier = ref.read(lotsControllerProvider.notifier);
      if (_isEdit) {
        lotsNotifier.updateLot(lot);
      } else {
        lotsNotifier.addLot(lot);
      }

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(_isEdit
              ? 'Harvest lot $serial updated successfully!'
              : 'Harvest lot $serial created and queued for sync!'),
          backgroundColor: const Color(0xFF047857),
        ),
      );

      context.go('/');
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error saving batch: $e'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      if (mounted) {
        setState(() {
          _isSubmitting = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authControllerProvider);
    final lotsState = ref.watch(lotsControllerProvider);
    final theme = Theme.of(context);

    if (!authState.isOrgVerified && authState.orgVerification == 'PENDING') {
      return Scaffold(
        appBar: AppBar(title: const Text('Create Harvest Batch')),
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.pending_actions,
                    size: 64, color: Colors.orange.shade700),
                const SizedBox(height: 16),
                Text(
                  'Organisation Pending Verification',
                  style: theme.textTheme.titleLarge
                      ?.copyWith(fontWeight: FontWeight.bold),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 12),
                const Text(
                  'Your organisation has not been verified yet. Supply-chain lot creation and dispatches are disabled until verified by the platform admin.',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Colors.black54),
                ),
                const SizedBox(height: 24),
                ElevatedButton(
                  onPressed: () => context.go('/'),
                  child: const Text('Return to Home'),
                ),
              ],
            ),
          ),
        ),
      );
    }

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAF7),
      appBar: AppBar(
        title: Text(_isEdit ? 'Edit Harvest Lot' : 'Create Harvest Batch'),
        backgroundColor: const Color(0xFF0B3D2E),
        foregroundColor: Colors.white,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20.0),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // SECTION 1: QR Label Serial & 10 Product Category Codes
                _buildSectionHeader(
                    '1. Deterministic Batch ID & 10 Product Categories',
                    Icons.qr_code_2),
                const SizedBox(height: 12),

                // Product Category Code (FG, PU, OI, FR, VG, SP, CC, LS, SC, OT)
                DropdownButtonFormField<String>(
                  isExpanded: true,
                  value: _selectedCategoryCode,
                  decoration: const InputDecoration(
                    labelText: 'Product Category Code (Mentor Scheme) *',
                    border: OutlineInputBorder(),
                  ),
                  items: kProductCategoryCodes.entries
                      .map((e) => DropdownMenuItem<String>(
                            value: e.key,
                            child: Text(e.value),
                          ))
                      .toList(),
                  onChanged: (val) {
                    if (val != null) {
                      setState(() {
                        _selectedCategoryCode = val;
                      });
                      if (!_isEdit) {
                        _regenerateDeterministicBatchId();
                      }
                    }
                  },
                ),
                const SizedBox(height: 16),

                // QR Label Serial *
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: TextFormField(
                        controller: _serialController,
                        textCapitalization: TextCapitalization.characters,
                        decoration: const InputDecoration(
                          labelText: 'QR Label Serial *',
                          hintText: 'YYYYDDHHMMSS+CountryCodeMobile+Code+Seq',
                          border: OutlineInputBorder(),
                        ),
                        validator: (value) {
                          if (value == null || value.trim().length < 6) {
                            return 'Enter valid QR serial code';
                          }
                          return null;
                        },
                      ),
                    ),
                    const SizedBox(width: 8),
                    SizedBox(
                      height: 56,
                      child: OutlinedButton(
                        onPressed: () {
                          _regenerateDeterministicBatchId();
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                                content: Text(
                                    'Generated fresh deterministic batch ID.')),
                          );
                        },
                        child: const Icon(Icons.refresh),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                // Produce Name *
                TextFormField(
                  controller: _productController,
                  decoration: const InputDecoration(
                    labelText: 'Produce Name *',
                    hintText: 'Enter crop or produce name',
                    border: OutlineInputBorder(),
                  ),
                  validator: (value) {
                    if (value == null || value.trim().isEmpty) {
                      return 'Produce name is required';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),

                // Variety *
                TextFormField(
                  controller: _varietyController,
                  decoration: const InputDecoration(
                    labelText: 'Variety *',
                    hintText: 'Enter seed or crop variety',
                    border: OutlineInputBorder(),
                  ),
                  validator: (value) {
                    if (value == null || value.trim().isEmpty) {
                      return 'Variety is required';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),

                // Harvest Date Picker
                InkWell(
                  onTap: () async {
                    final picked = await showDatePicker(
                      context: context,
                      initialDate: _harvestDate,
                      firstDate: DateTime(2020),
                      lastDate: DateTime.now().add(const Duration(days: 1)),
                    );
                    if (picked != null) {
                      setState(() {
                        _harvestDate = picked;
                      });
                    }
                  },
                  child: InputDecorator(
                    decoration: const InputDecoration(
                      labelText: 'Harvest Date *',
                      border: OutlineInputBorder(),
                      suffixIcon: Icon(Icons.calendar_today),
                    ),
                    child: Text(DateFormat('yyyy-MM-dd').format(_harvestDate)),
                  ),
                ),
                const SizedBox(height: 24),

                // SECTION 2: Quantity & Packaging
                _buildSectionHeader('2. Quantity & Packaging', Icons.scale),
                const SizedBox(height: 12),

                Row(
                  children: [
                    Expanded(
                      flex: 6,
                      child: TextFormField(
                        controller: _qtyController,
                        keyboardType: const TextInputType.numberWithOptions(
                            decimal: true),
                        decoration: const InputDecoration(
                          labelText: 'Net Quantity (kg) *',
                          hintText: 'Enter net weight in kg',
                          border: OutlineInputBorder(),
                        ),
                        validator: (value) {
                          if (value == null || value.trim().isEmpty) {
                            return 'Enter quantity';
                          }
                          final d = double.tryParse(value.trim());
                          if (d == null || d <= 0) {
                            return 'Enter positive number';
                          }
                          return null;
                        },
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      flex: 4,
                      child: DropdownButtonFormField<String>(
                        isExpanded: true,
                        value: _selectedUnit,
                        decoration: const InputDecoration(
                          labelText: 'Unit',
                          border: OutlineInputBorder(),
                        ),
                        items: ['Kg', 'Quintal', 'Metric Ton']
                            .map((u) =>
                                DropdownMenuItem(value: u, child: Text(u)))
                            .toList(),
                        onChanged: (v) =>
                            setState(() => _selectedUnit = v ?? 'Kg'),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                Row(
                  children: [
                    Expanded(
                      flex: 5,
                      child: DropdownButtonFormField<String>(
                        isExpanded: true,
                        value: _selectedPackageType,
                        decoration: const InputDecoration(
                          labelText: 'Package Type',
                          border: OutlineInputBorder(),
                        ),
                        items: [
                          'Crates',
                          'Gunny Bags',
                          'Corrugated Boxes',
                          'Loose Bulk'
                        ]
                            .map((p) =>
                                DropdownMenuItem(value: p, child: Text(p)))
                            .toList(),
                        onChanged: (v) => setState(
                            () => _selectedPackageType = v ?? 'Crates'),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      flex: 5,
                      child: TextFormField(
                        controller: _cratesController,
                        keyboardType: TextInputType.number,
                        decoration: const InputDecoration(
                          labelText: 'Packages Count',
                          hintText: 'Number of crates/bags',
                          border: OutlineInputBorder(),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),

                // SECTION 3: Origin Plot & Geo-tagging
                _buildSectionHeader(
                    '3. Farm & Plot Geo-tagging', Icons.place_outlined),
                const SizedBox(height: 12),

                TextFormField(
                  controller: _plotNameController,
                  decoration: const InputDecoration(
                    labelText: 'Origin Plot Name',
                    hintText: 'Enter registered farm plot name',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 16),

                Row(
                  children: [
                    Expanded(
                      child: TextFormField(
                        controller: _plotAreaController,
                        keyboardType: const TextInputType.numberWithOptions(
                            decimal: true),
                        decoration: const InputDecoration(
                          labelText: 'Area (Acres)',
                          hintText: 'Plot acreage',
                          border: OutlineInputBorder(),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: TextFormField(
                        controller: _surveyNoController,
                        decoration: const InputDecoration(
                          labelText: 'Survey / Khasra No.',
                          hintText: 'Land plot survey number',
                          border: OutlineInputBorder(),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),

                // SECTION 4: Quality & Grading
                _buildSectionHeader(
                    '4. Quality & Grading', Icons.verified_outlined),
                const SizedBox(height: 12),

                DropdownButtonFormField<String>(
                  isExpanded: true,
                  value: _selectedGrade,
                  decoration: const InputDecoration(
                    labelText: 'Quality Grade',
                    border: OutlineInputBorder(),
                  ),
                  items: [
                    'Grade A (Super)',
                    'Grade B',
                    'Grade C',
                    'Fair Average Quality'
                  ]
                      .map((g) => DropdownMenuItem(value: g, child: Text(g)))
                      .toList(),
                  onChanged: (v) =>
                      setState(() => _selectedGrade = v ?? 'Grade A (Super)'),
                ),
                const SizedBox(height: 16),

                Row(
                  children: [
                    Expanded(
                      child: TextFormField(
                        controller: _moistureController,
                        keyboardType: const TextInputType.numberWithOptions(
                            decimal: true),
                        decoration: const InputDecoration(
                          labelText: 'Moisture Content (%)',
                          hintText: 'Moisture %',
                          border: OutlineInputBorder(),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: TextFormField(
                        controller: _foreignMatterController,
                        keyboardType: const TextInputType.numberWithOptions(
                            decimal: true),
                        decoration: const InputDecoration(
                          labelText: 'Foreign Matter (%)',
                          hintText: 'Foreign matter %',
                          border: OutlineInputBorder(),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),

                // SECTION 5: Agri-Inputs & Sustainability
                _buildSectionHeader(
                    '5. Agri-Inputs & Sustainability', Icons.eco_outlined),
                const SizedBox(height: 12),

                Row(
                  children: [
                    Expanded(
                      child: DropdownButtonFormField<String>(
                        isExpanded: true,
                        value: _selectedFarmingMethod,
                        decoration: const InputDecoration(
                          labelText: 'Farming Method',
                          border: OutlineInputBorder(),
                        ),
                        items: ['Organic', 'Natural / ZBNF', 'Conventional']
                            .map((f) =>
                                DropdownMenuItem(value: f, child: Text(f)))
                            .toList(),
                        onChanged: (v) => setState(
                            () => _selectedFarmingMethod = v ?? 'Organic'),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: DropdownButtonFormField<String>(
                        isExpanded: true,
                        value: _selectedPesticideStatus,
                        decoration: const InputDecoration(
                          labelText: 'Pesticide Test',
                          border: OutlineInputBorder(),
                        ),
                        items: ['CLEAN', 'ORGANIC', 'UNTESTED']
                            .map((p) =>
                                DropdownMenuItem(value: p, child: Text(p)))
                            .toList(),
                        onChanged: (v) => setState(
                            () => _selectedPesticideStatus = v ?? 'CLEAN'),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                TextFormField(
                  controller: _fertilizerController,
                  decoration: const InputDecoration(
                    labelText: 'Fertilizer & Soil Amendments Log',
                    hintText: 'Enter organic or soil inputs applied',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 24),

                // SECTION 6: Post-Harvest & Storage
                _buildSectionHeader(
                    '6. Post-Harvest & Storage', Icons.inventory_2_outlined),
                const SizedBox(height: 12),

                Row(
                  children: [
                    Expanded(
                      child: DropdownButtonFormField<String>(
                        isExpanded: true,
                        value: _selectedStorageFacility,
                        decoration: const InputDecoration(
                          labelText: 'Storage Facility',
                          border: OutlineInputBorder(),
                        ),
                        items: [
                          'Farm Packhouse',
                          'Cold Storage Ambient Bay',
                          'Village Yard'
                        ]
                            .map((s) =>
                                DropdownMenuItem(value: s, child: Text(s)))
                            .toList(),
                        onChanged: (v) => setState(() =>
                            _selectedStorageFacility = v ?? 'Farm Packhouse'),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: TextFormField(
                        controller: _storageTempController,
                        keyboardType: const TextInputType.numberWithOptions(
                            decimal: true),
                        decoration: const InputDecoration(
                          labelText: 'Storage Temp (°C)',
                          hintText: 'Temperature in °C',
                          border: OutlineInputBorder(),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                TextFormField(
                  controller: _mandiGatepassController,
                  decoration: const InputDecoration(
                    labelText: 'Mandi Gatepass / E-Waybill Reference',
                    hintText: 'Optional gatepass or e-waybill number',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 24),

                // SECTION 7: Valuation & Commercial Target
                _buildSectionHeader(
                    '7. Valuation & Buyer Target', Icons.currency_rupee),
                const SizedBox(height: 12),

                Row(
                  children: [
                    Expanded(
                      child: TextFormField(
                        controller: _basePriceController,
                        keyboardType: const TextInputType.numberWithOptions(
                            decimal: true),
                        decoration: const InputDecoration(
                          labelText: 'Base Price (₹/unit)',
                          hintText: 'Price per unit',
                          border: OutlineInputBorder(),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: TextFormField(
                        controller: _intendedBuyerController,
                        decoration: const InputDecoration(
                          labelText: 'Intended Buyer',
                          hintText: 'Target Aggregator / Wholesaler / Retailer',
                          border: OutlineInputBorder(),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 28),

                // SUBMIT BUTTON (Matches test assertion: "Sign & Create Batch")
                ElevatedButton.icon(
                  onPressed: _isSubmitting ? null : _submitBatch,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF047857),
                    foregroundColor: Colors.white,
                    minimumSize: const Size(double.infinity, 54),
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12)),
                    elevation: 2,
                  ),
                  icon: _isSubmitting
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                              color: Colors.white, strokeWidth: 2.5),
                        )
                      : const Icon(Icons.check_circle_outline, size: 22),
                  label: Text(
                    _isEdit ? 'Save Changes to Lot' : 'Sign & Create Batch',
                    style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 0.3),
                  ),
                ),
                const SizedBox(height: 24),

                // LIVE LOT MOVEMENT MAP & NEXT-PARTY CUSTODY TELEMETRY SECTION
                _buildLiveLotMovementMapSection(lotsState),
                const SizedBox(height: 16),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildLiveLotMovementMapSection(LotsState lotsState) {
    final activeLots = lotsState.lots;
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFA7F3D0), width: 1.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.map_outlined, color: Color(0xFF047857), size: 20),
              SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Live Lot Movement Trajectory (Next-Party Scan Updates)',
                  style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF0B3D2E)),
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          const Text(
            'Real-time GPS custody hops as Aggregators, Wholesalers, Distributors, and Retailers accept custody and scan lot QR codes.',
            style: TextStyle(fontSize: 12, color: Color(0xFF64748B)),
          ),
          const SizedBox(height: 12),
          if (activeLots.isEmpty)
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFFF8FAFC),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: const Color(0xFFE2E8F0)),
              ),
              child: const Row(
                children: [
                  Icon(Icons.my_location, color: Color(0xFF047857), size: 20),
                  SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      'Create a harvest batch above to track its live GPS trajectory from Farm Origin to Retailer Shop.',
                      style: TextStyle(fontSize: 12, color: Color(0xFF475569)),
                    ),
                  ),
                ],
              ),
            )
          else
            ...activeLots.take(3).map((lot) {
              return Container(
                margin: const EdgeInsets.only(bottom: 10),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: const Color(0xFFF0FDF4),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: const Color(0xFFBBF7D0)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '${lot.publicCode} • ${lot.crop} (${lot.productCategoryCode})',
                      style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 12.5,
                          color: Color(0xFF065F46)),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Current Custodian: ${lot.currentCustodianName} (${lot.currentCustodianRole}) • '
                      '${lot.isRetailerVerified ? "Retailer Verified (Consumer Unlocked)" : "Supply-Chain In Transit"}',
                      style: const TextStyle(
                          fontSize: 11.5, color: Color(0xFF334155)),
                    ),
                  ],
                ),
              );
            }),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title, IconData icon) {
    return Row(
      children: [
        Icon(icon, size: 18, color: const Color(0xFF047857)),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            title,
            style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w800,
              color: Color(0xFF0B3D2E),
              letterSpacing: 0.2,
            ),
          ),
        ),
      ],
    );
  }
}
