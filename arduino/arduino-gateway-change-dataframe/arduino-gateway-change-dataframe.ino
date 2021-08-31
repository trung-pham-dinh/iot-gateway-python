char receiveByte = 0;
long long premil = millis();

struct Package
{
  int id;
  String feed;
  int value;
};


void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(13, OUTPUT);
  digitalWrite(13, 0);
}

void loop() {
  // put your main code here, to run repeatedly:
  
  if(Serial.available()) 
  {
    receiveByte = Serial.read();
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
      Package package = extract(mess);
      digitalWrite(13, package.value);
    }
    receiveByte = 0;
  }

  if(millis() - premil > 10000) 
  {
    premil = millis();
    String sendStr("!1:iot-temp:");
    sendStr += String(random(20,40)) + String("#");
    Serial.print(sendStr);
  }
}

struct Package extract(String mess)
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
  
