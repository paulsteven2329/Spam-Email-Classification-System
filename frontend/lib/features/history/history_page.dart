import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../core/providers.dart';
import '../../widgets/app_shell.dart';
import '../../widgets/result_card.dart';

class HistoryPage extends ConsumerStatefulWidget {
  const HistoryPage({super.key});

  @override
  ConsumerState<HistoryPage> createState() => _HistoryPageState();
}

class _HistoryPageState extends ConsumerState<HistoryPage> {
  String _query = '';

  @override
  Widget build(BuildContext context) {
    final history = ref.watch(historyProvider);
    final filtered = history.where((record) {
      final query = _query.toLowerCase();
      return record.subject.toLowerCase().contains(query) ||
          record.body.toLowerCase().contains(query) ||
          record.label.toLowerCase().contains(query);
    }).toList();
    return AppShell(
      title: 'Prediction History',
      child: Column(
        children: [
          TextField(
            decoration: const InputDecoration(
              hintText: 'Search subject, body, or label',
              prefixIcon: Icon(Icons.search),
              border: OutlineInputBorder(),
            ),
            onChanged: (value) => setState(() => _query = value),
          ),
          const SizedBox(height: 20),
          Expanded(
            child: filtered.isEmpty
                ? const Center(child: Text('No predictions stored yet'))
                : ListView.separated(
                    itemCount: filtered.length,
                    separatorBuilder: (_, __) => const SizedBox(height: 16),
                    itemBuilder: (context, index) {
                      final record = filtered[index];
                      return Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            DateFormat.yMMMd().add_jm().format(record.createdAt),
                            style: Theme.of(context).textTheme.bodySmall,
                          ),
                          const SizedBox(height: 8),
                          ResultCard(record: record),
                        ],
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }
}
