import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:uuid/uuid.dart';

import '../../../data/platform/platform_providers.dart';
import '../../sync/sync_service.dart';

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
  final TextEditingController _packSizeController = TextEditingController();
  final TextEditingController _packCountController = TextEditingController();
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

  void _generatePackets() {
    final size = double.tryParse(_packSizeController.text.trim()) ?? 0.0;
    final count = int.tryParse(_packCountController.text.trim()) ?? 0;
    if (size <= 0 || count <= 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
            content: Text('Please enter valid packet size and count.')),
      );
      return;
    }
    final total = size * count;
    if (total > widget.onHandKg) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
            content: Text(
                'Total ($total kg) exceeds on-hand stock (${widget.onHandKg} kg).')),
      );
      return;
    }
    setState(() {
      for (final c in _children) {
        c.dispose();
      }
      _children.clear();
      for (int i = 0; i < count; i++) {
        final child = ChildLotInput();
        final seq = (i + 1).toString().padLeft(3, '0');
        child.serialController.text = '${widget.lotCode}-PKT-$seq';
        child.qtyController.text = size.toString();
        _children.add(child);
      }
    });
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
    _packSizeController.dispose();
    _packCountController.dispose();
    for (final child in _children) {
      child.dispose();
    }
    super.dispose();
  }

  Future<void> _submitSplit() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    if (_totalChildQty > widget.onHandKg) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
            content: Text('Total child quantities exceed on-hand stock!')),
      );
      return;
    }

    setState(() => _isSubmitting = true);

    try {
      final signer = ref.read(signerProvider);
      final localDb = ref.read(localDatabaseProvider);

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
      final sigBase64 = await signer.sign(payloadBytes);
      payload['device_signature'] = sigBase64;

      await localDb.saveQueuedEvent({
        'path': '/v1/lots/${widget.lotCode}/split',
        'method': 'POST',
        'body': payload,
      });

      await ref.read(syncControllerProvider.notifier).refreshPendingCount();

      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Lot split queued successfully in local outbox!'),
          backgroundColor: Colors.green,
        ),
      );
      context.pop();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
            content: Text('Failed to split lot: $e'),
            backgroundColor: Colors.red),
      );
    } finally {
      if (mounted) {
        setState(() => _isSubmitting = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final remaining = widget.onHandKg - _totalChildQty;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Split Batch (Child Packets)'),
        backgroundColor: const Color(0xFF0B3D2E),
        foregroundColor: Colors.white,
      ),
      body: SafeArea(
        child: Form(
          key: _formKey,
          child: ListView(
            padding: const EdgeInsets.all(16.0),
            children: [
              Card(
                color: const Color(0xFFF8FAFC),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                    side: const BorderSide(color: Color(0xFFE2E8F0))),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Lot: ${widget.lotCode}',
                        style: const TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF0F172A)),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        'Initial On-Hand: ${widget.onHandKg.toStringAsFixed(1)} kg',
                        style: const TextStyle(
                            fontSize: 13, color: Color(0xFF475569)),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Remaining: ${remaining.toStringAsFixed(1)} kg',
                        style: TextStyle(
                          color: remaining < 0
                              ? const Color(0xFFDC2626)
                              : const Color(0xFF047857),
                          fontWeight: FontWeight.w800,
                          fontSize: 13,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 14),

              // Small Packet Batch Creator (Locked Core C12)
              Card(
                color: const Color(0xFFECFDF5),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                    side: const BorderSide(color: Color(0xFF86EFAC))),
                child: Padding(
                  padding: const EdgeInsets.all(14.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Row(
                        children: [
                          Icon(Icons.inventory_outlined,
                              size: 18, color: Color(0xFF047857)),
                          SizedBox(width: 8),
                          Text(
                            'Small Packet Batch Generator',
                            style: TextStyle(
                              fontSize: 13.5,
                              fontWeight: FontWeight.w800,
                              color: Color(0xFF065F46),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 4),
                      const Text(
                        'Auto-generate standard retail packet batches with child QR identifiers.',
                        style: TextStyle(fontSize: 11.5, color: Color(0xFF047857)),
                      ),
                      const SizedBox(height: 10),
                      Row(
                        children: [
                          Expanded(
                            child: TextField(
                              controller: _packSizeController,
                              keyboardType:
                                  const TextInputType.numberWithOptions(
                                      decimal: true),
                              decoration: const InputDecoration(
                                labelText: 'Pack Size (kg)',
                                hintText: 'e.g. 1.0',
                                isDense: true,
                                border: OutlineInputBorder(),
                                filled: true,
                                fillColor: Colors.white,
                              ),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: TextField(
                              controller: _packCountController,
                              keyboardType: TextInputType.number,
                              decoration: const InputDecoration(
                                labelText: 'Pack Count',
                                hintText: 'e.g. 50',
                                isDense: true,
                                border: OutlineInputBorder(),
                                filled: true,
                                fillColor: Colors.white,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 10),
                      OutlinedButton.icon(
                        onPressed: _generatePackets,
                        icon: const Icon(Icons.auto_awesome, size: 16),
                        label: const Text('Generate Packet Batches'),
                        style: OutlinedButton.styleFrom(
                          foregroundColor: const Color(0xFF047857),
                          side: const BorderSide(color: Color(0xFF047857)),
                          minimumSize: const Size(double.infinity, 38),
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
                              style:
                                  const TextStyle(fontWeight: FontWeight.bold),
                            ),
                            if (_children.length > 1)
                              IconButton(
                                icon:
                                    const Icon(Icons.delete, color: Colors.red),
                                onPressed: () => _removeChild(idx),
                              ),
                          ],
                        ),
                        TextFormField(
                          controller: child.serialController,
                          decoration: const InputDecoration(
                            labelText: 'Child Label Serial',
                            border: OutlineInputBorder(),
                          ),
                          validator: (v) {
                            if (v == null || v.trim().isEmpty) {
                              return 'Required';
                            }
                            return null;
                          },
                        ),
                        const SizedBox(height: 8),
                        TextFormField(
                          controller: child.qtyController,
                          keyboardType: const TextInputType.numberWithOptions(
                              decimal: true),
                          decoration: const InputDecoration(
                            labelText: 'Child Quantity (kg)',
                            border: OutlineInputBorder(),
                          ),
                          onChanged: (_) => setState(() {}),
                          validator: (v) {
                            final val = double.tryParse(v ?? '');
                            if (val == null || val <= 0) {
                              return 'Must be positive';
                            }
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
                label: const Text('Add Child Lot Manually'),
                onPressed: _addChild,
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size.fromHeight(50),
                  backgroundColor: const Color(0xFF0B3D2E),
                  foregroundColor: Colors.white,
                ),
                onPressed: _isSubmitting ? null : _submitSplit,
                child: _isSubmitting
                    ? const CircularProgressIndicator(color: Colors.white)
                    : const Text(
                        'Split Lot',
                        style: TextStyle(
                            fontSize: 15, fontWeight: FontWeight.bold),
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
