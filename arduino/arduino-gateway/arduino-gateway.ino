byte receiveByte = 0;
bool buttonState = 0;
long long premil = millis();
void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(13, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  if(Serial.available()) 
  {
    receiveByte = Serial.read();
    if(receiveByte != '#')
    {
      buttonState = receiveByte - 48;
    }
  }

  if(millis() - premil > 10000) 
  {
    premil = millis();
    String sendStr("!1:iot-temp:");
    sendStr += String(random(20,40)) + String("#");
    Serial.print(sendStr);
  }
  
  digitalWrite(13, buttonState);
}




//    receiveByte = Serial.read();
//    if(receiveByte != '!')
//    {
//      //buttonState = receiveByte - 48;
//      String mess = ""
//      while(1)
//      {
//          if(Serial.available())
//          {
//            receiveByte = Serial.read();
//            if(receiveByte == '#') break;
//            mess += String(receiveByte);
//          }
//          for(int i = 0; i < 2; i++) {
//            if(mess.indexOf(feeds[i]) != -1)
//            {
//              
//            }  
//          }
//      }
//      
//    }
