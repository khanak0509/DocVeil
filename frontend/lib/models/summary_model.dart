class SummaryEvent {
  final int page;
  final int totalPages;
  final String summary;
  final String status;

  SummaryEvent({
    required this.page,
    required this.totalPages,
    required this.summary,
    required this.status,
  });

  factory SummaryEvent.fromJson(Map<String, dynamic> json) {
    return SummaryEvent(
      page: json['page'] as int,
      totalPages: json['total_pages'] as int,
      summary: json['summary'] as String,
      status: json['status'] as String,
    );
  }

  bool get isComplete => status == 'complete';
  bool get isProcessing => status == 'processing';
}

class UploadResponse {
  final String jobId;
  final String filename;
  final String message;

  UploadResponse({
    required this.jobId,
    required this.filename,
    required this.message,
  });

  factory UploadResponse.fromJson(Map<String, dynamic> json) {
    return UploadResponse(
      jobId: json['job_id'] as String,
      filename: json['filename'] as String,
      message: json['message'] as String,
    );
  }
}
