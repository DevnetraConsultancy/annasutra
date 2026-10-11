import 'package:flutter/material.dart';
import '../../../l10n/app_localizations.dart';

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
    final l10n = AppLocalizations.of(context);
    final theme = Theme.of(context);

    return AlertDialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      title: Row(
        children: [
          Icon(Icons.shield_outlined, color: theme.colorScheme.primary, size: 28),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              l10n?.dpdpNoticeTitle ?? 'Data Protection & Privacy Notice',
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
              l10n?.dpdpNoticeBody ??
                  'In compliance with the Digital Personal Data Protection Act 2023, AnnaSutra collects only essential data (mobile number and device key) solely for agricultural custody verification and fraud prevention.',
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
                l10n?.dpdpGrievanceContact ?? 'Grievance Redressal Officer: grievance@annasutra.in',
                style: theme.textTheme.bodySmall?.copyWith(fontWeight: FontWeight.w600),
              ),
            ),
          ],
        ),
      ),
      actions: [
        Semantics(
          button: true,
          label: l10n?.acceptAndContinue ?? 'I Agree & Continue',
          child: SizedBox(
            height: 48, // Accessible touch target size >= 48dp
            child: ElevatedButton(
              onPressed: () {
                Navigator.of(context).pop();
                onConsentAccepted?.call();
              },
              child: Text(l10n?.acceptAndContinue ?? 'I Agree & Continue'),
            ),
          ),
        ),
      ],
    );
  }
}
