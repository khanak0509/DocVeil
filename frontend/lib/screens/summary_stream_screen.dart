import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'dart:ui';
import '../services/api_service.dart';
import '../models/summary_model.dart';
import '../widgets/summary_card.dart';

class SummaryStreamScreen extends StatefulWidget {
  final String jobId;
  final String filename;

  const SummaryStreamScreen({
    super.key,
    required this.jobId,
    required this.filename,
  });

  @override
  State<SummaryStreamScreen> createState() => _SummaryStreamScreenState();
}

class _SummaryStreamScreenState extends State<SummaryStreamScreen> {
  final ApiService _apiService = ApiService();
  final List<SummaryEvent> _summaries = [];
  bool _isComplete = false;
  bool _hasError = false;
  String? _errorMessage;
  int _totalPages = 0;

  @override
  void initState() {
    super.initState();
    _startStreaming();
  }

  Future<void> _startStreaming() async {
    try {
      await for (final event in _apiService.streamSummaries(widget.jobId)) {
        if (!mounted) return;

        setState(() {
          if (event.totalPages > 0) {
            _totalPages = event.totalPages;
          }

          if (event.isComplete) {
            _isComplete = true;
          } else if (event.isProcessing && event.summary.isNotEmpty) {
            _summaries.add(event);
          }
        });
      }
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _hasError = true;
        _errorMessage = e.toString();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFF0f0c29), Color(0xFF302b63), Color(0xFF24243e)],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              _buildHeader(),

              Expanded(
                child: _hasError
                    ? _buildError()
                    : _summaries.isEmpty && !_isComplete
                    ? _buildLoading()
                    : _buildSummariesList(),
              ),

              if (_isComplete) _buildCompletionBanner(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.all(20),
      child: Column(
        children: [
          Row(
            children: [
              IconButton(
                onPressed: () => Navigator.pop(context),
                icon: const Icon(Icons.arrow_back, color: Colors.white),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Processing PDF',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      widget.filename,
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.6),
                        fontSize: 14,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),
            ],
          ),

          if (!_isComplete && _totalPages > 0)
            Container(
              margin: const EdgeInsets.only(top: 16),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Progress: ${_summaries.length}/$_totalPages pages',
                        style: TextStyle(
                          color: Colors.white.withOpacity(0.8),
                          fontSize: 14,
                        ),
                      ),
                      Text(
                        '${((_summaries.length / _totalPages) * 100).toStringAsFixed(0)}%',
                        style: const TextStyle(
                          color: Color(0xFF667eea),
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(10),
                    child: LinearProgressIndicator(
                      value: _totalPages > 0
                          ? _summaries.length / _totalPages
                          : 0,
                      backgroundColor: Colors.white.withOpacity(0.2),
                      valueColor: const AlwaysStoppedAnimation<Color>(
                        Color(0xFF667eea),
                      ),
                      minHeight: 8,
                    ),
                  ),
                ],
              ),
            ).animate().fadeIn().slideY(begin: -0.3, end: 0),
        ],
      ),
    );
  }

  Widget _buildLoading() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: LinearGradient(
                    colors: [
                      const Color(0xFF667eea).withOpacity(0.2),
                      const Color(0xFF764ba2).withOpacity(0.2),
                    ],
                  ),
                ),
                child: const CircularProgressIndicator(
                  strokeWidth: 3,
                  valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF667eea)),
                ),
              )
              .animate(onPlay: (controller) => controller.repeat())
              .scale(
                duration: 1000.ms,
                begin: const Offset(0.8, 0.8),
                end: const Offset(1.2, 1.2),
              ),
          const SizedBox(height: 24),
          Text(
                'Analyzing your PDF...',
                style: TextStyle(
                  color: Colors.white.withOpacity(0.8),
                  fontSize: 18,
                  fontWeight: FontWeight.w500,
                ),
              )
              .animate(onPlay: (controller) => controller.repeat())
              .fadeIn(duration: 1000.ms)
              .then()
              .fadeOut(duration: 1000.ms),
        ],
      ),
    );
  }

  Widget _buildSummariesList() {
    return ListView.builder(
      padding: const EdgeInsets.all(20),
      itemCount: _summaries.length,
      itemBuilder: (context, index) {
        final summary = _summaries[index];
        return SummaryCard(
          pageNumber: summary.page,
          summary: summary.summary,
          totalPages: summary.totalPages,
          index: index,
        );
      },
    );
  }

  Widget _buildCompletionBanner() {
    return Container(
          width: double.infinity,
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF10b981), Color(0xFF059669)],
            ),
            boxShadow: [
              BoxShadow(
                color: const Color(0xFF10b981).withOpacity(0.3),
                blurRadius: 20,
                offset: const Offset(0, -10),
              ),
            ],
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.check_circle, color: Colors.white, size: 24),
              const SizedBox(width: 12),
              const Text(
                'Summary Complete!',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        )
        .animate()
        .slideY(begin: 1, end: 0, duration: 600.ms, curve: Curves.easeOutQuart)
        .shimmer(delay: 300.ms, duration: 1500.ms);
  }

  Widget _buildError() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(20),
              decoration: const BoxDecoration(
                color: Colors.red,
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.error_outline,
                size: 48,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 24),
            const Text(
              'An error occurred',
              style: TextStyle(
                color: Colors.white,
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            Text(
              _errorMessage ?? 'Unknown error',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: Colors.white.withOpacity(0.7),
                fontSize: 14,
              ),
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: () => Navigator.pop(context),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.white.withOpacity(0.2),
                foregroundColor: Colors.white,
              ),
              child: const Text('Go Back'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _apiService.cleanupJob(widget.jobId);
    super.dispose();
  }
}
