/*
SD card attached to SPI bus as follows:
on MEGA:
	MOSI - pin 51
	MISO - pin 50
	SCK  - pin 52
	CS   - pin 53 (for MKRZero SD: SDCARD_SS_PIN)
on UNO:
	MOSI - pin 11
	MISO - pin 12
	SCK  - pin 13
	CS   - pin 10 (for MKRZero SD: SDCARD_SS_PIN)

LCD wiring for MEGA:
	SDA SDA
	SCL SCL
*/

// TODO variable LCD backlight brightness

// ***** INCLUDES *****
#include <SPI.h>
#include <SD.h>
#include <Keypad.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

#define debug if(0)

// ------ BILLS ------
#define TERMINATE -1
#define BACK -2
#define B1 0
#define B2 1
#define B5 2
#define B10 3
#define B20 4
#define B50 5
#define B100 6
#define B200 7
#define B500 8
#define BILLS 9
const int bill_name[BILLS] = {1, 2, 5, 10, 20, 50, 100, 200, 500};

struct Money{
		int value;	// denomination
		int amt;		// amt of bills
		Money() : Money(0, 0){};
		Money(int v, int a){value = v; amt = a;}
};

// ------ DRAWER ------			//! using button as power delivery interuption used for now
//const int DRAWER_PIN = 10;
//#define drawer_closed() digitalRead(DRAWER_PIN) == LOW

// ------ SD DATA ------
const String FILENAME = "DATA.txt";
const int SD_PIN = 10;		// CS pin
File file;
int bills[BILLS];

// ------ KEYPAD ------
const byte ROWS = 4;
const byte COLS = 4;
char hexaKeys[ROWS][COLS] = {
	{'1', '2', '3', 'A'},
	{'4', '5', '6', 'B'},
	{'7', '8', '9', 'C'},
	{'*', '0', '#', 'D'}
};
byte rowPins[ROWS] = {9, 8, 7, 6};
byte colPins[COLS] = {5, 4, 3, 2};
Keypad Kpd = Keypad(makeKeymap(hexaKeys), rowPins, colPins, ROWS, COLS);

// ------ I2C LCD ------
const short int LCD_W = 20, LCD_H = 4;
LiquidCrystal_I2C lcd(0x27, LCD_W, LCD_H);


// ------------------ FUNCTIONS ------------------
// ------ SYSTEM ------
void sleep(){							// sleep the system (drawer closed)
	lcd.noBacklight();
	for(int i = 0; i < 4; i++) gui_println("", i);

//	while(drawer_closed()){}
}

void wake_up(){						// wake up the system (drawer opened)
	lcd.backlight();
	sd_load();
	main_menu();
}

void sd_init(){
	while(!SD.begin(SD_PIN)){
		debug Serial.println("SD card initialization failed");
	}
}

inline void gui_println(String line, int row){
	while(line.length() < LCD_W) line += " ";
	
	lcd.setCursor(0, row);
	lcd.print(line);
}

// ------ USER ------
int total_sum(){
	long long res = 0;
	for(int i = 0; i < BILLS; i++) res += (long long)(bill_name[i])*(long long)(bills[i]);
	return res;
}

int keypad_get_number(){ return keypad_get_number_def(0); }
int keypad_get_number_def(int num){  	//? gets from user number or returns TERMINATE
	char key = 0;
	// default amt for 0 is 1
	gui_println("Enter number:", 2);
	if(num == 0) gui_println("1", 3);
	else  		   gui_println(String(num), 3);
	
	while(true){
		if(key != 0) {
			gui_println("Enter number:", 2);
			gui_println(String(num), 3);
		}
		
		key = Kpd.getKey();

		if(key >= '0' && key <= '9') num = num*10 + (key-'0'); 
		else if(key == '#')	num /= 10;		// DEL
		else if(key == 'A') break;				// ACC
		else if(key == 'B') return BACK;
		else if(key == 'C') num = 0;			// CLEAR
		else if(key == 'D') return TERMINATE;
	}
	
	return num;
}

int keypad_get_bill(){		//? gets from user desired bill denomination or returns TERMINATE
	char key = 1;
	
	while(true){
		if(key != 0) {
			gui_println("Choose bill:", 2);
			gui_println("1-9 <=> 1-500", 3);
		}

		key = Kpd.getKey();

		if(key >= '0' && key <= '9') return key-'1';
		if(key == 'B') return BACK;
		if(key == 'D') return TERMINATE;
	}
}

