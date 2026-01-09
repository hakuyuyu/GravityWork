#!/usr/bin/env python3
"""
Run the GravityWork evaluation pipeline.
"""
import sys
import asyncio
sys.path.insert(0, '/workspace')

from backend.services.evaluation import run_evaluation

if __name__ == "__main__":
    report = asyncio.run(run_evaluation())
    
    # Exit with appropriate code for CI/CD
    if report.accuracy >= 0.9:
        print("\n✅ Quality gate PASSED (>= 90%)")
        sys.exit(0)
    else:
        print(f"\n❌ Quality gate FAILED ({report.accuracy*100:.1f}% < 90%)")
        sys.exit(1)
