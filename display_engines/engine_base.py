import base64
from io import BytesIO
from math import floor

from PIL import Image, ImageDraw, ImageFont


def get_text_width(draw, text, font):
    if hasattr(draw, "textbbox"):  # Pillow >=8.0
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0]
    elif hasattr(draw, "textsize"):  # Pillow <8.0
        return draw.textsize(text, font=font)[0]
    else:
        raise RuntimeError("Cannot measure text width: unsupported Pillow version")


class EngineBase:
    """
    Base engine for all kinds of displays
    """

    def __init__(self, config):
        self.name = config["name"]
        self.resolution = config["resolution"]  # (width, height)
        self.color = config["color"]
        self.fit_times = config["fit_times"]
        self.day_digits = 1
        width, height = self.resolution

        mode = "RGB" if self.color else "1"
        self.display_buffer = Image.new(mode, (width, height), 0)

    # --------------------------------------------------------
    # EXPORT METHODS
    # --------------------------------------------------------

    def get_data_frame(self):
        """
        Return base64 encoded display data frame of current buffer state.
        """
        bw_image = self.display_buffer.convert("1")
        width, height = bw_image.size
        pixels = bw_image.load()

        packed_bytes = bytearray()

        for y in range(height):
            byte_val = 0
            bit_count = 0
            for x in range(width):
                pixel_on = pixels[x, y] == 255
                if pixel_on:
                    byte_val |= 1 << bit_count
                bit_count += 1
                if bit_count == 8:
                    packed_bytes.append(byte_val)
                    byte_val = 0
                    bit_count = 0

            if bit_count > 0:
                packed_bytes.append(byte_val)

        encoded = base64.b64encode(packed_bytes).decode("ascii")
        return encoded

    def get_bitmap(self, path=None):
        """
        Export buffer as PNG image for debugging.
        If `path` is provided, save to file. Otherwise, return PNG bytes.
        """
        output = BytesIO()
        self.display_buffer.save(output, format="PNG")
        png_data = output.getvalue()

        if path:
            with open(path, "wb") as f:
                f.write(png_data)

        return png_data

    # --------------------------------------------------------
    # DRAW METHODS
    # --------------------------------------------------------
    def predraw_time(self, time_data):
        """
        Draw grid of time_data to buffer
        Format: L D:HH:MM:SS
        """

        if len(time_data) > self.fit_times:
            return False

        self.clear()

        formatted_times = []
        for entry in time_data:
            for label, total_seconds in entry.items():
                if total_seconds == 0:
                    formatted_times.append((label, "DEAD"))
                    continue

                days = total_seconds // 86400
                seconds = total_seconds % 86400

                hours = floor(seconds / 3600)
                minutes = floor((seconds % 3600) / 60)
                secs = seconds % 60

                day_chars = (
                    f"{days:0{self.day_digits}}"
                    if days < 10**self.day_digits
                    else "#" * self.day_digits
                )

                formatted_times.append(
                    (label, day_chars, f"{hours:02}", f"{minutes:02}", f"{secs:02}")
                )

        try:
            bold_font = ImageFont.truetype("DejaVuSansMono-Bold.ttf", 10)
        except:
            bold_font = ImageFont.load_default()

        try:
            regular_font = ImageFont.truetype("DejaVuSansMono.ttf", 10)
        except:
            regular_font = ImageFont.load_default()

        draw = ImageDraw.Draw(self.display_buffer)
        width, height = self.resolution

        row_height = height // 2
        col_width = width // 2

        for idx in range(self.fit_times):
            if idx >= len(formatted_times):
                continue

            data = formatted_times[idx]

            # DEAD mode
            if len(data) == 2 and data[1] == "DEAD":
                label = data[0]
                dead_text = " DEAD"

                label_width = get_text_width(draw, label, bold_font)
                dead_width = get_text_width(draw, dead_text, regular_font)
                total_width = label_width + 2 + dead_width

                x = col_width * (idx % 2) + (col_width - total_width) // 2 + 2
                y = row_height * (idx // 2) + (row_height - bold_font.size) // 2

                draw.text(
                    (x, y),
                    label,
                    fill=255 if not self.color else (255, 255, 255),
                    font=bold_font,
                )
                x += label_width + 2

                draw.text(
                    (x, y),
                    dead_text,
                    fill=255 if not self.color else (255, 255, 255),
                    font=regular_font,
                )

            else:
                label, day_char, hh, mm, ss = data

                label_width = get_text_width(draw, label, bold_font)
                space_width = 1
                day_width = get_text_width(draw, day_char, regular_font)
                colon_width = 3
                hh_width = get_text_width(draw, hh, regular_font)
                mm_width = get_text_width(draw, mm, regular_font)
                ss_width = get_text_width(draw, ss, regular_font)

                total_width = (
                    label_width
                    + space_width
                    + day_width
                    + colon_width
                    + hh_width
                    + colon_width
                    + mm_width
                    + colon_width
                    + ss_width
                )

                x = col_width * (idx % 2) + (col_width - total_width) // 2 + 2
                y = row_height * (idx // 2) + (row_height - bold_font.size) // 2

                draw.text(
                    (x, y),
                    label,
                    fill=255 if not self.color else (255, 255, 255),
                    font=bold_font,
                )
                x += label_width + space_width

                draw.text(
                    (x, y),
                    day_char,
                    fill=255 if not self.color else (255, 255, 255),
                    font=regular_font,
                )
                x += day_width
                draw.text(
                    (x - 1, y),
                    ":",
                    fill=255 if not self.color else (255, 255, 255),
                    font=regular_font,
                )
                x += colon_width - 1

                draw.text(
                    (x, y),
                    hh,
                    fill=255 if not self.color else (255, 255, 255),
                    font=regular_font,
                )
                x += hh_width
                draw.text(
                    (x - 1, y),
                    ":",
                    fill=255 if not self.color else (255, 255, 255),
                    font=regular_font,
                )
                x += colon_width - 1

                draw.text(
                    (x, y),
                    mm,
                    fill=255 if not self.color else (255, 255, 255),
                    font=regular_font,
                )
                x += mm_width
                draw.text(
                    (x - 1, y),
                    ":",
                    fill=255 if not self.color else (255, 255, 255),
                    font=regular_font,
                )
                x += colon_width - 1

                draw.text(
                    (x, y),
                    ss,
                    fill=255 if not self.color else (255, 255, 255),
                    font=regular_font,
                )

        return True

    def draw_announcement(self, base64_data):
        from io import BytesIO

        from PIL import Image, ImageOps

        img = Image.open(BytesIO(base64.b64decode(base64_data)))
        target_mode = "RGB" if self.color else "1"
        img = img.convert(target_mode)

        if target_mode == "RGB":
            img = ImageOps.invert(img)
        else:
            img = img.convert("L")
            img = ImageOps.invert(img)
            img = img.point(lambda x: 255 if x > 128 else 0, "1")

        self.display_buffer.paste(img)

    # --------------------------------------------------------
    # BUFFER CONTROL
    # --------------------------------------------------------

    def clear(self):
        draw = ImageDraw.Draw(self.display_buffer)
        fill_color = 0 if not self.color else (0, 0, 0)
        draw.rectangle([0, 0, *self.resolution], fill=fill_color)
        return True