Money money_input(){		//? gets Money from user or returns no change
	Money res;
	res.value = keypad_get_bill();
	if(res.value == TERMINATE || res.value == BACK) return Money(0, 0);

	gui_println("Bill: " + String(bill_name[res.value]), 1);
	res.amt = keypad_get_number();
	if(res.amt == TERMINATE) return Money(0, 0);
	if(res.amt == BACK) res = money_input();		//TODO not the best way to do that - builds stack
	if(res.amt == 0) res.amt = 1;
	
	return res;
}

// --------------------- SD ----------------------
void sd_save(){
	SD.remove(FILENAME);
	file = SD.open(FILENAME, FILE_WRITE);
	if(not file) debug Serial.println("SD write problem with opening the file");
	for(int i = 0; i < BILLS; i++) file.println(bills[i]);
	file.close();
}

void sd_load(){
	file = SD.open(FILENAME, O_READ);
	if(not file){
		debug Serial.println("SD read problem with opening the file");
		sd_save();			// error while opening the file? create new, working one
	}
	
	for(int i = 0; i < BILLS; i++) {
		if(file.available()) bills[i] = file.readStringUntil('\n').toInt();
		else {
			debug Serial.println("SD read not enough data");
			file.close(); sd_save(); return; 
		}
	}
	
	file.close();
}

// -------------------- MENU ---------------------
void main_menu(){
	const int PAGES = 4;
	const String PAGE_NAME[] = {"TOTAL AMT", "DEPOSIT", "WITHDRAW", "CHECK AMTS", "SETTINGS"};
	int page = 0;
	char key = 1;

	while(true){
		if(key != 0) for(int i = 0; i < 4; i++){
			int act_page = (page+i)%PAGES;
			if(act_page == 0) gui_println(PAGE_NAME[act_page] + ": " + String(total_sum()), i);
			else gui_println(PAGE_NAME[act_page], i);
		}

		key = Kpd.getKey();

		if(key == '#') 		  page = (page+1) % PAGES;						// go right
		else if(key == '*') page = ((page-1)+PAGES) % PAGES;		// go left
		else if(key == '0' || key == 'A') {			// enter selected page
			switch(page){
				case 1:
					menu_add();
					break;
				case 2:
				  menu_take_out();
				  break;
				case 3:
				  menu_check_amts();
				  break;
				case 4:
				  menu_settings();
				  break;
			}
		}

//		if(drawer_closed()) break;
	}
}

void menu_add(){
	gui_println("DEPOSIT MONEY", 0);
	gui_println("Acc Back Discard", 1);

	Money m = money_input();
	bills[m.value] += m.amt;
	sd_save();
}
void menu_take_out(){
	gui_println("WITHDRAW MONEY", 0);
	gui_println("Acc Back Discard", 1);

	Money m = money_input();
	bills[m.value] -= m.amt;
	sd_save();
}

void menu_check_amts(){
	gui_println("CHECK AMOUNTS", 0);
	int active_bill = 0;
	char key = 1;
	
	while(true){
		if(key != 0){
			for(int i = 0; i < BILLS; i+=3){
				String line = "";
				for(int j = 0; j < 3; j++){
					if(active_bill != i+j) line += String(bills[i+j]) + " ";
					else line += "-" + String(bills[i+j]) + "- ";
				}
				gui_println(line, i/3+1);
			}
		}

		key = Kpd.getKey();

		if(key == '#') 		  active_bill = (active_bill+1) % BILLS;						// go right
		else if(key == '*') active_bill = ((active_bill-1)+BILLS) % BILLS;		// go left
		else if(key == 'A') {			// save and quit
			sd_save();
			break;
		}	
		else if(key == 'D') {			// discard and quit
			sd_load();
			break;
		}
		else if(key == '0') {			// edit actual amt
			gui_println("Editing " + String(bill_name[active_bill]), 1);
			int new_amt = keypad_get_number_def(bills[active_bill]);
			if(new_amt != TERMINATE && new_amt != BACK)
				bills[active_bill] = new_amt;
		}
	}
}

void menu_settings(){
	const int PAGES = 1;
	int page = 0;
	char key = 0;

	while(true){
		gui_println("There aint", 0);
		gui_println("no settings", 1);
		gui_println("here", 2);
		gui_println(":<", 3);
		
		key = Kpd.getKey();

		if(key == '#') 		  page = (page+1) % PAGES;						// go right
		else if(key == '*') page = ((page-1)+PAGES) % PAGES;		// go left
		else if(key == 'D') break;		// go back
		else if(key == '0') {			// enter selected page
		}
	}
}

// -----------------------------------------------

void setup() {
	debug Serial.begin(9600);
	debug while(!Serial) {}		// wait for Serial to be ready
	debug Serial.println("Well hello there");
	
	lcd.begin();
	sd_init();
//	pinMode(DRAWER_PIN, INPUT_PULLUP);
}

void loop() {
	wake_up();
	//sleep();
}
