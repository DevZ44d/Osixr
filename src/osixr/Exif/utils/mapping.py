
# Human-readable value mappings
ORIENTATION_MAP = {
    1: "Normal (0°)", 2: "Flipped Horizontal", 3: "Rotated 180°",
    4: "Flipped Vertical", 5: "Transposed", 6: "Rotated 90° CW",
    7: "Transverse", 8: "Rotated 90° CCW"
}
METERING_MAP = {
    0: "Unknown", 1: "Average", 2: "Center-weighted Average",
    3: "Spot", 4: "Multi-spot", 5: "Multi-segment", 6: "Partial"
}
FLASH_MAP = {
    0x00: "No Flash", 0x01: "Flash Fired", 0x05: "Flash Fired, Strobe Return Not Detected",
    0x07: "Flash Fired, Strobe Return Detected", 0x08: "Flash On, Did Not Fire",
    0x09: "Flash On, Fired", 0x0D: "Flash On, Return Not Detected",
    0x0F: "Flash On, Return Detected", 0x10: "Flash Off, Did Not Fire",
    0x14: "Flash Off, Did Not Fire, Return Not Detected",
    0x18: "Flash Auto, Did Not Fire", 0x19: "Flash Auto, Fired",
    0x1D: "Flash Auto, Fired, Return Not Detected",
    0x1F: "Flash Auto, Fired, Return Detected",
    0x20: "No Flash Function", 0x30: "Flash Off, No Flash Function",
    0x41: "Flash Fired, Red-Eye Reduction", 0x45: "Flash Fired, Red-Eye Reduction, No Return",
    0x47: "Flash Fired, Red-Eye Reduction, Return Detected",
    0x49: "Flash On, Red-Eye Reduction", 0x4D: "Flash On, Red-Eye Reduction, Return Not Detected",
    0x4F: "Flash On, Red-Eye Reduction, Return Detected",
    0x50: "Flash Off, Red-Eye Reduction",
    0x58: "Flash Auto, Did Not Fire, Red-Eye Reduction",
    0x59: "Flash Auto, Fired, Red-Eye Reduction",
    0x5D: "Flash Auto, Fired, Red-Eye Reduction, Return Not Detected",
    0x5F: "Flash Auto, Fired, Red-Eye Reduction, Return Detected",
}
EXPOSURE_PROGRAM_MAP = {
    0: "Not Defined", 1: "Manual", 2: "Normal Program", 3: "Aperture Priority",
    4: "Shutter Priority", 5: "Creative Program", 6: "Action Program",
    7: "Portrait Mode", 8: "Landscape Mode"
}
WHITE_BALANCE_MAP = {0: "Auto", 1: "Manual"}
EXPOSURE_MODE_MAP = {0: "Auto Exposure", 1: "Manual Exposure", 2: "Auto Bracket"}
SCENE_CAPTURE_MAP = {0: "Standard", 1: "Landscape", 2: "Portrait", 3: "Night Scene"}
COLOR_SPACE_MAP = {1: "sRGB", 65535: "Uncalibrated"}
LIGHT_SOURCE_MAP = {
    0: "Unknown", 1: "Daylight", 2: "Fluorescent", 3: "Tungsten",
    4: "Flash", 9: "Fine Weather", 10: "Cloudy Weather", 11: "Shade",
    12: "Daylight Fluorescent", 13: "Day White Fluorescent",
    14: "Cool White Fluorescent", 15: "White Fluorescent",
    17: "Standard Light A", 18: "Standard Light B", 19: "Standard Light C",
    20: "D55", 21: "D65", 22: "D75", 23: "D50", 24: "ISO Studio Tungsten", 255: "Other"
}
CONTRAST_MAP = {0: "Normal", 1: "Soft", 2: "Hard"}
SATURATION_MAP = {0: "Normal", 1: "Low Saturation", 2: "High Saturation"}
SHARPNESS_MAP = {0: "Normal", 1: "Soft", 2: "Hard"}
GAIN_CONTROL_MAP = {0: "None", 1: "Low Gain Up", 2: "High Gain Up", 3: "Low Gain Down", 4: "High Gain Down"}
SENSING_METHOD_MAP = {
    1: "Not Defined", 2: "One-chip Color Area Sensor", 3: "Two-chip Color Area Sensor",
    4: "Three-chip Color Area Sensor", 5: "Color Sequential Area Sensor",
    7: "Trilinear Sensor", 8: "Color Sequential Linear Sensor"
}
RESOLUTION_UNIT_MAP = {1: "No Absolute Unit", 2: "Inch", 3: "Centimeter"}
CUSTOM_RENDERED_MAP = {0: "Normal Process", 1: "Custom Process"}