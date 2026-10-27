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
  final String? email;
  final String? farmerUid;
  final String? authProvider; // 'OTP', 'GOOGLE'
  final String? accessToken;
  final String? refreshToken;
  final String? orgVerification; // 'PENDING', 'VERIFIED'
  final String? orgName;
  final String? orgType;
  final String? errorMessage;
  final int cooldownSeconds;

  const AuthState({
    this.status = AuthStatus.initial,
    this.phone,
    this.email,
    this.farmerUid,
    this.authProvider,
    this.accessToken,
    this.refreshToken,
    this.orgVerification,
    this.orgName,
    this.orgType,
    this.errorMessage,
    this.cooldownSeconds = 0,
  });

  bool get isAuthenticated =>
      status == AuthStatus.authenticated && accessToken != null;
  bool get isOrgVerified => orgVerification == 'VERIFIED';

  AuthState copyWith({
    AuthStatus? status,
    String? phone,
    String? email,
    String? farmerUid,
    String? authProvider,
    String? accessToken,
    String? refreshToken,
    String? orgVerification,
    String? orgName,
    String? orgType,
    String? errorMessage,
    int? cooldownSeconds,
  }) {
    return AuthState(
      status: status ?? this.status,
      phone: phone ?? this.phone,
      email: email ?? this.email,
      farmerUid: farmerUid ?? this.farmerUid,
      authProvider: authProvider ?? this.authProvider,
      accessToken: accessToken ?? this.accessToken,
      refreshToken: refreshToken ?? this.refreshToken,
      orgVerification: orgVerification ?? this.orgVerification,
      orgName: orgName ?? this.orgName,
      orgType: orgType ?? this.orgType,
      errorMessage: errorMessage ?? this.errorMessage,
      cooldownSeconds: cooldownSeconds ?? this.cooldownSeconds,
    );
  }
}
