import cv2
import mediapipe as mp
import serial
import time

# === Comunicação Serial ===
arduino = serial.Serial('COM3', 9600)
time.sleep(2)

# === MediaPipe ===
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.8
)

tips = [4, 8, 12, 16, 20]

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

ultimo_gesto = None

def detectar_gesto(landmarks):
    dedos = []
    if landmarks[tips[0]].x < landmarks[tips[0] - 1].x:
        dedos.append(1)
    else:
        dedos.append(0)

    for id in range(1, 5):
        dedos.append(1 if landmarks[tips[id]].y < landmarks[tips[id] - 2].y else 0)

    total = sum(dedos)
    if total == 0:
        return "punho"
    elif total == 1:
        return "joinha"
    elif total == 2:
        return "paz"
    elif total == 3:
        return "tres"
    elif total == 5:
        return "aberta"
    else:
        return "desconhecido"

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    # Converte para RGB apenas quando necessário
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    gesto = "Nenhum"

    if result.multi_hand_landmarks:
        hand_landmarks = result.multi_hand_landmarks[0]
        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        gesto = detectar_gesto(hand_landmarks.landmark)

        # Envia apenas se mudar
        if gesto != ultimo_gesto:
            arduino.write((gesto + "\n").encode())
            ultimo_gesto = gesto

    cv2.putText(frame, f"Gesto: {gesto}", (30, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

    cv2.imshow("Reconhecimento de Gestos", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
arduino.close()
