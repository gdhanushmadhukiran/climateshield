"""ClimateShield Risk Intelligence Engine — Base Constants and Mathematical Utilities."""

from typing import Tuple, Dict, Any

ENGINE_VERSION = "v4.1.0-deterministic"

# Operational Risk Level Boundaries
# CRITICAL: >= 80
# HIGH: 65 - 79
# MODERATE: 45 - 64
# LOW: 0 - 44
LEVEL_CRITICAL_THRESHOLD = 80
LEVEL_HIGH_THRESHOLD = 65
LEVEL_MODERATE_THRESHOLD = 45


def get_risk_level(score: int) -> str:
    """Determines categorical risk level based on operational thresholds."""
    if score >= LEVEL_CRITICAL_THRESHOLD:
        return "CRITICAL"
    elif score >= LEVEL_HIGH_THRESHOLD:
        return "HIGH"
    elif score >= LEVEL_MODERATE_THRESHOLD:
        return "MODERATE"
    else:
        return "LOW"


def clamp(val: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
    """Clamps a floating point value within [min_val, max_val]."""
    return max(min_val, min(max_val, val))


def linear_scale(val: float, in_min: float, in_max: float, out_min: float = 0.0, out_max: float = 100.0) -> float:
    """Scales a value linearly from [in_min, in_max] to [out_min, out_max] with strict bounding."""
    if in_max <= in_min:
        return out_min
    norm = (val - in_min) / (in_max - in_min)
    scaled = out_min + norm * (out_max - out_min)
    return clamp(scaled, min(out_min, out_max), max(out_min, out_max))
