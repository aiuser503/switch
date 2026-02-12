import os
import time
import re
import pandas as pd

ABSENT_CSV = os.path.join("attendance", "absent_today.csv")


def normalize_phone(phone):
    digits = re.sub(r"\D", "", str(phone))
    return digits


def send_with_pywhatkit(phone, message, wait_time=20, close_time=5):
    try:
        import pywhatkit
    except Exception as exc:
        raise RuntimeError("pywhatkit is not installed") from exc

    # pywhatkit expects country code included
    pywhatkit.sendwhatmsg_instantly(
        phone_no=f"+{phone}",
        message=message,
        wait_time=wait_time,
        tab_close=True,
        close_time=close_time,
    )


def main():
    if not os.path.isfile(ABSENT_CSV):
        print("No absent list found. Run recognize_attendance.py first.")
        return

    df = pd.read_csv(ABSENT_CSV)
    if df.empty:
        print("No absentees today.")
        return

    dry_run = os.getenv("DRY_RUN") == "1"

    for _, row in df.iterrows():
        roll = str(row.get("Roll", "")).strip()
        name = str(row.get("Name", "")).strip()
        phone = normalize_phone(row.get("ParentPhone", ""))
        if not phone:
            print(f"Missing ParentPhone for roll {roll}, skipping")
            continue

        message = f"Attendance Alert: {name} (Roll {roll}) was marked absent today."

        if dry_run:
            print(f"DRY_RUN -> +{phone} | {message}")
            continue

        print(f"Sending to +{phone}...")
        send_with_pywhatkit(phone, message)
        # Small delay between messages to avoid rate limits
        time.sleep(3)


if __name__ == "__main__":
    main()
