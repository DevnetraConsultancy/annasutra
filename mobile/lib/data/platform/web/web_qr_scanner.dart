import 'package:flutter/material.dart';
import '../../../domain/platform/qr_scanner.dart';

/// Web implementation of QrScanner with browser stream or manual entry.
class WebQrScanner implements QrScanner {
  @override
  bool get canScanCamera => true;

  @override
  Widget buildScannerView({required void Function(String code) onScanned}) {
    final TextEditingController controller = TextEditingController();
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: <Widget>[
            const Icon(Icons.qr_code_scanner, size: 64, color: Colors.green),
            const SizedBox(height: 16),
            const Text(
              'Enter Batch Code (e.g., 7K3Q-9XMD)',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: controller,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                hintText: '12-character batch code',
              ),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {
                if (controller.text.trim().isNotEmpty) {
                  onScanned(controller.text.trim().toUpperCase());
                }
              },
              child: const Text('Submit Code'),
            ),
          ],
        ),
      ),
    );
  }
}
