import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:uuid/uuid.dart';

import 'package:annasutra_mobile/data/platform/platform_providers.dart';
import '../../auth/presentation/controllers/auth_controller.dart';

class BatchCreateScreen extends ConsumerStatefulWidget {
  const BatchCreateScreen({super.key});

  @override
  ConsumerState<BatchCreateScreen> createState() => _BatchCreateScreenState();
}

class _BatchCreateScreenState extends ConsumerState<BatchCreateScreen> {
  final _formKey = GlobalKey<FormState>();
  final TextEditingController _serialController = TextEditingController();
  final TextEditingController _productController = TextEditingController();
  final TextEditingController _varietyController = TextEditingController();
  final TextEditingController _qtyController = TextEditingController();
  final TextEditingController _cratesController = TextEditingController();

  DateTime _harvestDate = DateTime.now();
  bool _isSubmitting = false;

  @override
  void dispose() {
    _serialController.dispose();
    _productController.dispose();
    _varietyController.dispose();
    _qtyController.dispose();
    _cratesController.dispose();
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
      final eventId = const Uuid().v4();
      final serial = _serialController.text.trim().toUpperCase();
      final netQty = double.parse(_qtyController.text.trim());

      final payload = {
        'event_id': eventId,
        'label_serial': serial,
        'product': {
          'name': _productController.text.trim(),
          'variety': _varietyController.text.trim(),
        },
        'harvest_date': _harvestDate.toIso8601String().substring(0, 10),
        'net_qty_kg': netQty,
        'crates': int.tryParse(_cratesController.text.trim()) ?? 0,
        'event_time': DateTime.now().toIso8601String(),
      };

      // Canonical payload bytes for hardware/web key signature
      final canonicalJson = jsonEncode(payload);
      final payloadBytes = Uint8List.fromList(utf8.encode(canonicalJson));

      // Sign locally on device
      final deviceSignature = await signer.sign(payloadBytes);

      // Save locally to offline-first outbox in LocalDatabase
      await localDb.saveQueuedEvent({
        'event_id': eventId,
        'payload': canonicalJson,
        'signature': deviceSignature,
        'status': 'PENDING_SYNC',
        'created_at': DateTime.now().toIso8601String(),
      });

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Batch $serial created and queued for sync!'),
          backgroundColor: Colors.green,
        ),
      );

      context.go('/');
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error creating batch: $e'),
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
      appBar: AppBar(
        title: const Text('Create Harvest Batch'),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20.0),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // QR Sticker input row with scan shortcut
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: TextFormField(
                        controller: _serialController,
                        textCapitalization: TextCapitalization.characters,
                        decoration: const InputDecoration(
                          labelText: 'QR Label Serial *',
                          hintText: 'Scan or enter allocated QR serial',
                          border: OutlineInputBorder(),
                        ),
                        validator: (value) {
                          if (value == null || value.trim().length < 8) {
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
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Align camera with physical crate QR label to scan serial.')),
                          );
                        },
                        child: const Icon(Icons.qr_code_scanner),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                // Produce name
                TextFormField(
                  controller: _productController,
                  decoration: const InputDecoration(
                    labelText: 'Produce Name *',
                    hintText: 'e.g. Tomato, Potato, Rice',
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

                // Variety
                TextFormField(
                  controller: _varietyController,
                  decoration: const InputDecoration(
                    labelText: 'Variety *',
                    hintText: 'e.g. Roma, Hybrid, Basmati',
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
                    child: Text(
                      _harvestDate.toIso8601String().substring(0, 10),
                      style: const TextStyle(fontSize: 16),
                    ),
                  ),
                ),
                const SizedBox(height: 16),

                // Net Quantity kg
                TextFormField(
                  controller: _qtyController,
                  keyboardType: const TextInputType.numberWithOptions(decimal: true),
                  decoration: const InputDecoration(
                    labelText: 'Net Quantity (kg) *',
                    hintText: 'e.g. 500.0',
                    border: OutlineInputBorder(),
                  ),
                  validator: (value) {
                    if (value == null || double.tryParse(value.trim()) == null || double.parse(value.trim()) <= 0) {
                      return 'Enter a positive quantity in kg';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),

                // Crates / Bags count
                TextFormField(
                  controller: _cratesController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(
                    labelText: 'Crates or Bags Count (Optional)',
                    hintText: 'e.g. 20',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 28),

                // Big accessible Submit button
                SizedBox(
                  height: 52,
                  child: ElevatedButton.icon(
                    onPressed: _isSubmitting ? null : _submitBatch,
                    icon: _isSubmitting
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                          )
                        : const Icon(Icons.check_circle_outline, size: 24),
                    label: Text(
                      _isSubmitting ? 'Signing & Saving...' : 'Sign & Create Batch',
                      style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
                const SizedBox(height: 24),

                // Integrity & append-only notice
                Container(
                  padding: const EdgeInsets.all(12),
                  color: Colors.grey.shade100,
                  child: const Text(
                    'Notice: This action creates an immutable, append-only record signed by your device. '
                    'It proves supply-chain records entered and cannot be deleted.',
                    style: TextStyle(fontSize: 12, color: Colors.black54),
                    textAlign: TextAlign.center,
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
