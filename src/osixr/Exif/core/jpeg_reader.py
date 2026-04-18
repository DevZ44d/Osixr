import struct
from typing import Optional

class JpegSegmentReader:
    """
        Low-level JPEG Segment Parser for EXIF Extraction.

        This class is responsible for parsing raw JPEG binary data
        and locating the APP1 segment that contains EXIF metadata.

        It works by sequentially reading JPEG markers and extracting
        the EXIF payload if available.

        ------------------------------------------------------------------------

        Features:
            - Parses JPEG binary structure manually
            - Detects standard JPEG markers (SOI, EOI, APP0–APP2, etc.)
            - Locates APP1 segment containing EXIF data
            - Extracts raw EXIF payload (TIFF block)
            - Lightweight and dependency-free implementation

        ------------------------------------------------------------------------

        JPEG Markers Supported:
            SOI   (0xFFD8) - Start of Image
            EOI   (0xFFD9) - End of Image
            APP0  (0xFFE0) - JFIF metadata
            APP1  (0xFFE1) - EXIF metadata (primary target)
            APP2  (0xFFE2) - ICC profiles / extra data
            DQT   (0xFFDB) - Quantization tables
            SOF0  (0xFFC0) - Baseline frame
            SOF2  (0xFFC2) - Progressive frame
            DHT   (0xFFC4) - Huffman tables
            SOS   (0xFFDA) - Start of scan
            DRI   (0xFFDD) - Restart interval
            COM   (0xFFFE) - Comments

        ------------------------------------------------------------------------

        Arguments:
            data (bytes):
                Raw JPEG binary data loaded from an image file.

        ------------------------------------------------------------------------

        Attributes:
            data (bytes):
                Full JPEG file in binary form.

            pos (int):
                Current parsing position inside the byte stream.

        ------------------------------------------------------------------------

        Methods:

            read_uint16() -> int:
                Reads a 2-byte unsigned integer from the current position
                using big-endian format and advances the pointer.

            find_app1() -> Optional[bytes]:
                Scans JPEG segments and returns the raw EXIF block if found.

        ------------------------------------------------------------------------

        Return Value:
            find_app1():
                - bytes: Raw EXIF/TIFF block (without "Exif\\x00\\x00" header)
                - None: If no EXIF data is found or JPEG is invalid

        ------------------------------------------------------------------------

        Notes:
            - This is a low-level binary parser and does not validate EXIF content.
            - It only extracts the APP1 segment containing EXIF data.
            - Corrupted JPEG files may result in early termination or None.

        ------------------------------------------------------------------------

        Example:

            reader = JpegSegmentReader(image_bytes)
            exif_block = reader.find_app1()

            if exif_block:
                print("EXIF data found")
    """

    MARKERS = {
        0xFFD8: "SOI", 0xFFD9: "EOI", 0xFFE0: "APP0",
        0xFFE1: "APP1", 0xFFE2: "APP2", 0xFFDB: "DQT",
        0xFFC0: "SOF0", 0xFFC2: "SOF2", 0xFFC4: "DHT",
        0xFFDA: "SOS", 0xFFDD: "DRI", 0xFFFE: "COM",
    }

    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def read_uint16(self) -> int:
        val = struct.unpack_from(">H", self.data, self.pos)[0]
        self.pos += 2
        return val

    def find_app1(self) -> Optional[bytes]:
        if self.read_uint16() != 0xFFD8:
            return None
        while self.pos < len(self.data) - 4:
            marker = self.read_uint16()
            if marker == 0xFFD9:
                break
            if marker == 0xFFDA:
                break
            length = self.read_uint16()
            seg_data = self.data[self.pos: self.pos + length - 2]
            if marker == 0xFFE1 and seg_data[:4] == b"Exif":
                return seg_data[6:]  # skip "Exif\x00\x00"
            self.pos += length - 2
        return None