#include <SPI.h> 
#include <nRF24L01.h>
#include <RF24.h>
#include "GTS_4E.h"

RF24 myRadio(7, 8); // CE,CSN
const byte addresses[][6] = {"00001", "00002"};
//                            trans     receive


GPS gps(2,3,9600);
String lat = gps.getGGA_Data(GGA_Latitude);
String lon = gps.getGGA_Data(GGA_Longitude);
String ele = gps.getGGA_Data(GGA_MSL_Altitude);
long long premil = millis();


void setup()
{
  Serial.begin(115200);
  myRadio.begin(); 
  
  myRadio.openWritingPipe(addresses[1]); // for transmit
  myRadio.openReadingPipe(1, addresses[0]); // for receive
  
  myRadio.setPALevel(RF24_PA_MIN);
  myRadio.stopListening();
}

void loop()
{
  delay(5);
  myRadio.startListening();
  if(myRadio.available())
  {
    //Serial.println("Hello");
    char text[32] = "";
    myRadio.read(&text, sizeof(text));
    Serial.println(text);
  }

  if(Serial.available()) 
  {
    char receiveByte = Serial.read();
    if(receiveByte == '!')
    {
      String mess = "!";
      while(1)
      {
        if(Serial.available())
        {
          receiveByte = Serial.read();
          mess += String(receiveByte);
          if(receiveByte == '#') break;
          receiveByte = 0;
        }
      }
      myRadio.stopListening();
      const char *c_mess = mess.c_str();
      myRadio.write(c_mess, mess.length());
    }
  }


  gps.readGGA();
  lat = gps.getGGA_Data(GGA_Latitude);
  lon = gps.getGGA_Data(GGA_Longitude);
  ele = gps.getGGA_Data(GGA_MSL_Altitude);
  if(millis()-premil > 5000) {
    premil = millis();
    if(lat != "" && lon != "" && ele != "") {
      Serial.println("!1:iot-gps:" + lat + "," + lon + "," + ele + "#");
    }
  }
}
