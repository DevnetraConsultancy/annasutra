import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:annasutra_mobile/features/auth/presentation/login_screen.dart';

void main() {
  testWidgets('LoginScreen renders Mobile OTP and Google Sign-In tabs',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: LoginScreen(),
        ),
      ),
    );

    // Verify header and dual auth tabs
    expect(find.text('Agri-Traceability Secure Access'), findsOneWidget);
    expect(find.text('Mobile OTP'), findsOneWidget);
    expect(find.text('Google Sign-In'), findsOneWidget);
    expect(find.text('Send OTP'), findsOneWidget);
  });

  testWidgets('Tapping Send OTP with phone transitions to OTP input',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: LoginScreen(),
        ),
      ),
    );

    // Fill phone number into the first TextFormField
    final phoneFinder = find.byType(TextFormField).first;
    await tester.enterText(phoneFinder, '+919876543210');
    await tester.tap(find.text('Send OTP'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 500));

    // Verify OTP field and Verify Code button appear
    expect(find.text('Verify Code'), findsOneWidget);
  });
}
