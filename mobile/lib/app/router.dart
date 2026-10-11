import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../features/auth/presentation/login_screen.dart';
import '../features/auth/presentation/org_registration_screen.dart';
import '../features/home/presentation/home_screen.dart';
import '../features/lots/presentation/batch_create_screen.dart';
import '../features/custody/presentation/dispatch_screen.dart';
import '../features/custody/presentation/receive_screen.dart';

GoRouter createRouter({void Function(Locale)? onLocaleChanged}) {
  return GoRouter(
    initialLocation: '/',
    routes: [
      GoRoute(
        path: '/',
        name: 'home',
        builder: (context, state) => HomeScreen(onLocaleChanged: onLocaleChanged),
      ),
      GoRoute(
        path: '/login',
        name: 'login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/register-org',
        name: 'register-org',
        builder: (context, state) => const OrgRegistrationScreen(),
      ),
      GoRoute(
        path: '/create-batch',
        name: 'create-batch',
        builder: (context, state) => const BatchCreateScreen(),
      ),
      GoRoute(
        path: '/dispatch',
        name: 'dispatch',
        builder: (context, state) {
          final lotCode = state.uri.queryParameters['code'] ?? '7K3Q9XMD4T2B';
          return DispatchScreen(lotCode: lotCode);
        },
      ),
      GoRoute(
        path: '/receive',
        name: 'receive',
        builder: (context, state) {
          final handoverId = state.uri.queryParameters['handover_id'] ?? '00000000-0000-0000-0000-000000000001';
          final lotCode = state.uri.queryParameters['code'] ?? '7K3Q9XMD4T2B';
          final declaredQty = double.tryParse(state.uri.queryParameters['qty'] ?? '500.0') ?? 500.0;
          return ReceiveScreen(handoverId: handoverId, lotCode: lotCode, declaredQtyKg: declaredQty);
        },
      ),
    ],
  );
}
