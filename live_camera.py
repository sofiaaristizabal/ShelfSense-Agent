import cv2
from ultralytics import YOLO
from collections import Counter

# Cargar el modelo entrenado
model = YOLO("best.pt")  # Asegúrate de que best.pt esté en la misma carpeta

# Iniciar cámara
video_capture = cv2.VideoCapture(0)

while True:
    ret, frame = video_capture.read()
    if not ret:
        break

    try:
        # Ejecutar inferencia sobre el frame actual
        results = model(frame, verbose=False)

        # Dibujar las detecciones sobre el frame (recuadros normales de YOLO)
        annotated_frame = results[0].plot()

        # --- Conteo de objetos detectados por clase ---
        boxes = results[0].boxes
        class_ids = boxes.cls.tolist() if boxes is not None and len(boxes) > 0 else []
        class_names = model.names  # dict {id: nombre}
        conteo = Counter(class_ids)

        # --- Dibujar el conteo como texto en la esquina superior izquierda ---
        y_offset = 30
        total = 0
        for class_id, cantidad in conteo.items():
            nombre = class_names[int(class_id)]
            texto = f"{nombre}: {int(cantidad)}"
            cv2.putText(
                annotated_frame, texto, (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA
            )
            y_offset += 30
            total += cantidad

        cv2.putText(
            annotated_frame, f"Total: {int(total)}", (10, y_offset),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA
        )

        cv2.imshow("Deteccion de Objetos", annotated_frame)

    except Exception as e:
        print("ERROR en el loop:", repr(e))
        # seguimos mostrando el frame sin anotaciones para no crashear
        cv2.imshow("Deteccion de Objetos", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # Detener con Esc
        break

video_capture.release()
cv2.destroyAllWindows()