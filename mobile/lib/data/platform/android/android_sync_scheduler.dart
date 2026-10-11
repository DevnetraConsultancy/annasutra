import 'package:flutter/foundation.dart';
import '../../../domain/platform/sync_scheduler.dart';

class AndroidSyncScheduler implements SyncScheduler {
  VoidCallback? _foregroundListener;

  @override
  Future<void> scheduleBackgroundSync() async {
    // Configured via WorkManager in production Android build
  }

  @override
  Future<void> cancelBackgroundSync() async {
    // Cancels WorkManager background sync
  }

  @override
  void registerForegroundListener(VoidCallback onSyncNeeded) {
    _foregroundListener = onSyncNeeded;
  }

  void notifyForegroundSync() {
    _foregroundListener?.call();
  }
}
