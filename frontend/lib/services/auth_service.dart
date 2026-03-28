import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class AuthService {
  AuthService();
  static const _storage = FlutterSecureStorage();
  static const _tokenKey = 'access_token';

  Future<void> persistToken(String token) {
    return _storage.write(key: _tokenKey, value: token);
  }

  Future<String?> readToken() {
    return _storage.read(key: _tokenKey);
  }
}
