import sqlite3
import random
import string
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes


# 1. Initialize Database
def initialize_database():
    conn = sqlite3.connect("licenses.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS licenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            license_code TEXT UNIQUE,
            signature TEXT,
            expiration_date TEXT,
            revoked INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


# 2. Generate RSA Keys
def generate_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    with open("private_key.pem", "wb") as private_file:
        private_file.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    public_key = private_key.public_key()
    with open("public_key.pem", "wb") as public_file:
        public_file.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )
    print("Keys generated and saved.")


# 3. Generate License
def generate_license(length, duration):
    license_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    expiration_date = (datetime.now() + timedelta(days=duration)).strftime('%Y-%m-%d')

    with open("private_key.pem", "rb") as key_file:
        private_key = serialization.load_pem_private_key(key_file.read(), password=None)

    signature = private_key.sign(
        license_code.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    conn = sqlite3.connect("licenses.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO licenses (license_code, signature, expiration_date) VALUES (?, ?, ?)",
            (license_code, signature.hex(), expiration_date)
        )
        conn.commit()
        print(f"License generated: {license_code}")
        print(f"Expires on: {expiration_date}")
    except sqlite3.IntegrityError:
        print("License already exists.")
    conn.close()


# 4. Verify License
def verify_license(license_code):
    with open("public_key.pem", "rb") as key_file:
        public_key = serialization.load_pem_public_key(key_file.read())

    conn = sqlite3.connect("licenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT signature, expiration_date, revoked FROM licenses WHERE license_code = ?", (license_code,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        print("License not found.")
        return False

    signature, expiration_date, revoked = result

    if revoked:
        print("License has been revoked.")
        return False

    if datetime.strptime(expiration_date, '%Y-%m-%d') < datetime.now():
        print("License has expired.")
        return False

    try:
        public_key.verify(
            bytes.fromhex(signature),
            license_code.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        print("License is valid.")
        return True
    except Exception as e:
        print("License is invalid:", str(e))
        return False


# 5. Revoke License
def revoke_license(license_code):
    conn = sqlite3.connect("licenses.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE licenses SET revoked = 1 WHERE license_code = ?", (license_code,))
    if cursor.rowcount == 0:
        print("License not found.")
    else:
        print(f"License {license_code} has been revoked.")
    conn.commit()
    conn.close()


# 6. Command-Line Switches
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="License Manager")
    parser.add_argument("-i", "--initialize", action="store_true", help="Initialize the database and keys.")
    parser.add_argument("-g", "--generate", action="store_true", help="Generate a new license.")
    parser.add_argument("-v", "--verify", type=str, help="Verify a license key.")
    parser.add_argument("-r", "--revoke", type=str, help="Revoke a license key.")
    parser.add_argument("-d", "--duration", type=int, default=30, help="License duration in days (default: 30).")
    parser.add_argument("-l", "--length", type=int, default=16, help="License code length (default: 16).")

    args = parser.parse_args()

    if args.initialize:
        initialize_database()
        generate_keys()
    elif args.generate:
        generate_license(args.length, args.duration)
    elif args.verify:
        verify_license(args.verify)
    elif args.revoke:
        revoke_license(args.revoke)
    else:
        parser.print_help()
