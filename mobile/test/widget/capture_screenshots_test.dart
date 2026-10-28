import 'dart:io';
import 'dart:ui' as ui;
import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:annasutra_mobile/app/theme.dart';
import 'package:annasutra_mobile/features/auth/domain/auth_state.dart';
import 'package:annasutra_mobile/features/auth/presentation/controllers/auth_controller.dart';
import 'package:annasutra_mobile/features/home/presentation/home_screen.dart';
import 'package:annasutra_mobile/features/lots/domain/harvest_lot.dart';
import 'package:annasutra_mobile/features/lots/presentation/controllers/lots_controller.dart';

class MockLotsController extends StateNotifier<LotsState>
    implements LotsController {
  MockLotsController(super.state);

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class MockUnauthenticatedAuthController extends StateNotifier<AuthState>
    implements AuthController {
  MockUnauthenticatedAuthController()
      : super(const AuthState(
          status: AuthStatus.unauthenticated,
        ));

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class MockVerifiedAuthController extends StateNotifier<AuthState>
    implements AuthController {
  MockVerifiedAuthController()
      : super(const AuthState(
          status: AuthStatus.authenticated,
          accessToken: 'mock_token',
          orgVerification: 'VERIFIED',
          orgName: 'Maa Annapurna Organic FPO',
          farmerUid: '202628120000919876543210',
        ));

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

void main() {
  const targetDir =
      r'C:\Users\Dr_Nee\.gemini\antigravity\brain\88621903-92e6-491a-8803-57d56c55f134';

  final testLots = [
    const HarvestLot(
      publicCode: 'LOT-2026-WB-0042',
      crop: 'Basmati Paddy',
      variety: 'Pusa 1121',
      netQtyKg: 1450.0,
      harvestDate: '2026-10-25',
      createdAt: '2026-10-25T08:30:00Z',
      state: 'IN_CUSTODY',
      originPlotName: 'Plot 4A - North Sunderbans',
      packagesCount: 48,
      packageType: 'Jute Bags',
      qualityGrade: 'Grade A (Super)',
      basePricePerUnit: 34.50,
      estimatedValue: 50025.0,
    ),
    const HarvestLot(
      publicCode: 'LOT-2026-WB-0039',
      crop: 'Organic Mustard',
      variety: 'Pusa Bold',
      netQtyKg: 820.0,
      harvestDate: '2026-10-21',
      createdAt: '2026-10-21T09:15:00Z',
      state: 'IN_TRANSIT',
      originPlotName: 'Plot 2B - Kalyani Green',
      packagesCount: 25,
      packageType: 'Crates',
      qualityGrade: 'Standard',
      basePricePerUnit: 52.00,
      estimatedValue: 42640.0,
    ),
  ];

  testWidgets('Capture 1: Unauthenticated Login Screen',
      (WidgetTester tester) async {
    const size = Size(412, 892);
    await tester.binding.setSurfaceSize(size);

    final loginKey = GlobalKey();
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          authControllerProvider
              .overrideWith((ref) => MockUnauthenticatedAuthController()),
        ],
        child: MaterialApp(
          theme: AnnaSutraTheme.lightTheme,
          debugShowCheckedModeBanner: false,
          home: RepaintBoundary(
            key: loginKey,
            child: const Scaffold(
              body: HomeScreen(),
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    await tester.runAsync(() async {
      final boundary =
          loginKey.currentContext!.findRenderObject() as RenderRepaintBoundary;
      final image = await boundary.toImage(pixelRatio: 2.0);
      final byteData = await image.toByteData(format: ui.ImageByteFormat.png);
      final file = File('$targetDir\\screenshot_android_login.png');
      file.writeAsBytesSync(byteData!.buffer.asUint8List());
    });
  });

  testWidgets('Capture 2: Authenticated Screen - Batches Tab',
      (WidgetTester tester) async {
    const size = Size(412, 892);
    await tester.binding.setSurfaceSize(size);

    final batchesKey = GlobalKey();
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          authControllerProvider
              .overrideWith((ref) => MockVerifiedAuthController()),
          lotsControllerProvider.overrideWith((ref) => MockLotsController(
                LotsState(lots: testLots),
              )),
        ],
        child: MaterialApp(
          theme: AnnaSutraTheme.lightTheme,
          debugShowCheckedModeBanner: false,
          home: RepaintBoundary(
            key: batchesKey,
            child: const Scaffold(
              body: HomeScreen(),
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    await tester.runAsync(() async {
      final boundary = batchesKey.currentContext!.findRenderObject()
          as RenderRepaintBoundary;
      final image = await boundary.toImage(pixelRatio: 2.0);
      final byteData = await image.toByteData(format: ui.ImageByteFormat.png);
      final file = File('$targetDir\\screenshot_android_batches.png');
      file.writeAsBytesSync(byteData!.buffer.asUint8List());
    });
  });

  testWidgets('Capture 3: Authenticated Screen - Handover Tab',
      (WidgetTester tester) async {
    const size = Size(412, 892);
    await tester.binding.setSurfaceSize(size);

    final handoverKey = GlobalKey();
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          authControllerProvider
              .overrideWith((ref) => MockVerifiedAuthController()),
          lotsControllerProvider.overrideWith((ref) => MockLotsController(
                LotsState(lots: testLots),
              )),
        ],
        child: MaterialApp(
          theme: AnnaSutraTheme.lightTheme,
          debugShowCheckedModeBanner: false,
          home: RepaintBoundary(
            key: handoverKey,
            child: const Scaffold(
              body: HomeScreen(),
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    // Tap Handover navigation destination
    await tester.tap(find.byIcon(Icons.swap_horiz_outlined));
    await tester.pumpAndSettle();

    await tester.runAsync(() async {
      final boundary = handoverKey.currentContext!.findRenderObject()
          as RenderRepaintBoundary;
      final image = await boundary.toImage(pixelRatio: 2.0);
      final byteData = await image.toByteData(format: ui.ImageByteFormat.png);
      final file = File('$targetDir\\screenshot_android_handover.png');
      file.writeAsBytesSync(byteData!.buffer.asUint8List());
    });
  });

  testWidgets('Capture 4: Authenticated Screen - Insights Tab',
      (WidgetTester tester) async {
    const size = Size(412, 892);
    await tester.binding.setSurfaceSize(size);

    final insightsKey = GlobalKey();
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          authControllerProvider
              .overrideWith((ref) => MockVerifiedAuthController()),
          lotsControllerProvider.overrideWith((ref) => MockLotsController(
                LotsState(lots: testLots),
              )),
        ],
        child: MaterialApp(
          theme: AnnaSutraTheme.lightTheme,
          debugShowCheckedModeBanner: false,
          home: RepaintBoundary(
            key: insightsKey,
            child: const Scaffold(
              body: HomeScreen(),
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    // Tap Insights navigation destination
    await tester.tap(find.byIcon(Icons.insights_outlined));
    await tester.pumpAndSettle();

    await tester.runAsync(() async {
      final boundary = insightsKey.currentContext!.findRenderObject()
          as RenderRepaintBoundary;
      final image = await boundary.toImage(pixelRatio: 2.0);
      final byteData = await image.toByteData(format: ui.ImageByteFormat.png);
      final file = File('$targetDir\\screenshot_android_insights.png');
      file.writeAsBytesSync(byteData!.buffer.asUint8List());
    });
  });

  testWidgets('Capture 5: Authenticated Screen - Profile Tab',
      (WidgetTester tester) async {
    const size = Size(412, 892);
    await tester.binding.setSurfaceSize(size);

    final profileKey = GlobalKey();
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          authControllerProvider
              .overrideWith((ref) => MockVerifiedAuthController()),
          lotsControllerProvider.overrideWith((ref) => MockLotsController(
                LotsState(lots: testLots),
              )),
        ],
        child: MaterialApp(
          theme: AnnaSutraTheme.lightTheme,
          debugShowCheckedModeBanner: false,
          home: RepaintBoundary(
            key: profileKey,
            child: const Scaffold(
              body: HomeScreen(),
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    // Tap Profile navigation destination
    await tester.tap(find.byIcon(Icons.person_outline));
    await tester.pumpAndSettle();

    await tester.runAsync(() async {
      final boundary = profileKey.currentContext!.findRenderObject()
          as RenderRepaintBoundary;
      final image = await boundary.toImage(pixelRatio: 2.0);
      final byteData = await image.toByteData(format: ui.ImageByteFormat.png);
      final file = File('$targetDir\\screenshot_android_profile.png');
      file.writeAsBytesSync(byteData!.buffer.asUint8List());
    });
  });
}
