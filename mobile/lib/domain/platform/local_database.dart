/// Local encrypted database interface.
/// Android: Drift with SQLCipher encryption.
/// Web: Drift on IndexedDB with WebCrypto field-level encryption.
abstract class LocalDatabase {
  Future<void> initialize();
  Future<void> close();
  Future<void> wipeAll();
}
