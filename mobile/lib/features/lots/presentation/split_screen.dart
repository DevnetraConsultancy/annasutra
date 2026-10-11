import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:uuid/uuid.dart';

import 'package:annasutra_mobile/core/platform/signer.dart';
import 'package:annasutra_mobile/features/sync/sync_service.dart';
import 'package:annasutra_mobile/l10n/app_localizations.dart';

class ChildLotInput {
  final TextEditingController serialController = TextEditingController();
  final TextEditingController qtyController = TextEditingController();

  void dispose() {
    serialController.dispose();
    qtyController.dispose();
  }
}

class SplitScreen extends ConsumerStatefulWidget {
  final String lotCode;
  final double onHandKg;

  const SplitScreen({
    super.key,
    required this.lotCode,
    this.onHandKg = 100.0,
  });

  @override
  ConsumerState<SplitScreen> createState() => _SplitScreenState();
}

class _SplitScreenState extends ConsumerState<SplitScreen> {
  final _formKey = GlobalKey<FormState>();
  final List<ChildLotInput> _children = [];
  bool _isSubmitting = false;

  @override
  void initState() {
    super.initState();
    _addChild();
  }

  void _addChild() {
    setState(() {
      _children.add(ChildLotInput());
    });
  }

  void _removeChild(int index) {
    if (_children.length > 1) {
      setState(() {
        _children.removeAt(index).dispose();
      });
    }
  }

  double get _totalChildQty {
    double total = 0.0;
    for (final child in _children) {
      final val = double.tryParse(child.qtyController.text) ?? 0.0;
      total += val;
    }
    return total;
  }

  @override
  void dispose() {
    for (final child in _children) {
      child.dispose();
    }
    super.dispose();
  }

  Future<void> _submitSplit() async {
    if (!_formKey.currentState!.validate()) return;

    if (_totalChildQty > widget.onHandKg) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Total child quantities exceed on-hand stock!')),
      );
      return;
    }

    setState(() => _isSubmitting = true);

    try {
      final eventId = const Uuid().v4();
      final eventTime = DateTime.now().toUtc().toIso8601String();

      final childrenData = _children.map((c) {
        return {
          'label_serial': c.serialController.text.trim(),
          'qty_kg': double.parse(c.qtyController.text.trim()),
        };
      }).toList();

      final payload = {
        'event_id': eventId,
        'event_time': eventTime,
        'children': childrenData,
      };

      final payloadBytes = Uint8List.fromList(utf8.encode(jsonEncode(payload)));
      final signer = Signer();
      final sigBase64 = await signer.sign(payloadBytes);
      payload['device_signature'] = sigBase64;

      await ref.read(syncNotifierProvider.notifier).queueEvent(
        path: '/v1/lots/${widget.lotCode}/split',
        body: payload,
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Lot split submitted successfully.')),
        );
        context.pop();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to split lot: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final remaining = widget.onHandKg - _totalChildQty;

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.splitBatchTitle),
      ),
      body: SafeArea(
        child: Form(
          key: _formKey,
          child: ListView(
            padding: const EdgeInsets.all(16.0),
            children: [
              Card(
                color: Theme.of(context).colorScheme.surfaceContainerHighest,
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
                      Text('Initial On-Hand: ${widget.onHandKg.toStringAsFixed(1)} kg'),
                      const SizedBox(height: 4),
                      Text(
                        l10n.remainingKg(remaining.toStringAsFixed(1)),
                        style: TextStyle(
                          color: remaining < 0 ? Colors.red : Colors.green[800],
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              ..._children.asMap().entries.map((entry) {
                final idx = entry.key;
                final child = entry.value;
                return Card(
                  margin: const EdgeInsets.only(bottom: 12.0),
                  child: Padding(
                    padding: const EdgeInsets.all(12.0),
                    child: Column(
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              'Child Lot #${idx + 1}',
                              style: const TextStyle(fontWeight: FontWeight.bold),
                            ),
                            if (_children.length > 1)
                              IconButton(
                                icon: const Icon(Icons.delete, color: Colors.red),
                                onPressed: () => _removeChild(idx),
                              ),
                          ],
                        ),
                        TextFormField(
                          controller: child.serialController,
                          decoration: InputDecoration(
                            labelText: l10n.childSerial,
                            border: const OutlineInputBorder(),
                          ),
                          validator: (v) => v == null || v.trim().isEmpty ? 'Required' : null,
                        ),
                        const SizedBox(height: 8),
                        TextFormField(
                          controller: child.qtyController,
                          keyboardType: const TextInputType.numberWithOptions(decimal: true),
                          decoration: InputDecoration(
                            labelText: l10n.childQty,
                            border: const OutlineInputBorder(),
                          ),
                          onChanged: (_) => setState(() {}),
                          validator: (v) {
                            final val = double.tryParse(v ?? '');
                            if (val == null || val <= 0) return 'Must be positive';
                            return null;
                          },
                        ),
                      ],
                    ),
                  ),
                );
              }),
              OutlinedButton.icon(
                icon: const Icon(Icons.add),
                label: Text(l10n.addChild),
                onPressed: _addChild,
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size.fromHeight(50),
                  backgroundColor: Theme.of(context).colorScheme.primary,
                  foregroundColor: Colors.white,
                ),
                onPressed: _isSubmitting ? null : _submitSplit,
                child: _isSubmitting
                    ? const CircularProgressIndicator(color: Colors.white)
                    : Text(l10n.splitLot),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
