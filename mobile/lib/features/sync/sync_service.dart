import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/platform/local_database.dart';
import '../../data/platform/platform_providers.dart';

class SyncState {
  final int pendingCount;
  final bool isSyncing;
  final String? lastError;
  final DateTime? lastSyncedAt;

  const SyncState({
    this.pendingCount = 0,
    this.isSyncing = false,
    this.lastError,
    this.lastSyncedAt,
  });

  SyncState copyWith({
    int? pendingCount,
    bool? isSyncing,
    String? lastError,
    DateTime? lastSyncedAt,
  }) {
    return SyncState(
      pendingCount: pendingCount ?? this.pendingCount,
      isSyncing: isSyncing ?? this.isSyncing,
      lastError: lastError,
      lastSyncedAt: lastSyncedAt ?? this.lastSyncedAt,
    );
  }
}

class SyncNotifier extends StateNotifier<SyncState> {
  final LocalDatabase _localDb;
  final Dio _dio;

  SyncNotifier(this._localDb, this._dio) : super(const SyncState()) {
    refreshPendingCount();
  }

  Future<void> refreshPendingCount() async {
    final events = await _localDb.getQueuedEvents();
    state = state.copyWith(pendingCount: events.length);
  }

  Future<bool> syncNow() async {
    final queued = await _localDb.getQueuedEvents();
    if (queued.isEmpty) {
      state = state.copyWith(pendingCount: 0, lastSyncedAt: DateTime.now());
      return true;
    }

    state = state.copyWith(isSyncing: true, lastError: null);

    try {
      final itemsToSync = queued.take(100).toList();
      final batchPayload = {
        'items': itemsToSync.map((e) {
          return {
            'path': e['path'] ?? '/v1/lots',
            'method': e['method'] ?? 'POST',
            'body': e['body'] ?? e,
          };
        }).toList(),
      };

      final response = await _dio.post<dynamic>('/v1/sync/events', data: batchPayload);

      if (response.statusCode == 200) {
        // Successful sync batch execution
        await _localDb.wipeAll(); // In scaffold memory store, clear synced
        state = state.copyWith(
          isSyncing: false,
          pendingCount: 0,
          lastSyncedAt: DateTime.now(),
        );
        return true;
      } else {
        state = state.copyWith(
          isSyncing: false,
          lastError: 'Sync server returned status ${response.statusCode}',
        );
        return false;
      }
    } catch (e) {
      // Offline fallback: keep in outbox safely
      state = state.copyWith(
        isSyncing: false,
        lastError: 'Sync queued offline: $e',
      );
      return false;
    }
  }
}

final syncControllerProvider = StateNotifierProvider<SyncNotifier, SyncState>((ref) {
  final localDb = ref.watch(localDatabaseProvider);
  final dio = Dio(
    BaseOptions(
      baseUrl: 'http://localhost:8000',
      connectTimeout: const Duration(seconds: 5),
      receiveTimeout: const Duration(seconds: 5),
    ),
  );
  return SyncNotifier(localDb, dio);
});
