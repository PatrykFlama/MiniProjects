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

      body: Container(
        // padding: EdgeInsets.all(20.0),
        padding: EdgeInsets.symmetric(horizontal: 20.0, vertical: 5.0),
        // padding: EdgeInsets.fromLTRB(5.0, 15.0, 30.0, 50.0),
        margin: EdgeInsets.all(20.0),
        color: Color.fromARGB(255, 138, 230, 255),
        child: Text('hello'),
      ),

      // body: Padding(     // only padding can be applied
      //   padding: EdgeInsets.all(100.0),
      //   child: Text("HI!"),
      // ),

      // body: Center(
      //   // ---- BUTTONS ----
      //   child: IconButton(
      //     onPressed: () {},
      //     icon: Icon(Icons.alternate_email),
      //     style: ButtonStyle(
      //       shadowColor: MaterialStatePropertyAll(Colors.red),
      //       iconColor: MaterialStatePropertyAll(Colors.blue),
      //     ),
      //   ),

      // child: ElevatedButton.icon(
      //   onPressed: () {},
      //   icon: Icon(Icons.mail),
      //   label: Text('send mail'),
      // ),

      // child: ElevatedButton(
      //   onPressed: () {
      //     print('WOW');
      //   },
      //   child: Icon(Icons.ads_click),
      //   style: ButtonStyle(
      //     backgroundColor: MaterialStatePropertyAll(Colors.purple),
      //   ),
      // ),

      // ----- ICONS -----
      // child: Icon(
      //   Icons.macro_off,
      //   color: Colors.purple,
      //   size: 50.0,
      // ),

      // ----- IMAGES -----
      // child: Image.asset('assets/image1.jpg'),

      // child: Image.network(
      //     'https://images.unsplash.com/photo-1564754943164-e83c08469116?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Nnx8dmVydGljYWx8ZW58MHx8MHx8fDA%3D&w=1000&q=80'),

      // ----- TEXT -----
      // child: Text("Hello World!"),
      //   ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {},
        backgroundColor: const Color.fromARGB(255, 82, 169, 0),
        child: const Text('CLICK'),
      ),
    );
  }
}
