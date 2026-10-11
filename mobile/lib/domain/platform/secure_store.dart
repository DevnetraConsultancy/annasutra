/// Secure storage interface.
/// Android: flutter_secure_storage backed by Android Keystore.
/// Web: Non-extractable WebCrypto key protecting memory/session storage; cookies for session.
abstract class SecureStore {
  Future<void> write(String key, String value);
  Future<String?> read(String key);
  Future<void> delete(String key);
  Future<void> deleteAll();
}
