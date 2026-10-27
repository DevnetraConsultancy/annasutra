import 'dart:math' as math;
import 'package:flutter/material.dart';

/// Donut chart slice data
class DonutSlice {
  final String label;
  final double value;
  final Color color;

  const DonutSlice(
      {required this.label, required this.value, required this.color});
}

/// Vector Donut Chart for Crop Volume & Valuation Breakdown
class CropDonutChart extends StatelessWidget {
  final Map<String, double> data;
  final String unit;
  final double height;

  static const List<Color> palette = [
    Color(0xFF047857), // Emerald
    Color(0xFF10B981), // Light green
    Color(0xFFF59E0B), // Amber
    Color(0xFF3B82F6), // Blue
    Color(0xFF8B5CF6), // Purple
    Color(0xFFEC4899), // Pink
    Color(0xFF14B8A6), // Teal
    Color(0xFFF97316), // Orange
  ];

  const CropDonutChart({
    super.key,
    required this.data,
    this.unit = 'Kg',
    this.height = 200,
  });

  @override
  Widget build(BuildContext context) {
    final total = data.values.fold(0.0, (sum, v) => sum + v);
    if (total <= 0) {
      return Container(
        height: height,
        alignment: Alignment.center,
        child: const Text('No yield data recorded.',
            style: TextStyle(color: Color(0xFF64748B))),
      );
    }

    final List<DonutSlice> slices = [];
    int colorIdx = 0;
    data.forEach((crop, val) {
      if (val > 0) {
        slices.add(DonutSlice(
          label: crop,
          value: val,
          color: palette[colorIdx % palette.length],
        ));
        colorIdx++;
      }
    });

    return Column(
      children: [
        SizedBox(
          height: height,
          child: Row(
            children: [
              // Vector Donut
              Expanded(
                flex: 5,
                child: CustomPaint(
                  size: Size(height, height),
                  painter: _DonutChartPainter(slices: slices, total: total),
                  child: Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          total > 1000
                              ? '${(total / 1000).toStringAsFixed(1)}k'
                              : total.toStringAsFixed(0),
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.w900,
                            color: Color(0xFF0B3D2E),
                          ),
                        ),
                        Text(
                          unit,
                          style: const TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF64748B),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),

              // Legend
              Expanded(
                flex: 6,
                child: ListView.separated(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: slices.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 6),
                  itemBuilder: (context, idx) {
                    final s = slices[idx];
                    final pct = ((s.value / total) * 100).toStringAsFixed(1);
                    return Row(
                      children: [
                        Container(
                          width: 10,
                          height: 10,
                          decoration: BoxDecoration(
                            color: s.color,
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 6),
                        Expanded(
                          child: Text(
                            s.label,
                            style: const TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.w600,
                                color: Color(0xFF1E293B)),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        Text(
                          '$pct%',
                          style: const TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w700,
                              color: Color(0xFF64748B)),
                        ),
                      ],
                    );
                  },
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _DonutChartPainter extends CustomPainter {
  final List<DonutSlice> slices;
  final double total;

  _DonutChartPainter({required this.slices, required this.total});

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = math.min(size.width, size.height) / 2.3;
    const strokeWidth = 24.0;

    double startAngle = -math.pi / 2;

    for (final slice in slices) {
      final sweepAngle = (slice.value / total) * 2 * math.pi;
      final paint = Paint()
        ..color = slice.color
        ..style = PaintingStyle.stroke
        ..strokeWidth = strokeWidth
        ..strokeCap = StrokeCap.butt;

      canvas.drawArc(
        Rect.fromCircle(center: center, radius: radius),
        startAngle,
        sweepAngle - 0.04, // subtle gap
        false,
        paint,
      );

      startAngle += sweepAngle;
    }
  }

  @override
  bool shouldRepaint(covariant _DonutChartPainter oldDelegate) => true;
}

/// Custody Pipeline Funnel Widget
class CustodyFunnelWidget extends StatelessWidget {
  final Map<String, double> stages;
  final double totalWeightKg;

  const CustodyFunnelWidget({
    super.key,
    required this.stages,
    required this.totalWeightKg,
  });

  @override
  Widget build(BuildContext context) {
    final stageColors = {
      'In Farm Custody': const Color(0xFF10B981),
      'In Transit': const Color(0xFFF59E0B),
      'Delivered / Mandi': const Color(0xFF3B82F6),
      'Custody Closed': const Color(0xFF64748B),
    };

    return Column(
      children: stages.entries.map((entry) {
        final color = stageColors[entry.key] ?? const Color(0xFF047857);
        final weight = entry.value;
        final pct = totalWeightKg > 0 ? (weight / totalWeightKg) : 0.0;
        final pctDisplay = (pct * 100).toStringAsFixed(1);

        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 6.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      Container(
                        width: 8,
                        height: 8,
                        decoration:
                            BoxDecoration(color: color, shape: BoxShape.circle),
                      ),
                      const SizedBox(width: 6),
                      Text(
                        entry.key,
                        style: const TextStyle(
                            fontSize: 12.5,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF0F172A)),
                      ),
                    ],
                  ),
                  Text(
                    '${weight.toStringAsFixed(0)} Kg ($pctDisplay%)',
                    style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w700,
                        color: color),
                  ),
                ],
              ),
              const SizedBox(height: 5),
              ClipRRect(
                borderRadius: BorderRadius.circular(6),
                child: LinearProgressIndicator(
                  value: pct.clamp(0.0, 1.0),
                  minHeight: 7,
                  backgroundColor: const Color(0xFFF1F5F9),
                  valueColor: AlwaysStoppedAnimation<Color>(color),
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }
}

/// Settlement & Commercial Payment Health Widget
class SettlementHealthWidget extends StatelessWidget {
  final Map<String, double> stats;

  const SettlementHealthWidget({super.key, required this.stats});

  @override
  Widget build(BuildContext context) {
    final settled = stats['SETTLED'] ?? 0.0;
    final advance = stats['ADVANCE'] ?? 0.0;
    final pending = stats['PENDING'] ?? 0.0;
    final total = settled + advance + pending;

    final settledPct = total > 0 ? (settled / total) : 0.0;
    final advancePct = total > 0 ? (advance / total) : 0.0;
    final pendingPct = total > 0 ? (pending / total) : 0.0;

    return Column(
      children: [
        // Multi-segment progress bar
        ClipRRect(
          borderRadius: BorderRadius.circular(8),
          child: SizedBox(
            height: 12,
            child: Row(
              children: [
                if (settledPct > 0)
                  Expanded(
                    flex: (settledPct * 100).round(),
                    child: Container(color: const Color(0xFF059669)),
                  ),
                if (advancePct > 0)
                  Expanded(
                    flex: (advancePct * 100).round(),
                    child: Container(color: const Color(0xFF3B82F6)),
                  ),
                if (pendingPct > 0)
                  Expanded(
                    flex: (pendingPct * 100).round(),
                    child: Container(color: const Color(0xFFF59E0B)),
                  ),
                if (total <= 0)
                  Expanded(
                    child: Container(color: const Color(0xFFE2E8F0)),
                  ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),

        // Financial KPI breakdown
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            _buildStatItem('Settled', '₹${settled.toStringAsFixed(0)}',
                const Color(0xFF059669)),
            _buildStatItem('Advance', '₹${advance.toStringAsFixed(0)}',
                const Color(0xFF2563EB)),
            _buildStatItem('Pending', '₹${pending.toStringAsFixed(0)}',
                const Color(0xFFD97706)),
          ],
        ),
      ],
    );
  }

  Widget _buildStatItem(String label, String value, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
                width: 8,
                height: 8,
                decoration:
                    BoxDecoration(color: color, shape: BoxShape.circle)),
            const SizedBox(width: 5),
            Text(label,
                style: const TextStyle(
                    fontSize: 11.5,
                    color: Color(0xFF64748B),
                    fontWeight: FontWeight.w600)),
          ],
        ),
        const SizedBox(height: 2),
        Text(value,
            style: TextStyle(
                fontSize: 13, fontWeight: FontWeight.w800, color: color)),
      ],
    );
  }
}
