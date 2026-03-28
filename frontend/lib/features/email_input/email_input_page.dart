import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/providers.dart';
import '../../models/prediction_models.dart';
import '../../widgets/app_shell.dart';
import '../../widgets/result_card.dart';

final _predictionProvider =
    StateProvider<AsyncValue<PredictionRecord?>>((ref) => const AsyncData(null));

class EmailInputPage extends ConsumerStatefulWidget {
  const EmailInputPage({super.key});

  @override
  ConsumerState<EmailInputPage> createState() => _EmailInputPageState();
}

class _EmailInputPageState extends ConsumerState<EmailInputPage> {
  final _subjectController = TextEditingController();
  final _bodyController = TextEditingController();
  final _formKey = GlobalKey<FormState>();

  @override
  void dispose() {
    _subjectController.dispose();
    _bodyController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }
    final request = EmailRequestModel(
      subject: _subjectController.text.trim(),
      body: _bodyController.text.trim(),
      metadata: const {'source': 'flutter_app'},
    );
    ref.read(_predictionProvider.notifier).state = const AsyncLoading();
    try {
      final result = await ref.read(apiServiceProvider).predict(request);
      ref.read(_predictionProvider.notifier).state = AsyncData(result);
      await ref.read(historyProvider.notifier).add(result);
    } catch (error, stackTrace) {
      ref.read(_predictionProvider.notifier).state =
          AsyncError(error, stackTrace);
    }
  }

  @override
  Widget build(BuildContext context) {
    final prediction = ref.watch(_predictionProvider);
    return AppShell(
      title: 'Analyze Email',
      child: ListView(
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Private email triage',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _subjectController,
                      decoration: const InputDecoration(
                        labelText: 'Subject',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _bodyController,
                      maxLines: 12,
                      validator: (value) {
                        if (value == null || value.trim().isEmpty) {
                          return 'Email body is required';
                        }
                        return null;
                      },
                      decoration: const InputDecoration(
                        labelText: 'Body',
                        alignLabelWithHint: true,
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 16),
                    Wrap(
                      spacing: 12,
                      runSpacing: 12,
                      children: [
                        FilledButton.icon(
                          onPressed: _submit,
                          icon: const Icon(Icons.shield_outlined),
                          label: const Text('Classify'),
                        ),
                        OutlinedButton.icon(
                          onPressed: () {
                            _subjectController.text = 'Urgent password verification';
                            _bodyController.text =
                                'Click to verify your bank account password now to avoid suspension.';
                          },
                          icon: const Icon(Icons.auto_fix_high),
                          label: const Text('Load Sample'),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ),
          const SizedBox(height: 20),
          prediction.when(
            data: (record) => record == null
                ? const SizedBox.shrink()
                : ResultCard(record: record),
            error: (error, _) => Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Text('Prediction failed: $error'),
              ),
            ),
            loading: () => const Card(
              child: Padding(
                padding: EdgeInsets.all(20),
                child: Center(child: CircularProgressIndicator()),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
