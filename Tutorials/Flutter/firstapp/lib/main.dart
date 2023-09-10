// ignore_for_file: prefer_const_constructors, sort_child_properties_last, prefer_const_literals_to_create_immutables

import 'package:flutter/material.dart';
import 'package:carousel_slider/carousel_slider.dart';

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

      // ----- ROWS and COLUMNS -----
      body: widgetMain(),

      floatingActionButton: FloatingActionButton(
        onPressed: () {},
        backgroundColor: const Color.fromARGB(255, 82, 169, 0),
        child: const Text('CLICK'),
      ),
    );
  }
}

Widget? widgetMain() {
  return CarouselSlider(
    options: CarouselOptions(viewportFraction: 1),
    items: [
      widgetText(),
      widgetImage(),
      widgetIcon(),
      widgetButtons(),
      widgetContainer(),
      widgetRowsCols(),
      widgetExpanded(),
    ],
  );
}

Widget widgetExpanded() {
  return Row(
    children: [
      Expanded(
        flex: 10,
        child: Image.asset('assets/image2.jpg'),
      ),
      Expanded(
        flex: 1,
        child: Container(
          padding: EdgeInsets.all(30),
          color: Colors.cyan,
          child: Text('1'),
        ),
      ),
      Expanded(
        flex: 2,
        child: Container(
          padding: EdgeInsets.all(30),
          color: Colors.pinkAccent,
          child: Text('2'),
        ),
      ),
      Expanded(
        flex: 3,
        child: Container(
          padding: EdgeInsets.all(30),
          color: Colors.amber,
          child: Text('3'),
        ),
      ),
    ],
  );
}

Widget widgetRowsCols() {
  return Row(
    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
    // Widget is by default - not needed here
    children: <Widget>[
      Column(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: [Text('Hello'), Text('world!')],
      ),
      Column(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [Icon(Icons.abc), Icon(Icons.adb_sharp)],
      ),
      Column(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          Container(
            child: Text('one'),
            padding: EdgeInsets.all(20),
            color: Colors.blue,
          ),
          Container(
            child: Text('two'),
            padding: EdgeInsets.all(30),
            color: Colors.pink,
          ),
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Container(
              child: Text('three'),
              padding: EdgeInsets.all(40),
              color: Colors.amber,
            ),
          ),
        ],
      )
    ],
  );
}

Widget widgetContainer() {
  return Row(
    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
    children: [
      Container(
        // padding: EdgeInsets.all(20.0),
        padding: EdgeInsets.symmetric(horizontal: 20.0, vertical: 5.0),
        // padding: EdgeInsets.fromLTRB(5.0, 15.0, 30.0, 50.0),
        margin: EdgeInsets.all(20.0),
        color: Color.fromARGB(255, 138, 230, 255),
        child: Text('hello'),
      ),
      Padding(
        // only padding can be applied
        padding: EdgeInsets.all(100.0),
        child: Text("HI!"),
      ),
    ],
  );
}

Widget widgetButtons() {
  return Row(
    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
    children: [
      IconButton(
        onPressed: () {},
        icon: Icon(Icons.alternate_email),
        style: ButtonStyle(
          shadowColor: MaterialStatePropertyAll(Colors.red),
          iconColor: MaterialStatePropertyAll(Colors.blue),
        ),
      ),
      ElevatedButton.icon(
        onPressed: () {},
        icon: Icon(Icons.mail),
        label: Text('send mail'),
      ),
      ElevatedButton(
        onPressed: () {
          print('WOW');
        },
        child: Icon(Icons.ads_click),
        style: ButtonStyle(
          backgroundColor: MaterialStatePropertyAll(Colors.purple),
        ),
      ),
    ],
  );
}

Widget widgetIcon() {
  return Center(
    child: Icon(
      Icons.macro_off,
      color: Colors.purple,
      size: 50.0,
    ),
  );
}

Widget widgetImage() {
  return Row(
    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
    children: [
      Image.asset('assets/image1.jpg'),
      Image.network(
          'https://images.unsplash.com/photo-1564754943164-e83c08469116?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Nnx8dmVydGljYWx8ZW58MHx8MHx8fDA%3D&w=1000&q=80'),
    ],
  );
}

Widget widgetText() {
  return Text('Hello World!');
}
