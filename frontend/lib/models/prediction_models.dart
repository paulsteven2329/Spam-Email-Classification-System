class EmailRequestModel {
  const EmailRequestModel({
    required this.subject,
    required this.body,
    this.metadata = const {},
  });

  final String subject;
  final String body;
  final Map<String, dynamic> metadata;

  Map<String, dynamic> toJson() => {
        'subject': subject,
        'body': body,
        'metadata': metadata,
      };
}

class SuspiciousTerm {
  const SuspiciousTerm({
    required this.token,
    required this.score,
    required this.reason,
  });

  final String token;
  final double score;
  final String reason;

  factory SuspiciousTerm.fromJson(Map<String, dynamic> json) => SuspiciousTerm(
        token: json['token'] as String,
        score: (json['score'] as num).toDouble(),
        reason: json['reason'] as String,
      );

  Map<String, dynamic> toJson() => {
        'token': token,
        'score': score,
        'reason': reason,
      };
}

class PredictionRecord {
  const PredictionRecord({
    required this.subject,
    required this.body,
    required this.label,
    required this.confidence,
    required this.explanation,
    required this.riskScore,
    required this.suspiciousTerms,
    required this.retrievedExamples,
    required this.createdAt,
  });

  final String subject;
  final String body;
  final String label;
  final double confidence;
  final String explanation;
  final int riskScore;
  final List<SuspiciousTerm> suspiciousTerms;
  final List<String> retrievedExamples;
  final DateTime createdAt;

  factory PredictionRecord.fromJson(Map<String, dynamic> json) => PredictionRecord(
        subject: json['subject'] as String,
        body: json['body'] as String,
        label: json['label'] as String,
        confidence: (json['confidence'] as num).toDouble(),
        explanation: json['explanation'] as String,
        riskScore: json['risk_score'] as int,
        suspiciousTerms: (json['suspicious_terms'] as List<dynamic>)
            .map((item) => SuspiciousTerm.fromJson(item as Map<String, dynamic>))
            .toList(),
        retrievedExamples: (json['retrieved_examples'] as List<dynamic>)
            .map((item) => item as String)
            .toList(),
        createdAt: DateTime.parse(json['created_at'] as String),
      );

  Map<String, dynamic> toJson() => {
        'subject': subject,
        'body': body,
        'label': label,
        'confidence': confidence,
        'explanation': explanation,
        'risk_score': riskScore,
        'suspicious_terms':
            suspiciousTerms.map((item) => item.toJson()).toList(),
        'retrieved_examples': retrievedExamples,
        'created_at': createdAt.toIso8601String(),
      };

  factory PredictionRecord.fromApi(
    EmailRequestModel request,
    Map<String, dynamic> json,
  ) {
    return PredictionRecord(
      subject: request.subject,
      body: request.body,
      label: json['label'] as String,
      confidence: (json['confidence'] as num).toDouble(),
      explanation: json['explanation'] as String,
      riskScore: json['risk_score'] as int,
      suspiciousTerms: (json['suspicious_terms'] as List<dynamic>)
          .map((item) => SuspiciousTerm.fromJson(item as Map<String, dynamic>))
          .toList(),
      retrievedExamples: (json['retrieved_examples'] as List<dynamic>)
          .map((item) => item as String)
          .toList(),
      createdAt: DateTime.now(),
    );
  }
}

class MetricsModel {
  const MetricsModel({
    required this.totalPredictions,
    required this.labelCounts,
    required this.averageConfidence,
    required this.averageRiskScore,
  });

  final int totalPredictions;
  final Map<String, dynamic> labelCounts;
  final double averageConfidence;
  final double averageRiskScore;

  factory MetricsModel.fromJson(Map<String, dynamic> json) => MetricsModel(
        totalPredictions: json['total_predictions'] as int,
        labelCounts: json['label_counts'] as Map<String, dynamic>,
        averageConfidence: (json['average_confidence'] as num).toDouble(),
        averageRiskScore: (json['average_risk_score'] as num).toDouble(),
      );
}
