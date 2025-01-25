import sqlite3
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import base64
import os
import argparse

class LicenseManager:
    def __init__(self, db_path="licenses2.db"):
        self.db_path = db_path
        self.key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.key)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(''' 
                CREATE TABLE IF NOT EXISTS companies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute(''' 
                CREATE TABLE IF NOT EXISTS licenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    license_key TEXT NOT NULL,
                    expiration_date TIMESTAMP NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies (id)
                )
            ''')
            conn.commit()

    def generate_license(self, company_name, email, duration_days=365, key_length=32):
        # Ensure key_length is within reasonable bounds (16-128 bytes)
        key_length = max(16, min(128, key_length))
        
        # Generate a unique license key with specified length
        raw_key = base64.b64encode(os.urandom(key_length)).decode('utf-8')
        encrypted_key = self.cipher_suite.encrypt(raw_key.encode()).decode('utf-8')
        
        expiration_date = datetime.now() + timedelta(days=duration_days)
        expiration_date_str = expiration_date.strftime('%Y-%m-%d %H:%M:%S')
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create or get company
            cursor.execute(
                "INSERT OR IGNORE INTO companies (name, email) VALUES (?, ?)",
                (company_name, email)
            )
            
            cursor.execute(
                "SELECT id FROM companies WHERE email = ?",
                (email,)
            )
            company_id = cursor.fetchone()[0]
            
            # Create license
            cursor.execute(''' 
                INSERT INTO licenses 
                (company_id, license_key, expiration_date) 
                VALUES (?, ?, ?)
            ''', (company_id, encrypted_key, expiration_date_str))
            
            conn.commit()
            return encrypted_key

    def verify_license(self, license_key):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT l.id, l.license_key, l.expiration_date, l.is_active, 
                       c.name, c.email
                FROM licenses l
                JOIN companies c ON l.company_id = c.id
                WHERE l.license_key = ? AND l.is_active = TRUE
            ''', (license_key,))
            
            result = cursor.fetchone()
            if not result:
                return False, "Invalid or inactive license"
            
            expiration_date = datetime.strptime(result[2], '%Y-%m-%d %H:%M:%S')
            
            if expiration_date < datetime.now():
                return False, "License has expired"
                
            return True, {
                "company_name": result[4],
                "email": result[5],
                "expiration_date": result[2]
            }

    def revoke_license(self, license_key):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE licenses SET is_active = FALSE WHERE license_key = ?",
                (license_key,)
            )
            conn.commit()
            return cursor.rowcount > 0

def main():
    parser = argparse.ArgumentParser(description='License Manager CLI')
    parser.add_argument('-g', '--generate', action='store_true', help='Generate a new license')
    parser.add_argument('-v', '--verify', type=str, help='Verify a license key')
    parser.add_argument('-r', '--revoke', type=str, help='Revoke a license key')
    parser.add_argument('-d', '--duration', type=int, default=365, help='License duration in days (default: 365)')
    parser.add_argument('-l', '--length', type=int, default=32, 
                       help='License key length in bytes (default: 32, min: 16, max: 128)')
    
    args = parser.parse_args()
    manager = LicenseManager()

    if args.generate:
        company_name = input("Enter company name: ")
        email = input("Enter company email: ")
        license_key = manager.generate_license(
            company_name, 
            email, 
            duration_days=args.duration,
            key_length=args.length
        )
        print(f"\nGenerated license key: {license_key}")
        print(f"Duration: {args.duration} days")
        print(f"Key length: {args.length} bytes")
    
    elif args.verify:
        is_valid, result = manager.verify_license(args.verify)
        if is_valid:
            print("\nLicense is valid!")
            print(f"Company: {result['company_name']}")
            print(f"Email: {result['email']}")
            print(f"Expires: {result['expiration_date']}")
        else:
            print(f"\nLicense verification failed: {result}")
    
    elif args.revoke:
        if manager.revoke_license(args.revoke):
            print("\nLicense successfully revoked")
        else:
            print("\nFailed to revoke license: License key not found")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()