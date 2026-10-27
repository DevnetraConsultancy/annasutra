import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:annasutra_mobile/features/custody/presentation/dispatch_screen.dart';

void main() {
  testWidgets('DispatchScreen renders form fields and submit button',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: DispatchScreen(lotCode: '7K3Q9XMD4T2B'),
        ),
      ),
    );

    expect(find.textContaining('7K3Q9XMD4T2B'), findsOneWidget);
    expect(find.textContaining('Receiver Organisation ID'), findsOneWidget);
    expect(find.textContaining('Quantity to Dispatch'), findsOneWidget);
    expect(find.textContaining('Sign & Dispatch', skipOffstage: false),
        findsOneWidget);
    expect(find.byIcon(Icons.send, skipOffstage: false), findsOneWidget);
  });
}
