import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:annasutra_mobile/data/platform/android/android_local_database.dart';
import 'package:annasutra_mobile/features/sync/sync_service.dart';

void main() {
  test('SyncNotifier correctly tracks outbox items', () async {
    final localDb = AndroidLocalDatabase();
    await localDb.initialize();

    final dio = Dio();
    final notifier = SyncNotifier(localDb, dio);

    expect(notifier.state.pendingCount, 0);

    // Add an outbox event
    await localDb.saveQueuedEvent({
      'path': '/v1/lots/7K3Q9XMD4T2B/dispatch',
      'body': {'event_id': '00000000-0000-0000-0000-000000000001'},
    });

    await notifier.refreshPendingCount();
    expect(notifier.state.pendingCount, 1);
  });
}
