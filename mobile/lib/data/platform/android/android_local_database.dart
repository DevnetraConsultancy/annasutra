import '../../../domain/platform/local_database.dart';

class AndroidLocalDatabase implements LocalDatabase {
  bool _initialized = false;
  final List<Map<String, dynamic>> _queuedEvents = <Map<String, dynamic>>[];

  @override
  Future<void> initialize() async {
    // In Phase 0 scaffold, records initialization.
    // In Phase 1/2, binds to Drift QueryExecutor with SQLCipher key from AndroidKeystore.
    _initialized = true;
  }

  @override
  Future<void> close() async {
    _initialized = false;
  }

  @override
  Future<void> wipeAll() async {
    _queuedEvents.clear();
    _initialized = false;
  }

  @override
  Future<void> saveQueuedEvent(Map<String, dynamic> event) async {
    _queuedEvents.add(event);
  }

  @override
  Future<List<Map<String, dynamic>>> getQueuedEvents() async {
    return List<Map<String, dynamic>>.unmodifiable(_queuedEvents);
  }

  bool get isInitialized => _initialized;
}
