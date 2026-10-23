import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../features/auth/presentation/login_screen.dart';
import '../features/auth/presentation/org_registration_screen.dart';
import '../features/home/presentation/home_screen.dart';
import '../features/lots/presentation/batch_create_screen.dart';
import '../features/custody/presentation/dispatch_screen.dart';
import '../features/custody/presentation/receive_screen.dart';

import '../features/lots/presentation/split_screen.dart';
import '../features/lots/presentation/waste_screen.dart';
import '../features/lots/presentation/sale_screen.dart';
import '../features/quality/presentation/inspection_screen.dart';

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
          final lotCode = state.uri.queryParameters['code'] ?? '';
          return DispatchScreen(lotCode: lotCode);
        },
      ),
      GoRoute(
        path: '/receive',
        name: 'receive',
        builder: (context, state) {
          final handoverId = state.uri.queryParameters['handover_id'] ?? '';
          final lotCode = state.uri.queryParameters['code'] ?? '';
          final declaredQty = double.tryParse(state.uri.queryParameters['qty'] ?? '0.0') ?? 0.0;
          return ReceiveScreen(handoverId: handoverId, lotCode: lotCode, declaredQtyKg: declaredQty);
        },
      ),
      GoRoute(
        path: '/split',
        name: 'split',
        builder: (context, state) {
          final lotCode = state.uri.queryParameters['code'] ?? '';
          final onHand = double.tryParse(state.uri.queryParameters['qty'] ?? '0.0') ?? 0.0;
          return SplitScreen(lotCode: lotCode, onHandKg: onHand);
        },
      ),
      GoRoute(
        path: '/waste',
        name: 'waste',
        builder: (context, state) {
          final lotCode = state.uri.queryParameters['code'] ?? '';
          final onHand = double.tryParse(state.uri.queryParameters['qty'] ?? '0.0') ?? 0.0;
          return WasteScreen(lotCode: lotCode, onHandKg: onHand);
        },
      ),
      GoRoute(
        path: '/sale',
        name: 'sale',
        builder: (context, state) {
          final lotCode = state.uri.queryParameters['code'] ?? '';
          final onHand = double.tryParse(state.uri.queryParameters['qty'] ?? '0.0') ?? 0.0;
          return SaleScreen(lotCode: lotCode, onHandKg: onHand);
        },
      ),
      GoRoute(
        path: '/inspection',
        name: 'inspection',
        builder: (context, state) {
          final lotCode = state.uri.queryParameters['code'] ?? '';
          return InspectionScreen(lotCode: lotCode);
        },
      ),
    ],
  );
}
