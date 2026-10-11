import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:uuid/uuid.dart';

import 'package:annasutra_mobile/core/platform/signer.dart';
import 'package:annasutra_mobile/features/sync/sync_service.dart';
import 'package:annasutra_mobile/l10n/app_localizations.dart';

class SaleScreen extends ConsumerStatefulWidget {
  final String lotCode;
  final double onHandKg;

  const SaleScreen({
    super.key,
    required this.lotCode,
    this.onHandKg = 100.0,
  });

  @override
  ConsumerState<SaleScreen> createState() => _SaleScreenState();
}

class _SaleScreenState extends ConsumerState<SaleScreen> {
  final _formKey = GlobalKey<FormState>();
  final _qtyController = TextEditingController();
  bool _isSubmitting = false;

  @override
  void dispose() {
    _qtyController.dispose();
    super.dispose();
  }

  Future<void> _submitSale() async {
    if (!_formKey.currentState!.validate()) return;

    final qty = double.parse(_qtyController.text.trim());
    if (qty > widget.onHandKg) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Sale quantity exceeds current on-hand stock!')),
      );
      return;
    }

    setState(() => _isSubmitting = true);

    try {
      final eventId = const Uuid().v4();
      final eventTime = DateTime.now().toUtc().toIso8601String();

      // Zero consumer PII collected or transmitted per privacy rules
      final payload = {
        'event_id': eventId,
        'event_time': eventTime,
        'qty_kg': qty,
        'channel': 'RETAIL',
      };

      final payloadBytes = Uint8List.fromList(utf8.encode(jsonEncode(payload)));
      final signer = Signer();
      final sigBase64 = await signer.sign(payloadBytes);
      payload['device_signature'] = sigBase64;

      await ref.read(syncNotifierProvider.notifier).queueEvent(
        path: '/v1/lots/${widget.lotCode}/sales',
        body: payload,
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Retail sale recorded successfully.')),
        );
        context.pop();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to record sale: $e')),
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
        title: Text(l10n.recordSale),
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
                      const SizedBox(height: 8),
                      Text(
                        'Note: AnnaSutra records aggregate produce sold. No customer personal details are collected.',
                        style: TextStyle(color: Colors.grey[700], fontSize: 12),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _qtyController,
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                decoration: InputDecoration(
                  labelText: l10n.saleQtyKg,
                  border: const OutlineInputBorder(),
                  prefixIcon: const Icon(Icons.point_of_sale),
                ),
                validator: (v) {
                  final val = double.tryParse(v ?? '');
                  if (val == null || val <= 0) return 'Must be a positive quantity';
                  return null;
                },
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size.fromHeight(50),
                  backgroundColor: Theme.of(context).colorScheme.primary,
                  foregroundColor: Colors.white,
                ),
                onPressed: _isSubmitting ? null : _submitSale,
                child: _isSubmitting
                    ? const CircularProgressIndicator(color: Colors.white)
                    : Text(l10n.recordSale),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
