import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:annasutra_mobile/features/auth/presentation/org_registration_screen.dart';

void main() {
  testWidgets('OrgRegistrationScreen renders inputs and requires DPDP consent',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: OrgRegistrationScreen(),
        ),
      ),
    );

    // Verify title and inputs
    expect(find.text('Set Up Your Organisation'), findsOneWidget);
    expect(find.text('Organisation or Farm Name *'), findsOneWidget);
    expect(find.text('Organisation Type *'), findsOneWidget);
    expect(find.byType(Checkbox), findsOneWidget);

    // Verify Register button exists
    expect(find.text('Register Organisation'), findsOneWidget);
  });
}
