import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:intl/intl.dart';
import '../../domain/harvest_lot.dart';

class LotCard extends StatelessWidget {
  final HarvestLot lot;
  final VoidCallback? onEdit;
  final VoidCallback? onDispatch;
  final VoidCallback? onShowQr;

  const LotCard({
    super.key,
    required this.lot,
    this.onEdit,
    this.onDispatch,
    this.onShowQr,
  });

  @override
  Widget build(BuildContext context) {
    final isEditable = lot.isEditable;

    String harvestFormatted = lot.harvestDate;
    try {
      final dt = DateTime.parse(lot.harvestDate);
      harvestFormatted = DateFormat('dd MMM yyyy').format(dt);
    } catch (_) {}

    // Extract 2-letter category code from publicCode or default to VG
    String categoryCode = 'VG';
    if (lot.publicCode.length >= 26) {
      categoryCode = lot.publicCode.substring(22, 24);
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isEditable ? const Color(0xFFE2E8F0) : const Color(0xFFFED7AA),
          width: 1.2,
        ),
        boxShadow: const [
          BoxShadow(
            color: Color(0x08000000),
            blurRadius: 6,
            offset: Offset(0, 2),
          ),
        ],
      ),
      padding: const EdgeInsets.all(14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 1. TOP HEADER: Category Badge, Crop Name, Status Pill & Edit Icon
          Row(
            children: [
              // Category Code Pill (e.g., [VG])
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
                decoration: BoxDecoration(
                  color: const Color(0xFFECFDF5),
                  borderRadius: BorderRadius.circular(6),
                  border: Border.all(color: const Color(0xFFA7F3D0)),
                ),
                child: Text(
                  categoryCode,
                  style: const TextStyle(
                    fontFamily: 'monospace',
                    fontSize: 11,
                    fontWeight: FontWeight.w800,
                    color: Color(0xFF047857),
                  ),
                ),
              ),
              const SizedBox(width: 8),

              // Crop Name & Variety
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      lot.crop,
                      style: const TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w800,
                        color: Color(0xFF0F172A),
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                    if (lot.variety.isNotEmpty)
                      Text(
                        lot.variety,
                        style: const TextStyle(
                          fontSize: 11.5,
                          fontWeight: FontWeight.w500,
                          color: Color(0xFF64748B),
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                  ],
                ),
              ),

              // Custody Status Badge
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 8, vertical: 3.5),
                decoration: BoxDecoration(
                  color: isEditable
                      ? const Color(0xFFECFDF5)
                      : const Color(0xFFFFF7ED),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: isEditable
                        ? const Color(0xFF86EFAC)
                        : const Color(0xFFFDBA74),
                  ),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      isEditable
                          ? Icons.check_circle_outline
                          : Icons.local_shipping_outlined,
                      size: 11.5,
                      color: isEditable
                          ? const Color(0xFF059669)
                          : const Color(0xFFC2410C),
                    ),
                    const SizedBox(width: 4),
                    Text(
                      isEditable
                          ? 'Farm Custody'
                          : (lot.state == 'IN_TRANSIT'
                              ? 'In Transit'
                              : 'Accepted'),
                      style: TextStyle(
                        fontSize: 10.5,
                        fontWeight: FontWeight.w700,
                        color: isEditable
                            ? const Color(0xFF065F46)
                            : const Color(0xFF9A3412),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),

          const SizedBox(height: 8),

          // 2. LOT ID (Monospace with 1-tap copy)
          InkWell(
            onTap: () {
              Clipboard.setData(ClipboardData(text: lot.publicCode));
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('Copied lot ID: ${lot.publicCode}'),
                  duration: const Duration(seconds: 2),
                  backgroundColor: const Color(0xFF0B3D2E),
                  behavior: SnackBarBehavior.floating,
                ),
              );
            },
            borderRadius: BorderRadius.circular(6),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: const Color(0xFFF8FAFC),
                borderRadius: BorderRadius.circular(6),
                border: Border.all(color: const Color(0xFFE2E8F0)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.qr_code_2,
                      size: 14, color: Color(0xFF64748B)),
                  const SizedBox(width: 6),
                  Expanded(
                    child: Text(
                      lot.publicCode,
                      style: const TextStyle(
                        fontFamily: 'monospace',
                        fontSize: 11.5,
                        fontWeight: FontWeight.w700,
                        color: Color(0xFF334155),
                        letterSpacing: 0.3,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  const Icon(Icons.copy, size: 12, color: Color(0xFF64748B)),
                ],
              ),
            ),
          ),

          const SizedBox(height: 10),

          // 3. CORE METRIC STRIP (Weight, Quality, Valuation)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
            decoration: BoxDecoration(
              color: const Color(0xFFF8FAFC),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Row(
              children: [
                // Quantity
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'HARVEST QTY',
                        style: TextStyle(
                          fontSize: 9.5,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF64748B),
                          letterSpacing: 0.3,
                        ),
                      ),
                      const SizedBox(height: 1.5),
                      Text(
                        '${lot.netQtyKg.toStringAsFixed(1)} ${lot.unit}',
                        style: const TextStyle(
                          fontSize: 13.5,
                          fontWeight: FontWeight.w800,
                          color: Color(0xFF0B3D2E),
                        ),
                      ),
                    ],
                  ),
                ),

                // Quality Grade
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [
                      const Text(
                        'GRADE',
                        style: TextStyle(
                          fontSize: 9.5,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF64748B),
                          letterSpacing: 0.3,
                        ),
                      ),
                      const SizedBox(height: 1.5),
                      Text(
                        lot.qualityGrade
                            .replaceAll('Grade ', 'Gr-')
                            .replaceAll(' (Super)', ''),
                        style: const TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w700,
                          color: Color(0xFF1E40AF),
                        ),
                      ),
                    ],
                  ),
                ),

                // Valuation
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      const Text(
                        'VALUATION',
                        style: TextStyle(
                          fontSize: 9.5,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF64748B),
                          letterSpacing: 0.3,
                        ),
                      ),
                      const SizedBox(height: 1.5),
                      Text(
                        '₹${lot.estimatedValue.toStringAsFixed(0)}',
                        style: const TextStyle(
                          fontSize: 13.5,
                          fontWeight: FontWeight.w800,
                          color: Color(0xFF047857),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 8),

          // 4. FOOTER: Origin Plot, Harvest Date & Quick Action Buttons
          Row(
            children: [
              const Icon(Icons.location_on_outlined,
                  size: 12.5, color: Color(0xFF64748B)),
              const SizedBox(width: 3),
              Expanded(
                child: Text(
                  '${lot.originPlotName} • $harvestFormatted',
                  style: const TextStyle(
                    fontSize: 11,
                    color: Color(0xFF64748B),
                    fontWeight: FontWeight.w500,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),

              // Edit icon
              if (isEditable && onEdit != null) ...[
                IconButton(
                  icon: const Icon(Icons.edit_outlined,
                      size: 16, color: Color(0xFF047857)),
                  padding: EdgeInsets.zero,
                  constraints:
                      const BoxConstraints(minWidth: 28, minHeight: 28),
                  tooltip: 'Edit Batch',
                  onPressed: onEdit,
                ),
                const SizedBox(width: 6),
              ],

              // QR Labels Button (Compact 32dp height)
              OutlinedButton.icon(
                onPressed: onShowQr,
                icon: const Icon(Icons.qr_code,
                    size: 13, color: Color(0xFF047857)),
                label: const Text(
                  'QR',
                  style: TextStyle(
                    fontSize: 11.5,
                    fontWeight: FontWeight.w700,
                    color: Color(0xFF047857),
                  ),
                ),
                style: OutlinedButton.styleFrom(
                  minimumSize: const Size(60, 32),
                  padding:
                      const EdgeInsets.symmetric(horizontal: 9, vertical: 4),
                  side: const BorderSide(color: Color(0xFFA7F3D0), width: 1.2),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
              ),

              // Dispatch Button
              if (isEditable) ...[
                const SizedBox(width: 6),
                ElevatedButton.icon(
                  onPressed: onDispatch,
                  icon: const Icon(Icons.local_shipping_outlined, size: 13),
                  label: const Text(
                    'Dispatch',
                    style: TextStyle(
                      fontSize: 11.5,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF0B3D2E),
                    foregroundColor: Colors.white,
                    minimumSize: const Size(76, 32),
                    padding:
                        const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                ),
              ],
            ],
          ),
        ],
      ),
    );
  }
}
