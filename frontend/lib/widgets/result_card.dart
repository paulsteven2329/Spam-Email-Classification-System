import 'package:flutter/material.dart';

import '../models/prediction_models.dart';

class ResultCard extends StatelessWidget {
  const ResultCard({
    super.key,
    required this.record,
  });

  final PredictionRecord record;

  Color get _riskColor {
    if (record.riskScore >= 80) {
      return const Color(0xFFB42318);
    }
    if (record.riskScore >= 50) {
      return const Color(0xFFB54708);
    }
    return const Color(0xFF027A48);
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Wrap(
              spacing: 12,
              runSpacing: 12,
              children: [
                Chip(label: Text(record.label.toUpperCase())),
                Chip(label: Text('Confidence ${(record.confidence * 100).toStringAsFixed(1)}%')),
                Chip(
                  backgroundColor: _riskColor.withValues(alpha: 0.12),
                  label: Text(
                    'Risk ${record.riskScore}',
                    style: TextStyle(color: _riskColor, fontWeight: FontWeight.w700),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Text(record.explanation),
            const SizedBox(height: 16),
            if (record.suspiciousTerms.isNotEmpty) ...[
              Text(
                'Suspicious terms',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: record.suspiciousTerms
                    .map(
                      (term) => Chip(
                        label: Text('${term.token} • ${term.reason}'),
                      ),
                    )
                    .toList(),
              ),
              const SizedBox(height: 16),
            ],
            if (record.retrievedExamples.isNotEmpty) ...[
              Text(
                'Retrieved examples',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 8),
              ...record.retrievedExamples.map(Text.new),
            ],
          ],
        ),
      ),
    );
  }
}
