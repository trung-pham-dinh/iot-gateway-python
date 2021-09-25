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



// long long premil = millis();
// void setup() {
//   // put your setup code here, to run once:
//   Serial.begin(115200);
//   pinMode(13, OUTPUT);
// }
//
// void loop() {
//   if(millis() - premil > 5000)
//   {
//     premil = millis();
//     String str1("!1:iot-temp:");
//     str1 += String(random(20,40)) + String("#");
//     Serial.print(str1);
//
//     String str2("!1:iot-humid:");
//     str2 += String(random(60,100)) + String("#");
//     Serial.print(str2);
//   }
// }