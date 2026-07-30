"""
make_key.py  —  set the security key for the Cattle Management software.

Run this ONCE on your own computer. It asks for a key you choose, then prints a
SALT and a HASH. You paste those two values into the app (or set them as
environment variables). Your actual key is never written anywhere by this tool —
it exists only while you type it. Keep the key in your head; if you forget it,
just run this again to set a new one.

    python make_key.py

Then copy the two lines it prints into cattlemanagementapp.py, replacing:
    ACCESS_SALT = os.environ.get("CATTLE_ACCESS_SALT", "")
    ACCESS_HASH = os.environ.get("CATTLE_ACCESS_HASH", "")
with the printed values, e.g.:
    ACCESS_SALT = os.environ.get("CATTLE_ACCESS_SALT", "Xk9...==")
    ACCESS_HASH = os.environ.get("CATTLE_ACCESS_HASH", "7Fa...==")
"""
import base64
import getpass
import hashlib
import sys

ITERATIONS = 240000
MIN_LEN = 8


def main():
    print("Set the security key for the Cattle Management software.")
    print("The key is NOT stored anywhere; only a one-way hash is produced.\n")

    key = getpass.getpass("Enter a new security key: ")
    if len(key) < MIN_LEN:
        print(f"\nToo short. Use at least {MIN_LEN} characters "
              "(longer and more random is stronger).")
        sys.exit(1)
    again = getpass.getpass("Re-enter the same key: ")
    if key != again:
        print("\nThe two entries did not match. Nothing was changed.")
        sys.exit(1)

    salt = __import__("os").urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", key.encode("utf-8"), salt, ITERATIONS)

    salt_b64 = base64.b64encode(salt).decode("ascii")
    hash_b64 = base64.b64encode(dk).decode("ascii")

    print("\n" + "=" * 64)
    print(" Paste these two values into cattlemanagementapp.py")
    print(" (replace the empty \"\" defaults on the ACCESS_SALT / ACCESS_HASH")
    print("  lines), OR set them as environment variables.")
    print("=" * 64 + "\n")
    print(f'ACCESS_SALT = os.environ.get("CATTLE_ACCESS_SALT", "{salt_b64}")')
    print(f'ACCESS_HASH = os.environ.get("CATTLE_ACCESS_HASH", "{hash_b64}")')
    print(f"# iterations = {ITERATIONS}\n")
    print("Done. Keep your key safe — it is the only copy, and it is not stored.")


if __name__ == "__main__":
    main()
