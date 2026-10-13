import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../domain/auth_state.dart';
import 'controllers/auth_controller.dart';
import 'dpdp_consent_dialog.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final TextEditingController _phoneController = TextEditingController(text: '+919876543210');
  final TextEditingController _otpController = TextEditingController();
  final _formKey = GlobalKey<FormState>();

  @override
  void dispose() {
    _phoneController.dispose();
    _otpController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authControllerProvider);
    final authNotifier = ref.read(authControllerProvider.notifier);

    // Listen to authentication state changes to navigate
    ref.listen<AuthState>(authControllerProvider, (previous, next) {
      if (next.status == AuthStatus.authenticated) {
        if (next.orgVerification == 'PENDING') {
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
        title: const Text('AnnaSutra / অন্নসূত্র / अन्नसूत्र'),
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
                              border: Border.all(color: const Color(0xFFE67E22), width: 2),
                              boxShadow: const [
                                BoxShadow(color: Colors.black12, blurRadius: 8, offset: Offset(0, 3)),
                              ],
                            ),
                            child: ClipOval(
                              child: Image.asset(
                                'assets/images/annasutra_emblem.jpg',
                                fit: BoxFit.cover,
                                errorBuilder: (_, __, ___) => const CircleAvatar(
                                  backgroundColor: Color(0xFF0B3D2E),
                                  child: Icon(Icons.eco, color: Colors.amber, size: 36),
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
                                errorBuilder: (_, __, ___) => const Icon(Icons.memory, size: 14),
                              ),
                              const SizedBox(width: 6),
                              const Text(
                                'Technology Partner: C-DAC | MeitY',
                                style: TextStyle(fontSize: 11, color: Color(0xFF475569), fontWeight: FontWeight.w600),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 28),

                    // Quick Role Demo Shortcuts
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: const Color(0xFFF0FDF4),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: const Color(0xFF86EFAC)),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Row(
                            children: [
                              Icon(Icons.bolt, color: Color(0xFF15803D), size: 18),
                              SizedBox(width: 6),
                              Text(
                                '1-Tap Rapid Access for Field Entities:',
                                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: Color(0xFF14532D)),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Wrap(
                            spacing: 8,
                            runSpacing: 8,
                            children: [
                              ActionChip(
                                label: const Text('🌾 Farmer / FPO', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600)),
                                onPressed: () {
                                  authNotifier.quickLoginAsEntity(
                                    entityRole: 'FARMER',
                                    orgName: 'Bardhaman Farmer Coop (FPO-WB-0492)',
                                    phone: '+919876543210',
                                  );
                                },
                              ),
                              ActionChip(
                                label: const Text('🏢 Mandi APMC', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600)),
                                onPressed: () {
                                  authNotifier.quickLoginAsEntity(
                                    entityRole: 'MANDI',
                                    orgName: 'Kolkata Central APMC Traders Ltd',
                                    phone: '+919876543211',
                                  );
                                },
                              ),
                              ActionChip(
                                label: const Text('❄️ Cold Storage', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600)),
                                onPressed: () {
                                  authNotifier.quickLoginAsEntity(
                                    entityRole: 'COLD_STORAGE',
                                    orgName: 'Hooghly Cold Chain Logistics Ltd',
                                    phone: '+919876543212',
                                  );
                                },
                              ),
                              ActionChip(
                                label: const Text('🛒 Retailer', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600)),
                                onPressed: () {
                                  authNotifier.quickLoginAsEntity(
                                    entityRole: 'RETAILER',
                                    orgName: 'Maa Durga Retail Fresh Mart',
                                    phone: '+919876543213',
                                  );
                                },
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 20),

                    // Phone Input Field
                    TextFormField(
                      controller: _phoneController,
                      keyboardType: TextInputType.phone,
                      enabled: !isOtpSent && !isLoading,
                      decoration: const InputDecoration(
                        labelText: 'Registered Mobile Number (+91)',
                        hintText: '+919876543210',
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

                    // Request OTP button (visible before OTP is sent)
                    if (!isOtpSent) ...[
                      SizedBox(
                        height: 52,
                        child: ElevatedButton(
                          onPressed: isLoading
                              ? null
                              : () {
                                  if (_formKey.currentState?.validate() ?? false) {
                                    authNotifier.requestOtp(_phoneController.text.trim());
                                  }
                                },
                          child: isLoading
                              ? const SizedBox(width: 24, height: 24, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                              : const Text('Send OTP', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                        ),
                      ),
                    ],

                    // OTP Code input and verification (visible when OTP is sent)
                    if (isOtpSent) ...[
                      TextFormField(
                        controller: _otpController,
                        keyboardType: TextInputType.number,
                        maxLength: 6,
                        enabled: !isLoading,
                        decoration: const InputDecoration(
                          labelText: '6-Digit Verification Code',
                          hintText: '123456',
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
                                  if (_otpController.text.trim().length == 6) {
                                    authNotifier.verifyOtp(
                                      _phoneController.text.trim(),
                                      _otpController.text.trim(),
                                    );
                                  }
                                },
                          child: isLoading
                              ? const SizedBox(width: 24, height: 24, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                              : const Text('Verify Code', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
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
                            onPressed: (authState.cooldownSeconds > 0 || isLoading)
                                ? null
                                : () {
                                    authNotifier.requestOtp(_phoneController.text.trim());
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
                          style: TextStyle(color: Colors.red.shade900),
                          textAlign: TextAlign.center,
                        ),
                      ),
                    ],

                    const SizedBox(height: 36),
                    // Security & Privacy notice
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.grey.shade100,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.grey.shade300),
                      ),
                      child: const Column(
                        children: [
                          Text(
                            'AnnaSutra records are cryptographically signed on your device.',
                            style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.black87),
                            textAlign: TextAlign.center,
                          ),
                          SizedBox(height: 4),
                          Text(
                            'Personal details are masked and processed strictly under the Digital Personal Data Protection Act 2023.',
                            style: TextStyle(fontSize: 11, color: Colors.black54),
                            textAlign: TextAlign.center,
                          ),
                        ],
                      ),
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
