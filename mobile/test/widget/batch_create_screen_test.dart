import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:annasutra_mobile/features/auth/domain/auth_state.dart';
import 'package:annasutra_mobile/features/auth/presentation/controllers/auth_controller.dart';
import 'package:annasutra_mobile/features/lots/presentation/batch_create_screen.dart';

void main() {
  testWidgets('BatchCreateScreen renders form fields and sign button when verified', (WidgetTester tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          authControllerProvider.overrideWith((ref) => MockVerifiedAuthController()),
        ],
        child: const MaterialApp(
          home: BatchCreateScreen(),
        ),
      ),
    );

    // Verify fields
    expect(find.text('Create Harvest Batch'), findsOneWidget);
    expect(find.text('QR Label Serial *'), findsOneWidget);
    expect(find.text('Produce Name *'), findsOneWidget);
    expect(find.text('Variety *'), findsOneWidget);
    expect(find.text('Net Quantity (kg) *'), findsOneWidget);
    expect(find.text('Sign & Create Batch'), findsOneWidget);
  });
}

class MockVerifiedAuthController extends StateNotifier<AuthState> implements AuthController {
  MockVerifiedAuthController()
      : super(const AuthState(
          status: AuthStatus.authenticated,
          accessToken: 'mock_token',
          orgVerification: 'VERIFIED',
        ));

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}
