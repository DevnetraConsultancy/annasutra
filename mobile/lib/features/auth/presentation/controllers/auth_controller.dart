import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:annasutra_mobile/data/platform/platform_providers.dart';
import 'package:annasutra_mobile/domain/platform/secure_store.dart';
import 'package:annasutra_mobile/domain/platform/signer.dart';
import '../../domain/auth_state.dart';

final authControllerProvider = StateNotifierProvider<AuthController, AuthState>((ref) {
  final secureStore = ref.watch(secureStoreProvider);
  final signer = ref.watch(signerProvider);
  return AuthController(secureStore: secureStore, signer: signer);
});

class AuthController extends StateNotifier<AuthState> {
  final SecureStore _secureStore;
  final Signer _signer;
  Timer? _cooldownTimer;

  AuthController({
    required SecureStore secureStore,
    required Signer signer,
  })  : _secureStore = secureStore,
        _signer = signer,
        super(const AuthState()) {
    checkSavedAuth();
  }

  Future<void> checkSavedAuth() async {
    final token = await _secureStore.read('access_token');
    final orgVerification = await _secureStore.read('org_verification');
    final orgName = await _secureStore.read('org_name');
    final orgType = await _secureStore.read('org_type');
    final phone = await _secureStore.read('phone');
    if (token != null && token.isNotEmpty) {
      state = state.copyWith(
        status: AuthStatus.authenticated,
        phone: phone,
        accessToken: token,
        orgVerification: orgVerification ?? 'PENDING',
        orgName: orgName,
        orgType: orgType,
      );
    } else {
      state = state.copyWith(status: AuthStatus.unauthenticated);
    }
  }

  Future<bool> requestOtp(String phone, {String language = 'en'}) async {
    final cleanPhone = phone.trim();
    if (cleanPhone.isEmpty || cleanPhone.length < 10) {
      state = state.copyWith(
        status: AuthStatus.error,
        errorMessage: 'Invalid phone number. Must include country code (e.g. +919876543210).',
      );
      return false;
    }

    state = state.copyWith(status: AuthStatus.loading, errorMessage: null);

    // In-memory / HTTP simulated OTP delivery
    await Future<void>.delayed(const Duration(milliseconds: 300));

    state = state.copyWith(
      status: AuthStatus.otpSent,
      phone: cleanPhone,
      cooldownSeconds: 60,
    );

    _startCooldownTimer();
    return true;
  }

  void _startCooldownTimer() {
    _cooldownTimer?.cancel();
    _cooldownTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (state.cooldownSeconds <= 1) {
        timer.cancel();
        state = state.copyWith(cooldownSeconds: 0);
      } else {
        state = state.copyWith(cooldownSeconds: state.cooldownSeconds - 1);
      }
    });
  }

  Future<bool> verifyOtp(String phone, String code) async {
    final cleanCode = code.trim();
    if (cleanCode.length != 6) {
      state = state.copyWith(
        status: AuthStatus.error,
        errorMessage: 'Verification code must be 6 digits.',
      );
      return false;
    }

    state = state.copyWith(status: AuthStatus.loading, errorMessage: null);

    try {
      // Get hardware or web public key for device enrollment
      final pubKey = await _signer.getPublicKey();

      // Simulated network verify call (or real HTTP when connected)
      await Future<void>.delayed(const Duration(milliseconds: 400));

      const mockAccessToken = 'mock_jwt_access_token_annasutra';
      const mockRefreshToken = 'mock_jwt_refresh_token_annasutra';
      const orgVerification = 'PENDING';

      await _secureStore.write('access_token', mockAccessToken);
      await _secureStore.write('refresh_token', mockRefreshToken);
      await _secureStore.write('org_verification', orgVerification);
      await _secureStore.write('device_pub_key', pubKey);

      _cooldownTimer?.cancel();
      state = state.copyWith(
        status: AuthStatus.authenticated,
        phone: phone,
        accessToken: mockAccessToken,
        refreshToken: mockRefreshToken,
        orgVerification: orgVerification,
        cooldownSeconds: 0,
      );
      return true;
    } catch (e) {
      state = state.copyWith(
        status: AuthStatus.error,
        errorMessage: 'Failed to verify code: $e',
      );
      return false;
    }
  }

  Future<bool> registerOrganisation({
    required String name,
    required String orgType,
    String? fssaiNo,
    required String consentNoticeVersion,
    String consentLanguage = 'en',
  }) async {
    state = state.copyWith(status: AuthStatus.loading, errorMessage: null);

    try {
      await Future<void>.delayed(const Duration(milliseconds: 300));
      // Store org verification state
      const orgVerification = 'PENDING';
      await _secureStore.write('org_name', name);
      await _secureStore.write('org_type', orgType);
      await _secureStore.write('org_verification', orgVerification);

      state = state.copyWith(
        status: AuthStatus.authenticated,
        orgVerification: orgVerification,
      );
      return true;
    } catch (e) {
      state = state.copyWith(
        status: AuthStatus.error,
        errorMessage: 'Organisation registration failed: $e',
      );
      return false;
    }
  }

  Future<void> quickLoginAsEntity({
    required String entityRole,
    required String orgName,
    required String phone,
  }) async {
    state = state.copyWith(status: AuthStatus.loading, errorMessage: null);
    try {
      await Future<void>.delayed(const Duration(milliseconds: 300));
      const mockAccessToken = 'mock_jwt_access_token_annasutra';
      const mockRefreshToken = 'mock_jwt_refresh_token_annasutra';
      const orgVerification = 'VERIFIED';

      await _secureStore.write('access_token', mockAccessToken);
      await _secureStore.write('refresh_token', mockRefreshToken);
      await _secureStore.write('org_name', orgName);
      await _secureStore.write('org_type', entityRole);
      await _secureStore.write('org_verification', orgVerification);
      await _secureStore.write('phone', phone);

      state = state.copyWith(
        status: AuthStatus.authenticated,
        phone: phone,
        accessToken: mockAccessToken,
        refreshToken: mockRefreshToken,
        orgVerification: orgVerification,
        orgName: orgName,
        orgType: entityRole,
      );
    } catch (e) {
      state = state.copyWith(
        status: AuthStatus.error,
        errorMessage: 'Entity login failed: $e',
      );
    }
  }

  Future<void> logout() async {
    _cooldownTimer?.cancel();
    await _secureStore.deleteAll();
    state = const AuthState(status: AuthStatus.unauthenticated);
  }

  @override
  void dispose() {
    _cooldownTimer?.cancel();
    super.dispose();
  }
}
