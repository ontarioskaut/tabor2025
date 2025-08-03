import os
import time

import config
from display.engine_loader import load_display_engines
from routes.api_display import get_time_data


def run_loop(stop_event):
    displays = load_display_engines()

    state_dir = getattr(config, "DISPLAY_STATE_DIR", "display_state")
    os.makedirs(state_dir, exist_ok=True)

    screen_duration = getattr(config, "DISPLAY_TIME_SCREEN_DURATION", 5)

    last_index = 0

    while not stop_event.is_set():
        times = get_time_data()  # dict {acro: seconds}

        if not times:
            print("[Draw Loop] No times to display")
            stop_event.wait(screen_duration)
            continue

        time_list = []
        for acro, sec in times.items():
            if sec < 0:
                sec = 0
            time_list.append({acro: sec})

        total_slots = sum(d["engine_instance"].fit_times for d in displays)

        page = time_list[last_index : last_index + total_slots]
        if not page:  # wrap if needed
            last_index = 0
            page = time_list[:total_slots]

        slot_offset = 0
        for display in displays:
            engine = display["engine_instance"]
            fit = engine.fit_times

            slice_data = page[slot_offset : slot_offset + fit]
            slot_offset += fit

            ok = engine.draw_time(slice_data)
            if not ok:
                print(f"Error: Too many times for {display['name']}")
                continue

            file_png = os.path.join(state_dir, f"{display['name']}_current.png")
            engine.get_bitmap(file_png)

            file_dis = os.path.join(state_dir, f"{display['name']}_current.dis")
            with open(file_dis, "w") as f:
                f.write(engine.get_data_frame())

            print(f"[Draw Loop] Updated {file_png} and {file_dis}")

        last_index = (last_index + total_slots) % len(time_list)

        stop_event.wait(screen_duration)
