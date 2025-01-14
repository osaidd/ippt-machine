import cv2
import mediapipe as mp
import numpy as np
import math

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def calculate_angle(a,b,c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)

    if angle > 180.0:
        angle = 360.0 - angle
    return angle

#Method to check if ear is close to the wrist
def isEarTouching(rEar, wrist, lEar):
    R_is_x_close = math.isclose(rEar[0],wrist[0],rel_tol=.4)
    R_is_y_close = math.isclose(rEar[1],wrist[1],rel_tol=.4)
    L_is_x_close = math.isclose(lEar[0],wrist[0],rel_tol=.4)
    L_is_y_close = math.isclose(lEar[1],wrist[1],rel_tol=.4)
    
    #remeber to account for either right or left ear
    if R_is_x_close == True and R_is_y_close == True:
        print(True)
        return True
    elif L_is_x_close == True and L_is_y_close == True:
        print(True)
        return True
    else: 
        print(False)
        return False

stage = None
counter = 0
angle2 = 0
touching = False
earMessage = ""
# Video Feed
# Define the codec and create VideoWriter object
out = cv2.VideoWriter('output.avi', -1, 20.0, (640,480))
cap = cv2.VideoCapture(0)
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()

        #Recolour image
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        # Make detection
        results = pose.process(image)

        #Recolour back to RGB
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Extract landmarks
        try:
            landmarks = results.pose_landmarks.landmark

            # Get coordinates
            shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                        landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
            wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                        landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
            hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                     landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
            knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                     landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
            rEar = [landmarks[8].x,
                     landmarks[8].y]
            lEar = [landmarks[7].x,
                     landmarks[7].y]
            
            #Check if wrists are close to either ear
            touching = isEarTouching(rEar,wrist, lEar)

            # Calculate angle
            angle = calculate_angle(shoulder, elbow, wrist)
            angle2 = calculate_angle(shoulder, hip, knee)
            # print(angle)
            # print(tuple(np.multiply(elbow, [1280, 720]).astype(int)))
            #Visualize
            # cv2.putText(image, str(round(angle, 3)), tuple(np.multiply(elbow, [int(cap.get(3)), int(cap.get(4))]).astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2, cv2.LINE_AA)
            cv2.putText(image, str(round(angle2, 3)),
                        tuple(np.multiply(hip, [int(cap.get(3)), int(cap.get(4))]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
            print(angle)
            if angle2 > 100:
                stage = "up"
            if touching == False:
                earMessage = "Cup your ears"
            if touching == True:
                earMessage = ""
            if angle2 < 45 and stage == "up" and touching == True:
                earMessage = ""
                stage = "down"
                counter += 1

        except:
            pass
        #Render curl rectangle
        cv2.rectangle(image, (0,0), (225, 85), (143, 224, 120), -1)
        cv2.putText(image, "REPS", (15, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
        cv2.putText(image, str(counter), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 1, cv2.LINE_AA)
        #Show cup ears message if it needs to be shown 
        cv2.putText(image, earMessage, (100, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (30, 30, 255), 1, cv2.LINE_AA)
        if angle2 > 45 and stage == "up":
            cv2.putText(image, "GO HIGHER", (15, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        else:
            cv2.putText(image, "MAINTAIN FORM", (15, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1,
                        cv2.LINE_AA)



        # Render detections rgb(248, 194, 145)
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                  mp_drawing.DrawingSpec(color=(38,145,229), thickness=2, circle_radius=2),
                                  mp_drawing.DrawingSpec(color=(145, 194, 248), thickness=2, circle_radius=2)
                                  )

        out.write(image)
        cv2.imshow("IPPT Tracker", image)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

cap.release()
out.release()
cv2.destroyAllWindows()





