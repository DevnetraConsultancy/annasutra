enum AuthStatus {
  initial,
  loading,
  otpSent,
  authenticated,
  unauthenticated,
  error,
}

class AuthState {
  final AuthStatus status;
  final String? phone;
  final String? accessToken;
  final String? refreshToken;
  final String? orgVerification; // 'PENDING', 'VERIFIED'
  final String? errorMessage;
  final int cooldownSeconds;

  const AuthState({
    this.status = AuthStatus.initial,
    this.phone,
    this.accessToken,
    this.refreshToken,
    this.orgVerification,
    this.errorMessage,
    this.cooldownSeconds = 0,
  });

  bool get isAuthenticated => status == AuthStatus.authenticated && accessToken != null;
  bool get isOrgVerified => orgVerification == 'VERIFIED';

  AuthState copyWith({
    AuthStatus? status,
    String? phone,
    String? accessToken,
    String? refreshToken,
    String? orgVerification,
    String? errorMessage,
    int? cooldownSeconds,
  }) {
    return AuthState(
      status: status ?? this.status,
      phone: phone ?? this.phone,
      accessToken: accessToken ?? this.accessToken,
      refreshToken: refreshToken ?? this.refreshToken,
      orgVerification: orgVerification ?? this.orgVerification,
      errorMessage: errorMessage ?? this.errorMessage,
      cooldownSeconds: cooldownSeconds ?? this.cooldownSeconds,
    );
  }
}
