/*
   Copyright 2019 Leon Kiefer

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

	   http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/
#include <CorsairLightingProtocol.h>
#include <FastLED.h>

#define DATA_PIN_CHANNEL_1 9
#define RED_PIN 5
#define GREEN_PIN 3
#define BLUE_PIN 6

#define L 40
CRGB ledsChannel1[L];
CRGB ledsChannel2[10];

CorsairLightingFirmwareStorageEEPROM firmwareStorage;
CorsairLightingFirmware firmware(CORSAIR_LIGHTING_NODE_PRO, &firmwareStorage);
FastLEDControllerStorageEEPROM storage;
FastLEDController ledController(&storage);
CorsairLightingProtocolController cLP(&ledController, &firmware);
CorsairLightingProtocolHID cHID(&cLP);

void setup() {
	FastLED.addLeds<WS2812B, DATA_PIN_CHANNEL_1, RGB>(ledsChannel1, L);
	pinMode(RED_PIN, OUTPUT);
	pinMode(GREEN_PIN, OUTPUT);
	pinMode(BLUE_PIN, OUTPUT);

	ledController.addLEDs(0, ledsChannel1, L);
	
	ledController.addLEDs(1, ledsChannel2, 10);
	ledController.onUpdateHook(0, []() {
		// use color of first LED of the first channel
		set4PinLEDs(ledsChannel2[0]);
	});
}

void loop() {
	cHID.update();

	if (ledController.updateLEDs()) {
		FastLED.show();
	}
}

void set4PinLEDs(const CRGB& color) {
	analogWrite(RED_PIN, 255-color.r);
	analogWrite(GREEN_PIN, 255-color.g);
	analogWrite(BLUE_PIN, 255-color.b);
}
