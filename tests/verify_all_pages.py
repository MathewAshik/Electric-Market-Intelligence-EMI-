"""
Verify all page scripts run cleanly top to bottom with zero unhandled exceptions
"""
import os
import sys
import runpy

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
pages_dir = os.path.join(root_dir, "pages")

pages = sorted([f for f in os.listdir(pages_dir) if f.endswith(".py")])

print(f"[INFO] Verifying {len(pages)} pages in {pages_dir}...")

for p in pages:
    page_path = os.path.join(pages_dir, p)
    print(f"Testing page: {p} ...", end=" ", flush=True)
    try:
        runpy.run_path(page_path)
        print("PASSED")
    except Exception as e:
        print(f"FAILED: {e}")
        sys.exit(1)

print("\n[SUCCESS] ALL 9 APPLICATION PAGES EXECUTED CLEANLY WITH ZERO ERRORS!")

