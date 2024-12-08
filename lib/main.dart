import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';

void main() {
  runApp(const MainApp());
}

class MainApp extends StatelessWidget {
  const MainApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: "Pipe Downloader",
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
  HomePageState createState() => HomePageState();
}

 class HomePageState extends State<HomePage> {
  final TextEditingController _urlController = TextEditingController();
  String _status = "Enter a YouTube URL";
  String _filePath = "";

  // Function to request storage permission
  Future<bool> _requestStoragePermission() async {
    var status = await Permission.storage.status;

    if (status.isDenied) {
      // Request permission
      status = await Permission.storage.request();
    }

    if (status.isPermanentlyDenied) {
      // The user has denied the permission permanently, direct them to settings
      openAppSettings();
      return false;
    }

    return status.isGranted;
  } 

  Future<void> _downloadYouTubeVideo() async {
    // Check if the URL is non-empty
    final url = _urlController.text;

    if (url.isEmpty) {
        setState(() {
          _status = "Please enter a valid YouTube URL";
        });
        return;
      }

    // Request storage permission before downloading the video
    bool permissionGranted = await _requestStoragePermission();

    if (!permissionGranted) {
      setState(() {
        _status = "Storage permission denied";
      });
      return;
    }

    try {
      setState(() {
        _status = "Downloading video...";
      });

      // Make a POST request to the Flask backend to download the video
      final response = await http.post(Uri.parse('http://10.0.2.2:5000/download'),
                                      headers: {"Content-Type": "application/json"},
                                      body: jsonEncode({"url": url})); // Pass the YouTube URL here
      
      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        final downloadedFilePath = jsonResponse['file_path'];

        // Move downloaded file to app's local storage
        await _saveFileToLocalDirectory(downloadedFilePath);

        setState(() {
          _status = "Download complete!";
          _filePath = downloadedFilePath;
        });
      }
      else {
        setState(() {
          _status = "Error: ${response.body}";
        });
      }
    }
    catch (e) {
      setState(() {
        _status = "Error occurred: $e";
      });
    }
  }

  Future<void> _saveFileToLocalDirectory(String downloadedFilePath) async {
    final directory = await getExternalStorageDirectories();
    if (directory != null) {
      final fileName = downloadedFilePath.split('/').last;
      // ignore: unused_local_variable
      final savedFile = File('$directory/$fileName');

      // Move the file from temp download directory to app's local storage
      final tempFile = File(downloadedFilePath);
      await tempFile.copy(savedFile.path);

      setState(() {
        
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Pipe Downloader"),
      ),
      body:  Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            TextField(
              controller: _urlController,
              decoration: const InputDecoration(
                labelText: "YouTube URL",
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _downloadYouTubeVideo, 
              child: const Text("Download Video"),
            ),
            const SizedBox(height: 20),
            Text(_status),
            _filePath.isNotEmpty ? Text("Saved at: $_filePath") : Container(),
          ],),
      ),
    );
  }
}
