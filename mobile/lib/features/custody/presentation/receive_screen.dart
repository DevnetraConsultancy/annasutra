import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../data/platform/platform_providers.dart';
import '../../sync/sync_service.dart';

class ReceiveScreen extends ConsumerStatefulWidget {
  final String handoverId;
  final String lotCode;
  final double declaredQtyKg;

  const ReceiveScreen({
    super.key,
    required this.handoverId,
    this.lotCode = 'BATCH',
    this.declaredQtyKg = 0.0,
  });

  @override
  ConsumerState<ReceiveScreen> createState() => _ReceiveScreenState();
}

class _ReceiveScreenState extends ConsumerState<ReceiveScreen> {
  bool _showScaleForm = false;
  final _receivedController = TextEditingController();
  final _rejectedController = TextEditingController();
  final _conditionController = TextEditingController();
  final _cratesController = TextEditingController();
  bool _isSubmitting = false;

  @override
  void initState() {
    super.initState();
    if (widget.declaredQtyKg > 0) {
      _receivedController.text = widget.declaredQtyKg.toString();
    }
    _receivedController.addListener(_onWeightChanged);
    _rejectedController.addListener(_onWeightChanged);
  }

  @override
  void dispose() {
    _receivedController.removeListener(_onWeightChanged);
    _rejectedController.removeListener(_onWeightChanged);
    _receivedController.dispose();
    _rejectedController.dispose();
    _conditionController.dispose();
    _cratesController.dispose();
    super.dispose();
  }

  void _onWeightChanged() {
    setState(() {});
  }

  double get _currentDifference {
    final rec = double.tryParse(_receivedController.text) ?? widget.declaredQtyKg;
    final rej = double.tryParse(_rejectedController.text) ?? 0.0;
    return (widget.declaredQtyKg - (rec + rej)).abs();
  }

  double get _allowedTolerance {
    return [0.2, 0.02 * widget.declaredQtyKg].reduce((a, b) => a > b ? a : b);
  }

  bool get _isExceedingTolerance => _currentDifference > _allowedTolerance;

