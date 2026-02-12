import os
import cv2

def main():
    name = input("Enter student name: ").strip()
    if not name:
        print("Name is required.")
        return

    out_dir = os.path.join("data", "students", name)
    os.makedirs(out_dir, exist_ok=True)

    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("Could not open webcam.")
        return

    count = 0
    target = 20

    print("Press 's' to save a frame. Press 'q' to quit.")
    while True:
        ret, frame = cam.read()
        if not ret:
            break

        cv2.imshow("Capture Face", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("s"):
            filename = os.path.join(out_dir, f"{count}.jpg")
            cv2.imwrite(filename, frame)
            count += 1
            print(f"Saved {filename}")
            if count >= target:
                break
        elif key == ord("q"):
            break

    cam.release()
    cv2.destroyAllWindows()
    print(f"Captured {count} images for {name}.")

if __name__ == "__main__":
    main()
