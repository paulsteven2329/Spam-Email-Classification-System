import 'package:dio/dio.dart';

import '../models/prediction_models.dart';
import 'auth_service.dart';

class ApiService {
  ApiService(this._authService)
      : _dio = Dio(
          BaseOptions(
            baseUrl: const String.fromEnvironment(
              'API_BASE_URL',
              defaultValue: 'http://localhost:8000/api/v1',
            ),
            connectTimeout: const Duration(seconds: 10),
            receiveTimeout: const Duration(seconds: 10),
          ),
        );

  final AuthService _authService;
  final Dio _dio;

  Future<void> bootstrapAuth() async {
    final existing = await _authService.readToken();
    if (existing != null && existing.isNotEmpty) {
      _dio.options.headers['Authorization'] = 'Bearer $existing';
      return;
    }
    final response = await _dio.post<Map<String, dynamic>>('/auth/token');
    final token = response.data?['access_token'] as String;
    _dio.options.headers['Authorization'] = 'Bearer $token';
    await _authService.persistToken(token);
  }

  Future<PredictionRecord> predict(EmailRequestModel request) async {
    await bootstrapAuth();
    final response = await _dio.post<Map<String, dynamic>>(
      '/predict',
      data: request.toJson(),
    );
    return PredictionRecord.fromApi(request, response.data!);
  }

  Future<MetricsModel> fetchMetrics() async {
    await bootstrapAuth();
    final response = await _dio.get<Map<String, dynamic>>('/metrics');
    return MetricsModel.fromJson(response.data!);
  }
}
