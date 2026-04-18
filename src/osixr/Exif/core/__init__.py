"""
    Core Module
    ===========
    Contains the main parsing engines and low-level components.

    This package includes:
        - PhotoInfoExtractor (main class)
        - JpegSegmentReader
        - TiffParser
"""

from .photo_info import Exif


__all__ = [
    "Exif"
]