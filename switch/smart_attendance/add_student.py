import csv
import os
from pathlib import Path

STUDENTS_PATH = Path("data") / "students.csv"
DATA_DIR = Path("data") / "students"


def main():
    roll = input("Roll number: ").strip()
    name = input("Student name: ").strip()
    phone = input("Parent phone (with country code): ").strip()

    if not roll or not name or not phone:
        print("Roll, Name, and Parent phone are required.")
        return

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / roll).mkdir(parents=True, exist_ok=True)

    STUDENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not STUDENTS_PATH.exists():
        with open(STUDENTS_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["Roll", "Name", "ParentPhone"])
            writer.writeheader()

    # Check for duplicates
    rows = []
    with open(STUDENTS_PATH, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
            if row.get("Roll") == roll:
                print(f"Roll {roll} already exists. Update the row manually in {STUDENTS_PATH}.")
                return

    with open(STUDENTS_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Roll", "Name", "ParentPhone"])
        writer.writerow({"Roll": roll, "Name": name, "ParentPhone": phone})

    print(f"Added {name} (Roll {roll}). Place images in {DATA_DIR / roll}.")


if __name__ == "__main__":
    main()
