import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../domain/auth_state.dart';
import 'controllers/auth_controller.dart';

class OrgRegistrationScreen extends ConsumerStatefulWidget {
  const OrgRegistrationScreen({super.key});

  @override
  ConsumerState<OrgRegistrationScreen> createState() =>
      _OrgRegistrationScreenState();
}

class _OrgRegistrationScreenState extends ConsumerState<OrgRegistrationScreen> {
  final _formKey = GlobalKey<FormState>();
  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _fssaiController = TextEditingController();
  String _selectedOrgType = 'FARMER';
  bool _consentGiven = false;

  final List<String> _orgTypes = [
    'FARMER',
    'AGGREGATOR',
    'WHOLESALER',
    'DISTRIBUTOR',
    'RETAILER',
    'LAB',
    'OPERATOR',
  ];

  @override
  void dispose() {
    _nameController.dispose();
    _fssaiController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authControllerProvider);
    final authNotifier = ref.read(authControllerProvider.notifier);
    final theme = Theme.of(context);

    ref.listen<AuthState>(authControllerProvider, (previous, next) {
      if (previous?.status == AuthStatus.loading &&
          next.status == AuthStatus.authenticated) {
        context.go('/');
      }
    });

    return Scaffold(
      appBar: AppBar(
        title: const Text('Register Business / Farm'),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const SizedBox(height: 12),
                Text(
                  'Set Up Your Organisation',
                  style: theme.textTheme.headlineSmall
                      ?.copyWith(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                const Text(
                  'Provide your business identity to participate in digital supply-chain traceability.',
                  style: TextStyle(color: Colors.black54),
                ),
                const SizedBox(height: 24),

                // Org Name
                TextFormField(
                  controller: _nameController,
                  decoration: const InputDecoration(
                    labelText: 'Organisation or Farm Name *',
                    hintText: 'e.g., Sundarban Honey Farmers Co-op',
                    border: OutlineInputBorder(),
                  ),
                  validator: (value) {
                    if (value == null || value.trim().isEmpty) {
                      return 'Organisation name is required';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 20),

                // Org Type Dropdown
                DropdownButtonFormField<String>(
                  value: _selectedOrgType,
                  decoration: const InputDecoration(
                    labelText: 'Organisation Type *',
                    border: OutlineInputBorder(),
                  ),
                  items: _orgTypes.map((type) {
                    return DropdownMenuItem<String>(
                      value: type,
                      child: Text(type),
                    );
                  }).toList(),
                  onChanged: (val) {
                    if (val != null) {
                      setState(() {
                        _selectedOrgType = val;
                      });
                    }
                  },
                ),
                const SizedBox(height: 20),

                // FSSAI No
                TextFormField(
                  controller: _fssaiController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(
                    labelText: 'FSSAI License Number (Optional)',
                    hintText: '14-digit FSSAI number',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 24),

                // DPDP Consent Checkbox
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.blue.shade50,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.blue.shade200),
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Checkbox(
                        value: _consentGiven,
                        onChanged: (val) {
                          setState(() {
                            _consentGiven = val ?? false;
                          });
                        },
                      ),
                      const Expanded(
                        child: Text(
                          'I consent to store my business contact and supply chain events on AnnaSutra in accordance with the Digital Personal Data Protection (DPDP) Act 2023.',
                          style: TextStyle(fontSize: 13, height: 1.4),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 32),

                // Submit Button
                SizedBox(
                  height: 52,
                  child: ElevatedButton(
                    onPressed: (!_consentGiven ||
                            authState.status == AuthStatus.loading)
                        ? null
                        : () {
                            if (_formKey.currentState?.validate() ?? false) {
                              authNotifier.registerOrganisation(
                                name: _nameController.text.trim(),
                                orgType: _selectedOrgType,
                                fssaiNo: _fssaiController.text.trim().isEmpty
                                    ? null
                                    : _fssaiController.text.trim(),
                                consentNoticeVersion: '1.0',
                              );
                            }
                          },
                    child: authState.status == AuthStatus.loading
                        ? const CircularProgressIndicator(color: Colors.white)
                        : const Text(
                            'Register Organisation',
                            style: TextStyle(
                                fontSize: 18, fontWeight: FontWeight.bold),
                          ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
