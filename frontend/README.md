# Frontend

Flutter client for the private spam email classification platform.

## Platforms

- Web
- Android

## Features

- Email analysis screen
- Explainability with suspicious term highlighting
- Local secure token storage
- Local prediction history
- Admin metrics dashboard

## Run

```bash
flutter pub get
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000/api/v1
```

Android emulator example:

```bash
flutter run -d android --dart-define=API_BASE_URL=http://10.0.2.2:8000/api/v1
```
