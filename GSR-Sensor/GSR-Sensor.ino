int num_sensors;
uint8_t gsr_pins[20];

bool num_sensors_set = false;
bool pins_set = false;

int sensorValue=0;
int gsr_average=0;

bool build_connection = true;
bool measure = false;

const byte buffSize = 80;
char inputBuffer[buffSize];
const char startMarker = '<';
const char endMarker = '>';
byte bytesRecvd = 0;
boolean readInProgress = false;
boolean newDataFromPC = false;

char messageFromPC[buffSize];


void getDataFromPC() {

    // receive data from PC and save it into inputBuffer
    
  if(Serial.available() > 0) {

    char x = Serial.read();

      // the order of these IF clauses is significant
      
    if (x == endMarker) {
      readInProgress = false;
      newDataFromPC = true;
      inputBuffer[bytesRecvd] = 0;
      parseData();
    }
    
    if(readInProgress) {
      inputBuffer[bytesRecvd] = x;
      bytesRecvd ++;
      if (bytesRecvd == buffSize) {
        bytesRecvd = buffSize - 1;
      }
    }

    if (x == startMarker) { 
      bytesRecvd = 0; 
      readInProgress = true;
    }
  }
}

void parseData() {

    // split the data into its parts
    
  char * strtokIndx; // this is used by strtok() as an index

  strtokIndx = strtok(inputBuffer,",");      // get the first part - the string
  strcpy(messageFromPC, strtokIndx); // copy it to messageFromPC

  if (strcmp(messageFromPC, "NumSensors")==0){
    strtokIndx = strtok(NULL, ",");
    num_sensors = atoi(strtokIndx); 
    num_sensors_set = true;
  }

  if (strcmp(messageFromPC, "Pins")==0){
    for(int i=0;i<num_sensors;i++) {
      strtokIndx = strtok(NULL, ",");
      if (String(strtokIndx) == "A0") {
        gsr_pins[i] = A0;
      } else if (String(strtokIndx) == "A1") {
        gsr_pins[i] = A1;
      } else if (String(strtokIndx) == "A2") {
        gsr_pins[i] = A2;
      } else if (String(strtokIndx) == "A3") {
        gsr_pins[i] = A3;
      } else if (String(strtokIndx) == "A4") {
        gsr_pins[i] = A4;
      } else if (String(strtokIndx) == "A5") {
        gsr_pins[i] = A5;
      } else if (String(strtokIndx) == "A6") {
        gsr_pins[i] = A6;
      }
    }
    pins_set = true;
  }

  if (String(inputBuffer) == "start") {
    measure = true;
  }
  if (String(inputBuffer) == "stop") {
    measure = false;
  }
  if (String(inputBuffer) == "exit") {
    measure = false;
    build_connection = true;
  }


}


void setup(){
  Serial.begin(9600);
  while (!Serial) {
  ; // wait for serial port to connect. Needed for native USB port only
  }
  Serial.println("<ready>");
}

void loop(){
  getDataFromPC();

  if (build_connection) {
    Serial.println("<ready>");
    if (readInProgress) {
      build_connection = false;
    }
  }

  // if (num_sensors_set) {
  //   Serial.print("<Num Sensors ");
  //   Serial.print(num_sensors);
  //   Serial.println(">");
  // }
  // if (pins_set) {
  //   Serial.print("<Pins ");
  //   for(int i=0;i<num_sensors;i++) {
  //     Serial.print(gsr_pins[i]);
  //     Serial.print(" ");
  //   }
  //   Serial.println(">");
  // }

  if (measure) {
    for(int sensor=0;sensor<num_sensors;sensor++) {
      long sum=0;
      for(int i=0;i<10;i++)           //Average the 10 measurements to remove the glitch
          {
          sensorValue=analogRead(gsr_pins[sensor]);
          sum += sensorValue;
          delay(5);
          }
      gsr_average = sum/10;
      Serial.print("<Sensor,");
      Serial.print(sensor);
      Serial.print(",");
      Serial.print(gsr_average);
      Serial.println(">");
    }
    
  }

  delay(100);
  

  // <NumSensors,2>
  // <Pins,A0,A2>


  
}