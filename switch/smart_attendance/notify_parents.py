import os
import smtplib
import pandas as pd

PARENTS_PATH = os.path.join("data", "parents.csv")
ABSENT_PATH = os.path.join("attendance", "absent_today.txt")


def load_absent():
    if not os.path.isfile(ABSENT_PATH):
        return []
    with open(ABSENT_PATH, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def load_parents():
    if not os.path.isfile(PARENTS_PATH):
        print(f"Missing {PARENTS_PATH}. Create it first.")
        return {}
    df = pd.read_csv(PARENTS_PATH)
    mapping = {}
    for _, row in df.iterrows():
        name = str(row.get("Name", "")).strip()
        email = str(row.get("ParentEmail", "")).strip()
        if name and email:
            mapping[name] = email
    return mapping


def send_email(to_email, subject, message):
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")

    if not (host and user and password):
        raise RuntimeError("Missing SMTP_* environment variables")

    msg = f"Subject: {subject}\n\n{message}"

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.sendmail(user, to_email, msg)


def main():
    absent = load_absent()
    if not absent:
        print("No absent list found. Run recognize_attendance.py first.")
        return

    parents = load_parents()
    if not parents:
        return

    dry_run = os.getenv("DRY_RUN") == "1"

    for student in absent:
        email = parents.get(student)
        if not email:
            print(f"No parent email for {student}, skipping")
            continue

        subject = "Attendance Alert"
        message = f"Your child {student} was marked absent today."

        if dry_run:
            print(f"DRY_RUN -> To: {email} | {message}")
        else:
            send_email(email, subject, message)
            print(f"Sent to {email}")


if __name__ == "__main__":
    main()
