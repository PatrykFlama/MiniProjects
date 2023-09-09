import 'package:flutter/material.dart';

void main() {
  runApp(
    const MaterialApp(
      home: Home(),
    ),
  );
}

class Home extends StatelessWidget {
  const Home({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Color.fromARGB(255, 154, 255, 149),
      appBar: AppBar(
        title: const Text(
          'First app',
          style: TextStyle(
            fontSize: 40.0,
            fontWeight: FontWeight.bold,
            letterSpacing: 2.0,
            fontFamily: 'RubikIso',
          ),
        ),
        centerTitle: true,
        backgroundColor: Color.fromARGB(255, 82, 169, 0),
      ),
      body: const Center(
        child: Text('Hello World'),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {},
        backgroundColor: const Color.fromARGB(255, 82, 169, 0),
        child: const Text('CLICK'),
      ),
    );
  }
}
