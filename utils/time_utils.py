from datetime import datetime


def seconds_to_text(total_seconds: int):
    is_negative = total_seconds < 0
    abs_seconds = abs(total_seconds)

    hours = abs_seconds // 3600
    minutes = (abs_seconds % 3600) // 60
    seconds = abs_seconds % 60

    formatted_time = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
    return f"-{formatted_time}" if is_negative else formatted_time


def count_remaining_time(timestamp: str, offset: int):
    start_int = datetime.fromisoformat(timestamp)
    time_diff = (datetime.now() - start_int).total_seconds()
    return offset - round(time_diff)


def count_new_offset(old_offset: int, value: int, mode: str):
    print(old_offset, value, mode)
    if mode == "+":
        print("hehe")
        return old_offset + value
    elif mode == "-":
        return old_offset - value
    elif mode == "*":
        return int(old_offset * value)
    elif mode == "%":
        return int(old_offset * ((100 + value) / 100))
    elif mode == "h":
        return old_offset + value * 60 * 60
    elif mode == "d":
        return old_offset + value * 24 * 60 * 60
    elif mode == "s":
        return value
    # assert(false)
    return 0


def count_new_time(old_offset: int, start: str, value: int, symbol: str):
    rem_time = count_remaining_time(start, old_offset)
    base_offset = old_offset - rem_time

    return base_offset + count_new_offset(rem_time, value, symbol)
