#include "GTS_4E.h"
// $GPGGA,130304.838,1046.2619,N,10641.2620,E,1,03,4.6,-2.4,M,2.4,M,,0000*4DTX

GPS gps(2,3,9600);

void setup() {
  Serial.begin(115200);
}

void loop() {
  if(gps.readGGA()) {
    //Serial.println();
    String lat = gps.getGGA_Data(GGA_Latitude);
    String lon = gps.getGGA_Data(GGA_Longitude);
    if(lat != "") {
      Serial.println("!1:iot-lat:" + lat + "#");
    }
    if(lon != "") {
      Serial.println("!1:iot-lon:" + lon + "#");
    }
  }

  //delay(5000);
}
