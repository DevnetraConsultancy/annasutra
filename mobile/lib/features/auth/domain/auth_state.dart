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
  final String?
      orgVerification; // 'PENDING', 'UNDER_REVIEW', 'VERIFIED', 'APPROVED'
  final String? orgName;
  final String?
      orgType; // 'PRODUCER', 'AGGREGATOR', 'PROCESSOR', 'WHOLESALER', 'DISTRIBUTOR', 'RETAILER', 'VERIFIER'
  final String accountStatus; // 'ACTIVE', 'DELETION_REQUESTED'
  final String? deletionReason;
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
    this.accountStatus = 'ACTIVE',
    this.deletionReason,
    this.errorMessage,
    this.cooldownSeconds = 0,
  });

  bool get isAuthenticated =>
      status == AuthStatus.authenticated && accessToken != null;

  bool get isOrgVerified =>
      orgVerification == 'VERIFIED' || orgVerification == 'APPROVED';

  bool get isDeletionRequested => accountStatus == 'DELETION_REQUESTED';

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
    String? accountStatus,
    String? deletionReason,
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
      accountStatus: accountStatus ?? this.accountStatus,
      deletionReason: deletionReason ?? this.deletionReason,
      errorMessage: errorMessage ?? this.errorMessage,
      cooldownSeconds: cooldownSeconds ?? this.cooldownSeconds,
    );
  }
}
