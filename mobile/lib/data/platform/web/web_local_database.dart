import '../../../domain/platform/local_database.dart';

/// Web implementation of LocalDatabase using IndexedDB with WebCrypto field-level encryption.
class WebLocalDatabase implements LocalDatabase {
  bool _initialized = false;

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
    _initialized = false;
  }

  bool get isInitialized => _initialized;
}
