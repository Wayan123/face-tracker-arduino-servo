import cvzone
import cv2
import numpy as np
import time
import serial
from cvzone.FaceDetectionModule import FaceDetector

class PID:
    def __init__(self, pidVals, targetVal, axis=0, limit=None):
        self.pidVals = pidVals
        self.targetVal = targetVal
        self.axis = axis
        self.pError = 0
        self.limit = limit
        self.I = 0
        self.pTime = time.time()

    def update(self, cVal):
        # Current Value - Target Value
        t = time.time() - self.pTime
        error = cVal - self.targetVal
        P = self.pidVals[0] * error
        self.I = self.I + (self.pidVals[1] * error * t)
        D = (self.pidVals[2] * (error - self.pError)) / t

        result = P + self.I + D

        if self.limit is not None:
            result = float(np.clip(result, self.limit[0], self.limit[1]))
        self.pError = error
        self.pTime = time.time()

        return result

def main():
    cap = cv2.VideoCapture(1)
    detector = FaceDetector(minDetectionCon=0.8)
    
    xPID = PID([0.1, 0.0001, 0.01], 640 // 2, limit=[-90, 90])
    yPID = PID([0.1, 0.0001, 0.01], 480 // 2, axis=1, limit=[-90, 90])
    
    ser = serial.Serial('COM4', 115200)  # Update COM port as necessary

    while True:
        success, img = cap.read()
        ws, hs = img.shape[1], img.shape[0]
        img, bboxs = detector.findFaces(img)
        if bboxs:
            x, y, w, h = bboxs[0]["bbox"]
            cx, cy = bboxs[0]["center"]
            xVal = int(xPID.update(cx))
            yVal = int(yPID.update(cy))

            # Menggambar mode fokus
            cv2.circle(img, (cx, cy), 80, (0, 0, 255), 2)
            cv2.putText(img, f'{cx},{cy}', (cx + 15, cy - 15), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
            cv2.line(img, (0, cy), (ws, cy), (0, 0, 0), 2)  # x line
            cv2.line(img, (cx, hs), (cx, 0), (0, 0, 0), 2)  # y line
            cv2.circle(img, (cx, cy), 15, (0, 0, 255), cv2.FILLED)
            cv2.putText(img, "TARGET LOCKED", (850, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

            ser.write(f"{xVal},{yVal}\n".encode())
        else:
            # Mengatur titik merah kembali ke pusat
            center_x, center_y = ws // 2, hs // 2
            xVal = int(xPID.update(center_x))
            yVal = int(yPID.update(center_y))

            cv2.putText(img, "NO TARGET", (880, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)
            cv2.circle(img, (center_x, center_y), 80, (0, 0, 255), 2)
            cv2.circle(img, (center_x, center_y), 15, (0, 0, 255), cv2.FILLED)
            cv2.line(img, (0, center_y), (ws, center_y), (0, 0, 0), 2)  # x line
            cv2.line(img, (center_x, hs), (center_x, 0), (0, 0, 0), 2)  # y line

        cv2.putText(img, f'Servo X: {xVal} deg', (50, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
        cv2.putText(img, f'Servo Y: {yVal} deg', (50, 100), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    ser.close()

if __name__ == "__main__":
    main()
