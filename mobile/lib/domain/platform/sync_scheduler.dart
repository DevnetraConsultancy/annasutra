import 'package:flutter/foundation.dart';

/// Sync scheduler interface.
/// Android: WorkManager background tasks + foreground resume listener.
/// Web: Foreground periodic timer + window online/offline listeners.
abstract class SyncScheduler {
  Future<void> scheduleBackgroundSync();
  Future<void> cancelBackgroundSync();
  void registerForegroundListener(VoidCallback onSyncNeeded);
}
