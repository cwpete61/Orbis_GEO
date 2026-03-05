import math

class SimulationConstants:
    """Standard constants for GEO-SEO simulations."""
    MAX_RANK = 20
    IDEAL_RADIUS_KM = 8
    BASELINE_DECAY_RATE = 0.5  # Typical "unoptimized" fall-off
    OPTIMIZED_DECAY_RATE = 0.2 # Goal "optimized" fall-off (flatter)
    
    # Weights for different visibility signals
    CITABILITY_WEIGHT = 0.35
    BRAND_AUTH_WEIGHT = 0.25
    LOCAL_AUTH_WEIGHT = 0.20
    PLATFORM_WEIGHT = 0.20

class GeoEntity:
    """Representation of a business entity for simulation."""
    def __init__(self, name, lat, lng, scores=None):
        self.name = name
        self.lat = lat
        self.lng = lng
        self.scores = scores or {
            "ai_citability": 0,
            "brand_authority": 0,
            "local_authority": 0,
            "platform_optimization": 0
        }

    def to_dict(self):
        return {
            "name": self.name,
            "coords": {"lat": self.lat, "lng": self.lng},
            "scores": self.scores
        }
