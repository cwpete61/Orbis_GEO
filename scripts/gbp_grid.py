import sys
import json
import os
import math
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from utils import geocode_business, get_distance_py

def generate_grid_points(center_lat, center_lng, radius_km=5, grid_size=5):
    """Generate a grid_size x grid_size grid of coordinates centered on a point."""
    points = []
    # Approx 111km per degree of latitude
    lat_step = (radius_km / 111.0) / (grid_size // 2) if grid_size > 1 else 0
    lng_step = (radius_km / (111.0 * math.cos(math.radians(center_lat)))) / (grid_size // 2) if grid_size > 1 else 0

    start_idx = -(grid_size // 2)
    end_idx = grid_size // 2 + (1 if grid_size % 2 != 0 else 0)

    for i in range(start_idx, end_idx):
        for j in range(start_idx, end_idx):
            lat = center_lat + (i * lat_step)
            lng = center_lng + (j * lng_step)
            
            # Simulated Visibility Score (1-20)
            dist_sq = (i**2 + j**2)
            max_dist_sq = (grid_size // 2)**2 * 2
            
            # CURRENT RANK
            # Center is best (Rank 1), drops off to Rank 20 at edges
            current_intensity = 1.0 - (dist_sq / (max_dist_sq + 1))
            current_rank = 1 + int(19 * (1.0 - current_intensity)) 
            current_score = max(1, min(20, current_rank + int(math.sin(i+j) * 2)))
            
            # POTENTIAL RANK (Optimized SEO/GEO/Service Pages)
            # Potential represents a "flatter" rank distribution (staying Rank 1-3 for much longer)
            # We simulate this by slowing down the fall-off
            potential_intensity = 1.0 - (dist_sq / (max_dist_sq * 2 + 1)) # Quadratic fall-off is halved
            potential_rank = 1 + int(19 * (1.0 - potential_intensity))
            # Potential score is always better or equal to current, maxed at Rank 1
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
    
    # Step 2: Generate Grid (5x5)
    grid = generate_grid_points(geo['lat'], geo['lng'])

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
