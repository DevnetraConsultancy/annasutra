import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:uuid/uuid.dart';

import '../../../data/platform/platform_providers.dart';
import '../../sync/sync_service.dart';

class InspectionScreen extends ConsumerStatefulWidget {
  final String lotCode;

  const InspectionScreen({
    super.key,
    required this.lotCode,
  });

  @override
  ConsumerState<InspectionScreen> createState() => _InspectionScreenState();
}

class _InspectionScreenState extends ConsumerState<InspectionScreen> {
  final _formKey = GlobalKey<FormState>();
  String _selectedGrade = 'Grade A';
  double _defectPct = 2.0;
  final _tempController = TextEditingController(text: '18.0');
  final _notesController = TextEditingController();
  bool _photoAttached = false;
  bool _isSubmitting = false;

  final List<String> _grades = ['Grade A', 'Grade B', 'Grade C', 'Rejected'];

  @override
  void dispose() {
    _tempController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  Future<void> _submitInspection() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() => _isSubmitting = true);

    try {
      final signer = ref.read(signerProvider);
      final localDb = ref.read(localDatabaseProvider);

      final eventId = const Uuid().v4();
      final eventTime = DateTime.now().toUtc().toIso8601String();
      final tempVal = double.tryParse(_tempController.text.trim());

      final payload = <String, dynamic>{
        'event_id': eventId,
        'event_time': eventTime,
        'grade': _selectedGrade,
        'defect_pct': _defectPct,
        'temperature_c': tempVal,
        'notes': _notesController.text.trim(),
        'evidence_ids': _photoAttached ? <String>[const Uuid().v4()] : <String>[],
      };

      final payloadBytes = Uint8List.fromList(utf8.encode(jsonEncode(payload)));
      final sigBase64 = await signer.sign(payloadBytes);
      payload['device_signature'] = sigBase64;

      await localDb.saveQueuedEvent({
        'path': '/v1/lots/${widget.lotCode}/inspections',
        'method': 'POST',
        'body': payload,
      });

      await ref.read(syncControllerProvider.notifier).refreshPendingCount();

      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Quality inspection recorded successfully in local outbox!'),
          backgroundColor: Colors.green,
        ),
      );
      context.pop();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to record inspection: $e'), backgroundColor: Colors.red),
      );
    } finally {
      if (mounted) {
        setState(() => _isSubmitting = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Inspect Quality / গুণমান পরীক্ষা'),
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
                  child: Text(
                    'Lot: ${widget.lotCode}',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<String>(
                value: _selectedGrade,
                decoration: const InputDecoration(
                  labelText: 'Quality Grade / গ্রেড',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.verified),
                ),
                items: _grades.map((g) {
                  return DropdownMenuItem(value: g, child: Text(g));
                }).toList(),
                onChanged: (val) {
                  if (val != null) {
                    setState(() => _selectedGrade = val);
                  }
                },
              ),
              const SizedBox(height: 16),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Defect Percentage: ${_defectPct.toStringAsFixed(1)}%'),
                  Slider(
                    value: _defectPct,
                    min: 0.0,
                    max: 100.0,
                    divisions: 100,
                    label: '${_defectPct.toStringAsFixed(1)}%',
                    onChanged: (val) => setState(() => _defectPct = val),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _tempController,
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                decoration: const InputDecoration(
                  labelText: 'Storage Temperature (°C) / তাপমাত্রা',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.thermostat),
                ),
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _notesController,
                maxLines: 2,
                decoration: const InputDecoration(
                  labelText: 'Inspection Notes / বিবরণ',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.note),
                ),
              ),
              const SizedBox(height: 16),
              OutlinedButton.icon(
                icon: Icon(_photoAttached ? Icons.check_circle : Icons.camera_alt,
                    color: _photoAttached ? Colors.green : null),
                label: Text(_photoAttached ? 'Evidence Attached / প্রমাণ যুক্ত' : 'Upload Photo Evidence / ছবি আপলোড'),
                onPressed: () {
                  setState(() => _photoAttached = !_photoAttached);
                },
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size.fromHeight(50),
                  backgroundColor: Theme.of(context).colorScheme.primary,
                  foregroundColor: Colors.white,
                ),
                onPressed: _isSubmitting ? null : _submitInspection,
                child: _isSubmitting
                    ? const CircularProgressIndicator(color: Colors.white)
                    : const Text('Inspect Quality / গুণমান পরীক্ষা'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
