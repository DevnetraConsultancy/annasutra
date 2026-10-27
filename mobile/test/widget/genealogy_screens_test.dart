import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:annasutra_mobile/features/lots/presentation/split_screen.dart';
import 'package:annasutra_mobile/features/lots/presentation/waste_screen.dart';
import 'package:annasutra_mobile/features/lots/presentation/sale_screen.dart';
import 'package:annasutra_mobile/features/quality/presentation/inspection_screen.dart';

void main() {
  testWidgets('SplitScreen renders form fields and child inputs',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: SplitScreen(lotCode: '7K3Q9XMD4T2B', onHandKg: 500.0),
        ),
      ),
    );

    expect(find.textContaining('7K3Q9XMD4T2B'), findsOneWidget);
    expect(find.textContaining('Child Lot #1'), findsOneWidget);
    expect(find.byType(TextFormField), findsNWidgets(2));
    expect(find.textContaining('Split Lot', skipOffstage: false), findsWidgets);
  });

  testWidgets('WasteScreen renders quantity and reason fields',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: WasteScreen(lotCode: '7K3Q9XMD4T2B', onHandKg: 500.0),
        ),
      ),
    );

    expect(find.textContaining('7K3Q9XMD4T2B'), findsOneWidget);
    expect(find.textContaining('TRANSIT_SPOILAGE'), findsOneWidget);
    expect(
        find.textContaining('Record Waste', skipOffstage: false), findsWidgets);
  });

  testWidgets('SaleScreen renders quantity field and privacy notice',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: SaleScreen(lotCode: '7K3Q9XMD4T2B', onHandKg: 500.0),
        ),
      ),
    );

    expect(find.textContaining('7K3Q9XMD4T2B'), findsOneWidget);
    expect(find.textContaining('No customer personal details are collected'),
        findsOneWidget);
    expect(find.textContaining('Record Retail Sale', skipOffstage: false),
        findsWidgets);
  });

  testWidgets('InspectionScreen renders grade and defect slider',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: InspectionScreen(lotCode: '7K3Q9XMD4T2B'),
        ),
      ),
    );

    expect(find.textContaining('7K3Q9XMD4T2B'), findsOneWidget);
    expect(find.textContaining('Grade A'), findsOneWidget);
    expect(find.byType(Slider), findsOneWidget);
    expect(find.textContaining('Inspect Quality', skipOffstage: false),
        findsWidgets);
  });
}
