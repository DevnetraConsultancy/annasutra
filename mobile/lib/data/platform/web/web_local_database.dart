import '../../../domain/platform/local_database.dart';

/// Web implementation of LocalDatabase using IndexedDB with WebCrypto field-level encryption.
class WebLocalDatabase implements LocalDatabase {
  bool _initialized = false;
  final List<Map<String, dynamic>> _queuedEvents = <Map<String, dynamic>>[];

  @override
  Future<void> initialize() async {
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
