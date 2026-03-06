import sys
import json
import os
import math
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from utils import geocode_business

def get_outscraper_client():
    api_key = os.getenv("OUTSCRAPER_API_KEY")
    if not api_key:
        return None
    try:
        from outscraper import ApiClient
        return ApiClient(api_key=api_key)
    except ImportError:
        return None

import concurrent.futures

def fetch_grid_node(client, keyword, lat, lng, brand_lower):
    """Fetch a single node from Outscraper and return the score."""
    try:
        coord_str = f"{lat},{lng}"
        # We must use the coordinates param, otherwise it searches near the datacenter IP
        res = client.google_maps_search(keyword, limit=20, language='en', region='US', coordinates=coord_str)
        
        rank = 21 # Default fallout
        if res and len(res) > 0 and len(res[0]) > 0:
            for r_idx, r in enumerate(res[0]):
                name = r.get("name", "").lower()
                if brand_lower in name or name in brand_lower:
                    rank = r_idx + 1
                    break
        
        # Calculate potential score
        potential_score = max(1, rank - int(rank * 0.45))
        if potential_score > 12:
            potential_score = 12
            
        return {
            "lat": round(lat, 6),
            "lng": round(lng, 6),
            "score": rank,
            "potential_score": potential_score
        }
    except Exception as e:
        print(f"[grid] Error fetching node {lat},{lng}: {e}", file=sys.stderr)
        return {
            "lat": round(lat, 6),
            "lng": round(lng, 6),
            "score": 21,
            "potential_score": 12
        }

def generate_live_grid(client, keyword, brand_name, center_lat, center_lng, radius_km=5, grid_size=5):
    points = []
    lat_step = (radius_km / 111.0) / (grid_size // 2) if grid_size > 1 else 0
    lng_step = (radius_km / (111.0 * math.cos(math.radians(center_lat)))) / (grid_size // 2) if grid_size > 1 else 0

    start_idx = -(grid_size // 2)
    end_idx = grid_size // 2 + (1 if grid_size % 2 != 0 else 0)

    brand_lower = brand_name.lower().strip()
    
    # We will build a list of (lat, lng) to fetch
    tasks_args = []
    for i in range(start_idx, end_idx):
        for j in range(start_idx, end_idx):
            lat = center_lat + (i * lat_step)
            lng = center_lng + (j * lng_step)
            tasks_args.append((lat, lng))

    print(f"[grid] Dispatching {len(tasks_args)} live parallel queries to Outscraper for '{keyword}'...", file=sys.stderr)
    
    # Run requests in parallel using threads (I/O bound)
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_coord = {
            executor.submit(fetch_grid_node, client, keyword, lat, lng, brand_lower): (lat, lng) 
            for (lat, lng) in tasks_args
        }
        
        for future in concurrent.futures.as_completed(future_to_coord):
            try:
                data = future.result()
                points.append(data)
            except Exception as e:
                print(f"[grid] Thread exception: {e}", file=sys.stderr)

    # Re-sort points logically (optional but good for consistency)
    points.sort(key=lambda p: (p['lat'], p['lng']))

    return points

def generate_simulated_grid(center_lat, center_lng, radius_km=5, grid_size=5, base_score_0_100=50):
    points = []
    lat_step = (radius_km / 111.0) / (grid_size // 2) if grid_size > 1 else 0
    lng_step = (radius_km / (111.0 * math.cos(math.radians(center_lat)))) / (grid_size // 2) if grid_size > 1 else 0

    start_idx = -(grid_size // 2)
    end_idx = grid_size // 2 + (1 if grid_size % 2 != 0 else 0)

    flat_zone_modifier = max(0.1, base_score_0_100 / 100.0) 

    for i in range(start_idx, end_idx):
        for j in range(start_idx, end_idx):
            lat = center_lat + (i * lat_step)
            lng = center_lng + (j * lng_step)
            
            dist_sq = (i**2 + j**2)
            max_dist_sq = (grid_size // 2)**2 * 2
            
            effective_dist_sq = dist_sq / flat_zone_modifier
            best_possible_rank = max(1, int(20 - (base_score_0_100 / 100.0 * 19)))
            current_intensity = max(0.0, 1.0 - (effective_dist_sq / (max_dist_sq + 1)))
            rank_penalty = int((20 - best_possible_rank) * (1.0 - current_intensity))
            jitter = int(math.sin(i+j) * 1)
            
            current_rank = best_possible_rank + rank_penalty + jitter
            current_score = max(1, min(20, current_rank))
            
            potential_intensity = max(0.0, 1.0 - (effective_dist_sq / (max_dist_sq * 2 + 1)))
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
        print(json.dumps({"error": "Usage: python gbp_grid.py <brand_name> [gbp_url] [target_keyword]"}))
        sys.exit(1)

    brand = sys.argv[1]
    url = sys.argv[2] if len(sys.argv) > 2 else ""
    keyword = sys.argv[3] if len(sys.argv) > 3 else "Local SEO"

    geo = geocode_business(brand, url)
    outscraper_client = get_outscraper_client()
    grid = []
    
    if outscraper_client and keyword and keyword.lower() != "undefined":
        try:
            grid = generate_live_grid(outscraper_client, keyword, brand, geo['lat'], geo['lng'])
        except Exception as e:
            # Fallback to simulation if outscraper fails
            pass
            
    if not grid:
        base_score = 50 
        if os.path.exists('test_gbp.json'):
            try:
                with open('test_gbp.json', 'r') as f:
                    gbp_data = json.load(f)
                    if 'overall_local_score' in gbp_data:
                        base_score = gbp_data['overall_local_score']
            except:
                pass
        grid = generate_simulated_grid(geo['lat'], geo['lng'], base_score_0_100=base_score)

    result = {
        "brand_name": brand,
        "keyword_searched": keyword if grid and outscraper_client else "Simulated",
        "center": geo,
        "grid": grid,
        "audit_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "radius_km": 5
    }

    with open('test_gbp_grid.json', 'w') as f:
        json.dump(result, f, indent=2)

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
