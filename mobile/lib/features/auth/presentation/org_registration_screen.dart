import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../domain/auth_state.dart';
import 'controllers/auth_controller.dart';
import 'dpdp_consent_dialog.dart';

class OrgRegistrationScreen extends ConsumerStatefulWidget {
  final String initialRole;

  const OrgRegistrationScreen({super.key, this.initialRole = 'PRODUCER'});

  @override
  ConsumerState<OrgRegistrationScreen> createState() =>
      _OrgRegistrationScreenState();
}

class _OrgRegistrationScreenState
    extends ConsumerState<OrgRegistrationScreen> {
  final _formKey = GlobalKey<FormState>();
  int _currentStep = 0;
  late String _selectedRole;

  // Step 1: Basic Info / Identity
  final TextEditingController _fullNameCtrl = TextEditingController();
  final TextEditingController _orgNameCtrl = TextEditingController();
  final TextEditingController _designationCtrl = TextEditingController();
  final TextEditingController _altPhoneCtrl = TextEditingController();
  final TextEditingController _stateCtrl = TextEditingController(text: 'West Bengal');
  final TextEditingController _districtCtrl = TextEditingController(text: 'Purba Bardhaman');
  final TextEditingController _subDistrictCtrl = TextEditingController(text: 'Memari-I');
  final TextEditingController _villageCtrl = TextEditingController();
  final TextEditingController _pincodeCtrl = TextEditingController();
  final TextEditingController _addressCtrl = TextEditingController();

  // Business Identity (for non-producers)
  String _constitution = 'Proprietorship';
  final TextEditingController _regNoCtrl = TextEditingController();
  final TextEditingController _panCtrl = TextEditingController();
  final TextEditingController _gstinCtrl = TextEditingController();
  bool _basicTierNoGstin = false;

  // Step 2: Land Holdings (Producer) OR Premises/Licensing (Business)
  // Producer Land:
  double _totalLand = 0.0;
  String _landUnit = 'Acre';
  String _landOwnership = 'Owned';
  final TextEditingController _surveyNoCtrl = TextEditingController();
  final List<Map<String, dynamic>> _plots = [];

  // Business Premises & Licensing:
  final TextEditingController _fssaiCtrl = TextEditingController();
  String _fssaiType = 'State';
  String _premisesType = 'Packhouse / Warehouse';
  String _storageType = 'Ambient';
  final TextEditingController _storageCapacityCtrl = TextEditingController();
  final TextEditingController _scaleCertCtrl = TextEditingController();
  final double _lat = 23.1765;
  final double _lng = 88.1065;

  // Step 3: Role-Specific Module
  // Producer:
  String _farmingPractice = 'Natural Farming (PGS-India)';
  String _irrigationSource = 'Borewell + Canal';
  final List<String> _selectedCropCategories = ['FG', 'VG'];

  // Aggregator:
  final TextEditingController _fpoRegCtrl = TextEditingController();
  final TextEditingController _memberCountCtrl = TextEditingController();
  final TextEditingController _mandiLicenceCtrl = TextEditingController();
  final TextEditingController _catchmentCtrl = TextEditingController();

  // Processor:
  final TextEditingController _factoryLicenceCtrl = TextEditingController();
  final TextEditingController _fssaiMfgCtrl = TextEditingController();
  final TextEditingController _skuNameCtrl = TextEditingController();
  final TextEditingController _conversionRatioCtrl =
      TextEditingController(text: '4:1');

  // Wholesaler:
  final TextEditingController _enamIdCtrl = TextEditingController();
  final TextEditingController _commoditiesHandledCtrl =
      TextEditingController();

  // Distributor:
  final TextEditingController _brandsCtrl = TextEditingController();
  final TextEditingController _territoryCtrl = TextEditingController();
  final TextEditingController _fleetCountCtrl = TextEditingController();

  // Retailer:
  String _retailStoreType = 'Kirana';
  final TextEditingController _shopEstablishmentCtrl =
      TextEditingController();
  bool _sellsLooseProduce = true;

  // Step 4: KYC & Bank
  String _idType = 'PAN';
  final TextEditingController _idNumberCtrl = TextEditingController();
  final TextEditingController _bankNameCtrl = TextEditingController();
  final TextEditingController _accountHolderCtrl = TextEditingController();
  final TextEditingController _accountNoCtrl = TextEditingController();
  final TextEditingController _ifscCtrl = TextEditingController();
  final TextEditingController _upiCtrl = TextEditingController();

  // Step 5: Consents & Review
  bool _showFirstName = true;
  bool _showVillage = true;
  bool _showPhoto = false;
  bool _dpdpConsent = false;
  final TextEditingController _esignOtpCtrl = TextEditingController();
  bool _esignOtpRequested = false;

  static const List<Map<String, String>> _roleList = [
    {'code': 'PRODUCER', 'label': 'Producer / Farmer'},
    {'code': 'AGGREGATOR', 'label': 'Aggregator / FPO / Mandi'},
    {'code': 'PROCESSOR', 'label': 'Processor / Manufacturer / Mill'},
    {'code': 'WHOLESALER', 'label': 'Wholesaler'},
    {'code': 'DISTRIBUTOR', 'label': 'Distributor / Cold Storage'},
    {'code': 'RETAILER', 'label': 'Retailer Shop'},
  ];

  @override
  void initState() {
    super.initState();
    _selectedRole = widget.initialRole;
    if (_selectedRole == 'FARMER') _selectedRole = 'PRODUCER';
  }

  @override
  void dispose() {
    _fullNameCtrl.dispose();
    _orgNameCtrl.dispose();
    _designationCtrl.dispose();
    _altPhoneCtrl.dispose();
    _stateCtrl.dispose();
    _districtCtrl.dispose();
    _subDistrictCtrl.dispose();
    _villageCtrl.dispose();
    _pincodeCtrl.dispose();
    _addressCtrl.dispose();
    _regNoCtrl.dispose();
    _panCtrl.dispose();
    _gstinCtrl.dispose();
    _surveyNoCtrl.dispose();
    _fssaiCtrl.dispose();
    _storageCapacityCtrl.dispose();
    _scaleCertCtrl.dispose();
    _fpoRegCtrl.dispose();
    _memberCountCtrl.dispose();
    _mandiLicenceCtrl.dispose();
    _catchmentCtrl.dispose();
    _factoryLicenceCtrl.dispose();
    _fssaiMfgCtrl.dispose();
    _skuNameCtrl.dispose();
    _conversionRatioCtrl.dispose();
    _enamIdCtrl.dispose();
    _commoditiesHandledCtrl.dispose();
    _brandsCtrl.dispose();
    _territoryCtrl.dispose();
    _fleetCountCtrl.dispose();
    _shopEstablishmentCtrl.dispose();
    _idNumberCtrl.dispose();
    _bankNameCtrl.dispose();
    _accountHolderCtrl.dispose();
    _accountNoCtrl.dispose();
    _ifscCtrl.dispose();
    _upiCtrl.dispose();
    _esignOtpCtrl.dispose();
    super.dispose();
  }

  bool get _isProducer => _selectedRole == 'PRODUCER';

  void _addPlotRow() {
    setState(() {
      _plots.add({
        'name': 'Plot #${_plots.length + 1}',
        'survey_no': _surveyNoCtrl.text.trim().isNotEmpty
            ? _surveyNoCtrl.text.trim()
            : 'Survey ${_plots.length + 101}',
        'acres': 1.0,
        'lat': 23.1765 + (_plots.length * 0.001),
        'lng': 88.1065 + (_plots.length * 0.001),
      });
    });
  }

  Future<void> _submitWizard() async {
    if (!_dpdpConsent) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please accept the DPDP Act 2023 statutory consent.'),
          backgroundColor: Color(0xFFDC2626),
        ),
      );
      return;
    }

    final authNotifier = ref.read(authControllerProvider.notifier);
    final authState = ref.read(authControllerProvider);

    final payload = <String, dynamic>{
      'full_name': _fullNameCtrl.text.trim(),
      'org_name': _orgNameCtrl.text.trim().isNotEmpty
          ? _orgNameCtrl.text.trim()
          : (authState.orgName ?? _fullNameCtrl.text.trim()),
      'role': _selectedRole,
      'email': authState.email,
      'phone': authState.phone,
      'alt_phone': _altPhoneCtrl.text.trim(),
      'state': _stateCtrl.text.trim(),
      'district': _districtCtrl.text.trim(),
      'sub_district': _subDistrictCtrl.text.trim(),
      'village': _villageCtrl.text.trim(),
      'pincode': _pincodeCtrl.text.trim(),
      'address': _addressCtrl.text.trim(),
      'dpdp_consent': true,
      'consumer_visibility': {
        'show_first_name': _showFirstName,
        'show_village': _showVillage,
        'show_photo': _showPhoto,
      },
    };

    if (_isProducer) {
      payload['plots'] = _plots;
      payload['total_land'] = _totalLand;
      payload['land_unit'] = _landUnit;
      payload['farming_practice'] = _farmingPractice;
      payload['irrigation_source'] = _irrigationSource;
      payload['primary_crops'] = _selectedCropCategories;
    } else {
      payload['constitution'] = _constitution;
      payload['registration_no'] = _regNoCtrl.text.trim();
      payload['business_pan'] = _panCtrl.text.trim();
      payload['gstin'] = _basicTierNoGstin ? 'BASIC_TIER' : _gstinCtrl.text.trim();
      payload['fssai_no'] = _fssaiCtrl.text.trim();
      payload['fssai_type'] = _fssaiType;
      payload['premises_type'] = _premisesType;
      payload['storage_type'] = _storageType;
      payload['lat'] = _lat;
      payload['lng'] = _lng;
    }

    final success = await authNotifier.registerRole(
      role: _selectedRole,
      registrationData: payload,
    );

    if (!mounted) return;
    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            '$_selectedRole Registration Submitted! Status: UNDER_REVIEW. Awaiting Admin Approval.',
          ),
          backgroundColor: const Color(0xFF047857),
          behavior: SnackBarBehavior.floating,
        ),
      );
      context.go('/');
    }
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authControllerProvider);
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Entity Registration Wizard'),
        actions: [
          IconButton(
            icon: const Icon(Icons.shield_outlined),
            tooltip: 'DPDP Privacy Notice',
            onPressed: () => DpdpConsentDialog.show(context),
          ),
        ],
      ),
      bottomNavigationBar: SafeArea(
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: ElevatedButton(
            onPressed: () {
              if (_currentStep < 4) {
                setState(() => _currentStep += 1);
              } else {
                _submitWizard();
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF0B3D2E),
              foregroundColor: Colors.white,
              minimumSize: const Size(double.infinity, 50),
            ),
            child: const Text(
              'Register Organisation',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
          ),
        ),
      ),
      body: SafeArea(
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              // Header Banner with Diamond Rule 1 Notice
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                color: const Color(0xFFECFDF5),
                child: Row(
                  children: [
                    const Icon(Icons.verified_user_outlined,
                        color: Color(0xFF047857), size: 18),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Diamond Rule 1: Unique Role ID is minted only when Admin approves. Role: $_selectedRole',
                        style: const TextStyle(
                            fontSize: 11.5,
                            fontWeight: FontWeight.w700,
                            color: Color(0xFF065F46)),
                      ),
                    ),
                  ],
                ),
              ),

              // Role Selector Dropdown
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                child: DropdownButtonFormField<String>(
                  value: _selectedRole,
                  decoration: const InputDecoration(
                    labelText: 'Organisation Type *',
                    border: OutlineInputBorder(),
                    isDense: true,
                  ),
                  items: _roleList
                      .map((r) => DropdownMenuItem<String>(
                            value: r['code']!,
                            child: Text(r['label']!),
                          ))
                      .toList(),
                  onChanged: (val) {
                    if (val != null) setState(() => _selectedRole = val);
                  },
                ),
              ),

              Expanded(
                child: Stepper(
                  type: StepperType.horizontal,
                  currentStep: _currentStep,
                  onStepTapped: (step) => setState(() => _currentStep = step),
                  onStepContinue: () {
                    if (_currentStep < 4) {
                      setState(() => _currentStep += 1);
                    } else {
                      _submitWizard();
                    }
                  },
                  onStepCancel: () {
                    if (_currentStep > 0) {
                      setState(() => _currentStep -= 1);
                    }
                  },
                  controlsBuilder: (context, details) => const SizedBox.shrink(),
                  steps: [
                    // Step 1: Basic Info & Business Identity
                    Step(
                      title: const Text('Identity'),
                      isActive: _currentStep >= 0,
                      state: _currentStep > 0 ? StepState.complete : StepState.indexed,
                      content: _buildStep1Identity(authState, theme),
                    ),

                    // Step 2: Land Holdings OR Premises & Scale
                    Step(
                      title: Text(_isProducer ? 'Land Plots' : 'Premises'),
                      isActive: _currentStep >= 1,
                      state: _currentStep > 1 ? StepState.complete : StepState.indexed,
                      content: _isProducer
                          ? _buildStep2ProducerLand()
                          : _buildStep2BusinessPremises(),
                    ),

                    // Step 3: Cultivation Profile OR Role-Specific Module
                    Step(
                      title: Text(_isProducer ? 'Crops' : 'Operations'),
                      isActive: _currentStep >= 2,
                      state: _currentStep > 2 ? StepState.complete : StepState.indexed,
                      content: _isProducer
                          ? _buildStep3ProducerCultivation()
                          : _buildStep3BusinessOperations(),
                    ),

                    // Step 4: KYC & Bank
                    Step(
                      title: const Text('KYC'),
                      isActive: _currentStep >= 3,
                      state: _currentStep > 3 ? StepState.complete : StepState.indexed,
                      content: _buildStep4KycAndBank(),
                    ),

                    // Step 5: Consents & Submit
                    Step(
                      title: const Text('Consent'),
                      isActive: _currentStep >= 4,
                      state: _currentStep == 4 ? StepState.indexed : StepState.complete,
                      content: _buildStep5ConsentAndReview(authState),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStep1Identity(AuthState authState, ThemeData theme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Set Up Your Organisation',
          style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 4),
        const Text(
          'Step 1: Signatory & Entity Contact Coordinates',
          style: TextStyle(fontSize: 12, color: Color(0xFF64748B)),
        ),
        const SizedBox(height: 14),

        TextFormField(
          controller: _fullNameCtrl,
          decoration: const InputDecoration(
            labelText: 'Full Name (Signatory / Farmer) *',
            border: OutlineInputBorder(),
            isDense: true,
          ),
          validator: (v) => v == null || v.trim().isEmpty ? 'Name is required' : null,
        ),
        const SizedBox(height: 10),

        TextFormField(
          controller: _orgNameCtrl,
          decoration: const InputDecoration(
            labelText: 'Organisation or Farm Name *',
            hintText: 'e.g. Maa Annapurna Organic FPO',
            border: OutlineInputBorder(),
            isDense: true,
          ),
          validator: (v) =>
              v == null || v.trim().isEmpty ? 'Organisation name is required' : null,
        ),
        const SizedBox(height: 10),

        // Read-only Gmail Primary Key (Decision 30)
        TextFormField(
          initialValue: authState.email ?? 'primary-identity@gmail.com',
          readOnly: true,
          decoration: const InputDecoration(
            labelText: 'Primary Identity: Gmail (Mandatory, Read-Only)',
            prefixIcon: Icon(Icons.lock_outline, size: 16),
            border: OutlineInputBorder(),
            isDense: true,
            filled: true,
            fillColor: Color(0xFFF1F5F9),
          ),
        ),
        const SizedBox(height: 10),

        TextFormField(
          controller: _altPhoneCtrl,
          keyboardType: TextInputType.phone,
          decoration: const InputDecoration(
            labelText: 'Alternate / Contact Mobile (Optional)',
            hintText: '+919434011223',
            border: OutlineInputBorder(),
            isDense: true,
          ),
        ),
        const SizedBox(height: 10),

        Row(
          children: [
            Expanded(
              child: TextFormField(
                controller: _stateCtrl,
                decoration: const InputDecoration(
                  labelText: 'State *',
                  border: OutlineInputBorder(),
                  isDense: true,
                ),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: TextFormField(
                controller: _districtCtrl,
                decoration: const InputDecoration(
                  labelText: 'District *',
                  border: OutlineInputBorder(),
                  isDense: true,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 10),

        Row(
          children: [
            Expanded(
              child: TextFormField(
                controller: _villageCtrl,
                decoration: const InputDecoration(
                  labelText: 'Village / City *',
                  hintText: 'e.g. Memari',
                  border: OutlineInputBorder(),
                  isDense: true,
                ),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: TextFormField(
                controller: _pincodeCtrl,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Pincode *',
                  hintText: '6 digits',
                  border: OutlineInputBorder(),
                  isDense: true,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 10),

        TextFormField(
          controller: _addressCtrl,
          decoration: const InputDecoration(
            labelText: 'Address Line 1 / Landmark *',
            hintText: 'Near Gram Panchayat Office',
            border: OutlineInputBorder(),
            isDense: true,
          ),
        ),
        if (!_isProducer) ...[
          const SizedBox(height: 10),
          DropdownButtonFormField<String>(
            value: _constitution,
            decoration: const InputDecoration(
              labelText: 'Business Constitution',
              border: OutlineInputBorder(),
              isDense: true,
            ),
            items: [
              'Proprietorship',
              'Partnership',
              'LLP',
              'Pvt Ltd',
              'FPO',
              'Co-operative',
            ].map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(),
            onChanged: (v) => setState(() => _constitution = v ?? 'Proprietorship'),
          ),
          const SizedBox(height: 10),
          Row(
            children: [
              Expanded(
                child: TextFormField(
                  controller: _regNoCtrl,
                  decoration: const InputDecoration(
                    labelText: 'Registration / CIN No.',
                    border: OutlineInputBorder(),
                    isDense: true,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: TextFormField(
                  controller: _panCtrl,
                  decoration: const InputDecoration(
                    labelText: 'Business PAN',
                    border: OutlineInputBorder(),
                    isDense: true,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Row(
            children: [
              Expanded(
                child: TextFormField(
                  controller: _gstinCtrl,
                  enabled: !_basicTierNoGstin,
                  decoration: InputDecoration(
                    labelText: _basicTierNoGstin ? 'GSTIN (Basic Tier Exemption)' : 'GSTIN *',
                    border: const OutlineInputBorder(),
                    isDense: true,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              FilterChip(
                label: const Text('Basic Tier (No GSTIN)', style: TextStyle(fontSize: 10.5)),
                selected: _basicTierNoGstin,
                onSelected: (v) => setState(() => _basicTierNoGstin = v),
              ),
            ],
          ),
        ],
        const SizedBox(height: 14),
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: const Color(0xFFECFDF5),
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: const Color(0xFFA7F3D0)),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Checkbox(
                value: _dpdpConsent,
                activeColor: const Color(0xFF047857),
                onChanged: (v) => setState(() => _dpdpConsent = v ?? false),
              ),
              const Expanded(
                child: Text(
                  'I consent to store my business contact and supply chain events on AnnaSutra in accordance with the Digital Personal Data Protection (DPDP) Act 2023.',
                  style: TextStyle(fontSize: 12, height: 1.4, color: Color(0xFF065F46)),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildStep2ProducerLand() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Step 2: Farm Plots & Cadastral Land Holdings (Section 4.2)',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13.5),
        ),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: TextFormField(
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Total Land Holding *',
                  hintText: 'e.g. 5.0',
                  border: OutlineInputBorder(),
                  isDense: true,
                ),
                onChanged: (v) => _totalLand = double.tryParse(v.trim()) ?? 0.0,
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: DropdownButtonFormField<String>(
                value: _landOwnership,
                decoration: const InputDecoration(
                  labelText: 'Ownership Type',
                  border: OutlineInputBorder(),
                  isDense: true,
                ),
                items: ['Owned', 'Leased', 'Sharecropped', 'Community']
                    .map((s) => DropdownMenuItem(value: s, child: Text(s)))
                    .toList(),
                onChanged: (v) => setState(() => _landOwnership = v ?? 'Owned'),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: DropdownButtonFormField<String>(
                value: _landUnit,
                decoration: const InputDecoration(
                  labelText: 'Land Unit',
                  border: OutlineInputBorder(),
                  isDense: true,
                ),
                items: ['Acre', 'Hectare', 'Bigha']
                    .map((s) => DropdownMenuItem(value: s, child: Text(s)))
                    .toList(),
                onChanged: (v) => setState(() => _landUnit = v ?? 'Acre'),
              ),
            ),
          ],
        ),
        const SizedBox(height: 10),
        TextFormField(
          controller: _surveyNoCtrl,
          decoration: const InputDecoration(
            labelText: 'Survey / Khasra / Khatauni Number *',
            hintText: 'e.g. Survey 104/A, 108/B',
            border: OutlineInputBorder(),
            isDense: true,
          ),
        ),
        const SizedBox(height: 12),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Mapped Plots (${_plots.length})',
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
            ),
            TextButton.icon(
              onPressed: _addPlotRow,
              icon: const Icon(Icons.add_location_alt_outlined, size: 16),
              label: const Text('+ Add Plot Row'),
            ),
          ],
        ),
        if (_plots.isEmpty)
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFFF8FAFC),
              border: Border.all(color: const Color(0xFFE2E8F0)),
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Text(
              'Tap "+ Add Plot Row" to map individual parcels with GPS coordinate capture.',
              style: TextStyle(fontSize: 12, color: Color(0xFF64748B)),
            ),
          )
        else
          ..._plots.asMap().entries.map((entry) {
            final idx = entry.key;
            final p = entry.value;
            return Container(
              margin: const EdgeInsets.only(bottom: 6),
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: const Color(0xFFF1F5F9),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  const Icon(Icons.landscape, size: 16, color: Color(0xFF047857)),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      '${p['name']} • ${p['survey_no']} • ${p['acres']} Acre • GPS (${(p['lat'] as double).toStringAsFixed(4)}, ${(p['lng'] as double).toStringAsFixed(4)})',
                      style: const TextStyle(fontSize: 11.5, fontWeight: FontWeight.w700),
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.delete_outline, size: 16, color: Colors.red),
                    onPressed: () => setState(() => _plots.removeAt(idx)),
                  ),
                ],
              ),
            );
          }),
      ],
    );
  }

  Widget _buildStep2BusinessPremises() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Step 2: Food Licensing, Premises & Scale (Section 6.2)',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13.5),
        ),
        const SizedBox(height: 10),
        TextFormField(
          controller: _fssaiCtrl,
          keyboardType: TextInputType.number,
          decoration: const InputDecoration(
            labelText: 'FSSAI License Number (Optional)',
            hintText: '14-digit FSSAI licence',
            border: OutlineInputBorder(),
            isDense: true,
          ),
        ),
        const SizedBox(height: 10),
        Row(
          children: [
            Expanded(
              child: DropdownButtonFormField<String>(
                value: _fssaiType,
                decoration: const InputDecoration(
                  labelText: 'FSSAI Type',
                  border: OutlineInputBorder(),
                  isDense: true,
                ),
                items: ['Basic', 'State', 'Central']
                    .map((s) => DropdownMenuItem(value: s, child: Text(s)))
                    .toList(),
                onChanged: (v) => setState(() => _fssaiType = v ?? 'State'),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: DropdownButtonFormField<String>(
                value: _storageType,
                decoration: const InputDecoration(
                  labelText: 'Storage Type',
                  border: OutlineInputBorder(),
                  isDense: true,
                ),
                items: ['Ambient', 'Cold Storage', 'Controlled Atmosphere', 'Frozen']
                    .map((s) => DropdownMenuItem(value: s, child: Text(s)))
                    .toList(),
                onChanged: (v) => setState(() => _storageType = v ?? 'Ambient'),
              ),
            ),
          ],
        ),
        const SizedBox(height: 10),
        DropdownButtonFormField<String>(
          value: _premisesType,
          decoration: const InputDecoration(
            labelText: 'Premises Type *',
            border: OutlineInputBorder(),
            isDense: true,
          ),
          items: [
            'Packhouse / Warehouse',
            'Processing Mill / Factory',
            'Cold Storage Facility',
            'Mandi Shop / Stall',
            'Retail Outlet / Kirana',
          ].map((s) => DropdownMenuItem(value: s, child: Text(s))).toList(),
          onChanged: (v) => setState(() => _premisesType = v ?? 'Packhouse / Warehouse'),
        ),
        const SizedBox(height: 10),
        TextFormField(
          controller: _scaleCertCtrl,
          decoration: const InputDecoration(
            labelText: 'Legal Metrology Weighing Scale Cert No.',
            hintText: 'e.g. LM-WB-2026-9812',
            border: OutlineInputBorder(),
            isDense: true,
          ),
        ),
      ],
    );
  }

  Widget _buildStep3ProducerCultivation() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Step 3: Cultivation Profile & Agricultural Practice (Section 4.2)',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13.5),
        ),
        const SizedBox(height: 10),
        DropdownButtonFormField<String>(
          value: _farmingPractice,
          decoration: const InputDecoration(
            labelText: 'Farming Practice *',
            border: OutlineInputBorder(),
            isDense: true,
          ),
          items: [
            'Conventional',
            'Organic (NPOP Certified)',
            'Natural Farming (PGS-India)',
            'In-Conversion to Organic',
          ].map((s) => DropdownMenuItem(value: s, child: Text(s))).toList(),
          onChanged: (v) =>
              setState(() => _farmingPractice = v ?? 'Natural Farming (PGS-India)'),
        ),
        const SizedBox(height: 10),
        DropdownButtonFormField<String>(
          value: _irrigationSource,
          decoration: const InputDecoration(
            labelText: 'Irrigation Source *',
            border: OutlineInputBorder(),
            isDense: true,
          ),
          items: ['Borewell + Canal', 'Tube-well', 'Rainfed', 'Drip / Sprinkler', 'River']
              .map((s) => DropdownMenuItem(value: s, child: Text(s)))
              .toList(),
          onChanged: (v) => setState(() => _irrigationSource = v ?? 'Borewell + Canal'),
        ),
        const SizedBox(height: 12),
        const Text(
          'Primary Crop Categories (10 Categories):',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
        ),
        const SizedBox(height: 6),
        Wrap(
          spacing: 6,
          runSpacing: 4,
          children: [
            'FG (Grains)',
            'PU (Pulses)',
            'OI (Oilseeds)',
            'FR (Fruits)',
            'VG (Vegetables)',
            'SP (Spices)',
            'CC (Commercial)',
            'LS (Livestock/Dairy)',
            'SC (Special)',
            'OT (Others)',
          ].map((c) {
            final code = c.substring(0, 2);
            final isSel = _selectedCropCategories.contains(code);
            return FilterChip(
              label: Text(c, style: const TextStyle(fontSize: 11)),
              selected: isSel,
              onSelected: (val) {
                setState(() {
                  if (val) {
                    _selectedCropCategories.add(code);
                  } else {
                    _selectedCropCategories.remove(code);
                  }
                });
              },
            );
          }).toList(),
        ),
      ],
    );
  }

  Widget _buildStep3BusinessOperations() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Step 3: Role-Specific Operations Module ($_selectedRole)',
          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13.5),
        ),
        const SizedBox(height: 10),
        if (_selectedRole == 'AGGREGATOR') ...[
          TextFormField(
            controller: _fpoRegCtrl,
            decoration: const InputDecoration(
              labelText: 'FPO / Co-op Registration No.',
              border: OutlineInputBorder(),
              isDense: true,
            ),
          ),
          const SizedBox(height: 10),
          TextFormField(
            controller: _memberCountCtrl,
            keyboardType: TextInputType.number,
            decoration: const InputDecoration(
              labelText: 'Member Farmers Count',
              border: OutlineInputBorder(),
              isDense: true,
            ),
          ),
        ] else if (_selectedRole == 'PROCESSOR') ...[
          TextFormField(
            controller: _factoryLicenceCtrl,
            decoration: const InputDecoration(
              labelText: 'Factory / Mill Licence No.',
              border: OutlineInputBorder(),
              isDense: true,
            ),
          ),
          const SizedBox(height: 10),
          TextFormField(
            controller: _conversionRatioCtrl,
            decoration: const InputDecoration(
              labelText: 'Standard Conversion Ratio (Input:Output)',
              hintText: 'e.g. 4:1 (Potato to Chips)',
              border: OutlineInputBorder(),
              isDense: true,
            ),
          ),
        ] else if (_selectedRole == 'WHOLESALER') ...[
          TextFormField(
            controller: _enamIdCtrl,
            decoration: const InputDecoration(
              labelText: 'e-NAM Trader ID / Mandi Shop No.',
              border: OutlineInputBorder(),
              isDense: true,
            ),
          ),
        ] else if (_selectedRole == 'DISTRIBUTOR') ...[
          TextFormField(
            controller: _brandsCtrl,
            decoration: const InputDecoration(
              labelText: 'Brands Distributed',
              border: OutlineInputBorder(),
              isDense: true,
            ),
          ),
        ] else ...[
          // Retailer
          DropdownButtonFormField<String>(
            value: _retailStoreType,
            decoration: const InputDecoration(
              labelText: 'Retail Format',
              border: OutlineInputBorder(),
              isDense: true,
            ),
            items: ['Kirana', 'Supermarket', 'Online Store', 'HoReCa', 'Exporter']
                .map((s) => DropdownMenuItem(value: s, child: Text(s)))
                .toList(),
            onChanged: (v) => setState(() => _retailStoreType = v ?? 'Kirana'),
          ),
          const SizedBox(height: 10),
          SwitchListTile(
            title: const Text('Sells Loose Produce', style: TextStyle(fontSize: 13)),
            value: _sellsLooseProduce,
            onChanged: (v) => setState(() => _sellsLooseProduce = v),
          ),
        ],
      ],
    );
  }

  Widget _buildStep4KycAndBank() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Step 4: KYC & Settlement Bank Account (Section 4.2 & 6.2)',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13.5),
        ),
        const SizedBox(height: 4),
        const Text(
          'KYC details are permanently locked after Admin approval. Changes will require an Admin Change Request.',
          style: TextStyle(fontSize: 11.5, color: Color(0xFF64748B)),
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              flex: 2,
              child: DropdownButtonFormField<String>(
                value: _idType,
                decoration: const InputDecoration(
                  labelText: 'ID Type',
                  border: OutlineInputBorder(),
                  isDense: true,
                ),
                items: ['PAN', 'Voter ID', 'Aadhaar (Last-4)', 'AgriStack']
                    .map((s) => DropdownMenuItem(value: s, child: Text(s)))
                    .toList(),
                onChanged: (v) => setState(() => _idType = v ?? 'PAN'),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              flex: 3,
              child: TextFormField(
                controller: _idNumberCtrl,
                decoration: const InputDecoration(
                  labelText: 'Identity Number *',
                  hintText: 'e.g. ABCDE1234F',
                  border: OutlineInputBorder(),
                  isDense: true,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 10),
        TextFormField(
          controller: _bankNameCtrl,
          decoration: const InputDecoration(
            labelText: 'Bank Name *',
            hintText: 'e.g. State Bank of India',
            border: OutlineInputBorder(),
            isDense: true,
          ),
        ),
        const SizedBox(height: 10),
        Row(
          children: [
            Expanded(
              child: TextFormField(
                controller: _accountNoCtrl,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Account Number *',
                  border: OutlineInputBorder(),
                  isDense: true,
                ),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: TextFormField(
                controller: _ifscCtrl,
                textCapitalization: TextCapitalization.characters,
                decoration: const InputDecoration(
                  labelText: 'IFSC Code *',
                  hintText: 'SBIN0001234',
                  border: OutlineInputBorder(),
                  isDense: true,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 10),
        TextFormField(
          controller: _upiCtrl,
          decoration: const InputDecoration(
            labelText: 'UPI ID (Optional)',
            hintText: 'mobile@upi',
            border: OutlineInputBorder(),
            isDense: true,
          ),
        ),
      ],
    );
  }

  Widget _buildStep5ConsentAndReview(AuthState authState) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Step 5: Consent, Public Transparency & E-Sign (Section 4.2)',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13.5),
        ),
        const SizedBox(height: 10),

        // Consumer Visibility Toggles (Section 4.2 / Decision 20)
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: const Color(0xFFF8FAFC),
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: const Color(0xFFE2E8F0)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Consumer Transparency Toggles (Public Scan Page):',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
              ),
              SwitchListTile(
                contentPadding: EdgeInsets.zero,
                title: const Text('Show First Name to Consumers',
                    style: TextStyle(fontSize: 12.5)),
                value: _showFirstName,
                onChanged: (v) => setState(() => _showFirstName = v),
              ),
              SwitchListTile(
                contentPadding: EdgeInsets.zero,
                title: const Text('Show Village / District to Consumers',
                    style: TextStyle(fontSize: 12.5)),
                value: _showVillage,
                onChanged: (v) => setState(() => _showVillage = v),
              ),
              SwitchListTile(
                contentPadding: EdgeInsets.zero,
                title: const Text('Show Farm / Facility Photo to Consumers',
                    style: TextStyle(fontSize: 12.5)),
                value: _showPhoto,
                onChanged: (v) => setState(() => _showPhoto = v),
              ),
            ],
          ),
        ),
        const SizedBox(height: 14),

        // DPDP Act 2023 Consent Status
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: const Color(0xFFECFDF5),
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: const Color(0xFFA7F3D0)),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(
                _dpdpConsent ? Icons.check_circle : Icons.error_outline,
                color: _dpdpConsent ? const Color(0xFF047857) : Colors.orange,
                size: 20,
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  _dpdpConsent
                      ? 'DPDP Act 2023 Statutory Consent Accepted.'
                      : 'DPDP Consent Pending (Accepted in Step 1).',
                  style: const TextStyle(fontSize: 12, height: 1.4, color: Color(0xFF065F46), fontWeight: FontWeight.w700),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 14),

        // 6-digit verification code e-sign
        Text(
          'Digital Signature (Code sent to ${authState.email ?? "Gmail"}):',
          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
        ),
        const SizedBox(height: 6),
        Row(
          children: [
            Expanded(
              child: TextFormField(
                controller: _esignOtpCtrl,
                keyboardType: TextInputType.number,
                maxLength: 6,
                decoration: const InputDecoration(
                  labelText: '6-Digit Verification Code',
                  hintText: 'Enter 123456 or OTP',
                  counterText: '',
                  border: OutlineInputBorder(),
                  isDense: true,
                ),
              ),
            ),
            const SizedBox(width: 8),
            OutlinedButton(
              onPressed: () {
                setState(() => _esignOtpRequested = true);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Verification code sent to Gmail.'),
                    backgroundColor: Color(0xFF047857),
                  ),
                );
              },
              child: Text(_esignOtpRequested ? 'Resend Code' : 'Send Code'),
            ),
          ],
        ),
      ],
    );
  }
}
