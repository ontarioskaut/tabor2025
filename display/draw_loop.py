import os
import time

from PIL import Image

from display.engine_loader import load_display_engines
from routes.api_display import get_announcements, get_time_data


def run_loop(stop_event, config):
    displays = load_display_engines()

    state_dir = getattr(config, "DISPLAY_STATE_DIR", "display_state")
    os.makedirs(state_dir, exist_ok=True)

    screen_duration = getattr(config, "DISPLAY_TIME_SCREEN_DURATION", 5)
    cycles_until_announcement = getattr(
        config, "DISPLAY_ANNOUNCEMENT_AFTER_N_CYCLES", 2
    )
    announcement_duration = getattr(config, "DISPLAY_ANNOUNCEMENT_DURATION", 3)

    last_index = 0
    completed_cycles = 0

    while not stop_event.is_set():
        print("[Check loop]", config.SYSTEM_ACTIVE)

        if not config.SYSTEM_ACTIVE:
            print("not condition passed")
            for display in displays:
                engine = display["engine_instance"]
                name = display["name"]

                engine.draw_announcement(getattr(config, "INACTIVE_ANNOUNCEMENT", ""))

                file_png = os.path.join(state_dir, f"{name}_current.png")
                engine.get_bitmap(file_png)

                file_dis = os.path.join(state_dir, f"{name}_current.dis")
                with open(file_dis, "w") as f:
                    f.write(engine.get_data_frame())

                print(f"[Inactive] Updated {file_png} and {file_dis}")

            if stop_event.wait(screen_duration):
                return
            continue

        if completed_cycles >= cycles_until_announcement:
            completed_cycles = 0
            announcements = get_announcements()

            if announcements:
                announcements = sorted(
                    announcements,
                    key=lambda x: x["order"] if x["order"] is not None else 9999,
                )

                announcements_by_display = {}
                for ann in announcements:
                    if not ann.get("visible", True):
                        continue
                    name = ann["for_display"]
                    announcements_by_display.setdefault(name, []).append(ann)

                max_pairs = max(
                    (len(v) for v in announcements_by_display.values()), default=0
                )

                # show announcements pair-by-pair
                for i in range(max_pairs):
                    for _ in range(announcement_duration):
                        for display in displays:
                            engine = display["engine_instance"]
                            name = display["name"]

                            ann_list = announcements_by_display.get(name, [])
                            ann = ann_list[i] if i < len(ann_list) else None

                            if ann:
                                engine.draw_announcement(ann["data"])
                            else:
                                engine.clear()

                            # Save outputs
                            file_png = os.path.join(state_dir, f"{name}_current.png")
                            engine.get_bitmap(file_png)

                            file_dis = os.path.join(state_dir, f"{name}_current.dis")
                            with open(file_dis, "w") as f:
                                f.write(engine.get_data_frame())

                        if stop_event.wait(1):
                            return

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

        if last_index >= len(time_list):
            last_index = 0
            completed_cycles += 1

        page = time_list[last_index : last_index + total_slots]

        last_index += total_slots
        if last_index >= len(time_list):
            completed_cycles += 1
            last_index = 0

        if not page:
            continue

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

        stop_event.wait(screen_duration)


def run_format_loop(stop_event):
    """
    Draws periodically full black or white to format flip-dot displays
    """
    displays = load_display_engines()

    state_dir = getattr(config, "DISPLAY_STATE_DIR", "display_state")
    os.makedirs(state_dir, exist_ok=True)

    screen_duration = getattr(config, "DISPLAY_FORMAT_SCREEN_DURATION", 2)

    def _fill_engine(engine, white: bool):
        buf = engine.display_buffer
        mode = buf.mode
        size = buf.size

        if mode == "RGB":
            color = (255, 255, 255) if white else (0, 0, 0)
        elif mode in ("1", "L"):
            color = 255 if white else 0
        else:
            mode = "L"
            color = 255 if white else 0

        engine.display_buffer = Image.new(mode, size, color)

    while not stop_event.is_set():
        # White
        for display in displays:
            engine = display["engine_instance"]
            _fill_engine(engine, white=True)

            file_png = os.path.join(state_dir, f"{display['name']}_current.png")
            engine.get_bitmap(file_png)

            file_dis = os.path.join(state_dir, f"{display['name']}_current.dis")
            with open(file_dis, "w") as f:
                f.write(engine.get_data_frame())

            print(f"[Format Loop] WHITE -> {file_png} , {file_dis}")

        if stop_event.wait(screen_duration):
            return

        # Black
        for display in displays:
            engine = display["engine_instance"]
            _fill_engine(engine, white=False)

            file_png = os.path.join(state_dir, f"{display['name']}_current.png")
            engine.get_bitmap(file_png)

            file_dis = os.path.join(state_dir, f"{display['name']}_current.dis")
            with open(file_dis, "w") as f:
                f.write(engine.get_data_frame())

            print(f"[Format Loop] BLACK -> {file_png} , {file_dis}")

        if stop_event.wait(screen_duration):
            return
