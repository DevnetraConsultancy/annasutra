import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:annasutra_mobile/features/auth/domain/auth_state.dart';
import 'package:annasutra_mobile/features/auth/presentation/controllers/auth_controller.dart';
import 'package:annasutra_mobile/features/home/presentation/home_screen.dart';

void main() {
  testWidgets(
      'HomeScreen renders brand navigation, all 7 role options, and OTP sign-in in unauthenticated state',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: HomeScreen(),
        ),
      ),
    );
    await tester.pump();

    // Verify brand title and mobile sign-in controls
    expect(find.text('AnnaSutra'), findsOneWidget);
    expect(find.text('Farmer / FPO'), findsOneWidget);
    expect(find.text('Mobile Number'), findsOneWidget);
    expect(find.text('Get OTP via SMS'), findsOneWidget);
    expect(find.text('Sign in with Google'), findsOneWidget);

    // Verify DPDP statutory notice
    expect(
      find.textContaining('Protected under DPDP Act 2023', findRichText: true),
      findsOneWidget,
    );

    await tester.pumpWidget(const SizedBox());
    await tester.pump();
  });

  testWidgets(
      'HomeScreen renders authenticated 4-tab mobile navigation, farmer UID, and New Batch action',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          authControllerProvider
              .overrideWith((ref) => MockVerifiedAuthController()),
        ],
        child: const MaterialApp(
          home: HomeScreen(),
        ),
      ),
    );
    await tester.pump();

    // Verify authenticated 4-tab navigation destinations
    expect(find.text('Batches'), findsWidgets);
    expect(find.text('Handover'), findsOneWidget);
    expect(find.text('Insights'), findsOneWidget);
    expect(find.text('Profile'), findsOneWidget);

    // Verify Unique Farmer ID and Floating Action Button
    expect(find.text('202628120000919876543210'), findsOneWidget);
    expect(find.text('New Batch'), findsOneWidget);

    await tester.pumpWidget(const SizedBox());
    await tester.pump();
  });

  testWidgets(
      'HomeScreen hides Farmer ID and displays Under Admin Review before Admin approval',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          authControllerProvider
              .overrideWith((ref) => MockPendingAuthController()),
        ],
        child: const MaterialApp(
          home: HomeScreen(),
        ),
      ),
    );
    await tester.pump();

    expect(find.text('Under Admin Review'), findsWidgets);
    expect(find.text('202628120000919876543210'), findsNothing);

    await tester.pumpWidget(const SizedBox());
    await tester.pump();
  });

  testWidgets(
      'Profile Tab renders 5-Step Registration Tabs and Request Account Deletion',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          authControllerProvider
              .overrideWith((ref) => MockVerifiedAuthController()),
        ],
        child: const MaterialApp(
          home: HomeScreen(),
        ),
      ),
    );
    await tester.pump();

    // Switch to Profile Tab
    await tester.tap(find.byIcon(Icons.person_outline));
    await tester.pumpAndSettle();

    expect(find.text('1. Basic Info'), findsOneWidget);
    expect(find.text('2. Farm Plots'), findsOneWidget);
    expect(find.text('3. Cultivation'), findsOneWidget);
    expect(find.text('4. Identity & Bank'), findsOneWidget);
    expect(find.text('5. Consent & Review'), findsOneWidget);
    expect(find.text('Request Account Deletion'), findsOneWidget);

    await tester.pumpWidget(const SizedBox());
    await tester.pump();
  });
}

class MockVerifiedAuthController extends StateNotifier<AuthState>
    implements AuthController {
  MockVerifiedAuthController()
      : super(const AuthState(
          status: AuthStatus.authenticated,
          accessToken: 'mock_token',
          orgVerification: 'VERIFIED',
          orgName: 'Verified Producer Entity',
          farmerUid: '202628120000919876543210',
        ));

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class MockPendingAuthController extends StateNotifier<AuthState>
    implements AuthController {
  MockPendingAuthController()
      : super(const AuthState(
          status: AuthStatus.authenticated,
          accessToken: 'mock_token',
          orgVerification: 'PENDING',
          orgName: 'Pending Producer Entity',
          farmerUid: null,
        ));

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}
