import 'dart:convert';
import 'package:flutter/services.dart';
import '../../../domain/platform/signer.dart';

class AndroidSigner implements Signer {
  static const MethodChannel _channel =
      MethodChannel('in.example.annasutra/keystore_signer');

  @override
  Future<String> getPublicKey() async {
    try {
      final String? pubKey =
          await _channel.invokeMethod<String>('getPublicKey');
      return pubKey ?? 'android_mock_public_key_es256';
    } on MissingPluginException {
      return 'android_stub_public_key_es256';
    }
  }

  @override
  Future<String> sign(Uint8List payloadHash) async {
    try {
      final String? signature =
          await _channel.invokeMethod<String>('signHash', {
        'hash': base64Encode(payloadHash),
      });
      return signature ?? 'android_mock_signature';
    } on MissingPluginException {
      return 'android_stub_signature_${base64Encode(payloadHash).substring(0, 8)}';
    }
  }

  @override
  Future<bool> isHardwareSupported() async {
    try {
      final bool? supported =
          await _channel.invokeMethod<bool>('isHardwareSupported');
      return supported ?? true;
    } on MissingPluginException {
      return true;
    }
  }
}
