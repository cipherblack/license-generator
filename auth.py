from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes ,serialization
import sqlite3

def verify_license(license_code):
    with open("public_key.pem", "rb") as key_file:
        public_key = serialization.load_pem_public_key(key_file.read())

    conn = sqlite3.connect("licenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT signature FROM licenses WHERE license_code = ?", (license_code,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        print("license not found")
        return False

    signature = bytes.fromhex(result[0])

    try:
        public_key.verify(
            signature,
            license_code.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        print("license is valid")
        return True
    except Exception as e:
        print("license is invalid ", str(e))
        return False

license_to_check = input("Enter the license code: ")
verify_license(license_to_check)
