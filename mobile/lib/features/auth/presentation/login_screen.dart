import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../domain/auth_state.dart';
import 'controllers/auth_controller.dart';
import 'dpdp_consent_dialog.dart';

class LoginScreen extends ConsumerStatefulWidget {
  final String initialRole;

  const LoginScreen({super.key, this.initialRole = 'PRODUCER'});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final TextEditingController _phoneController = TextEditingController();
  final TextEditingController _otpController = TextEditingController();
  final _formKey = GlobalKey<FormState>();

  bool _isGoogleMode = false;
  late String _selectedRole;

  static const List<Map<String, String>> _roles = [
    {'code': 'PRODUCER', 'label': 'Farmer / FPO Producer'},
    {'code': 'AGGREGATOR', 'label': 'Mandi Aggregator / APMC'},
    {'code': 'PROCESSOR', 'label': 'Processor / Mill'},
    {'code': 'WHOLESALER', 'label': 'Wholesaler'},
    {'code': 'DISTRIBUTOR', 'label': 'Distributor / Cold Chain'},
    {'code': 'RETAILER', 'label': 'Retailer Shop'},
    {'code': 'VERIFIER', 'label': 'Public Consumer / Verifier'},
  ];

  @override
  void initState() {
    super.initState();
    _selectedRole = widget.initialRole;
  }

  @override
  void dispose() {
    _phoneController.dispose();
    _otpController.dispose();
    super.dispose();
  }

