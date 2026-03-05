import sys
import json
import math
import os
from datetime import datetime
from sim_utils import SimulationConstants, GeoEntity
from utils import get_distance_py

def calculate_simulation_score(distance_km, base_score, decay_rate):
    """
    Simulates a rank score based on distance and optimization decay.
    A 'flatter' decay rate means the business stays visible further out.
    """
    # Inverse square law simplified for GEO visibility
    # Score 1 is best (Rank 1), Score 20 is worst (Out of top 20)
    sim_rank = 1 + (base_score * (distance_km ** (1 + decay_rate)))
    return min(math.ceil(sim_rank), SimulationConstants.MAX_RANK)

def run_geo_simulation(brand_name, lat, lng, current_avg_score, is_optimized=False):
    """
    Generates a 5x5 grid of simulated visibility points.
    """
    radius = SimulationConstants.IDEAL_RADIUS_KM / 2
    grid_size = 5
    decay = SimulationConstants.OPTIMIZED_DECAY_RATE if is_optimized else SimulationConstants.BASELINE_DECAY_RATE
    
    # Base score represents the "core" visibility at the center (0.5 to 2.0 range)
    # Higher average score (0-100) reduces the base penalty
    base_penalty = max(0.5, 2.0 - (current_avg_score / 50.0))
    
    grid = []
    # Simplified grid generation logic
    for i in range(grid_size):
        for j in range(grid_size):
            # Calculate offset from center
            rel_lat = (i - (grid_size - 1) / 2) * (radius / 55.5) # approx km to deg
            rel_lng = (j - (grid_size - 1) / 2) * (radius / 55.5)
            
            p_lat = lat + rel_lat
            p_lng = lng + rel_lng
            
            dist = get_distance_py(lat, lng, p_lat, p_lng)
            score = calculate_simulation_score(dist, base_penalty, decay)
            
            grid.append({
                "lat": p_lat,
                "lng": p_lng,
                "score": score
            })
            
    return {
        "brand_name": brand_name,
        "is_optimized": is_optimized,
        "grid": grid,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Internal CLI test for the simulation engine
    if len(sys.argv) < 4:
        # Default test for LightBox SEO Allentown if no args
        test_brand = "LightBox SEO"
        test_lat = 40.6030
        test_lng = -75.4740
        test_score = 65
    else:
        test_brand = sys.argv[1]
        test_lat = float(sys.argv[2])
        test_lng = float(sys.argv[3])
        test_score = float(sys.argv[4]) if len(sys.argv) > 4 else 50
        
    baseline = run_geo_simulation(test_brand, test_lat, test_lng, test_score, is_optimized=False)
    optimized = run_geo_simulation(test_brand, test_lat, test_lng, test_score, is_optimized=True)
    
    result = {
        "baseline": baseline,
        "optimized": optimized,
        "comparison": {
            "avg_baseline": sum(p['score'] for p in baseline['grid']) / 25.0,
            "avg_optimized": sum(p['score'] for p in optimized['grid']) / 25.0,
            "delta": (sum(p['score'] for p in baseline['grid']) / 25.0) - (sum(p['score'] for p in optimized['grid']) / 25.0)
        }
    }
    
    print(json.dumps(result, indent=2))
