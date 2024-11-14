"""
This script helps to convert the problems which has testcases format
compatible with Themis by Le Minh Hoang & Do Duc Dong to the format
this project uses
Just place problem folders to convert/ in the same directory as this
script and run it
"""

import os

if not os.path.exists("convert"):
    exit()
    
entries = os.scandir("convert")
for entry in entries:
    if not entry.is_dir():
        continue
        
    print(f"Converting {entry.name}...")
    os.makedirs(f"problems/{entry.name}", exist_ok=True)
    count = 0
    scan = os.scandir(f"convert/{entry.name}")
    for i in scan:
        if not i.is_dir():
            continue
        if not i.name.lower().startswith("test"):
            continue
            
        try:
            with open(f"convert/{entry.name}/{i.name}/{entry.name}.inp", "rb") as f:
                _inp = f.read()
            with open(f"convert/{entry.name}/{i.name}/{entry.name}.out", "rb") as f:
                _out = f.read()
                
            os.makedirs(f"problems/{entry.name}/testcases", exist_ok=True)
            
            with open(f"problems/{entry.name}/testcases/{count + 1}.in", "wb") as f:
                f.write(_inp)
            with open(f"problems/{entry.name}/testcases/{count + 1}.out", "wb") as f:
                f.write(_out)

            count += 1
        
        except Exception as e:
            print(e)
    
    if not os.path.exists(f"problems/{entry.name}/config.cfg"):
        with open(f"problems/{entry.name}/config.cfg", "w", encoding="utf-8") as f:
            f.write("TEST_CASES=" + str(count) + "\n")
            
            # Optional
            f.write("TIME_LIMIT=1\n")
            f.write("MEMORY_LIMIT=1024\n")
        
    print(f"Converted {entry.name} with {count} testcases")
    