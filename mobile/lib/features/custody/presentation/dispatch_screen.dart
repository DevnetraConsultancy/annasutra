import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../data/platform/platform_providers.dart';
import '../../sync/sync_service.dart';

class DispatchScreen extends ConsumerStatefulWidget {
  final String lotCode;

  const DispatchScreen({super.key, required this.lotCode});

  @override
  ConsumerState<DispatchScreen> createState() => _DispatchScreenState();
}

class _DispatchScreenState extends ConsumerState<DispatchScreen> {
  final _formKey = GlobalKey<FormState>();
  final _toOrgController = TextEditingController();
  final _qtyController = TextEditingController();
  final _vehicleController = TextEditingController();
  final _destinationController = TextEditingController();
  final _cratesController = TextEditingController();
  bool _isSubmitting = false;

  @override
  void dispose() {
    _toOrgController.dispose();
    _qtyController.dispose();
    _vehicleController.dispose();
    _destinationController.dispose();
    _cratesController.dispose();
    super.dispose();
  }

  Future<void> _submitDispatch() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isSubmitting = true);

    try {
      final signer = ref.read(signerProvider);
      final localDb = ref.read(localDatabaseProvider);

      final eventId = 'd0000000-0000-0000-0000-${DateTime.now().millisecondsSinceEpoch.toString().padLeft(12, '0').substring(0, 12)}';
      final eventTime = DateTime.now().toUtc().toIso8601String();
      final qtyKg = double.parse(_qtyController.text.trim());
      final toOrgId = _toOrgController.text.trim();

      // Sign event payload with hardware device key
      final payloadToSign = Uint8List.fromList(utf8.encode('DISPATCH:$eventId:${widget.lotCode}:$qtyKg:$toOrgId'));
      final signatureBase64 = await signer.sign(payloadToSign);

      final body = {
        'event_id': eventId,
        'event_time': eventTime,
        'to_org_id': toOrgId,
        'qty_kg': qtyKg,
        'vehicle_no': _vehicleController.text.trim().isEmpty ? null : _vehicleController.text.trim(),
        'destination': _destinationController.text.trim().isEmpty ? null : _destinationController.text.trim(),
        'crates': _cratesController.text.trim().isEmpty ? null : int.tryParse(_cratesController.text.trim()),
        'device_signature': signatureBase64,
      };

      // Store in local offline outbox
      await localDb.saveQueuedEvent({
        'path': '/v1/lots/${widget.lotCode}/dispatch',
        'method': 'POST',
        'body': body,
      });

      // Update sync count
      await ref.read(syncControllerProvider.notifier).refreshPendingCount();

      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Dispatch queued successfully in local outbox!'),
          backgroundColor: Colors.green,
        ),
      );
      context.pop();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to dispatch: $e'), backgroundColor: Colors.red),
      );
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Dispatch Batch'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Card(
                color: Colors.green.shade50,
                child: Padding(
                  padding: const EdgeInsets.all(12.0),
                  child: Row(
                    children: [
                      const Icon(Icons.qr_code, color: Colors.green),
                      const SizedBox(width: 8),
                      Text(
                        'Batch Code: ${widget.lotCode}',
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _toOrgController,
                decoration: const InputDecoration(
                  labelText: 'Receiver Organisation ID',
                  hintText: 'Enter partner UUID or select partner',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.business),
                ),
                validator: (val) {
                  if (val == null || val.trim().isEmpty) {
                    return 'Receiver Organisation ID is required';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _qtyController,
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                decoration: const InputDecoration(
                  labelText: 'Quantity to Dispatch (kg)',
                  hintText: 'e.g. 500.0',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.scale),
                ),
                validator: (val) {
                  if (val == null || val.trim().isEmpty) {
                    return 'Quantity is required';
                  }
                  final parsed = double.tryParse(val.trim());
                  if (parsed == null || parsed <= 0) {
                    return 'Quantity must be a positive number';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _cratesController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Crates Count (Optional)',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.inbox),
                ),
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _vehicleController,
                decoration: const InputDecoration(
                  labelText: 'Vehicle Number (Optional)',
                  hintText: 'e.g. WB-02-AB-1234',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.local_shipping),
                ),
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _destinationController,
                decoration: const InputDecoration(
                  labelText: 'Destination (Optional)',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.location_on),
                ),
              ),
              const SizedBox(height: 24),
              ElevatedButton.icon(
                onPressed: _isSubmitting ? null : _submitDispatch,
                icon: _isSubmitting
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                      )
                    : const Icon(Icons.send),
                label: Text(
                  _isSubmitting ? 'Signing & Dispatching...' : 'Sign & Dispatch',
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size.fromHeight(54),
                  backgroundColor: Colors.green.shade800,
                  foregroundColor: Colors.white,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
