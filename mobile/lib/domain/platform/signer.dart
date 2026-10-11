import 'dart:typed_data';

/// Abstract hardware/web signing interface.
/// Android: Hardware-backed ES256 key in Android Keystore.
/// Web: WebAuthn passkey assertion.
abstract class Signer {
  Future<String> getPublicKey();
  Future<String> sign(Uint8List payloadHash);
  Future<bool> isHardwareSupported();
}
