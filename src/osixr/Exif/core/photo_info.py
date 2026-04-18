import struct
from datetime import datetime
from pathlib import Path
from .jpeg_reader import JpegSegmentReader
from .tiff_parser import TiffParser
from ...Banners.helper import Color
from ..utils.tags import (
    EXIF_TAGS,
    EXIF_SUBIFD_TAGS,
    GPS_TAGS
)


from ..utils.mapping import (
    ORIENTATION_MAP,
    METERING_MAP,
    FLASH_MAP,
    EXPOSURE_PROGRAM_MAP,
    WHITE_BALANCE_MAP,
    EXPOSURE_MODE_MAP,
    SCENE_CAPTURE_MAP,
    COLOR_SPACE_MAP,
    LIGHT_SOURCE_MAP,
    CONTRAST_MAP,
    SATURATION_MAP,
    SHARPNESS_MAP,
    GAIN_CONTROL_MAP,
    SENSING_METHOD_MAP,
    RESOLUTION_UNIT_MAP,
    CUSTOM_RENDERED_MAP
)


class Exif:
    """
        High-level Photo Metadata Extraction Engine.

        This class provides a complete pipeline for extracting, parsing,
        and formatting metadata from image files (primarily JPEG and TIFF).

        It combines low-level EXIF parsing with high-level data interpretation
        and organizes the output into structured sections.

        ------------------------------------------------------------------------

        Features:
            - Automatic EXIF extraction from JPEG (APP1 segment)
            - Direct TIFF parsing support
            - Decoding of EXIF, SubIFD, and GPS metadata
            - Human-readable formatting of camera, image, and capture data
            - GPS coordinate conversion (Decimal + DMS + Google Maps link)
            - Exposure, lens, and processing metadata interpretation
            - File system metadata (size, timestamps, path)
            - Fallback JPEG dimension detection (SOF parsing)

        ------------------------------------------------------------------------

        Supported Formats:
            - JPEG (.jpg, .jpeg)
            - TIFF (.tif, .tiff)

        ------------------------------------------------------------------------

        Arguments:
            filepath (str):
                Path to the image file to analyze.

        ------------------------------------------------------------------------

        Attributes:

            Raw Data:
                raw_data (bytes):
                    Full binary content of the image file.

                exif_raw (dict):
                    Primary EXIF tags (IFD0).

                exif_sub (dict):
                    SubIFD EXIF data (detailed metadata).

                gps_raw (dict):
                    Raw GPS metadata.

            Processed Sections:
                file_info (dict)
                camera_info (dict)
                image_info (dict)
                capture_settings (dict)
                datetime_info (dict)
                gps_info (dict)
                lens_info (dict)
                processing_info (dict)

        ------------------------------------------------------------------------

        Internal Workflow:
            1. Load file into memory
            2. Extract EXIF segment (JPEG) or use raw data (TIFF)
            3. Parse TIFF structure via TiffParser
            4. Extract IFD0, SubIFD, and GPS IFD
            5. Build structured metadata sections

        ------------------------------------------------------------------------

        Methods:

            print_all() -> str:
                Returns a fully formatted, human-readable metadata report.

            to_dict() -> dict:
                Returns all extracted metadata as structured dictionaries.

        ------------------------------------------------------------------------

        Notes:
            - This class is designed as a high-level interface on top of
              low-level parsing (TiffParser).
            - Some EXIF fields may be missing depending on the image source.
            - Corrupted or incomplete EXIF data is safely ignored.

        ------------------------------------------------------------------------

        Example:

            info = PhotoInfo("image.jpg")

            # Get formatted output
            print(info.print_all())

            # Get structured data
            data = info.to_dict()

        ------------------------------------------------------------------------

        Dependencies:
            - struct
            - datetime
            - pathlib
            - Custom modules:
                * JpegSegmentReader
                * TiffParser
                * EXIF tag maps
                * Value mapping utilities
    """

    def __init__(self, filepath: str):
        self.color = Color()
        self.filepath = Path(filepath)
        if not self.filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        self.raw_data: bytes = b""
        self.exif_raw: dict = {}
        self.exif_sub: dict = {}
        self.gps_raw: dict = {}

        self.file_info: dict = {}
        self.camera_info: dict = {}
        self.image_info: dict = {}
        self.capture_settings: dict = {}
        self.datetime_info: dict = {}
        self.gps_info: dict = {}
        self.lens_info: dict = {}
        self.processing_info: dict = {}

        self._load()
        self._parse()
        self._build_sections()


    def _load(self):
        with open(self.filepath, "rb") as f:
            self.raw_data = f.read()


    def _parse(self):
        ext = self.filepath.suffix.lower()

        if ext in (".jpg", ".jpeg"):
            reader = JpegSegmentReader(self.raw_data)
            exif_block = reader.find_app1()
        elif ext in (".tiff", ".tif"):
            exif_block = self.raw_data
        else:
            exif_block = None

        if exif_block:
            try:
                parser = TiffParser(exif_block)
                self.exif_raw = parser.read_ifd(parser.ifd0_offset, EXIF_TAGS)

                # Read SubIFD (EXIF data)
                exif_ptr = self.exif_raw.pop("_ptr_34665", None)
                if exif_ptr is None:
                    exif_ptr = self.exif_raw.pop("_ptr_" + str(0x8769), None)
                for key in list(self.exif_raw.keys()):
                    if key.startswith("_ptr_") and "8769" in key:
                        exif_ptr = self.exif_raw.pop(key)
                        break
                if exif_ptr:
                    self.exif_sub = parser.read_ifd(exif_ptr, EXIF_SUBIFD_TAGS)

                # Read GPS IFD
                gps_ptr = None
                for key in list(self.exif_raw.keys()):
                    if key.startswith("_ptr_") and "8825" in key:
                        gps_ptr = self.exif_raw.pop(key)
                        break
                if gps_ptr:
                    self.gps_raw = parser.read_ifd(gps_ptr, GPS_TAGS)
            except Exception as e:
                pass  # Silently skip unreadable EXIF


    def _build_sections(self):
        self._build_file_info()
        self._build_camera_info()
        self._build_image_info()
        self._build_capture_settings()
        self._build_datetime_info()
        self._build_gps_info()
        self._build_lens_info()
        self._build_processing_info()


    def _build_file_info(self):
        stat = self.filepath.stat()
        size = stat.st_size
        if size < 1024:
            size_str = f"{size} bytes"
        elif size < 1024 ** 2:
            size_str = f"{size / 1024:.1f} KB"
        elif size < 1024 ** 3:
            size_str = f"{size / 1024 ** 2:.2f} MB"
        else:
            size_str = f"{size / 1024 ** 3:.3f} GB"

        self.file_info = {
            "File Name": self.filepath.name,
            "File Path": str(self.filepath.resolve()),
            "File Size": size_str,
            "File Size (bytes)": f"{stat.st_size:,}",
            "File Extension": self.filepath.suffix.upper(),
            "File Modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "File Created": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Detect image dimensions from JPEG header if no EXIF
        if self.filepath.suffix.lower() in (".jpg", ".jpeg"):
            w, h = self._get_jpeg_dimensions()
            if w and h:
                self.file_info["Dimensions (from header)"] = f"{w} × {h} px"

    def _get_jpeg_dimensions(self):
        """Read JPEG SOF marker for width/height."""
        data = self.raw_data
        i = 0
        while i < len(data) - 9:
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xC0, 0xC1, 0xC2):  # SOF markers
                h = struct.unpack_from(">H", data, i + 5)[0]
                w = struct.unpack_from(">H", data, i + 7)[0]
                return w, h
            elif marker in (0xD8, 0xD9):
                i += 2
            else:
                if i + 4 > len(data):
                    break
                length = struct.unpack_from(">H", data, i + 2)[0]
                i += 2 + length
        return None, None


    def _build_camera_info(self):
        d = {}
        make = self.exif_raw.get("camera_make", "")
        model = self.exif_raw.get("camera_model", "")
        if make:
            d["Camera Make"] = make.strip()
        if model:
            d["Camera Model"] = model.strip()
        if make and model:
            d["Full Device Name"] = f"{make.strip()} {model.strip()}"

        software = self.exif_raw.get("software", "")
        if software:
            d["Software"] = software.strip()

        owner = self.exif_sub.get("camera_owner_name", "")
        if owner:
            d["Camera Owner"] = owner.strip()

        serial = self.exif_sub.get("body_serial_number", "")
        if serial:
            d["Body Serial Number"] = serial.strip()

        artist = self.exif_raw.get("artist", "")
        if artist:
            d["Artist / Photographer"] = artist.strip()

        copyright_ = self.exif_raw.get("copyright", "")
        if copyright_:
            d["Copyright"] = copyright_.strip()

        self.camera_info = d


    def _build_image_info(self):
        d = {}
        w = self.exif_sub.get("pixel_x_dimension")
        h = self.exif_sub.get("pixel_y_dimension")
        if w and h:
            d["Width"] = f"{w:,} px"
            d["Height"] = f"{h:,} px"
            d["Dimensions"] = f"{w:,} × {h:,} px"
            megapixels = (w * h) / 1_000_000
            d["Megapixels"] = f"{megapixels:.1f} MP"
            d["Aspect Ratio"] = self._calc_aspect(w, h)

        xres = self.exif_raw.get("x_resolution")
        yres = self.exif_raw.get("y_resolution")
        unit = self.exif_raw.get("resolution_unit")
        if xres:
            xval = self._rational_to_float(xres)
            yval = self._rational_to_float(yres) if yres else xval
            unit_str = RESOLUTION_UNIT_MAP.get(unit, "Inch")
            d["X Resolution"] = f"{xval:.0f} DPI ({unit_str})"
            d["Y Resolution"] = f"{yval:.0f} DPI ({unit_str})"

        orientation = self.exif_raw.get("orientation")
        if orientation:
            d["Orientation"] = ORIENTATION_MAP.get(orientation, str(orientation))

        color_space = self.exif_sub.get("color_space")
        if color_space is not None:
            d["Color Space"] = COLOR_SPACE_MAP.get(color_space, f"Unknown ({color_space})")

        sensing = self.exif_sub.get("sensing_method")
        if sensing is not None:
            d["Sensing Method"] = SENSING_METHOD_MAP.get(sensing, str(sensing))

        self.image_info = d

    def _build_capture_settings(self):
        d = {}

        # Exposure time
        et = self.exif_sub.get("exposure_time")
        if et:
            val = self._rational_to_float(et)
            if val < 1:
                frac = self._to_fraction(val)
                d["Exposure Time"] = f"{frac} sec ({val:.6f}s)"
            else:
                d["Exposure Time"] = f"{val:.1f} sec"

        # F-number
        fn = self.exif_sub.get("f_number")
        if fn:
            d["Aperture (F-Number)"] = f"f/{self._rational_to_float(fn):.1f}"

        # ISO
        iso = self.exif_sub.get("iso_speed")
        if iso:
            d["ISO Speed"] = str(iso)

        # Focal length
        fl = self.exif_sub.get("focal_length")
        if fl:
            d["Focal Length"] = f"{self._rational_to_float(fl):.1f} mm"

        fl35 = self.exif_sub.get("focal_length_35mm")
        if fl35:
            d["Focal Length (35mm equiv)"] = f"{fl35} mm"

        # Shutter speed (APEX)
        ss = self.exif_sub.get("shutter_speed")
        if ss:
            val = self._rational_to_float(ss)
            speed = 1 / (2 ** val) if val != 0 else 0
            if speed > 0 and speed < 1:
                d["Shutter Speed (APEX)"] = self._to_fraction(speed) + " sec"
            elif speed >= 1:
                d["Shutter Speed (APEX)"] = f"{speed:.1f} sec"

        # Aperture (APEX)
        ap = self.exif_sub.get("aperture")
        if ap:
            val = self._rational_to_float(ap)
            d["Aperture (APEX)"] = f"f/{2 ** (val / 2):.1f}"

        # Exposure bias
        eb = self.exif_sub.get("exposure_bias")
        if eb:
            val = self._rational_to_float(eb)
            d["Exposure Bias"] = f"{val:+.1f} EV"

        # Exposure program
        ep = self.exif_sub.get("exposure_program")
        if ep is not None:
            d["Exposure Program"] = EXPOSURE_PROGRAM_MAP.get(ep, str(ep))

        # Metering mode
        mm = self.exif_sub.get("metering_mode")
        if mm is not None:
            d["Metering Mode"] = METERING_MAP.get(mm, str(mm))

        # Flash
        flash = self.exif_sub.get("flash")
        if flash is not None:
            d["Flash"] = FLASH_MAP.get(flash, f"Unknown (0x{flash:02X})")

        # White balance
        wb = self.exif_sub.get("white_balance")
        if wb is not None:
            d["White Balance"] = WHITE_BALANCE_MAP.get(wb, str(wb))

        # Exposure mode
        exm = self.exif_sub.get("exposure_mode")
        if exm is not None:
            d["Exposure Mode"] = EXPOSURE_MODE_MAP.get(exm, str(exm))

        # Light source
        ls = self.exif_sub.get("light_source")
        if ls is not None:
            d["Light Source"] = LIGHT_SOURCE_MAP.get(ls, str(ls))

        # Subject distance
        sd = self.exif_sub.get("subject_distance")
        if sd:
            val = self._rational_to_float(sd)
            if val > 0:
                d["Subject Distance"] = f"{val:.2f} m"

        # Max aperture
        ma = self.exif_sub.get("max_aperture")
        if ma:
            val = self._rational_to_float(ma)
            d["Max Aperture"] = f"f/{2 ** (val / 2):.1f}"

        # Brightness
        br = self.exif_sub.get("brightness")
        if br:
            d["Brightness (APEX)"] = str(self._rational_to_float(br))

        # Digital zoom
        dz = self.exif_sub.get("digital_zoom_ratio")
        if dz:
            val = self._rational_to_float(dz)
            d["Digital Zoom"] = f"{val:.2f}×" if val != 0 else "No Digital Zoom"

        # Scene capture type
        sct = self.exif_sub.get("scene_capture_type")
        if sct is not None:
            d["Scene Capture Type"] = SCENE_CAPTURE_MAP.get(sct, str(sct))

        self.capture_settings = d


    def _build_datetime_info(self):
        d = {}
        fields = [
            ("datetime_original", "Date/Time Original (Capture)"),
            ("datetime_digitized", "Date/Time Digitized"),
            ("datetime_modified", "Date/Time Modified"),
        ]
        for key, label in fields:
            val = self.exif_sub.get(key) or self.exif_raw.get(key)
            if val:
                parsed = self._parse_datetime(val)
                d[label] = parsed if parsed else val

        gps_date = self.gps_raw.get("gps_date_stamp")
        gps_time = self.gps_raw.get("gps_time_stamp")
        if gps_date:
            d["GPS Date"] = gps_date
        if gps_time:
            parts = [self._rational_to_float(t) for t in gps_time] if isinstance(gps_time, list) else []
            if parts:
                d["GPS Time (UTC)"] = f"{int(parts[0]):02d}:{int(parts[1]):02d}:{parts[2]:.2f}"

        self.datetime_info = d


    def _build_gps_info(self):
        d = {}
        lat_raw = self.gps_raw.get("gps_latitude")
        lat_ref = self.gps_raw.get("gps_latitude_ref", "N")
        lon_raw = self.gps_raw.get("gps_longitude")
        lon_ref = self.gps_raw.get("gps_longitude_ref", "E")

        if lat_raw and lon_raw:
            lat = self._dms_to_decimal(lat_raw, lat_ref)
            lon = self._dms_to_decimal(lon_raw, lon_ref)
            d["Latitude"] = f"{lat:.8f}° {lat_ref}"
            d["Longitude"] = f"{lon:.8f}° {lon_ref}"
            d["Decimal Coordinates"] = f"{lat:.8f}, {lon:.8f}"
            d["Google Maps Link"] = f"https://maps.google.com/?q={lat:.8f},{lon:.8f}"
            d["DMS Coordinates"] = (
                f"{self._decimal_to_dms(lat)} {lat_ref}, "
                f"{self._decimal_to_dms(lon)} {lon_ref}"
            )

        alt = self.gps_raw.get("gps_altitude")
        alt_ref = self.gps_raw.get("gps_altitude_ref", 0)
        if alt:
            alt_val = self._rational_to_float(alt)
            prefix = "Below Sea Level" if alt_ref == 1 else "Above Sea Level"
            d["Altitude"] = f"{alt_val:.1f} m ({prefix})"

        speed = self.gps_raw.get("gps_speed")
        speed_ref = self.gps_raw.get("gps_speed_ref", "K")
        if speed:
            spd_val = self._rational_to_float(speed)
            units = {"K": "km/h", "M": "mph", "N": "knots"}
            d["GPS Speed"] = f"{spd_val:.2f} {units.get(speed_ref, speed_ref)}"

        direction = self.gps_raw.get("gps_img_direction")
        dir_ref = self.gps_raw.get("gps_img_direction_ref", "T")
        if direction:
            dir_val = self._rational_to_float(direction)
            ref_str = "True North" if dir_ref == "T" else "Magnetic North"
            d["Image Direction"] = f"{dir_val:.2f}° ({ref_str})"

        sats = self.gps_raw.get("gps_satellites")
        if sats:
            d["GPS Satellites"] = sats

        self.gps_info = d


    def _build_lens_info(self):
        d = {}
        lens_make = self.exif_sub.get("lens_make", "")
        lens_model = self.exif_sub.get("lens_model", "")
        lens_serial = self.exif_sub.get("lens_serial_number", "")
        lens_spec = self.exif_sub.get("lens_specification")

        if lens_make:
            d["Lens Make"] = lens_make.strip()
        if lens_model:
            d["Lens Model"] = lens_model.strip()
        if lens_serial:
            d["Lens Serial Number"] = lens_serial.strip()
        if lens_spec and isinstance(lens_spec, list) and len(lens_spec) >= 4:
            min_fl = self._rational_to_float(lens_spec[0])
            max_fl = self._rational_to_float(lens_spec[1])
            min_fn = self._rational_to_float(lens_spec[2])
            max_fn = self._rational_to_float(lens_spec[3])
            d["Lens Focal Range"] = f"{min_fl:.0f}–{max_fl:.0f} mm"
            d["Lens Max Aperture Range"] = f"f/{min_fn:.1f}–f/{max_fn:.1f}"

        self.lens_info = d


    def _build_processing_info(self):
        d = {}
        contrast = self.exif_sub.get("contrast")
        if contrast is not None:
            d["Contrast"] = CONTRAST_MAP.get(contrast, str(contrast))

        saturation = self.exif_sub.get("saturation")
        if saturation is not None:
            d["Saturation"] = SATURATION_MAP.get(saturation, str(saturation))

        sharpness = self.exif_sub.get("sharpness")
        if sharpness is not None:
            d["Sharpness"] = SHARPNESS_MAP.get(sharpness, str(sharpness))

        gain = self.exif_sub.get("gain_control")
        if gain is not None:
            d["Gain Control"] = GAIN_CONTROL_MAP.get(gain, str(gain))

        cr = self.exif_sub.get("custom_rendered")
        if cr is not None:
            d["Custom Rendered"] = CUSTOM_RENDERED_MAP.get(cr, str(cr))

        uid = self.exif_sub.get("image_unique_id", "")
        if uid:
            d["Image Unique ID"] = uid.strip()

        user_comment = self.exif_sub.get("user_comment", b"")
        if user_comment:
            if isinstance(user_comment, (bytes, list)):
                try:
                    raw_bytes = bytes(user_comment) if isinstance(user_comment, list) else user_comment
                    comment = raw_bytes[8:].decode("utf-8", errors="replace").strip("\x00").strip()
                    if comment:
                        d["User Comment"] = comment
                except Exception:
                    pass

        exif_ver = self.exif_sub.get("exif_version")
        if exif_ver:
            if isinstance(exif_ver, (bytes, list)):
                try:
                    ver_str = bytes(exif_ver).decode("ascii", errors="replace")
                    d["EXIF Version"] = ver_str
                except Exception:
                    pass

        self.processing_info = d


    def _rational_to_float(self, val) -> float:
        if isinstance(val, tuple) and len(val) == 2:
            n, d = val
            return n / d if d != 0 else 0.0
        if isinstance(val, (int, float)):
            return float(val)
        return 0.0

    def _to_fraction(self, val: float) -> str:
        """Convert a float like 0.001 to a fraction string like 1/1000."""
        if val <= 0:
            return str(val)
        denom = round(1 / val)
        return f"1/{denom}"

    def _calc_aspect(self, w: int, h: int) -> str:
        from math import gcd
        g = gcd(w, h)
        return f"{w // g}:{h // g}"

    def _parse_datetime(self, s: str) -> str:
        try:
            dt = datetime.strptime(s.strip(), "%Y:%m:%d %H:%M:%S")
            return dt.strftime("%A, %B %d, %Y at %H:%M:%S")
        except Exception:
            return s

    def _dms_to_decimal(self, dms, ref: str) -> float:
        if not isinstance(dms, list) or len(dms) < 3:
            return 0.0
        d = self._rational_to_float(dms[0])
        m = self._rational_to_float(dms[1])
        s = self._rational_to_float(dms[2])
        dec = d + m / 60 + s / 3600
        if ref in ("S", "W"):
            dec = -dec
        return dec

    def _decimal_to_dms(self, decimal: float) -> str:
        decimal = abs(decimal)
        d = int(decimal)
        m_float = (decimal - d) * 60
        m = int(m_float)
        s = (m_float - m) * 60
        return f"{d}°{m}'{s:.2f}\""

    def _section_to_string(self, title: str, data: dict, emoji: str = "📌"):
        if not data:
            return ""

        lines = []
        lines.append(f"\n  {emoji}  {title}")
        lines.append("  " + "─" * 60)

        max_key = max(len(k) for k in data.keys())

        for key, val in data.items():
            lines.append(f"  {key:<{max_key + 2}}: {val}")

        return "\n".join(lines)

    def print_all(self):
        output = []

        output.append("\n" + "═" * 65)
        output.append("  📸  PHOTO METADATA EXTRACTOR  —  Full Report")
        output.append("═" * 65)

        output.append(self._section_to_string("FILE INFORMATION", self.file_info, "📁"))
        output.append(self._section_to_string("CAMERA & DEVICE INFO", self.camera_info, "📷"))
        output.append(self._section_to_string("IMAGE PROPERTIES", self.image_info, "🖼️"))
        output.append(self._section_to_string("CAPTURE SETTINGS", self.capture_settings, "⚙️"))
        output.append(self._section_to_string("DATE & TIME", self.datetime_info, "📅"))
        output.append(self._section_to_string("GPS LOCATION", self.gps_info, "📍"))
        output.append(self._section_to_string("LENS INFORMATION", self.lens_info, "🔭"))
        output.append(self._section_to_string("IMAGE PROCESSING", self.processing_info, "🎨"))

        # Summary
        has_exif = bool(self.exif_raw or self.exif_sub)
        has_gps = bool(self.gps_info)
        has_camera = bool(self.camera_info)

        output.append("\n" + "═" * 65)
        output.append("  📊  SUMMARY")
        output.append("  " + "─" * 60)
        output.append(f"  EXIF Data Found    : {'✅ Yes' if has_exif else '❌ No'}")
        output.append(f"  Camera Info Found  : {'✅ Yes' if has_camera else '❌ No'}")
        output.append(f"  GPS Location Found : {'✅ Yes' if has_gps else '❌ No'}")

        total_fields = sum(len(s) for s in [
            self.file_info, self.camera_info, self.image_info,
            self.capture_settings, self.datetime_info, self.gps_info,
            self.lens_info, self.processing_info
        ])

        output.append(f"  Total Fields Found : {total_fields}")
        output.append("═" * 65 + "\n")

        return "\n".join(output)

    def to_dict(self) -> dict:
        """Returns all info as a flat dictionary."""
        return {
            "file_info": self.file_info,
            "camera_info": self.camera_info,
            "image_info": self.image_info,
            "capture_settings": self.capture_settings,
            "datetime_info": self.datetime_info,
            "gps_info": self.gps_info,
            "lens_info": self.lens_info,
            "processing_info": self.processing_info,
        }