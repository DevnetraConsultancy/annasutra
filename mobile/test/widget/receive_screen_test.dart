import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:annasutra_mobile/features/custody/presentation/receive_screen.dart';

void main() {
  testWidgets('ReceiveScreen renders Matches button and toggles scale form', (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: ReceiveScreen(
            handoverId: '00000000-0000-0000-0000-000000000001',
            lotCode: '7K3Q9XMD4T2B',
            declaredQtyKg: 500.0,
          ),
        ),
      ),
    );

    // Matches 1-tap button is prominent
    expect(find.textContaining('Matches Declared Weight'), findsOneWidget);
    expect(find.textContaining('500.0 kg'), findsOneWidget);

    // Toggle scale form
    final scaleToggle = find.textContaining('Weigh on Scale');
    expect(scaleToggle, findsOneWidget);
    await tester.tap(scaleToggle);
    await tester.pumpAndSettle();

    // Scale entry fields should now be visible
    expect(find.textContaining('Received Net Weight'), findsOneWidget);
    expect(find.textContaining('Rejected Weight'), findsOneWidget);
  });
}
