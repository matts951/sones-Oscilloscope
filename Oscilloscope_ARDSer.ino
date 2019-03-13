/*
  Analog input, analog output, serial output

  Reads an analog input pin, maps the result to a range from 0 to 255 and uses
  the result to set the pulse width modulation (PWM) of an output pin.
  Also prints the results to the Serial Monitor.

  The circuit:
  - potentiometer connected to analog pin 0.
    Center pin of the potentiometer goes to the analog pin.
    side pins of the potentiometer go to +5V and ground
  - LED connected from digital pin 9 to ground

  created 29 Dec. 2008
  modified 9 Apr 2012
  by Tom Igoe

  This example code is in the public domain.

  http://www.arduino.cc/en/Tutorial/AnalogInOutSerial
*/

// These constants won't change. They're used to give names to the pins used:
const int analogInPin = A0;  // Analog input pin that the potentiometer is attached to
const int analogOutPin = 9; // Analog output pin that the LED is attached to

int BUFFERLENGTH = 100, READRATE = 10;
const int READ = 0, WRITE = 1;
bool ReadWrite = READ;

bool forceHold = true; // Stops the program from transmitting anydata.

int n = 0;

int sensorValue = 0;        // value read from the pot
int outputValue = 0;        // value output to the PWM (analog out)

String ardCommand = "DATA";

String y;

void setup() {
  // initialize serial communications at 9600 bps:
  Serial.begin(115200);
}

void loop() {
// wait 2 milliseconds before the next loop for the analog-to-digital
// converter to settle after the last reading:
  switch (ReadWrite) {
    case READ: {        // Here you READ from the serial lines to get information from the computer
        Serial.println("Reading...");
        String pytCommand = Serial.readString();
        if (pytCommand.substring(0, 4) == "THRH") {
          // change the treshold pin
        } else if (pytCommand.substring(0, 4) == "BUFF") {
          // change the bufferlength
          BUFFERLENGTH = pytCommand.substring(4).toInt();
          if (BUFFERLENGTH <= 10) {
            BUFFERLENGTH = 10;
            Serial.print("MESGAuto adjust to BUFFERLENGTH = 10");
          }
        } else if (pytCommand.substring(0, 4) == "BEGN") {
          Serial.println("MESGBegininning transmission");
          forceHold = false;
          break;
        } else if (pytCommand.substring(0, 4) == "HOLD" || forceHold) {
          forceHold = true;
          break;
        } 
        delay(2);
        ReadWrite = WRITE;
        ardCommand="REFR";
        break;
    }
    case WRITE: {
      if (Serial.available() > 0) {
        ReadWrite = READ;
        break;
      }
      if (ardCommand == "REFR") {
        Serial.print("REFR");
        Serial.println(BUFFERLENGTH*READRATE);
        ardCommand = "DATA";
      } else if (ardCommand == "DATA") {
        for (int n = 0; n < BUFFERLENGTH; n ++) {
          // read the analog in value:
          sensorValue = analogRead(analogInPin);
          // map it to the range of the analog out:
          outputValue = map(sensorValue, 0, 1023, 0, 255);
          y += String(outputValue);
          y += ",";
        
          // wait n milliseconds before the next loop for the analog-to-digital
          // converter to settle after the last reading:
          delay(1000 * (1 / READRATE));
        }
        String c = "DATA";
        c += y.substring(0, y.length() - 1);
        c += "";
        Serial.println(c);  // At the minute this is sending two sets of data, not really needed long term.
        y = "";
        ReadWrite = WRITE;
      }
      break;
    }  
  }          
}
