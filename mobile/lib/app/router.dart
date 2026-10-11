import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../features/home/presentation/home_screen.dart';

GoRouter createRouter({void Function(Locale)? onLocaleChanged}) {
  return GoRouter(
    initialLocation: '/',
    routes: [
      GoRoute(
        path: '/',
        name: 'home',
        builder: (context, state) => HomeScreen(onLocaleChanged: onLocaleChanged),
      ),
    ],
  );
}
