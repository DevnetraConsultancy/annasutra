import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:annasutra_mobile/domain/platform/local_database.dart';
import 'package:annasutra_mobile/domain/platform/qr_scanner.dart';
import 'package:annasutra_mobile/domain/platform/secure_store.dart';
import 'package:annasutra_mobile/domain/platform/signer.dart';
import 'package:annasutra_mobile/domain/platform/sync_scheduler.dart';

import 'android/android_local_database.dart';
import 'android/android_qr_scanner.dart';
import 'android/android_secure_store.dart';
import 'android/android_signer.dart';
import 'android/android_sync_scheduler.dart';

import 'web/web_local_database.dart';
import 'web/web_qr_scanner.dart';
import 'web/web_secure_store.dart';
import 'web/web_signer.dart';
import 'web/web_sync_scheduler.dart';

final secureStoreProvider = Provider<SecureStore>((ref) {
  if (kIsWeb) {
    return WebSecureStore();
  }
  return AndroidSecureStore();
});

final signerProvider = Provider<Signer>((ref) {
  if (kIsWeb) {
    return WebSigner();
  }
  return AndroidSigner();
});

final localDatabaseProvider = Provider<LocalDatabase>((ref) {
  if (kIsWeb) {
    return WebLocalDatabase();
  }
  return AndroidLocalDatabase();
});

final syncSchedulerProvider = Provider<SyncScheduler>((ref) {
  if (kIsWeb) {
    return WebSyncScheduler();
  }
  return AndroidSyncScheduler();
});

final qrScannerProvider = Provider<QrScanner>((ref) {
  if (kIsWeb) {
    return WebQrScanner();
  }
  return AndroidQrScanner();
});
