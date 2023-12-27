// Arduino UNO:		VCC: 3.3v; CS: 9; DC: 8; RST: 7; SCL: 13; SDA: 11

#include <Arduino_GFX_Library.h>

Arduino_DataBus *bus = create_default_Arduino_DataBus();
Arduino_GFX *gfx = new Arduino_GC9A01(bus, 7 /* RST */, 0 /* rotation */, true /* IPS */);

static int16_t w, h, center;


void setup() {
	// put your setup code here, to run once:
	gfx->begin();
	gfx->fillScreen(BLACK);

	w = gfx->width();		//240
  h = gfx->height();  //240

  if (w < h) center = w / 2;	//120
  else center = h / 2;
}

void loop() {
	// put your main code here, to run repeatedly:
//	for(int i = 0; i < w; i++) for(int j = 0; j < h; j++){
//		gfx->drawLine(center, center, i, j, WHITE);
//		delay(10);
//		gfx->drawLine(center, center, i, j, BLACK);
////		gfx->fillScreen(BLACK);  // slooooooow
//	}

  gfx->setCursor(random(gfx->width()), random(gfx->height()));
  
  gfx->setTextColor(random(0xffff), random(0xffff));
  gfx->setTextSize(random(6) /* x scale */, random(6) /* y scale */, random(2) /* pixel_margin */);

  gfx->println(w);
	gfx->println(h);
	gfx->println(center);

	delay(2000);
}
