from Crypto import Random
from Crypto.Cipher import AES
import hashlib
import hmac
import jks
import os
import subprocess

# Hash + salt on passwords + restoration codes + authentication codes
#   to securely store them on the database
def hash(data):
    salt = os.urandom(16)
    dt_hash = hashlib.pbkdf2_hmac('sha512', data.encode("utf-8"), salt, 100000)

    enc = salt + dt_hash

    return enc.hex()

# Hash + salt on image names
#   to securely present them on the website
def hash_img_name(image_name):
    filename, file_extension = os.path.splitext(image_name)
    
    salt = os.urandom(16)
    dt_hash = hashlib.pbkdf2_hmac('sha1', filename.encode("utf-8"), salt, 100000)

    enc = salt + dt_hash
    secure_name = enc.hex() + file_extension 

    return secure_name

# Validate the entered password by hashing it using the extracted 
#   salt from the stored hash
def validate(entered, stored):
    stored = bytes.fromhex(stored)

    list1 = []
    start_b = 0
    list1.append(stored[start_b : start_b + 16])
    ext_salt = list1[0]

    list1.clear()

    start_b = 16
    list1.append(stored[start_b : start_b + 64])
    ext_hash = list1[0]

    entered_byte = bytes(entered, "utf-8")

    return hmac.compare_digest(
        ext_hash,
        hashlib.pbkdf2_hmac('sha512', entered_byte, ext_salt, 100000)
    )

# Generates 256-bit AES key and stores it 
#   in the keystore
def generate_key(key_store, alias, store_password):
    try:
        os.system(f"keytool -genseckey -alias {alias} -keypass {store_password} -keyalg AES -keysize 256 -keystore {key_store} -storepass {store_password} -storetype jceks")
        return True
    except Exception as e:
        return False

# Returns the key of the key entry from the key store
#   using the store password
def get_key(key_store, alias, store_password, key_password):
    key_store = jks.KeyStore.load(key_store, store_password)
    key_entry = key_store.secret_keys[alias]

    if not key_entry.is_decrypted():
        key_entry.decrypt(key_password)

    return key_entry.key

# AES block size pad
#
def pad(data):
    return data + b"\0" * (AES.block_size - len(data) % AES.block_size)

# AES 256 CBC encrypt the images to securely store them on the server
# 
def encrypt(data, key):
    data = pad(data)
    iv = Random.new().read(AES.block_size)
    enc = AES.new(key, AES.MODE_CBC, iv)

    return iv + enc.encrypt(data)

def encrypt_file(file_name, key):
    with open(file_name, "rb") as f:
        data = f.read()

    cipherText = encrypt(data, key)

    with open(file_name + ".enc", "wb") as f:
        f.write(cipherText)
    
    os.remove(file_name)

def encrypt_dir(dir_path, key):
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            file = root + "/" + file
            path, ext = os.path.splitext(file)

            if not ext == ".enc":
                encrypt_file(file, key)

# AES 256 CBC decrypt the images before presenting on the website
# 
def decrypt(ciphertext, key):
    iv = ciphertext[:AES.block_size]
    dec = AES.new(key, AES.MODE_CBC, iv)
    plainText = dec.decrypt(ciphertext[AES.block_size:])

    return plainText.rstrip(b"\0")

def decrypt_file(file_name, key):
    with open(file_name, "rb") as f:
        data = f.read()
    
    plainText = decrypt(data, key)

    with open(file_name[:-4], "wb") as f:
        f.write(plainText)

    os.remove(file_name)

def decrypt_dir(dir_path, key):
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            file = root + "/" + file
            path, ext = os.path.splitext(file)

            if ext == ".enc":
                decrypt_file(file, key)

# Returns the existance of a key through its alias
#   in a keystore
def key_exists(key_store, alias, store_password):
    command = f"keytool -list -v -alias {alias} -keystore {key_store} -storetype jceks -storepass {store_password}"
    
    try:
        data = str(subprocess.check_output(command.split(" ")).decode("utf-8"))
        return True if data.startswith("Alias") else False
    except:
        return False

# Changes (Re-creates) the key entry in the key store
#   for the same alias (same user) after a while
def change_key(key_store, alias, store_password):
    if delete_key(key_store, alias, store_password):
        return generate_key(key_store, alias, store_password)

# Deletes the key entry in the key store
#   in case the user delete's their account
def delete_key(key_store, alias, store_password):
    try:
        os.system(f"keytool -delete -alias {alias} -keystore {key_store} -storepass {store_password}")
        return True
    except:
        return False

# Changes the password of the key store
#   after a while
def change_store_pass(key_store, old_password, new_password):
    os.system(f"keytool -storepasswd -new {new_password} -keystore {key_store} -storepass {old_password} -storetype jceks")
