import os
from pathlib import Path
import pickle
from datetime import datetime

import cv2
import face_recognition
import pandas as pd

MODEL_PATH = os.path.join("models", "face_model.pkl")
ATTENDANCE_PATH = os.path.join("attendance", "attendance.csv")
DATA_DIR = Path("data") / "students"
STUDENTS_PATH = Path("data") / "students.csv"


def load_model():
    if not os.path.isfile(MODEL_PATH):
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}. Run train_model.py first.")
    with open(MODEL_PATH, "rb") as f:
        data = pickle.load(f)
    return data["encodings"], data["names"]


def mark_attendance(present_names):
    os.makedirs(os.path.dirname(ATTENDANCE_PATH), exist_ok=True)
    now = datetime.now()
    rows = []
    for name in sorted(present_names):
        rows.append({
            "Roll": name,
            "Date": now.strftime("%Y-%m-%d"),
            "Time": now.strftime("%H:%M:%S"),
        })

    if rows:
        df = pd.DataFrame(rows)
        write_header = not os.path.isfile(ATTENDANCE_PATH)
        df.to_csv(ATTENDANCE_PATH, mode="a", header=write_header, index=False)


def main():
    encodings, names = load_model()

    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("Could not open webcam.")
        return

    present = set()
    print("Press 'q' to stop and save attendance.")

    while True:
        ret, frame = cam.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb)
        face_encs = face_recognition.face_encodings(rgb, boxes)

        for (top, right, bottom, left), face in zip(boxes, face_encs):
            matches = face_recognition.compare_faces(encodings, face, tolerance=0.5)
            name = "Unknown"
            if True in matches:
                idx = matches.index(True)
                name = names[idx]
                present.add(name)

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.imshow("Attendance", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cam.release()
    cv2.destroyAllWindows()

    mark_attendance(present)

    students = {}
    if STUDENTS_PATH.is_file():
        df = pd.read_csv(STUDENTS_PATH)
        for _, row in df.iterrows():
            roll = str(row.get("Roll", "")).strip()
            name = str(row.get("Name", "")).strip()
            phone = str(row.get("ParentPhone", "")).strip()
            if roll:
                students[roll] = {"Name": name, "ParentPhone": phone}

    all_students = set()
    if DATA_DIR.is_dir():
        subdirs = [p for p in DATA_DIR.iterdir() if p.is_dir()]
        if subdirs:
            all_students = {p.name for p in subdirs}
        else:
            all_students = {p.stem for p in DATA_DIR.iterdir() if p.is_file()}
    absent = sorted(all_students - present)

    print(f"Present (rolls): {sorted(present)}")
    print(f"Absent (rolls): {absent}")

    # Write absent list for notify_parents.py
    absent_path = os.path.join("attendance", "absent_today.txt")
    with open(absent_path, "w", encoding="utf-8") as f:
        for name in absent:
            f.write(name + "\n")

    # Write absent details for WhatsApp
    absent_csv = os.path.join("attendance", "absent_today.csv")
    rows = []
    for roll in absent:
        meta = students.get(roll, {})
        rows.append({
            "Roll": roll,
            "Name": meta.get("Name", ""),
            "ParentPhone": meta.get("ParentPhone", ""),
        })
    pd.DataFrame(rows).to_csv(absent_csv, index=False)


if __name__ == "__main__":
    main()
