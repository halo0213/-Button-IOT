#include <Arduino.h>
const uint8_t pins[16]={13,14,16,17,18,19,21,22,23,25,26,27,32,33,4,5};
const unsigned long DEBOUNCE=35;
bool stable[16],previous[16];
unsigned long changed[16];
void setup(){
  Serial.begin(115200);
  for(int i=0;i<16;i++){
    pinMode(pins[i],INPUT_PULLUP);
    stable[i]=previous[i]=digitalRead(pins[i]);
    changed[i]=0;
  }
  delay(350);
  Serial.println("READY,16");
}
void loop(){
  unsigned long now=millis();
  for(int i=0;i<16;i++){
    bool v=digitalRead(pins[i]);
    if(v!=previous[i])changed[i]=now;
    if(now-changed[i]>=DEBOUNCE && v!=stable[i]){
      stable[i]=v;
      Serial.print("BTN,"); Serial.print(i+1); Serial.print(',');
      Serial.println(v==LOW?"DOWN":"UP");
    }
    previous[i]=v;
  }
}
