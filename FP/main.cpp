#include "mbed.h"
#include "bbcar.h"
#include "bbcar_rpc.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>

Ticker servo_ticker;
Ticker en_ticker;
Ticker display_ticker;
DigitalIn encoder_in(D6);
PwmOut pind10(D10), pin11(D11);

BufferedSerial xbee(A1, A0);
DigitalInOut PING(D12);
BufferedSerial PC_OPENCV(USBTX,USBRX); //tx,rx
BufferedSerial UART_OPENCV(D1,D0); //tx,rx

parallax_ping  ping1(PING);
DigitalOut led1(LED1);
DigitalOut led2(LED2);
//parallax_encoder ENCODER( DigitalIn& input, Ticker &encoder_ticker );

EventQueue queueAT(32 * EVENTS_EVENT_SIZE);
Thread threadAT;

//BBCar car(pind10, pin11, servo_ticker);
BBCar car(pind10, pin11, servo_ticker, encoder_in, en_ticker);

int CAR_DIRECTION;
int DISTANCE_X;
int DISTANCE_Y;



volatile int steps;
volatile int last;


void encoder_control() {
   int value = encoder_in;
   if (!last && value) steps++;
   last = value;
}

void display()
{
   printf("steps: %d\r\n",steps);
}
//int FINISH=0;


int main() {
   
   char buf[256], outbuf[256];
   FILE *devin = fdopen(&xbee, "r");
   FILE *devout = fdopen(&xbee, "w");
   //en_ticker.attach(&encoder_control, .01);
   //display_ticker.attach(queue.event(&display),500ms);
   while (1) {

      memset(buf, 0, 256);
      for( int i = 0; ; i++ ) {
         char recv = fgetc(devin);
         if(recv == '\n') {
            printf("\r\n");
            break;
         }
         buf[i] = fputc(recv, devout);
      }
   RPC::call(buf, outbuf);
   }
}

/*
int ACC=0;

int DISTANCE_AT()
{
   //EventQueue queue;
   //queue.call_every(1s,printf,"PINGI: %1.2f \n\r",(float)ping1); 
   while(1) {
       ThisThread:: sleep_for(10s);
       printf("DISTANCE : %1.2f\r\n",(float)ping1);

   }
   
   return 1;
}
*/
/*//THIS IS THE ONE
int main()
{
   // threadAT.start(callback(&queueAT, &EventQueue::dispatch_forever));
   // queueAT.call(DISTANCE_AT);
    
    printf("ENTER\r\n");

    UART_OPENCV.set_baud(9600);
    float angle;
    char buff[5];
    int i=0;
    
   //UART_OPENCV.printf("FINISH");
   //char mes[1]={'2'};
   /*
   while(1){
      UART_OPENCV.write(mes,1);
      PC_OPENCV.write(mes,1);
      printf("write\r\n");
   }
     */ 
   //printf("distance: %1.2f\r\n",(float)ping1);
   
   /*
   while((float)ping1>30){
         
         car.goStraight(50);
         printf("distance: %1.2f\r\n",(float)ping1);
      

   }*/
  //car.stop(); 
  
  //car.stop();
  // char finish[7]="FINISH";
  // int num = sizeof(finish);
   //uint32_t num = serial_port.read(finish, sizeof(finish);
  // UART_OPENCV.write(finish,num);

/*   // THIS IS THE ONE
   while(1){
      
      if(UART_OPENCV.readable()){
            
            //printf("ENTER 1\r\n");
            char recv[1];
            UART_OPENCV.read(recv, sizeof(recv));
            buff[i++]=recv[0];

            if(recv[0] == '\n'){
                angle = atof(buff);
                i=0; 
                //printf("%s\n",buff);
                //printf("len:%d\r\n",strlen(buff));
                if(angle!=1000)printf("Angle: %1.2f\r\n",angle);
                //else printf("STOP\r\n");
            }

         if(angle <= -0.1){
            car.turn(30,-0.4); //turning right
            printf("A RIGHT\r\n");
            FINISH=0;
         }  
         else if(angle>=0.1 && angle!= 1000 && angle!=2000
                 && angle!= 1500 )
         {
            car.turn(40,0.4);
            printf("A LEFT\r\n"); //turning left
            FINISH=0; 
         }  
         else if(angle==1000){
            car.stop();
         }
         else if(angle==1500){
            car.stop();
            led2=1;
            printf("LAST LOOP\r\n"); 
            break;
         }
         else{//angle =2000
            printf("A Finish");
            FINISH++;
            if(FINISH<=3)
               car.stop();
         }
        
      }
      
    }
    printf("distance: %1.2f\r\n",(float)ping1);
   int LINE=0;
   while(1)
   {
      if(LINE==1)
         led2=0;
      if(UART_OPENCV.readable()){
            if(LINE==0) LINE++;
            //printf("ENTER 1\r\n");
            char recv[1];
            UART_OPENCV.read(recv, sizeof(recv));
            buff[i++]=recv[0];

            if(recv[0] == '\n'){
                angle = atof(buff);
                i=0; 
                //printf("%s\n",buff);
                //printf("len:%d\r\n",strlen(buff));
                if(angle!=1000)printf("Angle: %1.2f\r\n",angle);
                //else printf("STOP\r\n");
            }

         if(angle <= 14){
            car.turn(80,0.4); //turning right, adjust
            printf("RIGHT\r\n");
         }  
         else if(angle>38 && angle!=1000){
            car.turn(70,-0.4);
            printf("LEFT\r\n"); //turning left 
         }  
         else if(angle==1000){
            car.stop();

         }
         else{//angle =2000
            car.goStraight(40);
         }
        
      }
   }
}

//*/