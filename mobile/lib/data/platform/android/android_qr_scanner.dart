import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import '../../../domain/platform/qr_scanner.dart';

class AndroidQrScanner implements QrScanner {
  @override
  bool get canScanCamera => true;

  @override
  Widget buildScannerView({required void Function(String code) onScanned}) {
    return MobileScanner(
      onDetect: (capture) {
        final List<Barcode> barcodes = capture.barcodes;
        for (final barcode in barcodes) {
          final String? rawValue = barcode.rawValue;
          if (rawValue != null && rawValue.isNotEmpty) {
            onScanned(rawValue);
            break;
          }
        }
      },
    );
  }
}
