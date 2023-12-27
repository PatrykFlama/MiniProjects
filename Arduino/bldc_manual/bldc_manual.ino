/*
https://www.digikey.pl/-/media/Images/Article%20Library/TechZone%20Articles/2017/January/Why%20and%20How%20to%20Sinusoidally%20Control%20Three-Phase%20Brushless%20DC%20Motors/article-2017january-why-and-how-to-fig1.jpg?ts=a3782098-65d9-4178-86c9-972a632a32d0&la=pl-PL
https://community.simplefoc.com/t/3-bldc-and-stepper-foc-driver-l298n/296
https://docs.simplefoc.com/bldcdriver6pwm
*/

int a1 = 2, a2 = 3, b1 = 4, b2 = 5, c1 = 7, c2 = 8;
int pins[6] = {2, 3, 4, 5, 7, 8};
int sa = 0, sb = 0, sc = 0;	// 0 -> N; 1 -> +; 2 -> -

String phases[6] = {"acb", "bca", "bac", "cab", "cba", "abc"};		// from / to / off
int spd = 10; //time delay

void setup() {
	Serial.begin(9600);

	for(int i : pins){
		pinMode(i,OUTPUT);
		digitalWrite(i, LOW);
	}
}

void loop() {
//	 read serial
//	char temp = Serial.read();
//	while(temp == -1) temp = Serial.read();
//	String s = "";
//	
//	while(temp != 10){
//		if(temp != -1) {s += temp;}
//		temp = Serial.read();
//	}

	for(String s : phases){

		execute(s);
	
		Serial.print('a');
		switch(sa){
		  case 0:
		  	Serial.println('n');
		  	break;
			case 1:
				Serial.println('+');
				break;
			case 2:
				Serial.println('-');
				break;
		}
		Serial.print('b');
		switch(sb){
		  case 0:
		  	Serial.println('n');
		  	break;
			case 1:
				Serial.println('+');
				break;
			case 2:
				Serial.println('-');
				break;
		}
		Serial.print('c');
		switch(sc){
		  case 0:
		  	Serial.println('n');
		  	break;
			case 1:
				Serial.println('+');
				break;
			case 2:
				Serial.println('-');
				break;
		}

		delay(spd);
	}
}

void execute(String s){
	switch(s[0]){
		case 'a':
			bldc("a+");
			break;
		case 'b':
			bldc("b+");
			break;
		case 'c':
			bldc("c+");
			break;
	}
	switch(s[1]){
		case 'a':
			bldc("a-");
			break;
		case 'b':
			bldc("b-");
			break;
		case 'c':
			bldc("c-");
			break;
	}
	switch(s[2]){
		case 'a':
			bldc("an");
			break;
		case 'b':
			bldc("bn");
			break;
		case 'c':
			bldc("cn");
			break;
	}
}

void bldc(String s){
	if(s[0] == 'a'){
		if(s[1] == '0' || s[1] == 'n'){
			sa = 0;
			digitalWrite(a1, LOW);
			digitalWrite(a2, LOW);
		} else if(s[1] == '1' || s[1] == '+'){
			sa = 1;
			digitalWrite(a1, LOW);
			digitalWrite(a2, HIGH);
		} else if(s[1] == '2' || s[1] == '-'){
			sa = 2;
			digitalWrite(a1, HIGH);
			digitalWrite(a2, LOW);
		}
	} else if(s[0] == 'b'){
		if(s[1] == '0' || s[1] == 'n'){
			sb = 0;
			digitalWrite(b1, LOW);
			digitalWrite(b2, LOW);
		} else if(s[1] == '1' || s[1] == '+'){
			sb = 1;
			digitalWrite(b1, LOW);
			digitalWrite(b2, HIGH);
		} else if(s[1] == '2' || s[1] == '-'){
			sb = 2;
			digitalWrite(b1, HIGH);
			digitalWrite(b2, LOW);
		}
	} else if(s[0] == 'c'){
		if(s[1] == '0' || s[1] == 'n'){
			sc = 0;
			digitalWrite(c1, LOW);
			digitalWrite(c2, LOW);
		} else if(s[1] == '1' || s[1] == '+'){
			sc = 1;
			digitalWrite(c1, LOW);
			digitalWrite(c2, HIGH);
		} else if(s[1] == '2' || s[1] == '-'){
			sc = 2;
			digitalWrite(c1, HIGH);
			digitalWrite(c2, LOW);
		}
	}
}
