import base64
from io import BytesIO
from math import floor

from PIL import Image, ImageDraw, ImageFont


class EngineBase:
    """
    Base engine for all kinds of displays
    """

    def __init__(self, config):
        self.name = config["name"]
        self.resolution = config["resolution"]  # (width, height)
        self.color = config["color"]
        self.fit_times = config["fit_times"]

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

        if self.color:
            raw_data = self.display_buffer.tobytes()  # RGB triplets
        else:
            bw_image = self.display_buffer.convert("1")
            raw_data = bw_image.tobytes()

        encoded = base64.b64encode(raw_data).decode("ascii")
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
                # If total_seconds is 0, mark as DEAD
                if total_seconds == 0:
                    formatted_times.append((label, "DEAD"))
                    continue

                days = total_seconds // 86400
                seconds = total_seconds % 86400

                hours = floor(seconds / 3600)
                minutes = floor((seconds % 3600) / 60)
                secs = seconds % 60

                day_char = str(days) if days <= 9 else "#"

                formatted_times.append(
                    (label, day_char, f"{hours:02}", f"{minutes:02}", f"{secs:02}")
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

                label_width = draw.textlength(label, font=bold_font)
                dead_width = draw.textlength(dead_text, font=regular_font)
                total_width = label_width + 2 + dead_width

                x = col_width * (idx % 2) + (col_width - total_width) // 2 + 2
                y = row_height * (idx // 2) + (row_height - bold_font.size) // 2

                # Draw label
                draw.text(
                    (x, y),
                    label,
                    fill=255 if not self.color else (255, 255, 255),
                    font=bold_font,
                )
                x += label_width + 2

                # Draw DEAD
                draw.text(
                    (x, y),
                    dead_text,
                    fill=255 if not self.color else (255, 255, 255),
                    font=regular_font,
                )

            else:
                label, day_char, hh, mm, ss = data

                label_width = draw.textlength(label, font=bold_font)
                space_width = 1
                day_width = draw.textlength(day_char, font=regular_font)
                colon_width = 3
                hh_width = draw.textlength(hh, font=regular_font)
                mm_width = draw.textlength(mm, font=regular_font)
                ss_width = draw.textlength(ss, font=regular_font)

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

        # Decode base64 to image
        img = Image.open(BytesIO(base64.b64decode(base64_data)))

        # Ensure mode matches target (convert to "1" or "RGB")
        target_mode = "RGB" if self.color else "1"
        img = img.convert(target_mode)

        # Invert colors (white <-> black)
        if target_mode == "RGB":
            img = ImageOps.invert(img)
        else:
            # For 1-bit images, invert manually: convert to L, invert, then back
            img = img.convert("L")
            img = ImageOps.invert(img)
            img = img.point(lambda x: 255 if x > 128 else 0, "1")

        # Paste inverted image into display buffer
        self.display_buffer.paste(img)

    # --------------------------------------------------------
    # BUFFER CONTROL
    # --------------------------------------------------------

    def clear(self):
        """
        Clear the display buffer.
        """
        draw = ImageDraw.Draw(self.display_buffer)
        fill_color = 0 if not self.color else (0, 0, 0)
        draw.rectangle([0, 0, *self.resolution], fill=fill_color)
        return True
