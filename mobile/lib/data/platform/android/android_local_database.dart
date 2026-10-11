import '../../../domain/platform/local_database.dart';

class AndroidLocalDatabase implements LocalDatabase {
  bool _initialized = false;

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
    // Wipes encrypted database on logout
    _initialized = false;
  }

  bool get isInitialized => _initialized;
}
