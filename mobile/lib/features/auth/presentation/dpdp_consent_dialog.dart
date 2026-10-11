import 'package:flutter/material.dart';

/// Trilingual strings for DPDP Act 2023 / Rules 2025 compliance.
class DpdpStrings {
  static String title(String lang) {
    switch (lang) {
      case 'bn':
        return 'তথ্য সুরক্ষা ও গোপনীয়তা বিজ্ঞপ্তি';
      case 'hi':
        return 'डेटा सुरक्षा एवं गोपनीयता सूचना';
      default:
        return 'Data Protection & Privacy Notice';
    }
  }

  static String body(String lang) {
    switch (lang) {
      case 'bn':
        return 'ডিজিটাল পার্সোনাল ডেটা প্রোটেকশন অ্যাক্ট ২০২৩ অনুসারে, অন্নসূত্র শুধুমাত্র কৃষি হেফাজত যাচাই ও জালিয়াতি প্রতিরোধের জন্য প্রয়োজনীয় তথ্য (মোবাইল নম্বর ও ডিভাইস কি) সংগ্রহ করে। আপনার তথ্য দেখার, সংশোধন করার বা মুছে ফেলার অধিকার রয়েছে।';
      case 'hi':
        return 'डिजिटल पर्सनल डेटा प्रोटेक्शन एक्ट 2023 के तहत, अन्नासूत्र केवल कृषि कस्टडी सत्यापन और धोखाधड़ी रोकथाम के लिए आवश्यक डेटा (मोबाइल नंबर और डिवाइस कुंजी) एकत्र करता है। आपको अपने डेटा को देखने, सुधारने या हटाने का अधिकार है।';
      default:
        return 'In compliance with the Digital Personal Data Protection Act 2023, AnnaSutra collects only essential data (mobile number and device key) solely for agricultural custody verification and fraud prevention. You have the right to access, correct, or erase your information.';
    }
  }

  static String grievance(String lang) {
    switch (lang) {
      case 'bn':
        return 'অভিযোগ নিষ্পত্তি কর্মকর্তা: grievance@annasutra.in';
      case 'hi':
        return 'शिकायत निवारण अधिकारी: grievance@annasutra.in';
      default:
        return 'Grievance Redressal Officer: grievance@annasutra.in';
    }
  }

  static String button(String lang) {
    switch (lang) {
      case 'bn':
        return 'আমি সম্মত ও এগিয়ে যান';
      case 'hi':
        return 'मैं सहमत हूँ एवं आगे बढ़ें';
      default:
        return 'I Agree & Continue';
    }
  }
}

/// DPDP Act 2023 / Rules 2025 compliant privacy notice & consent dialog.
class DpdpConsentDialog extends StatelessWidget {
  const DpdpConsentDialog({super.key, this.onConsentAccepted});

  final VoidCallback? onConsentAccepted;

  static Future<void> show(BuildContext context, {VoidCallback? onAccepted}) {
    return showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => DpdpConsentDialog(onConsentAccepted: onAccepted),
    );
  }

  @override
  Widget build(BuildContext context) {
    final lang = Localizations.localeOf(context).languageCode;
    final theme = Theme.of(context);

    return AlertDialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      title: Row(
        children: [
          Icon(Icons.shield_outlined, color: theme.colorScheme.primary, size: 28),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              DpdpStrings.title(lang),
              style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
            ),
          ),
        ],
      ),
      content: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              DpdpStrings.body(lang),
              style: theme.textTheme.bodyMedium,
            ),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: theme.colorScheme.surfaceContainerHighest,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                DpdpStrings.grievance(lang),
                style: theme.textTheme.bodySmall?.copyWith(fontWeight: FontWeight.w600),
              ),
            ),
          ],
        ),
      ),
      actions: [
        Semantics(
          button: true,
          label: DpdpStrings.button(lang),
          child: SizedBox(
            height: 48, // Accessible touch target size >= 48dp
            child: ElevatedButton(
              onPressed: () {
                Navigator.of(context).pop();
                onConsentAccepted?.call();
              },
              child: Text(DpdpStrings.button(lang)),
            ),
          ),
        ),
      ],
    );
  }
}
