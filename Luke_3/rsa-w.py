import os
import sys
import time

from Crypto.Util.number import bytes_to_long, getPrime


FLAG = os.getenv("FLAG")
if FLAG is None:
    FLAG = "JUL{placeholder}"

message = f"Jeg vil ha flagget ({FLAG}) fordi "
message_censored = message.replace(FLAG, "SENSURERT")


def say(entity: str, message: str):
    print(f"{entity}: ", end="")
    for ch in message:
        print(ch, end="")
        sys.stdout.flush()
        time.sleep(0.03)


def main():
    global message

    say("JULENISSEN", "Hvorfor vil du ha flagget?")
    print("\n")

    while True:
        try:
            time.sleep(0.8)
            say("MEG", message_censored)
            answer = input()
            print()
            break
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception:
            time.sleep(0.8)
            say("JULENISSEN", "Prøv igjen...")
            print("\n")
            continue

    message += answer.strip()

    time.sleep(0.8)
    say(
        "JULENISSEN",
        "Du er på listen over slemme barn! Ingen dekrypterte flagg til deg i år.",
    )
    print("\n")

    time.sleep(0.8)
    say(
        "JULENISSEN",
        "Er du snill neste år så skal du selvfølgelig få flagg! I år får du slettes ikke annet enn et kryptert flagg.",
    )
    print("\n")

    time.sleep(0.8)
    say("JULENISSEN", "Ho, ho hooooo! God advent og gledelig jul!")
    print("\n")

    m = bytes_to_long(message.encode("utf-8"))

    p = getPrime(1024)
    q = getPrime(1024)
    N = p * q

    e = 2 ** 16 + 1

    w = m // N
    m = m % N

    c = pow(m, e, N)

    time.sleep(0.5)
    print(f"---\n{N=}\n{e=}\n{w=}\n{c=}\n---")


if __name__ == "__main__":
    main()
