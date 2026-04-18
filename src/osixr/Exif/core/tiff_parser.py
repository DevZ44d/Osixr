import struct

class TiffParser:
    """
        TIFF / EXIF Binary Parser.

        This class is responsible for parsing raw TIFF/EXIF byte streams
        extracted from image files (typically JPEG APP1 segments).

        It provides low-level decoding of Image File Directories (IFDs),
        tag values, and supports multiple EXIF data types.

        ------------------------------------------------------------------------

        Features:
            - Supports both little-endian (II) and big-endian (MM) formats
            - Parses TIFF header and validates structure
            - Reads Image File Directories (IFDs)
            - Decodes multiple EXIF data types:
                * BYTE, ASCII, SHORT, LONG
                * RATIONAL / SRATIONAL
                * FLOAT / DOUBLE
            - Handles inline values and offset-based values
            - Extracts sub-IFD pointers (EXIF, GPS)

        ------------------------------------------------------------------------

        Arguments:
            data (bytes):
                Raw TIFF/EXIF binary data extracted from an image.

        ------------------------------------------------------------------------

        Attributes:
            data (bytes):
                Raw EXIF binary data.

            endian (str):
                Byte order used for parsing:
                    "<" for little-endian (II)
                    ">" for big-endian (MM)

            ifd0_offset (int):
                Offset to the first Image File Directory (IFD0).

        ------------------------------------------------------------------------

        Methods:
            read_ifd(offset: int, tag_map: dict) -> dict:
                Parses an Image File Directory and returns decoded tag values.

            _read_value(type_id: int, count: int, offset_or_value: int, field_offset: int):
                Decodes a TIFF field value based on its type and size.

            _unpack(fmt: str, offset: int):
                Internal helper for reading structured binary data.

        ------------------------------------------------------------------------

        Notes:
            - This is a low-level parser and does not interpret semantic meaning
              of tags (e.g., converting exposure values or GPS coordinates).
            - Higher-level formatting should be handled outside this class.
            - Invalid offsets or corrupted EXIF data may raise exceptions.

        ------------------------------------------------------------------------

        Example:
            parser = TiffParser(exif_bytes)
            ifd0 = parser.read_ifd(parser.ifd0_offset, TAG_MAP)

        ------------------------------------------------------------------------

        Dependencies:
            - struct (standard library)
    """

    TYPE_SIZES = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 6: 1, 7: 1, 8: 2, 9: 4, 10: 8, 11: 4, 12: 8}

    def __init__(self, data: bytes):
        self.data = data
        byte_order = data[:2]
        if byte_order == b"II":
            self.endian = "<"
        elif byte_order == b"MM":
            self.endian = ">"
        else:
            raise ValueError("Invalid TIFF byte order")
        magic = self._unpack("H", 2)
        if magic != 42:
            raise ValueError("Not a valid TIFF")
        self.ifd0_offset = self._unpack("I", 4)

    def _unpack(self, fmt: str, offset: int):
        size = struct.calcsize(fmt)
        return struct.unpack_from(self.endian + fmt, self.data, offset)[0]

    def _read_value(self, type_id: int, count: int, offset_or_value: int, field_offset: int):
        """Decode field value(s) from TIFF entry."""
        type_map = {
            1: ("B", 1), 2: ("s", 1), 3: ("H", 2), 4: ("I", 4),
            5: ("II", 8), 6: ("b", 1), 7: ("B", 1), 8: ("h", 2),
            9: ("i", 4), 10: ("ii", 8), 11: ("f", 4), 12: ("d", 8),
        }
        if type_id not in type_map:
            return None

        fmt_char, unit_size = type_map[type_id]
        total_size = unit_size * count

        if total_size <= 4:
            raw = struct.pack(self.endian + "I", offset_or_value)[:total_size]
        else:
            ptr = offset_or_value
            raw = self.data[ptr: ptr + total_size]

        if type_id == 2:  # ASCII string
            return raw.decode("latin-1", errors="replace").rstrip("\x00")

        if type_id in (5, 10):  # Rational
            results = []
            for i in range(count):
                n, d = struct.unpack_from(self.endian + ("II" if type_id == 5 else "ii"), raw, i * 8)
                results.append((n, d))
            return results[0] if count == 1 else results

        fmt_full = self.endian + fmt_char * count
        vals = struct.unpack_from(fmt_full, raw)
        if len(vals) == 1:
            return vals[0]
        return list(vals)

    def read_ifd(self, offset: int, tag_map: dict) -> dict:
        """Read an IFD (Image File Directory) at given offset."""
        result = {}
        try:
            count = self._unpack("H", offset)
        except Exception:
            return result

        for i in range(count):
            entry_offset = offset + 2 + i * 12
            try:
                tag = self._unpack("H", entry_offset)
                type_id = self._unpack("H", entry_offset + 2)
                value_count = self._unpack("I", entry_offset + 4)
                raw_val = self._unpack("I", entry_offset + 8)
                name = tag_map.get(tag)
                if name:
                    val = self._read_value(type_id, value_count, raw_val, entry_offset + 8)
                    if val is not None:
                        result[name] = val
                # Store raw pointer for sub-IFDs
                if tag in (0x8769, 0x8825):
                    result[f"_ptr_{tag}"] = raw_val
            except Exception:
                continue
        return result