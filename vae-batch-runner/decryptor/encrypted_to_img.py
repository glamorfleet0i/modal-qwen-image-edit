import os
import torch
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from safetensors import safe_open
from PIL import Image
import numpy as np

TENSOR_ENC_KEY = ""
OUTPUT_DIR="/home/kevin/AI/ComfyUI/output"
LATENTS_DIR="/latents/test"

def derive_key(secret: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=1200000,
    )
    return base64.urlsafe_b64encode(kdf.derive(secret.encode('utf-8')))


# Discover encrypted safetensors that end with .enc
tensors = []
for root, dirs, files in os.walk(OUTPUT_DIR + LATENTS_DIR):
    for file in files:
        if file.endswith(".enc") and "__decrypt_processed" not in root:
            tensors.append(os.path.join(root, file))
print('Found ' + str(len(tensors)) + ' encrypted image tensors to convert.')

with torch.inference_mode():
    for idx, tensor in enumerate(tensors):
        print(f'Converting {idx + 1} of {len(tensors)}: `{tensor}`', end=" ")

        tensor_filename = tensor.split('/')[-1]

        # 1. Decrypt tensor with filename "orig_file_name.<salt in hex>.enc"
        filename_parts = tensor_filename.split('.')
        if len(filename_parts) < 3:
            raise ValueError(f"Salt not found in filename: {tensor}")
        salt = filename_parts[-2]
        salt_bytes = bytes.fromhex(salt)

        # 2. Decrypt tensor
        with open(tensor, "rb") as f:
            encrypted_tensor = f.read()

        key = derive_key(TENSOR_ENC_KEY, salt_bytes)
        try:
            decrypted_tensor = Fernet(key).decrypt(encrypted_tensor)
        except:
            print("Failed to decrypt tensor: " + tensor)
            continue

        # Save tensor to file but remove salt from filename
        dec_filename = tensor.replace("." + salt + ".enc", ".safetensors")
        with open(dec_filename, "wb") as f:
            f.write(decrypted_tensor)
        
        # Load tensor from file
        with safe_open(dec_filename, framework="pt", device="cpu") as f:
            loaded_tensor = f.get_tensor("dec")

        # 4. Convert tensor to image
        for (batch_number, image) in enumerate(loaded_tensor):
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

        # 5. Save image next to encrypted tensor and remove salt from filename
        img_filename = tensor_filename.split('.')[0] + '.png'
        img.save(os.path.join(os.path.dirname(tensor), img_filename))

        print(f'-> {img_filename}')

        # Delete the decrypted_tensor file and move the .enc file to __decrypt_processed
        os.remove(dec_filename)
        os.makedirs(os.path.join(os.path.dirname(tensor), "__decrypt_processed"), exist_ok=True)
        os.rename(tensor, os.path.join(os.path.dirname(tensor), "__decrypt_processed", os.path.basename(tensor)))

print('Conversion finished.')
        