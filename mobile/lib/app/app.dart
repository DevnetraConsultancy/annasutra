import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'router.dart';
import 'theme.dart';

class AnnaSutraApp extends StatefulWidget {
  const AnnaSutraApp({super.key});

  @override
  State<AnnaSutraApp> createState() => _AnnaSutraAppState();
}

class _AnnaSutraAppState extends State<AnnaSutraApp> {
  Locale _locale = const Locale('en');

  void _changeLocale(Locale newLocale) {
    setState(() {
      _locale = newLocale;
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'AnnaSutra',
      theme: AnnaSutraTheme.lightTheme,
      locale: _locale,
      supportedLocales: const [
        Locale('en'),
        Locale('hi'),
        Locale('bn'),
      ],
      localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      routerConfig: createRouter(onLocaleChanged: _changeLocale),
    );
  }
}
