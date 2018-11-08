char serialData;
int pin1;
int pin2;

int fade;
void setup() {
  pin1 = 10;
  pin2 = 11;
  fade = 15;
  pinMode(pin1,OUTPUT);
  pinMode(pin2,OUTPUT);
  Serial.begin(9600);
}

void loop() {
  if(Serial.available() > 0)
  {
    serialData = Serial.read();
    Serial.print(serialData);

    if(serialData == '0')
    {
     digitalWrite(pin1,LOW); 
    }
    else if(serialData == '1')
    {
      digitalWrite(pin1,HIGH);
    }
    else if(serialData == '2')
    {
      for(int i=0;i < 255;i += fade)
      { 
      analogWrite(pin1,i);
      }
      delay(100);
      for(int i=255;i >= 0;i -= fade)
      { 
      analogWrite(pin1,i);
      delay(100);
      } 
      serialData = '0';
    }
    else if(serialData == '3')
    {
      digitalWrite(pin2,HIGH); 
    }
    else if(serialData == '4')
    {
      digitalWrite(pin2,LOW); 
    }
    else if(serialData == '5')
    {
     for(int i=0;i < 255;i += fade)
      { 
      analogWrite(pin2,i);
      }
      delay(100);
      for(int i=255;i >= 0;i -= fade)
      { 
      analogWrite(pin2,i);
      delay(100);
      } 
      serialData = '0';
    }
  }
}