  Future<void> _submitReceipt({required bool isMatches}) async {
    setState(() => _isSubmitting = true);

    try {
      final signer = ref.read(signerProvider);
      final localDb = ref.read(localDatabaseProvider);

      final eventId = 'r0000000-0000-0000-0000-${DateTime.now().millisecondsSinceEpoch.toString().padLeft(12, '0').substring(0, 12)}';
      final eventTime = DateTime.now().toUtc().toIso8601String();

      double receivedQty = widget.declaredQtyKg;
      double rejectedQty = 0.0;

      if (!isMatches) {
        receivedQty = double.tryParse(_receivedController.text.trim()) ?? widget.declaredQtyKg;
        rejectedQty = double.tryParse(_rejectedController.text.trim()) ?? 0.0;
      }

      final payloadToSign = Uint8List.fromList(utf8.encode('RECEIVE:$eventId:${widget.handoverId}:$receivedQty:$rejectedQty'));
      final signatureBase64 = await signer.sign(payloadToSign);

      final body = {
        'event_id': eventId,
        'event_time': eventTime,
        'matches': isMatches,
        'received_qty_kg': receivedQty,
        'rejected_qty_kg': rejectedQty,
        'condition': _conditionController.text.trim().isEmpty ? null : _conditionController.text.trim(),
        'crates_counted': _cratesController.text.trim().isEmpty ? null : int.tryParse(_cratesController.text.trim()),
        'device_signature': signatureBase64,
      };

      await localDb.saveQueuedEvent({
        'path': '/v1/handovers/${widget.handoverId}/receive',
        'method': 'POST',
        'body': body,
      });

      await ref.read(syncControllerProvider.notifier).refreshPendingCount();

      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            isMatches
                ? 'Matches confirmed! Custody accepted in local outbox.'
                : (_isExceedingTolerance
                    ? 'Receipt with discrepancy queued for counterparty review.'
                    : 'Receipt accepted and queued in local outbox.'),
          ),
          backgroundColor: _isExceedingTolerance ? Colors.orange.shade800 : Colors.green,
        ),
      );
      context.pop();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to receive handover: $e'), backgroundColor: Colors.red),
      );
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Receive Batch'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Card(
              color: Colors.blue.shade50,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Batch: ${widget.lotCode}',
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      'Declared by Sender: ${widget.declaredQtyKg} kg',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.blue.shade900,
                      ),
                    ),
                    const SizedBox(height: 4),
                    const Text(
                      'Handover ID: Pending counterparty confirmation',
                      style: TextStyle(fontSize: 12, color: Colors.black54),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),
            // Large 1-Tap "Matches" Button
            ElevatedButton.icon(
              onPressed: _isSubmitting ? null : () => _submitReceipt(isMatches: true),
              icon: const Icon(Icons.check_circle, size: 28),
              label: const Text(
                'Matches Declared Weight',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              style: ElevatedButton.styleFrom(
                minimumSize: const Size.fromHeight(60),
                backgroundColor: Colors.green.shade700,
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              ),
            ),
            const SizedBox(height: 16),
            OutlinedButton.icon(
              onPressed: () {
                setState(() => _showScaleForm = !_showScaleForm);
              },
              icon: Icon(_showScaleForm ? Icons.expand_less : Icons.scale),
              label: Text(_showScaleForm ? 'Hide Scale Entry' : 'Weigh on Scale'),
              style: OutlinedButton.styleFrom(
                minimumSize: const Size.fromHeight(48),
              ),
            ),
            if (_showScaleForm) ...[
              const SizedBox(height: 16),
              Card(
                elevation: 2,
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const Text(
                        'Actual Scale Weights',
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                      ),
                      const SizedBox(height: 12),
                      TextFormField(
                        controller: _receivedController,
                        keyboardType: const TextInputType.numberWithOptions(decimal: true),
                        decoration: const InputDecoration(
                          labelText: 'Received Net Weight (kg)',
                          border: OutlineInputBorder(),
                          prefixIcon: Icon(Icons.check),
                        ),
                      ),
                      const SizedBox(height: 12),
                      TextFormField(
                        controller: _rejectedController,
                        keyboardType: const TextInputType.numberWithOptions(decimal: true),
                        decoration: const InputDecoration(
                          labelText: 'Rejected Weight (kg)',
                          border: OutlineInputBorder(),
                          prefixIcon: Icon(Icons.remove_circle_outline),
                        ),
                      ),
                      const SizedBox(height: 12),
                      TextFormField(
                        controller: _conditionController,
                        decoration: const InputDecoration(
                          labelText: 'Produce Condition',
                          border: OutlineInputBorder(),
                        ),
                      ),
                      const SizedBox(height: 12),
                      TextFormField(
                        controller: _cratesController,
                        keyboardType: TextInputType.number,
                        decoration: const InputDecoration(
                          labelText: 'Crates Counted',
                          border: OutlineInputBorder(),
                        ),
                      ),
                      const SizedBox(height: 14),
                      if (_isExceedingTolerance)
                        Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: Colors.amber.shade100,
                            border: Border.all(color: Colors.amber.shade800),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Row(
                            children: [
                              Icon(Icons.warning, color: Colors.amber.shade900),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  'Discrepancy: ${_currentDifference.toStringAsFixed(1)} kg exceeds allowed tolerance (${_allowedTolerance.toStringAsFixed(1)} kg). Will be flagged for counterparty dispute review.',
                                  style: TextStyle(
                                    color: Colors.amber.shade900,
                                    fontSize: 13,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: _isSubmitting ? null : () => _submitReceipt(isMatches: false),
                        style: ElevatedButton.styleFrom(
                          minimumSize: const Size.fromHeight(50),
                          backgroundColor: Colors.blue.shade800,
                          foregroundColor: Colors.white,
                        ),
                        child: Text(
                          _isSubmitting ? 'Signing & Saving...' : 'Sign & Accept with Scale Weights',
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
