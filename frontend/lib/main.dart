import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'screens/upload_screen.dart';

void main() {
  runApp(const DocVeilApp());
}

class DocVeilApp extends StatelessWidget {
  const DocVeilApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'DocVeil',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        textTheme: GoogleFonts.interTextTheme(
          Theme.of(context).textTheme.apply(
            bodyColor: Colors.white,
            displayColor: Colors.white,
          ),
        ),
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF667eea),
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
      ),
      home: const UploadScreen(),
    );
  }
}
