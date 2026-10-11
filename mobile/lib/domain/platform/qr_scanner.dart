import 'package:flutter/widgets.dart';

/// QR scanner interface.
/// Android: Hardware camera scanner.
/// Web: Browser camera stream + manual code entry fallback.
abstract class QrScanner {
  Widget buildScannerView({required void Function(String code) onScanned});
  bool get canScanCamera;
}
