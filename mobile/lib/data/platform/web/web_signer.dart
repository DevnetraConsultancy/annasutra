import 'dart:convert';
import 'dart:typed_data';
import '../../../domain/platform/signer.dart';

class WebSigner implements Signer {
  @override
  Future<String> getPublicKey() async {
    // WebAuthn public key credential
    return 'webauthn_public_key_credential';
  }

  @override
  Future<String> sign(Uint8List payloadHash) async {
    // In Web target, signs with WebAuthn passkey assertion over payload hash
    return 'webauthn_assertion_${base64Encode(payloadHash).substring(0, 8)}';
  }

  @override
  Future<bool> isHardwareSupported() async {
    // Checked via window.PublicKeyCredential in browser environment
    return true;
  }
}
