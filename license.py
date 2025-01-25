import random
import string
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import sqlite3

def generate_license():
    license_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

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
        cursor.execute("INSERT INTO licenses (license_code, signature) VALUES (?, ?)", (license_code, signature.hex()))
        conn.commit()
        print("license generated", license_code)
    except sqlite3.IntegrityError:
        print("license already exists")
    conn.close()

    return license_code

generate_license()
