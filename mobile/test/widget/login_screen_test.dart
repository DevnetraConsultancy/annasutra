import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:annasutra_mobile/features/auth/presentation/login_screen.dart';

void main() {
  testWidgets('LoginScreen renders phone field and Send OTP button', (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: LoginScreen(),
        ),
      ),
    );

    // Verify header and fields
    expect(find.text('Agri-Traceability Secure Access'), findsOneWidget);
    expect(find.byType(TextFormField), findsOneWidget);
    expect(find.text('Send OTP'), findsOneWidget);
  });

  testWidgets('Tapping Send OTP with phone transitions to OTP input', (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: LoginScreen(),
        ),
      ),
    );

    // Fill phone number
    final phoneFinder = find.byType(TextFormField);
    await tester.enterText(phoneFinder, '+919876543210');
    await tester.tap(find.text('Send OTP'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 500));

    // Verify OTP field and Verify Code button appear
    expect(find.text('Verify Code'), findsOneWidget);
  });
}
