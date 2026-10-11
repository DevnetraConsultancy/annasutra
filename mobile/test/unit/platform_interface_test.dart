import 'dart:typed_data';
import 'package:flutter_test/flutter_test.dart';
import 'package:annasutra_mobile/domain/platform/signer.dart';
import 'package:annasutra_mobile/domain/platform/secure_store.dart';
import 'package:annasutra_mobile/data/platform/android/android_signer.dart';
import 'package:annasutra_mobile/data/platform/android/android_local_database.dart';
import 'package:annasutra_mobile/data/platform/web/web_signer.dart';
import 'package:annasutra_mobile/data/platform/web/web_secure_store.dart';
import 'package:annasutra_mobile/data/platform/web/web_local_database.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('Signer Platform Interface Tests', () {
    test('AndroidSigner conforms to Signer interface', () async {
      final Signer signer = AndroidSigner();
      final String pubKey = await signer.getPublicKey();
      expect(pubKey, isNotEmpty);

      final Uint8List hash = Uint8List.fromList(<int>[1, 2, 3, 4, 5, 6, 7, 8]);
      final String signature = await signer.sign(hash);
      expect(signature, isNotEmpty);
    });

    test('WebSigner conforms to Signer interface', () async {
      final Signer signer = WebSigner();
      final String pubKey = await signer.getPublicKey();
      expect(pubKey, isNotEmpty);

      final Uint8List hash = Uint8List.fromList(<int>[1, 2, 3, 4, 5, 6, 7, 8]);
      final String signature = await signer.sign(hash);
      expect(signature, isNotEmpty);
    });
  });

  group('SecureStore Platform Interface Tests', () {
    test('WebSecureStore writes, reads, and deletes safely in memory', () async {
      final SecureStore store = WebSecureStore();
      await store.write('token', 'sample_secret_token');
      expect(await store.read('token'), 'sample_secret_token');

      await store.delete('token');
      expect(await store.read('token'), isNull);
    });
  });

  group('LocalDatabase Platform Interface Tests', () {
    test('AndroidLocalDatabase and WebLocalDatabase initialize and close cleanly', () async {
      final androidDb = AndroidLocalDatabase();
      await androidDb.initialize();
      expect(androidDb.isInitialized, isTrue);
      await androidDb.close();
      expect(androidDb.isInitialized, isFalse);

      final webDb = WebLocalDatabase();
      await webDb.initialize();
      expect(webDb.isInitialized, isTrue);
      await webDb.close();
      expect(webDb.isInitialized, isFalse);
    });
  });
}
