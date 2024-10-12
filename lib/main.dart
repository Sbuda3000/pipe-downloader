// import 'dart:convert';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(const MainApp());
}

class MainApp extends StatelessWidget {
  const MainApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: "Flutter Python Integration",
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: const HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  // ignore: library_private_types_in_public_api
  _HomePageState createState() => _HomePageState();
}

 class _HomePageState extends State<HomePage> {
  String _response = "Response will appear here";

  Future<void> _sendDataToPython() async {
    // Send a POST request with some sample data.
    final url = Uri.parse('http://127.0.0.1:5000/data');
    final response = await http.post(
      url, 
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "name": "Flutter",
        "message": "Hello, Python!"
      }));

    if (response.statusCode == 200) {
      setState(() {
        _response = response.body;
      });
    }
    else {
      setState(() {
        _response = "Error: ${response.statusCode}";
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Flutter Python Integration"),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(_response),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _sendDataToPython, 
              child: const Text('Send Data to Python'))
          ],
        ),
      ),
    );
  }
}
