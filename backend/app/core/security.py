# Encryption/decryption utilities for secure PII storage
import hashlib
from cryptography.fernet import Fernet

# In production, store/load this key securely (e.g., from KMS)
FERNET_KEY = Fernet.generate_key()
fernet = Fernet(FERNET_KEY)

def hash_value(value: str) -> str:
	return hashlib.sha256(value.encode()).hexdigest()

def encrypt_value(value: str) -> bytes:
	return fernet.encrypt(value.encode())

def decrypt_value(token: bytes) -> str:
	return fernet.decrypt(token).decode()
