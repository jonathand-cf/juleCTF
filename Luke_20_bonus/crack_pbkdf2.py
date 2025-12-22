#!/usr/bin/env python3
"""
Parallel PBKDF2-SHA256 cracker for the provided Gogs hash.

Usage examples:
  python3 crack_pbkdf2.py --file ../../SecLists/Passwords/Leaked-Databases/rockyou.txt --start 0 --count 500000
  python3 crack_pbkdf2.py --file ../../SecLists/Passwords/Common-Credentials/darkweb2017_top-10000.txt
"""
import argparse
import binascii
import hashlib
import itertools
import sys
from multiprocessing import Pool, cpu_count

# Fixed target values from hash_new.txt / hash_correct.txt
SALT = b"nBiFIYAU2L"
TARGET = binascii.unhexlify(
    "ec55c2f083b287589fa9788a7adffe07bb49d8b83c441bb88cc6787ba9ea91c0"
    "2069341bc3f957af72bf84174062d8733a55"
)


def _check_pw(pw: str) -> str | None:
    """Return the password if it matches, else None."""
    if hashlib.pbkdf2_hmac("sha256", pw.encode(), SALT, 10000, dklen=50) == TARGET:
        return pw
    return None


def iter_range(fh, start: int, count: int | None):
    """Yield lines starting at `start` for `count` lines (or to EOF)."""
    for idx, line in enumerate(fh):
        if idx < start:
            continue
        if count is not None and idx >= start + count:
            break
        pw = line.rstrip("\r\n")
        if pw:
            yield pw


def main() -> int:
    ap = argparse.ArgumentParser(description="PBKDF2-SHA256 cracker (CPU, parallel).")
    ap.add_argument("--file", required=True, help="Path to wordlist")
    ap.add_argument("--start", type=int, default=0, help="Start line (0-indexed)")
    ap.add_argument(
        "--count", type=int, default=None, help="Number of lines to process (default: to EOF)"
    )
    ap.add_argument("--batch", type=int, default=5000, help="Batch size per map() call")
    ap.add_argument("--procs", type=int, default=cpu_count(), help="Worker processes")
    args = ap.parse_args()

    with open(args.file, "r", errors="ignore") as fh, Pool(args.procs) as pool:
        chunk_iter = iter_range(fh, args.start, args.count)
        while True:
            batch = list(itertools.islice(chunk_iter, args.batch))
            if not batch:
                print("Exhausted wordlist chunk without a hit.")
                return 1
            for result in pool.map(_check_pw, batch):
                if result:
                    print("FOUND:", result)
                    return 0
            # progress indicator
            args.start += len(batch)
            if args.start % 50000 == 0:
                print(f"Checked {args.start} candidates...", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
