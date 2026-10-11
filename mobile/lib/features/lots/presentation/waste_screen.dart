import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:uuid/uuid.dart';

import 'package:annasutra_mobile/core/platform/signer.dart';
import 'package:annasutra_mobile/features/sync/sync_service.dart';
import 'package:annasutra_mobile/l10n/app_localizations.dart';

class WasteScreen extends ConsumerStatefulWidget {
  final String lotCode;
  final double onHandKg;

  const WasteScreen({
    super.key,
    required this.lotCode,
    this.onHandKg = 100.0,
  });

  @override
  ConsumerState<WasteScreen> createState() => _WasteScreenState();
}

class _WasteScreenState extends ConsumerState<WasteScreen> {
  final _formKey = GlobalKey<FormState>();
  final _qtyController = TextEditingController();
  String _selectedReason = 'TRANSIT_SPOILAGE';
  bool _photoAttached = false;
  bool _isSubmitting = false;

  final List<String> _reasons = [
    'TRANSIT_SPOILAGE',
    'PEST_DAMAGE',
    'HANDLING_DAMAGE',
    'EXPIRED_SHELF_LIFE',
    'OVER_RIPENESS',
  ];

  @override
  void dispose() {
    _qtyController.dispose();
    super.dispose();
  }

  Future<void> _submitWaste() async {
    if (!_formKey.currentState!.validate()) return;

    final qty = double.parse(_qtyController.text.trim());
    if (qty > widget.onHandKg) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Waste quantity exceeds current on-hand stock!')),
      );
      return;
    }

    setState(() => _isSubmitting = true);

    try {
      final eventId = const Uuid().v4();
      final eventTime = DateTime.now().toUtc().toIso8601String();

      final payload = {
        'event_id': eventId,
        'event_time': eventTime,
        'qty_kg': qty,
        'reason_code': _selectedReason,
        'evidence_ids': _photoAttached ? [const Uuid().v4()] : [],
      };

      final payloadBytes = Uint8List.fromList(utf8.encode(jsonEncode(payload)));
      final signer = Signer();
      final sigBase64 = await signer.sign(payloadBytes);
      payload['device_signature'] = sigBase64;

      await ref.read(syncNotifierProvider.notifier).queueEvent(
        path: '/v1/lots/${widget.lotCode}/waste',
        body: payload,
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Waste recorded successfully.')),
        );
        context.pop();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to record waste: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.recordWaste),
      ),
      body: SafeArea(
        child: Form(
          key: _formKey,
          child: ListView(
            padding: const EdgeInsets.all(16.0),
            children: [
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Lot: ${widget.lotCode}',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 4),
                      Text('On-Hand: ${widget.onHandKg.toStringAsFixed(1)} kg'),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _qtyController,
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                decoration: InputDecoration(
                  labelText: l10n.wasteQtyKg,
                  border: const OutlineInputBorder(),
                  prefixIcon: const Icon(Icons.delete_outline),
                ),
                validator: (v) {
                  final val = double.tryParse(v ?? '');
                  if (val == null || val <= 0) return 'Must be a positive quantity';
                  return null;
                },
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<String>(
                value: _selectedReason,
                decoration: InputDecoration(
                  labelText: l10n.wasteReason,
                  border: const OutlineInputBorder(),
                  prefixIcon: const Icon(Icons.report_problem_outlined),
                ),
                items: _reasons.map((r) {
                  return DropdownMenuItem(value: r, child: Text(r));
                }).toList(),
                onChanged: (val) {
                  if (val != null) setState(() => _selectedReason = val);
                },
              ),
              const SizedBox(height: 16),
              OutlinedButton.icon(
                icon: Icon(_photoAttached ? Icons.check_circle : Icons.camera_alt,
                    color: _photoAttached ? Colors.green : null),
                label: Text(_photoAttached ? 'Evidence Attached' : l10n.uploadPhoto),
                onPressed: () {
                  setState(() => _photoAttached = !_photoAttached);
                },
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size.fromHeight(50),
                  backgroundColor: Colors.orange[800],
                  foregroundColor: Colors.white,
                ),
                onPressed: _isSubmitting ? null : _submitWaste,
                child: _isSubmitting
                    ? const CircularProgressIndicator(color: Colors.white)
                    : Text(l10n.recordWaste),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
