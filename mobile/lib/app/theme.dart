import 'package:flutter/material.dart';

/// Design system tokens adhering to WCAG 2.1 AA accessibility standards &
/// inspired by NPCI / Govt. of India top-tier fintech portal aesthetics:
/// - Deep Forest Green (#0B3D2E) & Vibrant Saffron (#E67E22) brand harmony
/// - Accessible touch targets (min 52dp height)
/// - High contrast typography & tactile surfaces
/// - Adaptive card elevations with crisp border definition
class AnnaSutraTheme {
  // Brand Color Tokens
  static const Color primaryGreen =
      Color(0xFF0B3D2E); // Deep National Forest Green
  static const Color secondaryGreen =
      Color(0xFF14532D); // Vibrant Foliage Green
  static const Color brandSaffron = Color(0xFFE67E22); // Warm Saffron / Gold
  static const Color accentGold = Color(0xFFD97706); // Golden Grain Harvest
  static const Color slateDark = Color(0xFF0F172A); // Ultra-deep Slate Navy
  static const Color surfaceColor = Color(0xFFF8FAF7); // Soft Natural Off-White
  static const Color surfaceCard = Color(0xFFFFFFFF); // Pure White Cards
  static const Color textHighContrast = Color(0xFF0F172A); // High Contrast Text
  static const Color textMuted = Color(0xFF64748B); // Slate Muted Text
  static const Color borderLight = Color(0xFFE2E8F0); // Subtle Slate Border
  static const Color alertRed = Color(0xFFDC2626); // Statutory Alert / Recall
  static const Color verifiedTeal =
      Color(0xFF0D9488); // Cryptographic Seal Teal

  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: primaryGreen,
        primary: primaryGreen,
        secondary: secondaryGreen,
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
        elevation: 1.5,
        shadowColor: Colors.black.withOpacity(0.08),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(14),
          side: const BorderSide(color: borderLight, width: 1),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          minimumSize: const Size(120, 52), // Meets ≥48x48dp accessible target
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          backgroundColor: primaryGreen,
          foregroundColor: Colors.white,
          elevation: 1,
          textStyle: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            letterSpacing: 0.2,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          minimumSize: const Size(120, 52),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          foregroundColor: primaryGreen,
          side: const BorderSide(color: primaryGreen, width: 1.8),
          textStyle: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            letterSpacing: 0.2,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
      textTheme: const TextTheme(
        headlineLarge: TextStyle(
            fontSize: 28,
            fontWeight: FontWeight.w800,
            color: textHighContrast,
            letterSpacing: -0.5),
        headlineMedium: TextStyle(
            fontSize: 22, fontWeight: FontWeight.w700, color: textHighContrast),
        titleLarge: TextStyle(
            fontSize: 18, fontWeight: FontWeight.w700, color: textHighContrast),
        titleMedium: TextStyle(
            fontSize: 16, fontWeight: FontWeight.w600, color: textHighContrast),
        bodyLarge: TextStyle(
            fontSize: 15, fontWeight: FontWeight.w400, color: textHighContrast),
        bodyMedium: TextStyle(
            fontSize: 14, fontWeight: FontWeight.w400, color: textMuted),
        labelLarge: TextStyle(
            fontSize: 14, fontWeight: FontWeight.w600, letterSpacing: 0.3),
      ),
    );
  }
}
