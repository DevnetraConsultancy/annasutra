import 'package:flutter/material.dart';

/// Gold-Standard Design System Tokens for AnnaSutra Native Android:
/// - Bharat Deep Emerald (#0B3D2E) & Harvest Saffron (#E67E22) brand identity
/// - Native mobile ergonomics with proportional touch targets (42-48dp)
/// - Modern Material 3 surfaces, subtle borders, and crisp card definition
/// - High-contrast typography optimized for outdoor sunlight visibility
class AnnaSutraTheme {
  // Brand Color Tokens
  static const Color primaryGreen = Color(0xFF0B3D2E); // Deep Bharat Emerald
  static const Color vibrantGreen = Color(0xFF059669); // Vibrant Harvest Green
  static const Color lightGreenSurface =
      Color(0xFFECFDF5); // Soft Emerald Surface
  static const Color brandSaffron = Color(0xFFE67E22); // Warm Saffron
  static const Color accentGold = Color(0xFFD97706); // Golden Grain
  static const Color slateDark = Color(0xFF0F172A); // Ultra-deep Slate Navy
  static const Color surfaceColor =
      Color(0xFFF8FAFC); // Clean Modern Slate Surface
  static const Color surfaceCard = Color(0xFFFFFFFF); // Pure White Cards
  static const Color textHighContrast = Color(0xFF0F172A); // High Contrast Text
  static const Color textMuted = Color(0xFF64748B); // Slate Muted Text
  static const Color borderLight = Color(0xFFE2E8F0); // Subtle Border
  static const Color borderSubtle = Color(0xFFCBD5E1); // Defined Border
  static const Color alertRed = Color(0xFFDC2626); // Statutory Alert / Recall
  static const Color verifiedTeal =
      Color(0xFF0D9488); // Cryptographic Seal Teal

  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: primaryGreen,
        primary: primaryGreen,
        secondary: vibrantGreen,
        tertiary: brandSaffron,
        surface: surfaceColor,
        onSurface: textHighContrast,
      ),
      scaffoldBackgroundColor: surfaceColor,
      appBarTheme: const AppBarTheme(
        backgroundColor: primaryGreen,
        foregroundColor: Colors.white,
        elevation: 0,
        centerTitle: false,
        iconTheme: IconThemeData(color: Colors.white),
      ),
      cardTheme: CardTheme(
        color: surfaceCard,
        elevation: 0,
        margin: EdgeInsets.zero,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: borderLight, width: 1.2),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          minimumSize: const Size(64, 44),
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 11),
          backgroundColor: primaryGreen,
          foregroundColor: Colors.white,
          elevation: 0,
          textStyle: const TextStyle(
            fontSize: 14.5,
            fontWeight: FontWeight.w700,
            letterSpacing: 0.1,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          minimumSize: const Size(64, 44),
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 11),
          foregroundColor: primaryGreen,
          side: const BorderSide(color: borderSubtle, width: 1.2),
          textStyle: const TextStyle(
            fontSize: 14.5,
            fontWeight: FontWeight.w700,
            letterSpacing: 0.1,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.white,
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 16, vertical: 13),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: borderLight, width: 1.2),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: borderLight, width: 1.2),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: primaryGreen, width: 1.8),
        ),
        hintStyle: const TextStyle(fontSize: 14, color: textMuted),
        labelStyle: const TextStyle(fontSize: 14, color: textMuted),
      ),
      textTheme: const TextTheme(
        headlineLarge: TextStyle(
            fontSize: 26,
            fontWeight: FontWeight.w800,
            color: textHighContrast,
            letterSpacing: -0.4),
        headlineMedium: TextStyle(
            fontSize: 20, fontWeight: FontWeight.w700, color: textHighContrast),
        titleLarge: TextStyle(
            fontSize: 17, fontWeight: FontWeight.w700, color: textHighContrast),
        titleMedium: TextStyle(
            fontSize: 15, fontWeight: FontWeight.w600, color: textHighContrast),
        bodyLarge: TextStyle(
            fontSize: 14.5,
            fontWeight: FontWeight.w400,
            color: textHighContrast),
        bodyMedium: TextStyle(
            fontSize: 13.5, fontWeight: FontWeight.w400, color: textMuted),
        labelLarge: TextStyle(
            fontSize: 13.5, fontWeight: FontWeight.w600, letterSpacing: 0.2),
      ),
    );
  }
}
