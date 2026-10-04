"""Print a line-by-line comparison of the engine against the sample PDF.

Run from the backend folder:  .venv\\Scripts\\python -m tests.compare_sample
"""

import sys

from app.astro import calculate_chart
from tests.darak_sample import BIRTH, KNOWN_SAMPLE_DIFFERENCES, compare


def main():
    # Windows consoles default to an encoding that cannot print every character
    sys.stdout.reconfigure(encoding="utf-8")

    rows = compare(calculate_chart(**BIRTH))
    width = max(len(r["item"]) for r in rows)
    sample_width = max(len(r["sample"]) for r in rows)

    print(f"{'ITEM'.ljust(width)}  {'SAMPLE PDF'.ljust(sample_width)}  ENGINE (Swiss Ephemeris)")
    print("-" * (width + sample_width + 40))
    for r in rows:
        flag = "ok  " if r["match"] else "DIFF"
        print(f"{r['item'].ljust(width)}  {r['sample'].ljust(sample_width)}  {flag} {r['engine']}")

    differences = [r for r in rows if not r["match"]]
    print()
    print(f"{len(rows) - len(differences)} of {len(rows)} values agree with the sample.")
    if differences:
        print("Differences:")
        for r in differences:
            reason = KNOWN_SAMPLE_DIFFERENCES.get(r["item"], "NEW - NOT YET EXPLAINED")
            print(f"  - {r['item']}: sample says {r['sample']}, engine says {r['engine']}")
            print(f"      why: {reason}")


if __name__ == "__main__":
    main()
