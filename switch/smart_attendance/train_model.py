import pickle
from pathlib import Path

import face_recognition
import pandas as pd

DATA_DIR = Path("data") / "students"
MODEL_PATH = Path("models") / "face_model.pkl"
STUDENTS_PATH = Path("data") / "students.csv"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp"}


def load_students():
    if not STUDENTS_PATH.is_file():
        return {}
    df = pd.read_csv(STUDENTS_PATH)
    mapping = {}
    for _, row in df.iterrows():
        roll = str(row.get("Roll", "")).strip()
        name = str(row.get("Name", "")).strip()
        if roll:
            mapping[roll.lower()] = roll
            if name:
                mapping[name.lower()] = roll
    return mapping


def iter_dataset():
    if not DATA_DIR.is_dir():
        return []

    items = []
    subdirs = [p for p in DATA_DIR.iterdir() if p.is_dir()]
    if subdirs:
        # Structure: data/students/ROLL/*.jpg
        for student_dir in sorted(subdirs):
            for img_path in sorted(student_dir.iterdir()):
                if img_path.suffix.lower() in IMAGE_EXTS:
                    items.append((student_dir.name, img_path))
        return items

    # Flat structure: data/students/ROLL.jpg
    for img_path in sorted(DATA_DIR.iterdir()):
        if img_path.is_file() and img_path.suffix.lower() in IMAGE_EXTS:
            items.append((img_path.stem, img_path))
    return items


def main():
    items = iter_dataset()
    if not items:
        print(f"Missing or empty dataset folder: {DATA_DIR}")
        return

    student_map = load_students()
    encodings = []
    names = []
    skipped = 0

    for student, img_path in items:
        try:
            image = face_recognition.load_image_file(str(img_path))
            face_encs = face_recognition.face_encodings(image)
            if not face_encs:
                skipped += 1
                print(f"No face found in {img_path}, skipping")
                continue
            label = student_map.get(student.lower(), student)
            encodings.append(face_encs[0])
            names.append(label)
        except Exception as exc:
            skipped += 1
            print(f"Failed on {img_path}: {exc}")

    if not encodings:
        print("No encodings created. Add clear face images and retry.")
        return

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump({"encodings": encodings, "names": names}, f)

    print(f"Saved model with {len(encodings)} encodings to {MODEL_PATH}")
    if skipped:
        print(f"Skipped {skipped} images with no face or errors.")


if __name__ == "__main__":
    main()