  Future<void> _continueWithGoogle() async {
    final success = await ref
        .read(authControllerProvider.notifier)
        .signInWithNativeGoogle(role: _selectedRole);
    if (!mounted) return;
    if (success) {
      final auth = ref.read(authControllerProvider);
      if (auth.orgVerification == 'PENDING' ||
          auth.orgVerification == 'UNDER_REVIEW') {
        context.go('/register-org');
      } else {
        context.go('/');
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authControllerProvider);
    final authNotifier = ref.read(authControllerProvider.notifier);

    ref.listen<AuthState>(authControllerProvider, (previous, next) {
      if (next.status == AuthStatus.authenticated) {
        if (next.orgVerification == 'PENDING' ||
            next.orgVerification == 'UNDER_REVIEW') {
          context.go('/register-org');
        } else {
          context.go('/');
        }
      }
    });

    final bool isOtpSent = authState.status == AuthStatus.otpSent;
    final bool isLoading = authState.status == AuthStatus.loading;

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAF7),
      appBar: AppBar(
        title: const Text('AnnaSutra'),
        actions: [
          IconButton(
            icon: const Icon(Icons.shield_outlined),
            tooltip: 'Data Protection & Privacy Notice',
            onPressed: () => DpdpConsentDialog.show(context),
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 20.0),
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 520),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // Brand & Developer Header
                    Center(
                      child: Column(
                        children: [
                          Container(
                            width: 72,
                            height: 72,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              border: Border.all(
                                  color: const Color(0xFFE67E22), width: 2),
                              boxShadow: const [
                                BoxShadow(
                                    color: Colors.black12,
                                    blurRadius: 8,
                                    offset: Offset(0, 3)),
                              ],
                            ),
                            child: ClipOval(
                              child: Image.asset(
                                'assets/images/annasutra_emblem.jpg',
                                fit: BoxFit.cover,
                                errorBuilder: (_, __, ___) =>
                                    const CircleAvatar(
                                  backgroundColor: Color(0xFF0B3D2E),
                                  child: Icon(Icons.eco,
                                      color: Colors.amber, size: 36),
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(height: 12),
                          const Text(
                            'AnnaSutra',
                            style: TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.w900,
                              color: Color(0xFF0B3D2E),
                            ),
                          ),
                          const SizedBox(height: 4),
                          const Text(
                            'Agri-Traceability Secure Access',
                            style: TextStyle(
                              fontSize: 13,
                              color: Color(0xFF64748B),
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Image.asset(
                                'assets/images/cdac_logo.png',
                                height: 16,
                                errorBuilder: (_, __, ___) =>
                                    const Icon(Icons.memory, size: 14),
                              ),
                              const SizedBox(width: 6),
                              const Text(
                                'Technology Partner: C-DAC | MeitY',
                                style: TextStyle(
                                    fontSize: 11,
                                    color: Color(0xFF475569),
                                    fontWeight: FontWeight.w600),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 24),

                    // Primary Note: Gmail Identity
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: const Color(0xFFECFDF5),
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(color: const Color(0xFFA7F3D0)),
                      ),
                      child: const Row(
                        children: [
                          Icon(Icons.mark_email_read_outlined,
                              size: 16, color: Color(0xFF047857)),
                          SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              'Primary Identity: Sign in with Google (Gmail). Mobile number is optional.',
                              style: TextStyle(
                                  fontSize: 11.5,
                                  fontWeight: FontWeight.w700,
                                  color: Color(0xFF065F46)),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Mode Switcher: Mobile OTP vs Google Sign-In
                    Row(
                      children: [
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: () =>
                                setState(() => _isGoogleMode = false),
                            icon: Icon(
                              Icons.sms_outlined,
                              size: 16,
                              color: !_isGoogleMode
                                  ? Colors.white
                                  : const Color(0xFF0B3D2E),
                            ),
                            label: const Text('Mobile OTP'),
                            style: OutlinedButton.styleFrom(
                              backgroundColor: !_isGoogleMode
                                  ? const Color(0xFF0B3D2E)
                                  : Colors.white,
                              foregroundColor: !_isGoogleMode
                                  ? Colors.white
                                  : const Color(0xFF0B3D2E),
                              side: const BorderSide(color: Color(0xFF0B3D2E)),
                            ),
                          ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: () =>
                                setState(() => _isGoogleMode = true),
                            icon: Icon(
                              Icons.account_circle_outlined,
                              size: 16,
                              color: _isGoogleMode
                                  ? Colors.white
                                  : const Color(0xFF0B3D2E),
                            ),
                            label: const Text('Google Sign-In'),
                            style: OutlinedButton.styleFrom(
                              backgroundColor: _isGoogleMode
                                  ? const Color(0xFF0B3D2E)
                                  : Colors.white,
                              foregroundColor: _isGoogleMode
                                  ? Colors.white
                                  : const Color(0xFF0B3D2E),
                              side: const BorderSide(color: Color(0xFF0B3D2E)),
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 20),

                    if (!_isGoogleMode) ...[
                      // Secondary Option Notice (Decision 30)
                      const Text(
                        'Only for mobile numbers already verified and linked to your Gmail account',
                        style: TextStyle(
                          fontSize: 11.5,
                          color: Color(0xFF64748B),
                          fontStyle: FontStyle.italic,
                        ),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 10),

                      // Phone Input Field
                      TextFormField(
                        controller: _phoneController,
                        keyboardType: TextInputType.phone,
                        enabled: !isOtpSent && !isLoading,
                        decoration: const InputDecoration(
                          labelText: 'Registered Mobile Number (+91)',
                          hintText: 'Enter 10-digit mobile number',
                          prefixIcon: Icon(Icons.phone),
                          border: OutlineInputBorder(),
                        ),
                        validator: (value) {
                          if (value == null || value.trim().length < 10) {
                            return 'Enter a valid phone number with country code';
                          }
                          return null;
                        },
                      ),
                      const SizedBox(height: 16),

                      if (!isOtpSent) ...[
                        SizedBox(
                          height: 52,
                          child: ElevatedButton(
                            onPressed: isLoading
                                ? null
                                : () {
                                    if (_formKey.currentState?.validate() ??
                                        false) {
                                      authNotifier.requestOtp(
                                          _phoneController.text.trim());
                                    }
                                  },
                            child: isLoading
                                ? const SizedBox(
                                    width: 24,
                                    height: 24,
                                    child: CircularProgressIndicator(
                                        color: Colors.white, strokeWidth: 2),
                                  )
                                : const Text('Send OTP',
                                    style: TextStyle(
                                        fontSize: 16,
                                        fontWeight: FontWeight.bold)),
                          ),
                        ),
                      ],

                      if (isOtpSent) ...[
                        TextFormField(
                          controller: _otpController,
                          keyboardType: TextInputType.number,
                          maxLength: 6,
                          enabled: !isLoading,
                          decoration: const InputDecoration(
                            labelText: '6-Digit Verification Code',
                            hintText: 'Enter 6-digit OTP',
                            prefixIcon: Icon(Icons.password),
                            border: OutlineInputBorder(),
                          ),
                          validator: (value) {
                            if (value == null || value.trim().length != 6) {
                              return 'Enter 6-digit code';
                            }
                            return null;
                          },
                        ),
                        const SizedBox(height: 14),
                        SizedBox(
                          height: 52,
                          child: ElevatedButton(
                            onPressed: isLoading
                                ? null
                                : () {
                                    if (_otpController.text.trim().length ==
                                        6) {
                                      authNotifier.verifyOtp(
                                        _phoneController.text.trim(),
                                        _otpController.text.trim(),
                                        role: _selectedRole,
                                      );
                                    }
                                  },
                            child: isLoading
                                ? const SizedBox(
                                    width: 24,
                                    height: 24,
                                    child: CircularProgressIndicator(
                                        color: Colors.white, strokeWidth: 2),
                                  )
                                : const Text('Verify Code',
                                    style: TextStyle(
                                        fontSize: 16,
                                        fontWeight: FontWeight.bold)),
                          ),
                        ),
                        const SizedBox(height: 12),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            TextButton(
                              onPressed: isLoading
                                  ? null
                                  : () {
                                      _otpController.clear();
                                      authNotifier.logout();
                                    },
                              child: const Text('Change Phone'),
                            ),
                            TextButton(
                              onPressed:
                                  (authState.cooldownSeconds > 0 || isLoading)
                                      ? null
                                      : () {
                                          authNotifier.requestOtp(
                                              _phoneController.text.trim());
                                        },
                              child: Text(
                                authState.cooldownSeconds > 0
                                    ? 'Resend in ${authState.cooldownSeconds}s'
                                    : 'Resend Code',
                              ),
                            ),
                          ],
                        ),
                      ],
                    ] else ...[
                      DropdownButtonFormField<String>(
                        value: _selectedRole,
                        decoration: const InputDecoration(
                          labelText: 'Supply-Chain Role',
                          border: OutlineInputBorder(),
                          prefixIcon: Icon(Icons.badge_outlined),
                        ),
                        items: _roles
                            .map((r) => DropdownMenuItem<String>(
                                  value: r['code'],
                                  child: Text(r['label']!),
                                ))
                            .toList(),
                        onChanged: (val) {
                          if (val != null) setState(() => _selectedRole = val);
                        },
                      ),
                      const SizedBox(height: 18),
                      SizedBox(
                        height: 52,
                        child: ElevatedButton.icon(
                          onPressed:
                              isLoading ? null : () => _continueWithGoogle(),
                          icon: const Icon(Icons.account_circle_outlined),
                          label: const Text(
                            'Continue with Google (Gmail)',
                            style: TextStyle(
                                fontSize: 16, fontWeight: FontWeight.bold),
                          ),
                        ),
                      ),
                    ],

                    if (authState.errorMessage != null) ...[
                      const SizedBox(height: 16),
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.red.shade50,
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: Colors.red.shade200),
                        ),
                        child: Text(
                          authState.errorMessage!,
                          style: TextStyle(color: Colors.red.shade800),
                          textAlign: TextAlign.center,
                        ),
                      ),
                    ],

                    const SizedBox(height: 28),
                    const Divider(),
                    const SizedBox(height: 12),
                    const Text(
                      'Protected under DPDP Act 2023 • National Cloud Node',
                      style: TextStyle(fontSize: 11, color: Color(0xFF64748B)),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
