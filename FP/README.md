Final Project README

Make sure that the 
bbcar.cpp, bbcar.h, bbacr_rpc.cpp, bbcar_rpc.h,
parallax_encoder.cpp, parallax_encoder.h 
has been replaced from the 'car' folder.

main.cpp is the main program in mbed.
car_control.py is for communication with the car
using Xbee.
final.py is for the OpenMV.

To setup the program,
flash the main.cpp to the mbed and final.py to the 
OpenMV. 
Make sure that Xbees are connected properly 
one to a laptop and one on the car.

Next, user should run car_control.py by using
sudo python3 car_control.py /dev/ttyUSB*
where * represents the ttyUSB number.

Then, user should press f and the car will start detecting
the available AprilTag and it will make
itself perpendicular with the apriltag.
After detecting the available Apriltag,
the car will go closer to it until their distance is 40cm (measured by PING)
When it is perpendicular, LED2  on mbed will be turned on and the car.
After few seconds, the car 
will start detecting a line and follow it.

