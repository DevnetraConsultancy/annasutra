import 'dart:async';
import 'package:flutter/foundation.dart';
import '../../../domain/platform/sync_scheduler.dart';

/// Web implementation of SyncScheduler.
/// Uses active foreground timers and online event listeners.
class WebSyncScheduler implements SyncScheduler {
  Timer? _periodicTimer;
  VoidCallback? _listener;

  @override
  Future<void> scheduleBackgroundSync() async {
    // Web has no persistent background service: run periodic sync while tab is open
    _periodicTimer?.cancel();
    _periodicTimer = Timer.periodic(const Duration(minutes: 5), (_) {
      _listener?.call();
    });
  }

  @override
  Future<void> cancelBackgroundSync() async {
    _periodicTimer?.cancel();
    _periodicTimer = null;
  }

  @override
  void registerForegroundListener(VoidCallback onSyncNeeded) {
    _listener = onSyncNeeded;
  }
}
