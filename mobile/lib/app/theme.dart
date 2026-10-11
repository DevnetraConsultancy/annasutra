import 'package:flutter/material.dart';

/// Design system tokens adhering to WCAG 2.1 AA accessibility standards:
/// - Minimum 48x48dp touch targets
/// - High contrast color palette
/// - Clear typography without visual clutter
class AnnaSutraTheme {
  static const Color primaryGreen = Color(0xFF1B5E20); // Dark forest green
  static const Color secondaryGreen = Color(0xFF2E7D32);
  static const Color accentOrange = Color(0xFFE65100);
  static const Color surfaceColor = Color(0xFFF9FBF7);
  static const Color textHighContrast = Color(0xFF1A1C19);

  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: primaryGreen,
        primary: primaryGreen,
        secondary: secondaryGreen,
        tertiary: accentOrange,
        surface: surfaceColor,
      ),
      scaffoldBackgroundColor: surfaceColor,
      appBarTheme: const AppBarTheme(
        backgroundColor: primaryGreen,
        foregroundColor: Colors.white,
        elevation: 2,
        centerTitle: false,
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          minimumSize: const Size(120, 52), // Meets ≥48x48dp accessible target
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(10),
          ),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          minimumSize: const Size(120, 52),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(10),
          ),
        ),
      ),
      textTheme: const TextTheme(
        headlineMedium: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: textHighContrast),
        titleLarge: TextStyle(fontSize: 20, fontWeight: FontWeight.w600, color: textHighContrast),
        bodyLarge: TextStyle(fontSize: 16, color: textHighContrast),
        bodyMedium: TextStyle(fontSize: 14, color: textHighContrast),
      ),
    );
  }
}
