import os
from io import BytesIO
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from dotenv import load_dotenv

load_dotenv()

SALT_SIZE = 16
NONCE_SIZE = 12
KEY_SIZE = 32
PBKDF2_ITERATIONS = 100000


def _get_passphrase() -> bytes:
    passphrase = os.getenv("ENCRYPTION_PASSPHRASE")
    if not passphrase:
        raise ValueError(
            "ENCRYPTION_PASSPHRASE not found in environment variables. "
            "Please set it in your .env file."
        )
    return passphrase.encode('utf-8')


def _derive_key(passphrase: bytes, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
        backend=default_backend()
    )
    return kdf.derive(passphrase)


def encrypt_file(input_path: str, output_path: str) -> None:
    passphrase = _get_passphrase()
    salt = os.urandom(SALT_SIZE)
    key = _derive_key(passphrase, salt)
    
    aesgcm = AESGCM(key)
    nonce = os.urandom(NONCE_SIZE)
    
    with open(input_path, 'rb') as f:
        plaintext = f.read()
    
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    
    with open(output_path, 'wb') as f:
        f.write(salt)
        f.write(nonce)
        f.write(ciphertext)
    
    print(f"Encrypted: {input_path} -> {output_path}")


def decrypt_file_to_memory(encrypted_path: str) -> BytesIO:
    passphrase = _get_passphrase()
    
    with open(encrypted_path, 'rb') as f:
        salt = f.read(SALT_SIZE)
        nonce = f.read(NONCE_SIZE)
        ciphertext = f.read()
    
    key = _derive_key(passphrase, salt)
    aesgcm = AESGCM(key)
    
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    
    print(f"Decrypted to memory: {encrypted_path}")
    
    return BytesIO(plaintext)


def is_encrypted_file(file_path: str) -> bool:
    return file_path.endswith('.enc')
