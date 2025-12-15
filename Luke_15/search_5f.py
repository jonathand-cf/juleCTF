
import sys

def search_5f(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    
    start = 0x1350
    end = 0x1e39
    
    print(f"Searching 5f in range {start:x}-{end:x}")
    for i in range(start, end):
        if data[i] == 0x5f:
            following = data[i+1:i+10].hex()
            print(f"Offset {i:x} (VA {0x400000+i:x}): 5f {following}")

if __name__ == "__main__":
    search_5f("main2")
