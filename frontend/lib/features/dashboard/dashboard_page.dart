import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/providers.dart';
import '../../models/prediction_models.dart';
import '../../widgets/app_shell.dart';

final _metricsProvider = FutureProvider<MetricsModel>((ref) async {
  return ref.read(apiServiceProvider).fetchMetrics();
});

class DashboardPage extends ConsumerWidget {
  const DashboardPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final metrics = ref.watch(_metricsProvider);
    return AppShell(
      title: 'Admin Dashboard',
      child: metrics.when(
        data: (data) => GridView.count(
          crossAxisCount: MediaQuery.of(context).size.width > 900 ? 3 : 1,
          mainAxisSpacing: 16,
          crossAxisSpacing: 16,
          children: [
            _MetricTile(
              title: 'Total Predictions',
              value: '${data.totalPredictions}',
            ),
            _MetricTile(
              title: 'Average Confidence',
              value: '${(data.averageConfidence * 100).toStringAsFixed(1)}%',
            ),
            _MetricTile(
              title: 'Average Risk Score',
              value: data.averageRiskScore.toStringAsFixed(1),
            ),
            _MetricTile(
              title: 'Ham',
              value: '${data.labelCounts['ham'] ?? 0}',
            ),
            _MetricTile(
              title: 'Spam',
              value: '${data.labelCounts['spam'] ?? 0}',
            ),
            _MetricTile(
              title: 'Phishing',
              value: '${data.labelCounts['phishing'] ?? 0}',
            ),
          ],
        ),
        error: (error, _) => Center(child: Text('Metrics failed: $error')),
        loading: () => const Center(child: CircularProgressIndicator()),
      ),
    );
  }
}

class _MetricTile extends StatelessWidget {
  const _MetricTile({
    required this.title,
    required this.value,
  });

  final String title;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(title, style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 12),
            Text(
              value,
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
          ],
        ),
      ),
    );
  }
}
