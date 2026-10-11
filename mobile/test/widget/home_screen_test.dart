import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:annasutra_mobile/features/home/presentation/home_screen.dart';

void main() {
  testWidgets('HomeScreen renders tabs, action buttons, and disclaimer notice', (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: HomeScreen(),
        ),
      ),
    );

    // Verify tabs
    expect(find.text('Incoming'), findsOneWidget);
    expect(find.text('My Stock'), findsOneWidget);
    expect(find.text('Waiting'), findsOneWidget);

    // Verify action buttons
    expect(find.text('Scan QR'), findsOneWidget);
    expect(find.text('Create Batch'), findsOneWidget);

    // Verify mandatory disclaimer from docs/00_MASTER_BRIEF.md
    expect(
      find.textContaining('Records are based on information entered by supply-chain participants', findRichText: true),
      findsOneWidget,
    );
  });
}
