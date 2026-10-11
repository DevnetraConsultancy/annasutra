import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:annasutra_mobile/features/auth/presentation/dpdp_consent_dialog.dart';

void main() {
  Widget buildTestableWidget(Widget child, {Locale locale = const Locale('en')}) {
    return MaterialApp(
      locale: locale,
      localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [
        Locale('en'),
        Locale('hi'),
        Locale('bn'),
      ],
      home: Scaffold(body: child),
    );
  }

  group('Phase 4: DPDP Consent & Accessibility Tests', () {
    testWidgets('DpdpConsentDialog displays notice and grievance officer details in English', (tester) async {
      bool accepted = false;

      await tester.pumpWidget(
        buildTestableWidget(
          Builder(
            builder: (ctx) => ElevatedButton(
              onPressed: () => DpdpConsentDialog.show(ctx, onAccepted: () => accepted = true),
              child: const Text('Show Consent'),
            ),
          ),
        ),
      );

      // Open dialog
      await tester.tap(find.text('Show Consent'));
      await tester.pumpAndSettle();

      // Verify DPDP content
      expect(find.text('Data Protection & Privacy Notice'), findsOneWidget);
      expect(find.textContaining('Digital Personal Data Protection Act 2023'), findsOneWidget);
      expect(find.textContaining('Grievance Redressal Officer: grievance@annasutra.in'), findsOneWidget);

      // Verify touch target height >= 48dp
      final buttonFinder = find.widgetWithText(ElevatedButton, 'I Agree & Continue');
      expect(buttonFinder, findsOneWidget);
      final RenderBox renderBox = tester.renderObject(buttonFinder);
      expect(renderBox.size.height, greaterThanOrEqualTo(48.0));

      // Tap accept button
      await tester.tap(buttonFinder);
      await tester.pumpAndSettle();

      expect(accepted, isTrue);
      expect(find.byType(DpdpConsentDialog), findsNothing);
    });

    testWidgets('DpdpConsentDialog displays notice in Bengali (bn)', (tester) async {
      await tester.pumpWidget(
        buildTestableWidget(
          Builder(
            builder: (ctx) => ElevatedButton(
              onPressed: () => DpdpConsentDialog.show(ctx),
              child: const Text('Show Bengali Consent'),
            ),
          ),
          locale: const Locale('bn'),
        ),
      );

      await tester.tap(find.text('Show Bengali Consent'));
      await tester.pumpAndSettle();

      expect(find.text('তথ্য সুরক্ষা ও গোপনীয়তা বিজ্ঞপ্তি'), findsOneWidget);
      expect(find.textContaining('ডিজিটাল পার্সোনাল ডেটা প্রোটেকশন অ্যাক্ট ২০২৩'), findsOneWidget);
      expect(find.textContaining('অভিযোগ নিষ্পত্তি কর্মকর্তা: grievance@annasutra.in'), findsOneWidget);
      expect(find.text('আমি সম্মত ও এগিয়ে যান'), findsOneWidget);
    });

    testWidgets('DpdpConsentDialog displays notice in Hindi (hi)', (tester) async {
      await tester.pumpWidget(
        buildTestableWidget(
          Builder(
            builder: (ctx) => ElevatedButton(
              onPressed: () => DpdpConsentDialog.show(ctx),
              child: const Text('Show Hindi Consent'),
            ),
          ),
          locale: const Locale('hi'),
        ),
      );

      await tester.tap(find.text('Show Hindi Consent'));
      await tester.pumpAndSettle();

      expect(find.text('डेटा सुरक्षा एवं गोपनीयता सूचना'), findsOneWidget);
      expect(find.textContaining('डिजिटल पर्सनल डेटा प्रोटेक्शन एक्ट 2023'), findsOneWidget);
      expect(find.textContaining('शिकायत निवारण अधिकारी: grievance@annasutra.in'), findsOneWidget);
      expect(find.text('मैं सहमत हूँ एवं आगे बढ़ें'), findsOneWidget);
    });
  });
}
