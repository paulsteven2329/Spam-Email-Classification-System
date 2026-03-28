import 'dart:convert';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../models/prediction_models.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';

final authServiceProvider = Provider<AuthService>((ref) => AuthService());
final apiServiceProvider = Provider<ApiService>(
  (ref) => ApiService(ref.read(authServiceProvider)),
);

final historyProvider =
    StateNotifierProvider<HistoryNotifier, List<PredictionRecord>>((ref) {
  return HistoryNotifier()..load();
});

class HistoryNotifier extends StateNotifier<List<PredictionRecord>> {
  HistoryNotifier() : super(const []);

  static const _storageKey = 'prediction_history';

  Future<void> load() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_storageKey);
    if (raw == null || raw.isEmpty) {
      return;
    }
    final items = (jsonDecode(raw) as List<dynamic>)
        .map((entry) => PredictionRecord.fromJson(entry as Map<String, dynamic>))
        .toList()
        .reversed
        .toList();
    state = items;
  }

  Future<void> add(PredictionRecord record) async {
    state = [record, ...state].take(100).toList();
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(
      _storageKey,
      jsonEncode(state.map((item) => item.toJson()).toList()),
    );
  }
}
