#!/usr/bin/env python3
import os

from display.engine_loader import load_display_engines

sample_time_data = [
    {"A": 12345},  # 03:25:45
    {"C": 600007890},  # ~6944 days
    {"E": 4321},  # 01:12:01
    {"F": 6378},
]


def main():
    os.makedirs("test_imgs", exist_ok=True)

    displays = load_display_engines()

    for display in displays:
        engine = display["engine_instance"]

        print(f"=== Display: {display['name']} ===")

        ok = engine.draw_time(sample_time_data)
        if not ok:
            print(f"Error: Too many times for {display['name']}")
            continue

        frame_b64 = engine.get_data_frame()
        print(f"Base64 frame (first 60 chars): {frame_b64[:60]}...")

        file_name = f"test_imgs/{display['name']}_debug.png"
        engine.get_bitmap(file_name)
        print(f"Saved debug bitmap to {file_name}\n")


if __name__ == "__main__":
    main()
