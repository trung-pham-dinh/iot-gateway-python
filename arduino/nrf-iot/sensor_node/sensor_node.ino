#include <SPI.h> 
#include <nRF24L01.h> 
#include <RF24.h>
#include<Wire.h>

#define LED 2
#define PUMP 3

#define MEASUREMENT 0x2400
const int SHT31ADDR = 0x44;
struct HumidTemp {
  uint16_t raw_temp;
  uint16_t raw_humid;
  float temp;
  float humid;
};
HumidTemp humid_temp;


long long preTime = millis();

struct Package
{
  int id;
  String feed;
  int value;
};


RF24 myRadio(7, 8); // CE,CSN

const byte addresses[][6] = {"00001", "00002"};


void setup() 
{
  pinMode(PUMP, OUTPUT);
  pinMode(LED, OUTPUT);
  digitalWrite(PUMP, LOW);
  digitalWrite(LED, LOW);
  
  Serial.begin(115200); // for receiver
  
  myRadio.begin(); 
  myRadio.openWritingPipe(addresses[0]); // for transmit
  myRadio.openReadingPipe(1, addresses[1]); // for receive
  
  myRadio.setPALevel(RF24_PA_MIN);

  Wire.begin();
  
}


void loop()  
{
  delay(5);
  myRadio.startListening();
  if(myRadio.available())
  {
    char text[32] = "";
    myRadio.read(&text, sizeof(text));
    //Serial.println(text);
    Package package = extract(String(text));
    if(package.feed == "iot-led")
    {
      digitalWrite(LED, package.value);
    }
    else if(package.feed == "iot-pump")
    {
      digitalWrite(PUMP, package.value);
    }
  }
  
  
  if(millis() - preTime >= 10000)
  {
    myRadio.stopListening();
    preTime = millis();

    sendCMD(MEASUREMENT);
    readData(humid_temp);
    
    String tempStr = "!0:iot-temp:" + String(int(humid_temp.temp)) + "#";
    String humidStr = "!0:iot-humid:" + String(int(humid_temp.humid)) + "#";
    //Serial.println(humid_temp.humid);
    const char *c_tempMess = tempStr.c_str();
    const char *c_humidMess = humidStr.c_str();
    myRadio.write(c_tempMess, tempStr.length());
    myRadio.write(c_humidMess, humidStr.length());
  }
}

Package extract(String mess)
{
  Package package;
  int index1 = mess.indexOf(':');
  String id = mess.substring(1, index1);
  
  int index2 = mess.indexOf(':', index1+1);
  String feed = mess.substring(index1+1, index2);
  
  int index3 = mess.indexOf('#', index2+1);
  String value = mess.substring(index2+1, index3);

  package.id = id.toInt();
  package.feed = feed;
  package.value = value.toInt();

  return package;
}





// sht31
void readByte(uint8_t *data, int numberOfBytes) {
  Wire.requestFrom(SHT31ADDR, numberOfBytes);
  for(int i = 0; i < numberOfBytes; i++) {
    data[i] = Wire.read();
  }
}

void sendCMD(uint16_t cmd) {
  Wire.beginTransmission(SHT31ADDR);
  Wire.write(cmd >> 8); // send MSB of command
  Wire.write(cmd & 0x00FF); // send LSB of command
  Wire.endTransmission();
}

void readData(HumidTemp &data) {
  uint8_t bytes[6]; // 2 bytes TEMP, 1 byte CRC, 2 bytes HUMID, 1 bytes CRC
  readByte(bytes, 6);
  
  data.raw_temp = (bytes[0] << 8) | bytes[1];
  data.raw_humid = (bytes[3] << 8) | bytes[4];

  data.temp = (175.0 / 65535) * data.raw_temp - 45;
  data.humid = (100.0 / 65535) * data.raw_humid;
}
