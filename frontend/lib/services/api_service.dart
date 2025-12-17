import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/summary_model.dart';

class ApiService {
  static const String baseUrl = 'http://localhost:8000';

  Future<UploadResponse> uploadPdf(String filePath) async {
    try {
      final uri = Uri.parse('$baseUrl/upload');
      final request = http.MultipartRequest('POST', uri);

      request.files.add(await http.MultipartFile.fromPath('file', filePath));

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(response.body);
        return UploadResponse.fromJson(data);
      } else {
        throw Exception('Upload failed: ${response.body}');
      }
    } catch (e) {
      throw Exception('Upload error: $e');
    }
  }

  Stream<SummaryEvent> streamSummaries(String jobId) async* {
    final uri = Uri.parse('$baseUrl/stream-summary/$jobId');

    try {
      final client = http.Client();
      final request = http.Request('GET', uri);
      final streamedResponse = await client.send(request);

      if (streamedResponse.statusCode != 200) {
        throw Exception(
          'Failed to start stream: ${streamedResponse.statusCode}',
        );
      }

      String buffer = '';

      await for (final chunk in streamedResponse.stream.transform(
        utf8.decoder,
      )) {
        buffer += chunk;

        final lines = buffer.split('\n');
        buffer = lines.removeLast();

        for (final line in lines) {
          if (line.startsWith('data: ')) {
            final dataStr = line.substring(6).trim();
            if (dataStr.isNotEmpty) {
              try {
                final Map<String, dynamic> data = json.decode(dataStr);
                final event = SummaryEvent.fromJson(data);
                yield event;

                if (event.isComplete) {
                  client.close();
                  return;
                }
              } catch (e) {
                print('Error parsing SSE data: $e');
              }
            }
          }
        }
      }
    } catch (e) {
      throw Exception('Stream error: $e');
    }
  }

  Future<Map<String, dynamic>> getJobStatus(String jobId) async {
    try {
      final uri = Uri.parse('$baseUrl/status/$jobId');
      final response = await http.get(uri);

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to get status: ${response.body}');
      }
    } catch (e) {
      throw Exception('Status check error: $e');
    }
  }

  Future<void> cleanupJob(String jobId) async {
    try {
      final uri = Uri.parse('$baseUrl/cleanup/$jobId');
      final response = await http.delete(uri);

      if (response.statusCode != 200) {
        throw Exception('Cleanup failed: ${response.body}');
      }
    } catch (e) {
      print('Cleanup error: $e');
    }
  }
}
