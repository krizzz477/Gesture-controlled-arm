import cv2
import mediapipe as mp
import serial
import time
import math

# Serial setup
ser = serial.Serial('COM4', 9600)
time.sleep(2)

# Mediapipe hands
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1)
mpDraw = mp.solutions.drawing_utils

# Camera
cap = cv2.VideoCapture(0)

# Track previous command to avoid overlap
prev_cmd = ""

def send_cmd(cmd):
    global prev_cmd
    if cmd != prev_cmd:
        print("Sending:", cmd)
        ser.write((cmd + "\n").encode())
        prev_cmd = cmd

def distance(p1, p2):
    return math.hypot(p2.x - p1.x, p2.y - p1.y)

while True:
    success, img = cap.read()
    if not success:
        break

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            lm = handLms.landmark

            # Fingers state
            finger_open = [lm[8].y < lm[6].y,  # index
                           lm[12].y < lm[10].y, # middle
                           lm[16].y < lm[14].y, # ring
                           lm[20].y < lm[18].y] # pinky
            open_count = sum(finger_open)

            # Palm vs close (claw control)
            if open_count >= 3:
                send_cmd("claw_open")
            else:
                send_cmd("claw_close")

            # Base control by x movement
            x_pos = lm[0].x
            if x_pos < 0.4:
                send_cmd("base_left")
            elif x_pos > 0.6:
                send_cmd("base_right")

            # Forward/backward by hand-z (depth)
            z_pos = lm[0].z
            if z_pos < -0.15:  # closer
                send_cmd("arm_forward")
            elif z_pos > 0.15:  # farther
                send_cmd("arm_backward")

            # Two-finger reset
            if finger_open[0] and finger_open[1] and not finger_open[2] and not finger_open[3]:
                send_cmd("base_reset")

            # Index finger up/down for arm lift
            if finger_open[0] and not any(finger_open[1:]):
                if lm[8].y < lm[7].y:  # lifted
                    send_cmd("arm_up")
                else:  # declined
                    send_cmd("arm_down")

            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

    cv2.imshow("Gesture Arm Control", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
ser.close()
cv2.destroyAllWindows()
