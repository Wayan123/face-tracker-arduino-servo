# face-tracker-arduino-servo
This project is designed for the purpose of tracking a person's face using the cvzone library, which is developed from the mediapipe library. To ensure the accuracy of the coordinate positions, a Proportional Integral Derivative (PID) algorithm is added. As for the Arduino code, PID is also used to control the servos more accurately and is combined with an exponential filter. This filter smooths the position data before it is applied to the servos. FilteredX and filteredY are the filtered positions.

![gambar1](https://github.com/Wayan123/face-tracker-arduino-servo/assets/17795544/1252a8e6-3905-467f-bc6b-8f95b25274a4)
