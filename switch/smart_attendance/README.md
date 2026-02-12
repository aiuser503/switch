# Smart Attendance (Face Recognition)

This project captures student faces, trains a face-encoding model, marks attendance from the webcam, and notifies parents of absences.

## Folder layout

- data/students/StudentName/*.jpg
- data/students.csv
- models/face_model.pkl
- attendance/attendance.csv

## Setup

```powershell
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
```

If `face-recognition` fails to install, install CMake/Visual Studio Build Tools and retry.

## 1) Add student details

Add students with unique roll number and parent phone:

```powershell
python add_student.py
```

This creates a folder for the roll number in `data/students/`.

## 2) Add student images

Create a folder per roll number inside `data/students/` and add clear face images:

```
data/students/101/1.jpg
```

You can also capture via webcam:

```powershell
python capture_faces.py
```

## 3) Train the model

```powershell
python train_model.py
```

## 4) Run attendance (live group)

```powershell
python recognize_attendance.py
```

Press `q` to stop. Attendance is appended to `attendance/attendance.csv`.

## 5) Notify parents (WhatsApp)

WhatsApp uses `data/students.csv` with `Roll,Name,ParentPhone` (include country code).

Then run:

```powershell
python notify_whatsapp.py
```

Set `DRY_RUN=1` to preview messages without sending.

## 6) Sequential attendance (one student at a time)

This mode follows the order in `data/students.csv`. The camera stays on for each student (up to 60 seconds). It marks Present if the correct face is detected, otherwise marks Absent and sends WhatsApp immediately.

```powershell
python sequential_attendance.py
```

Press Enter to move to the next student, or wait 60 seconds.
