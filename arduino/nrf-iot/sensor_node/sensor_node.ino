#include <SPI.h> 
#include <nRF24L01.h> 
#include <RF24.h>

#define LED 2
#define PUMP 3
#define TEMP 0

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
  
  //Serial.begin(9600); // for receiver
  
  myRadio.begin(); 
  myRadio.openWritingPipe(addresses[0]); // for transmit
  myRadio.openReadingPipe(1, addresses[1]); // for receive
  
  myRadio.setPALevel(RF24_PA_MIN);
  
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
    
    int tempVal = analogRead(TEMP);
    tempVal = map(tempVal, 0, 1023, 20,40);
    String string = "!0:iot-temp:";
    string += String(tempVal) + "#";
    
    const char *c_mess = string.c_str();
    myRadio.write(c_mess, string.length());
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
