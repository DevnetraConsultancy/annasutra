import '../../../domain/platform/secure_store.dart';

/// Web implementation of SecureStore.
/// Per docs/16: Tokens are kept in-memory or HttpOnly cookies, never in plaintext localStorage.
class WebSecureStore implements SecureStore {
  final Map<String, String> _inMemoryStore = <String, String>{};

  @override
  Future<void> write(String key, String value) async {
    _inMemoryStore[key] = value;
  }

  @override
  Future<String?> read(String key) async {
    return _inMemoryStore[key];
  }

  @override
  Future<void> delete(String key) async {
    _inMemoryStore.remove(key);
  }

  @override
  Future<void> deleteAll() async {
    _inMemoryStore.clear();
  }
}
