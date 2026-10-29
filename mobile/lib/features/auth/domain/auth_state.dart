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
  final String? farmerUid; // Unique Role ID: 26-digit YYYYMMDDHHMMSS+CC+IdentitySegment (null until approved)
  final String? authProvider; // 'OTP', 'GOOGLE'
  final String? accessToken;
  final String? refreshToken;
  final String? orgVerification; // 'NOT_REGISTERED', 'DRAFT', 'SUBMITTED', 'UNDER_REVIEW', 'CHANGES_REQUESTED', 'VERIFIED', 'APPROVED', 'REJECTED'
  final String? orgName;
  final String? orgType; // 'PRODUCER', 'AGGREGATOR', 'PROCESSOR', 'WHOLESALER', 'DISTRIBUTOR', 'RETAILER', 'VERIFIER', 'ADMIN'
  final String accountStatus; // 'ACTIVE', 'DELETION_REQUESTED'
  final String? deletionReason;
  final String? errorMessage;
  final int cooldownSeconds;
  final List<Map<String, dynamic>> roleRegistrations; // C2: All role registrations under this Gmail
  final bool showRolePortal; // True when user is in the Post-Login Role Status Portal

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
    this.roleRegistrations = const [],
    this.showRolePortal = false,
  });

  bool get isAuthenticated =>
      status == AuthStatus.authenticated && accessToken != null;

  bool get isOrgVerified =>
      orgVerification == 'VERIFIED' || orgVerification == 'APPROVED';

  bool get isDeletionRequested => accountStatus == 'DELETION_REQUESTED';

  /// Single Admin identity locked strictly to devnetraconsultancy@gmail.com (Rule 16 / Decision 32)
  bool get isAdmin =>
      email?.trim().toLowerCase() == 'devnetraconsultancy@gmail.com';

  /// List of roles that have been approved by Admin for this Gmail account (Decision 31)
  List<String> get approvedRoles {
    final List<String> list = [];
    for (final reg in roleRegistrations) {
      final st = (reg['status'] ?? '').toString().toUpperCase();
      final r = (reg['role'] ?? '').toString().toUpperCase();
      if ((st == 'APPROVED' || st == 'VERIFIED') && r.isNotEmpty) {
        if (!list.contains(r)) list.add(r);
      }
    }
    // Fallback if roleRegistrations hasn't loaded yet but orgVerification is approved
    if (list.isEmpty && isOrgVerified && orgType != null) {
      final cur = orgType!.toUpperCase();
      if (cur != 'ADMIN' && cur != 'VERIFIER') list.add(cur);
    }
    if (isAdmin && !list.contains('ADMIN')) {
      list.add('ADMIN');
    }
    return list;
  }

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
    List<Map<String, dynamic>>? roleRegistrations,
    bool? showRolePortal,
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
      roleRegistrations: roleRegistrations ?? this.roleRegistrations,
      showRolePortal: showRolePortal ?? this.showRolePortal,
    );
  }
}
