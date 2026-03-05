import sys
import json
import os
import math
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from utils import geocode_business, get_distance_py

def generate_grid_points(center_lat, center_lng, radius_km=5, grid_size=5, base_score_0_100=50):
    """Generate a grid_size x grid_size grid of coordinates centered on a point.
    Scales the center visibility based on base_score_0_100 (which is an AI trust score)."""
    points = []
    # Approx 111km per degree of latitude
    lat_step = (radius_km / 111.0) / (grid_size // 2) if grid_size > 1 else 0
    lng_step = (radius_km / (111.0 * math.cos(math.radians(center_lat)))) / (grid_size // 2) if grid_size > 1 else 0

    start_idx = -(grid_size // 2)
    end_idx = grid_size // 2 + (1 if grid_size % 2 != 0 else 0)

    # Convert the 0-100 score into a "flat zone" modifier. 
    # If score is 95, the flat zone is huge (most of the grid is rank 1-3).
    # If score is 20, the flat zone is tiny (only the absolute center is rank 1, rapidly decaying).
    flat_zone_modifier = max(0.1, base_score_0_100 / 100.0) 

    for i in range(start_idx, end_idx):
        for j in range(start_idx, end_idx):
            lat = center_lat + (i * lat_step)
            lng = center_lng + (j * lng_step)
            
            # Simulated Visibility Score (1-20+)
            dist_sq = (i**2 + j**2)
            max_dist_sq = (grid_size // 2)**2 * 2
            
            # The higher the flat_zone_modifier, the lower the effective dist_sq penalty
            effective_dist_sq = dist_sq / (flat_zone_modifier * 3)
            
            # CURRENT RANK
            # Calculate the best possible rank for this business based on its AI trust score
            # A score of 100 means they can hit #1. A score of 20 means even at their doorstep they might only hit #14.
            best_possible_rank = max(1, int(20 - (base_score_0_100 / 100.0 * 19)))
            
            # Decay intensity based on distance from center
            current_intensity = max(0.0, 1.0 - (effective_dist_sq / (max_dist_sq + 1)))
            
            # Calculate rank penalty based on intensity dropoff
            rank_penalty = int((20 - best_possible_rank) * (1.0 - current_intensity))
            
            # Add trigonometric jitter to simulate fluctuating local search results
            jitter = int(math.sin(i+j) * 1)
            
            current_rank = best_possible_rank + rank_penalty + jitter
            current_score = max(1, min(20, current_rank))
            
            # POTENTIAL RANK (Optimized SEO/GEO/Service Pages)
            # Simulated by doubling the flat zone effect (expanding the max reach significantly)
            potential_intensity = max(0.0, 1.0 - (effective_dist_sq / (max_dist_sq * 2 + 1)))
            
            # Reduce the rank penalty for optimized SEO efforts
            potential_rank_penalty = int((20 - best_possible_rank) * (1.0 - potential_intensity) * 0.5)
            
            potential_rank = max(1, best_possible_rank - 2) + potential_rank_penalty + jitter
            potential_score = max(1, min(current_score, potential_rank))
            
            points.append({
                "lat": round(lat, 6),
                "lng": round(lng, 6),
                "score": current_score,
                "potential_score": potential_score
            })
    return points

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python gbp_grid.py <brand_name> [gbp_url]"}))
        sys.exit(1)

    brand = sys.argv[1]
    url = sys.argv[2] if len(sys.argv) > 2 else ""

    # Step 1: Geocode
    geo = geocode_business(brand, url)
    
    # Attempt to load the AI GBP score to ground the simulation in reality
    base_score = 50 
    if os.path.exists('test_gbp.json'):
        try:
            with open('test_gbp.json', 'r') as f:
                gbp_data = json.load(f)
                if 'overall_local_score' in gbp_data:
                    base_score = gbp_data['overall_local_score']
        except:
            pass

    # Step 2: Generate Grid (5x5) using the AI score as a radius modifier
    grid = generate_grid_points(geo['lat'], geo['lng'], base_score_0_100=base_score)

    result = {
        "brand_name": brand,
        "center": geo,
        "grid": grid,
        "audit_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "radius_km": 5
    }

    # Save to file for the PDF generator if needed
    with open('test_gbp_grid.json', 'w') as f:
        json.dump(result, f, indent=2)

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
