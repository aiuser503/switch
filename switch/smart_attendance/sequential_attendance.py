import os
import time
from datetime import datetime
from pathlib import Path

import cv2
import face_recognition
import pandas as pd

MODEL_PATH = Path("models") / "face_model.pkl"
STUDENTS_PATH = Path("data") / "students.csv"
ATTENDANCE_STATUS = Path("attendance") / "attendance_status.csv"


def load_model():
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}. Run train_model.py first.")
    data = pd.read_pickle(MODEL_PATH)
    return data["encodings"], data["names"]


def load_students_in_order():
    if not STUDENTS_PATH.is_file():
        raise FileNotFoundError(f"Missing {STUDENTS_PATH}. Fill Roll,Name,ParentPhone.")
    df = pd.read_csv(STUDENTS_PATH)
    rows = []
    for _, row in df.iterrows():
        roll = str(row.get("Roll", "")).strip()
        name = str(row.get("Name", "")).strip()
        phone = str(row.get("ParentPhone", "")).strip()
        if roll:
            rows.append({"Roll": roll, "Name": name, "ParentPhone": phone})
    return rows


def send_whatsapp(phone, message, wait_time=20, close_time=5):
    import pywhatkit
    pywhatkit.sendwhatmsg_instantly(
        phone_no=f"+{phone}",
        message=message,
        wait_time=wait_time,
        tab_close=True,
        close_time=close_time,
    )


def main():
    encodings, names = load_model()
    students = load_students_in_order()

    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("Could not open webcam.")
        return

    os.makedirs(ATTENDANCE_STATUS.parent, exist_ok=True)
    write_header = not ATTENDANCE_STATUS.exists()

    dry_run = os.getenv("DRY_RUN") == "1"

    print("Sequential attendance starting.")
    print("Instructions: show one student at a time.")
    print("Press ENTER to move to next student, or wait 60 seconds.")
    print("Press 'q' to quit early.\n")

    results = []

    for idx, student in enumerate(students, start=1):
        roll = student["Roll"]
        name = student["Name"] or roll
        phone = student["ParentPhone"]

        start_time = time.time()
        matched = False

        while True:
            ret, frame = cam.read()
            if not ret:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb)
            face_encs = face_recognition.face_encodings(rgb, boxes)

            for (top, right, bottom, left), face in zip(boxes, face_encs):
                matches = face_recognition.compare_faces(encodings, face, tolerance=0.5)
                label = "Unknown"
                if True in matches:
                    label = names[matches.index(True)]

                color = (0, 255, 0) if label == roll else (0, 0, 255)
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(frame, label, (left, top - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                if label == roll:
                    matched = True

            elapsed = int(time.time() - start_time)
            remaining = max(0, 60 - elapsed)
            header = f"{idx}/{len(students)}  Roll: {roll}  Name: {name}  Time left: {remaining}s"
            cv2.putText(frame, header, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.imshow("Attendance", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                cam.release()
                cv2.destroyAllWindows()
                print("Stopped early by user.")
                pd.DataFrame(results).to_csv(ATTENDANCE_STATUS, mode="a", header=write_header, index=False)
                return
            if key == 13:  # Enter
                break
            if remaining <= 0:
                break
            if matched:
                break

        status = "Present" if matched else "Absent"
        now = datetime.now()
        results.append({
            "Roll": roll,
            "Name": name,
            "Status": status,
            "Date": now.strftime("%Y-%m-%d"),
            "Time": now.strftime("%H:%M:%S"),
        })

        if status == "Absent":
            if phone:
                message = f"Attendance Alert: {name} (Roll {roll}) was marked absent today."
                if dry_run:
                    print(f"DRY_RUN -> +{phone} | {message}")
                else:
                    print(f"Sending WhatsApp to +{phone}...")
                    send_whatsapp(phone, message)
                    time.sleep(3)
            else:
                print(f"Missing ParentPhone for roll {roll}, skipping message")

        print(f"{roll} - {name}: {status}")

    cam.release()
    cv2.destroyAllWindows()

    pd.DataFrame(results).to_csv(ATTENDANCE_STATUS, mode="a", header=write_header, index=False)
    print(f"Saved attendance to {ATTENDANCE_STATUS}")


if __name__ == "__main__":
    main()
