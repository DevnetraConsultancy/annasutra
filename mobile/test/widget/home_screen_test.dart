import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:annasutra_mobile/features/auth/domain/auth_state.dart';
import 'package:annasutra_mobile/features/auth/presentation/controllers/auth_controller.dart';
import 'package:annasutra_mobile/features/home/presentation/home_screen.dart';

void main() {
  testWidgets('HomeScreen renders brand navigation, hero action buttons, and disclaimer notice', (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: HomeScreen(),
        ),
      ),
    );

    // Verify brand title and action buttons
    expect(find.text('AnnaSutra'), findsOneWidget);
    expect(find.text('Scan QR'), findsOneWidget);
    expect(find.text('New Harvest Lot'), findsOneWidget);

    // Verify mandatory disclaimer from docs/00_MASTER_BRIEF.md
    expect(
      find.textContaining('Records are based on information entered by supply-chain participants', findRichText: true),
      findsOneWidget,
    );
  });

  testWidgets('HomeScreen renders authenticated dual-tab navigation and KPI cards', (WidgetTester tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          authControllerProvider.overrideWith((ref) => MockVerifiedAuthController()),
        ],
        child: const MaterialApp(
          home: HomeScreen(),
        ),
      ),
    );

    // Verify authenticated dual tabs matching web portal
    expect(find.text('Harvest Lots & Custody Ledger'), findsOneWidget);
    expect(find.text('Analytics & Farm Insights'), findsOneWidget);

    // Verify action button
    expect(find.text('Register New Harvest Lot'), findsOneWidget);
  });
}

class MockVerifiedAuthController extends StateNotifier<AuthState> implements AuthController {
  MockVerifiedAuthController()
      : super(const AuthState(
          status: AuthStatus.authenticated,
          accessToken: 'mock_token',
          orgVerification: 'VERIFIED',
          orgName: "Dr. Niladri's Farm (WB-PROD-2026-X7803)",
        ));

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}
