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

    // Payment styling
    final paymentMeta = switch (lot.paymentStatus) {
      'SETTLED' => (label: 'Fully Settled', bg: const Color(0xFFECFDF5), text: const Color(0xFF065F46), border: const Color(0xFF86EFAC)),
      'ADVANCE' => (label: 'Advance Received', bg: const Color(0xFFEFF6FF), text: const Color(0xFF1E40AF), border: const Color(0xFFBFDBFE)),
      _ => (label: 'Pending Settlement', bg: const Color(0xFFFFFBEB), text: const Color(0xFF92400E), border: const Color(0xFFFDE68A)),
    };

    String harvestFormatted = lot.harvestDate;
    try {
      final dt = DateTime.parse(lot.harvestDate);
      harvestFormatted = DateFormat('dd MMM yyyy, hh:mm a').format(dt);
    } catch (_) {}

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: isEditable ? const Color(0xFFE2E8F0) : const Color(0xFFFED7AA),
          width: 1.5,
        ),
        boxShadow: const [
          BoxShadow(color: Color(0x0A000000), blurRadius: 4, offset: Offset(0, 1)),
        ],
      ),
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 1. TOP HEADER: Public Code, Crop, Grade, Payment Status & Lock/Edit Button
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Wrap(
                  spacing: 6,
                  runSpacing: 6,
                  crossAxisAlignment: WrapCrossAlignment.center,
                  children: [
                    // Sovereign Code Pill with Copy Action
                    InkWell(
                      onTap: () {
                        Clipboard.setData(ClipboardData(text: lot.publicCode));
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text('Copied lot code ${lot.publicCode} to clipboard'),
                            duration: const Duration(seconds: 2),
                            backgroundColor: const Color(0xFF047857),
                          ),
                        );
                      },
                      borderRadius: BorderRadius.circular(6),
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3.5),
                        decoration: BoxDecoration(
                          color: const Color(0xFFECFDF5),
                          border: Border.all(color: const Color(0xFFA7F3D0)),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(
                              lot.publicCode,
                              style: const TextStyle(
                                fontFamily: 'monospace',
                                fontSize: 13,
                                fontWeight: FontWeight.w800,
                                color: Color(0xFF047857),
                                letterSpacing: 0.5,
                              ),
                            ),
                            const SizedBox(width: 4),
                            const Icon(Icons.copy, size: 12, color: Color(0xFF047857)),
                          ],
                        ),
                      ),
                    ),

                    // Crop Name & Variety
                    Text(
                      lot.crop,
                      style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                    ),
                    if (lot.variety.isNotEmpty)
                      Text(
                        '• ${lot.variety}',
                        style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF475569)),
                      ),

                    // Quality Grade Chip
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
                      decoration: BoxDecoration(
                        color: const Color(0xFFEFF6FF),
                        border: Border.all(color: const Color(0xFFBFDBFE)),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Text(
                        lot.qualityGrade,
                        style: const TextStyle(fontSize: 10.5, fontWeight: FontWeight.w800, color: Color(0xFF1E40AF)),
                      ),
                    ),

                    // Payment Status Chip
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
                      decoration: BoxDecoration(
                        color: paymentMeta.bg,
                        border: Border.all(color: paymentMeta.border),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Text(
                        paymentMeta.label,
                        style: TextStyle(fontSize: 10.5, fontWeight: FontWeight.w700, color: paymentMeta.text),
                      ),
                    ),
                  ],
                ),
              ),

              // Right-hand Custody Status & Pencil Edit Icon
              if (isEditable) ...[
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: const Color(0xFFECFDF5),
                        border: Border.all(color: const Color(0xFF86EFAC)),
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: const Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.check_circle_outline, size: 13, color: Color(0xFF10B981)),
                          SizedBox(width: 4),
                          Text(
                            'In Farm Custody',
                            style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFF065F46)),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 6),
                    IconButton(
                      icon: const Icon(Icons.edit, size: 18, color: Color(0xFF047857)),
                      tooltip: 'Edit Harvest Lot',
                      visualDensity: VisualDensity.compact,
                      onPressed: onEdit,
                    ),
                  ],
                ),
              ] else ...[
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 4),
                  decoration: BoxDecoration(
                    color: const Color(0xFFFFF7ED),
                    border: Border.all(color: const Color(0xFFFDBA74)),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.lock, size: 13, color: Color(0xFFC2410C)),
                      const SizedBox(width: 4),
                      Text(
                        lot.state == 'IN_TRANSIT' ? 'In Transit (Locked)' : 'Handover Done (Locked)',
                        style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFF9A3412)),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),

          const Divider(height: 20, color: Color(0xFFF1F5F9)),

          // 2. BODY METRICS GRID
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Harvest Quantity
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('QUANTITY', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF64748B))),
                    const SizedBox(height: 2),
                    Text(
                      '${lot.netQtyKg.toStringAsFixed(1)} ${lot.unit}',
                      style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w900, color: Color(0xFF0B3D2E)),
                    ),
                    Text(
                      lot.packagesCount > 0 ? '${lot.packagesCount} ${lot.packageType}' : 'Bulk Produce',
                      style: const TextStyle(fontSize: 11.5, color: Color(0xFF64748B)),
                    ),
                  ],
                ),
              ),

              // Origin Plot & Land
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('ORIGIN PLOT', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF64748B))),
                    const SizedBox(height: 2),
                    Text(
                      lot.originPlotName,
                      style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF0F172A)),
                      overflow: TextOverflow.ellipsis,
                    ),
                    Text(
                      '${lot.plotAreaAcres} Ac • ${lot.farmingMethod}',
                      style: const TextStyle(fontSize: 11.5, color: Color(0xFF64748B)),
                    ),
                  ],
                ),
              ),

              // Valuation & Target
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('VALUATION', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF64748B))),
                    const SizedBox(height: 2),
                    Text(
                      '₹${lot.basePricePerUnit.toStringAsFixed(0)} / ${lot.unit}',
                      style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF0F172A)),
                    ),
                    Text(
                      'Total: ₹${lot.estimatedValue.toStringAsFixed(0)}',
                      style: const TextStyle(fontSize: 11.5, fontWeight: FontWeight.bold, color: Color(0xFF047857)),
                    ),
                  ],
                ),
              ),
            ],
          ),

          const SizedBox(height: 10),
          Row(
            children: [
              const Icon(Icons.event_outlined, size: 14, color: Color(0xFF64748B)),
              const SizedBox(width: 4),
              Text(
                'Harvested: $harvestFormatted',
                style: const TextStyle(fontSize: 11.5, color: Color(0xFF64748B)),
              ),
              const Spacer(),
              Text(
                'Target: ${lot.intendedBuyer}',
                style: const TextStyle(fontSize: 11.5, fontWeight: FontWeight.w600, color: Color(0xFF475569)),
              ),
            ],
          ),

          const Divider(height: 20, color: Color(0xFFF1F5F9)),

          // 3. ACTION BAR: Print QR Labels (Unlimited) + Public Trace + Dispatch
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              // Print QR Labels (Unlimited)
              OutlinedButton.icon(
                onPressed: onShowQr,
                icon: const Icon(Icons.qr_code, size: 16, color: Color(0xFF047857)),
                label: const Text(
                  'QR Labels',
                  style: TextStyle(fontSize: 12.5, fontWeight: FontWeight.bold, color: Color(0xFF047857)),
                ),
                style: OutlinedButton.styleFrom(
                  minimumSize: const Size(100, 40),
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  side: const BorderSide(color: Color(0xFFA7F3D0)),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                ),
              ),

              // Dispatch to Mandi / Buyer Button
              if (isEditable)
                ElevatedButton.icon(
                  onPressed: onDispatch,
                  icon: const Icon(Icons.local_shipping_outlined, size: 16),
                  label: const Text(
                    'Dispatch to Mandi',
                    style: TextStyle(fontSize: 12.5, fontWeight: FontWeight.bold),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF047857),
                    foregroundColor: Colors.white,
                    minimumSize: const Size(120, 40),
                    padding: const EdgeInsets.symmetric(horizontal: 14),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                ),
            ],
          ),
        ],
      ),
    );
  }
}
