import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:annasutra_mobile/features/auth/domain/auth_state.dart';
import 'package:annasutra_mobile/features/auth/presentation/controllers/auth_controller.dart';
import 'package:annasutra_mobile/features/lots/presentation/batch_create_screen.dart';

void main() {
  testWidgets(
      'BatchCreateScreen renders form fields, category codes, trajectory map and sign button when verified',
      (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          authControllerProvider
              .overrideWith((ref) => MockVerifiedAuthController()),
        ],
        child: const MaterialApp(
          home: BatchCreateScreen(),
        ),
      ),
    );
    await tester.pump();

    // Verify fields and sections
    expect(find.text('Create Harvest Batch'), findsOneWidget);
    expect(
      find.text('1. Batch Identification & Product Category'),
      findsOneWidget,
    );
    expect(
      find.text('Product Category *'),
      findsOneWidget,
    );
    expect(find.text('QR Label Serial *'), findsOneWidget);
    expect(find.text('Produce Name *'), findsOneWidget);
    expect(find.text('Variety *'), findsOneWidget);
    expect(find.text('Net Quantity (kg) *'), findsOneWidget);
    expect(find.text('Sign & Create Batch'), findsOneWidget);
    expect(
      find.text('Live Lot Movement Trajectory (Next-Party Scan Updates)'),
      findsOneWidget,
    );
  });
}

class MockVerifiedAuthController extends StateNotifier<AuthState>
    implements AuthController {
  MockVerifiedAuthController()
      : super(const AuthState(
          status: AuthStatus.authenticated,
          accessToken: 'mock_token',
          orgVerification: 'VERIFIED',
          farmerUid: '202628120000919876543210',
        ));

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}
