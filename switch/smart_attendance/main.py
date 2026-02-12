import subprocess
import sys


def run(cmd):
    print(f"\n> {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        sys.exit(result.returncode)


def main():
    run("python train_model.py")
    run("python recognize_attendance.py")
    # Optional: run notifications after attendance
    # run("python notify_parents.py")


if __name__ == "__main__":
    main()
