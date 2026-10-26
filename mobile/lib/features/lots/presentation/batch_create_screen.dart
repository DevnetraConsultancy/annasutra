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

  // Controllers for all required & agricultural fields
  late TextEditingController _serialController;
  late TextEditingController _productController;
  late TextEditingController _varietyController;
  late TextEditingController _qtyController;
  late TextEditingController _cratesController;

  // Additional 29-field controllers
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

  // Dropdown selections
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

    _serialController = TextEditingController();
    _productController = TextEditingController(text: 'Tomato');
    _varietyController = TextEditingController(text: 'Hybrid Red (Abhinav)');
    _qtyController = TextEditingController(text: '500.0');
    _cratesController = TextEditingController(text: '25');

    _plotNameController = TextEditingController(text: 'Plot #1 (North Yard)');
    _plotAreaController = TextEditingController(text: '2.5');
    _surveyNoController = TextEditingController(text: 'LR-442/19');
    _moistureController = TextEditingController(text: '12.0');
    _foreignMatterController = TextEditingController(text: '0.5');
    _fertilizerController = TextEditingController(text: 'Vermicompost + Neem Cake');
    _storageTempController = TextEditingController(text: '18.0');
    _mandiGatepassController = TextEditingController();
    _intendedBuyerController = TextEditingController(text: 'APMC Mandi');
    _basePriceController = TextEditingController(text: '32.0');

    // Auto-generate sovereign code if creating new
    if (!_isEdit) {
      _serialController.text = LotsController.generateSovereignCode();
    }
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_isEdit) {
      final lotsState = ref.read(lotsControllerProvider);
      final existing = lotsState.lots.firstWhere(
        (l) => l.publicCode == widget.lotCode,
        orElse: () => HarvestLot(
          publicCode: widget.lotCode!,
          crop: 'Tomato',
          netQtyKg: 500.0,
          harvestDate: DateTime.now().toIso8601String(),
          createdAt: DateTime.now().toIso8601String(),
        ),
      );

      _serialController.text = existing.publicCode;
      _productController.text = existing.crop;
      _varietyController.text = existing.variety;
      _qtyController.text = existing.netQtyKg.toString();
      _cratesController.text = existing.packagesCount.toString();
      _plotNameController.text = existing.originPlotName;
      _plotAreaController.text = existing.plotAreaAcres.toString();
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

  Future<void> _submitBatch() async {
    if (!(_formKey.currentState?.validate() ?? false)) {
      return;
    }

    setState(() {
      _isSubmitting = true;
    });

    try {
      final signer = ref.read(signerProvider);
      final localDb = ref.read(localDatabaseProvider);
      final serial = _serialController.text.trim().toUpperCase();
      final netQty = double.tryParse(_qtyController.text.trim()) ?? 0.0;
      final price = double.tryParse(_basePriceController.text.trim()) ?? 30.0;
      final estVal = netQty * price;

      final lot = HarvestLot(
        publicCode: serial,
        crop: _productController.text.trim(),
        variety: _varietyController.text.trim(),
        netQtyKg: netQty,
        unit: _selectedUnit,
        packageType: _selectedPackageType,
        packagesCount: int.tryParse(_cratesController.text.trim()) ?? 0,
        originPlotName: _plotNameController.text.trim(),
        originPlotId: 'PLOT-01',
        plotAreaAcres: double.tryParse(_plotAreaController.text.trim()) ?? 2.0,
        surveyNumber: _surveyNoController.text.trim(),
        qualityGrade: _selectedGrade,
        moisturePct: double.tryParse(_moistureController.text.trim()) ?? 12.0,
        foreignMatterPct: double.tryParse(_foreignMatterController.text.trim()) ?? 0.5,
        farmingMethod: _selectedFarmingMethod,
        pesticideTested: _selectedPesticideStatus,
        fertilizerLog: _fertilizerController.text.trim(),
        storageFacility: _selectedStorageFacility,
        storageTempC: double.tryParse(_storageTempController.text.trim()) ?? 18.0,
        mandiGatepass: _mandiGatepassController.text.trim(),
        intendedBuyer: _intendedBuyerController.text.trim(),
        basePricePerUnit: price,
        estimatedValue: estVal,
        paymentStatus: _selectedPaymentStatus,
        harvestDate: _harvestDate.toIso8601String(),
        createdAt: DateTime.now().toIso8601String(),
      );

      // Sign locally on device
      final canonicalJson = jsonEncode(lot.toJson());
      final payloadBytes = Uint8List.fromList(utf8.encode(canonicalJson));
      final deviceSignature = await signer.sign(payloadBytes);

      // Save locally to offline-first outbox in LocalDatabase
      await localDb.saveQueuedEvent({
        'event_id': const Uuid().v4(),
        'public_code': serial,
        'payload': canonicalJson,
        'signature': deviceSignature,
        'status': 'PENDING_SYNC',
        'created_at': DateTime.now().toIso8601String(),
      });

      // Update reactive lots controller
      final lotsNotifier = ref.read(lotsControllerProvider.notifier);
      if (_isEdit) {
        lotsNotifier.updateLot(lot);
      } else {
        lotsNotifier.addLot(lot);
      }

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(_isEdit ? 'Harvest lot $serial updated successfully!' : 'Harvest lot $serial created and queued for sync!'),
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
    final theme = Theme.of(context);

    // If organisation is unverified, show blocking banner per docs/14
    if (!authState.isOrgVerified && authState.orgVerification == 'PENDING') {
      return Scaffold(
        appBar: AppBar(title: const Text('Create Harvest Batch')),
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.pending_actions, size: 64, color: Colors.orange.shade700),
                const SizedBox(height: 16),
                Text(
                  'Organisation Pending Verification',
                  style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
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
                // SECTION 1: QR Label Serial & Crop Identification
                _buildSectionHeader('1. Crop Identification & Sovereign Code', Icons.qr_code_2),
                const SizedBox(height: 12),

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
                          hintText: 'Scan or generate QR serial',
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
                          setState(() {
                            _serialController.text = LotsController.generateSovereignCode();
                          });
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Generated fresh sovereign lot code.')),
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
                    hintText: 'e.g. Tomato, Potato, Paddy, Wheat',
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
                    hintText: 'e.g. Roma, Hybrid Red, Jyoti, Basmati',
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

                // Net Quantity (kg) *
                Row(
                  children: [
                    Expanded(
                      flex: 6,
                      child: TextFormField(
                        controller: _qtyController,
                        keyboardType: const TextInputType.numberWithOptions(decimal: true),
                        decoration: const InputDecoration(
                          labelText: 'Net Quantity (kg) *',
                          hintText: 'e.g. 500.0',
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
                            .map((u) => DropdownMenuItem(value: u, child: Text(u)))
                            .toList(),
                        onChanged: (v) => setState(() => _selectedUnit = v ?? 'Kg'),
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
                        items: ['Crates', 'Gunny Bags', 'Corrugated Boxes', 'Loose Bulk']
                            .map((p) => DropdownMenuItem(value: p, child: Text(p)))
                            .toList(),
                        onChanged: (v) => setState(() => _selectedPackageType = v ?? 'Crates'),
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
                          hintText: 'e.g. 25',
                          border: OutlineInputBorder(),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),

                // SECTION 3: Origin Plot & Geo-tagging
                _buildSectionHeader('3. Farm & Plot Geo-tagging', Icons.place_outlined),
                const SizedBox(height: 12),

                TextFormField(
                  controller: _plotNameController,
                  decoration: const InputDecoration(
                    labelText: 'Origin Plot Name',
                    hintText: 'e.g. Plot #1 (North Yard)',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 16),

                Row(
                  children: [
                    Expanded(
                      child: TextFormField(
                        controller: _plotAreaController,
                        keyboardType: const TextInputType.numberWithOptions(decimal: true),
                        decoration: const InputDecoration(
                          labelText: 'Area (Acres)',
                          hintText: 'e.g. 2.5',
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
                          hintText: 'e.g. LR-442/19',
                          border: OutlineInputBorder(),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),

                // SECTION 4: Quality & Grading
                _buildSectionHeader('4. Quality & Grading', Icons.verified_outlined),
                const SizedBox(height: 12),

                DropdownButtonFormField<String>(
                  isExpanded: true,
                        value: _selectedGrade,
                  decoration: const InputDecoration(
                    labelText: 'Quality Grade',
                    border: OutlineInputBorder(),
                  ),
                  items: ['Grade A (Super)', 'Grade B', 'Grade C', 'Fair Average Quality']
                      .map((g) => DropdownMenuItem(value: g, child: Text(g)))
                      .toList(),
                  onChanged: (v) => setState(() => _selectedGrade = v ?? 'Grade A (Super)'),
                ),
                const SizedBox(height: 16),

                Row(
                  children: [
                    Expanded(
                      child: TextFormField(
                        controller: _moistureController,
                        keyboardType: const TextInputType.numberWithOptions(decimal: true),
                        decoration: const InputDecoration(
                          labelText: 'Moisture Content (%)',
                          hintText: 'e.g. 11.5',
                          border: OutlineInputBorder(),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: TextFormField(
                        controller: _foreignMatterController,
                        keyboardType: const TextInputType.numberWithOptions(decimal: true),
                        decoration: const InputDecoration(
                          labelText: 'Foreign Matter (%)',
                          hintText: 'e.g. 0.2',
                          border: OutlineInputBorder(),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),

                // SECTION 5: Agri-Inputs & Sustainability
                _buildSectionHeader('5. Agri-Inputs & Sustainability', Icons.eco_outlined),
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
                            .map((f) => DropdownMenuItem(value: f, child: Text(f)))
                            .toList(),
                        onChanged: (v) => setState(() => _selectedFarmingMethod = v ?? 'Organic'),
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
                            .map((p) => DropdownMenuItem(value: p, child: Text(p)))
                            .toList(),
                        onChanged: (v) => setState(() => _selectedPesticideStatus = v ?? 'CLEAN'),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                TextFormField(
                  controller: _fertilizerController,
                  decoration: const InputDecoration(
                    labelText: 'Fertilizer & Soil Amendments Log',
                    hintText: 'e.g. Vermicompost, Neem Cake, Bio-N',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 24),

                // SECTION 6: Post-Harvest & Storage
                _buildSectionHeader('6. Post-Harvest & Storage', Icons.inventory_2_outlined),
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
                        items: ['Farm Packhouse', 'Cold Storage Ambient Bay', 'Village Yard']
                            .map((s) => DropdownMenuItem(value: s, child: Text(s)))
                            .toList(),
                        onChanged: (v) => setState(() => _selectedStorageFacility = v ?? 'Farm Packhouse'),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: TextFormField(
                        controller: _storageTempController,
                        keyboardType: const TextInputType.numberWithOptions(decimal: true),
                        decoration: const InputDecoration(
                          labelText: 'Storage Temp (°C)',
                          hintText: 'e.g. 18.0',
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
                    hintText: 'e.g. WB-GP-2026-904',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 24),

                // SECTION 7: Valuation & Commercial Target
                _buildSectionHeader('7. Valuation & Buyer Target', Icons.currency_rupee),
                const SizedBox(height: 12),

                Row(
                  children: [
                    Expanded(
                      child: TextFormField(
                        controller: _basePriceController,
                        keyboardType: const TextInputType.numberWithOptions(decimal: true),
                        decoration: const InputDecoration(
                          labelText: 'Base Price (₹/unit)',
                          hintText: 'e.g. 32.0',
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
                          hintText: 'e.g. APMC Mandi, FPO Hub',
                          border: OutlineInputBorder(),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 32),

                // SUBMIT BUTTON (Matches test assertion: "Sign & Create Batch")
                ElevatedButton.icon(
                  onPressed: _isSubmitting ? null : _submitBatch,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF047857),
                    foregroundColor: Colors.white,
                    minimumSize: const Size(double.infinity, 54),
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    elevation: 2,
                  ),
                  icon: _isSubmitting
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2.5),
                        )
                      : const Icon(Icons.check_circle_outline, size: 22),
                  label: Text(
                    _isEdit ? 'Save Changes to Lot' : 'Sign & Create Batch',
                    style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800, letterSpacing: 0.3),
                  ),
                ),
                const SizedBox(height: 16),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildSectionHeader(String title, IconData icon) {
    return Row(
      children: [
        Icon(icon, size: 18, color: const Color(0xFF047857)),
        const SizedBox(width: 8),
        Text(
          title,
          style: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w800,
            color: Color(0xFF0B3D2E),
            letterSpacing: 0.2,
          ),
        ),
      ],
    );
  }
}
