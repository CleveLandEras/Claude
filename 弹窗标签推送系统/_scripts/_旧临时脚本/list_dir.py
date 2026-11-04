import os
base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for root, dirs, files in os.walk(base):
    for f in sorted(files):
        p = os.path.join(root, f)
        print(os.path.relpath(p, base), os.path.getsize(p))
