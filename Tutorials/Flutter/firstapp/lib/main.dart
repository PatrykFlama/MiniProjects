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
      body: Center(
        child: Image.asset('assets/image1.jpg'),
        // child: Image.network(
        //     'https://images.unsplash.com/photo-1564754943164-e83c08469116?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Nnx8dmVydGljYWx8ZW58MHx8MHx8fDA%3D&w=1000&q=80'),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {},
        backgroundColor: const Color.fromARGB(255, 82, 169, 0),
        child: const Text('CLICK'),
      ),
    );
  }
}
