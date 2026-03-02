#!/usr/bin/env python3
"""
Batch Auditor — Runs GEO-SEO audits for multiple URLs in one pass.
Outputs a combined summary JSON and triggers individual score calculations.
"""

import sys
import json
import subprocess
import os

def run_audit(url: str, output_dir: str):
    """Run core audit scripts for a single URL."""
    print(f"--- Auditing: {url} ---")
    
    # 1. Fetch Page
    fetch_cmd = ["python", "scripts/fetch_page.py", url]
    fetch_out = subprocess.check_output(fetch_cmd).decode('utf-8')
    fetch_data = json.loads(fetch_out)
    
    # 2. Score Citability
    score_cmd = ["python", "scripts/citability_scorer.py", url]
    score_out = subprocess.check_output(score_cmd).decode('utf-8')
    score_data = json.loads(score_out)
    
    # 3. Analyze Crawlers
    crawler_cmd = ["python", "scripts/llmstxt_generator.py", url]
    crawler_out = subprocess.check_output(crawler_cmd).decode('utf-8')
    crawler_data = json.loads(crawler_out)
    
    return {
        "url": url,
        "fetch_status": "SUCCESS" if "error" not in fetch_data else "FAILED",
        "citability_score": score_data.get("average_citability_score", 0),
        "crawler_access": crawler_data.get("access_summary", "UNKNOWN"),
        "timestamp": "2026-03-02"
    }

def batch_process(input_file: str):
    """Process all URLs in a file."""
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    with open(input_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    results = []
    for url in urls:
        try:
            res = run_audit(url, "output")
            results.append(res)
        except Exception as e:
            print(f"Failed to audit {url}: {e}")
            results.append({"url": url, "status": "ERROR", "error": str(e)})

    # Final summary
    summary = {
        "batch_total": len(urls),
        "results": results,
        "average_score": sum(r.get("citability_score", 0) for r in results) / len(results) if results else 0
    }
    
    with open("BATCH-AUDIT-SUMMARY.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print("\n--- BATCH AUDIT COMPLETE ---")
    print(f"Stats: {len(urls)} URLs processed.")
    print(f"Average Citability: {summary['average_score']}/100")
    print("Summary saved to: BATCH-AUDIT-SUMMARY.json")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python batch_audit.py <urls.txt>")
        print("Create a text file with one URL per line.")
        sys.exit(1)
        
    batch_process(sys.argv[1])
