OUTPUT_DIR="/home/kevin/AI/ComfyUI/output"
LATENTS_DIR="/latents/test"
INPUT_DIR="/home/kevin/AI/ComfyUI/input"

from math import e
import os
import sys
from typing import Sequence, Mapping, Any, Union
import torch
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import safetensors


def is_kaggle():
    return os.environ.get("KAGGLE_KERNEL_TYPE") is not None

def is_colab():
    return os.environ.get("COLAB_GPU") is not None


if is_kaggle():
    from kaggle_secrets import UserSecretsClient
    user_secrets = UserSecretsClient()
    TENSOR_ENC_KEY = user_secrets.get_secret("tensor_enc_key")
elif is_colab():
    from google.colab import runtime
    TENSOR_ENC_KEY = runtime.get_secret("tensor_enc_key")
else:
    TENSOR_ENC_KEY = os.environ.get("TENSOR_ENC_KEY") if os.environ.get("TENSOR_ENC_KEY") is not None else ""


def get_value_at_index(obj: Union[Sequence, Mapping], index: int) -> Any:
    """Returns the value at the given index of a sequence or mapping.

    If the object is a sequence (like list or string), returns the value at the given index.
    If the object is a mapping (like a dictionary), returns the value at the index-th key.

    Some return a dictionary, in these cases, we look for the "results" key

    Args:
        obj (Union[Sequence, Mapping]): The object to retrieve the value from.
        index (int): The index of the value to retrieve.

    Returns:
        Any: The value at the given index.

    Raises:
        IndexError: If the index is out of bounds for the object and the object is not a mapping.
    """
    try:
        return obj[index]
    except KeyError:
        return obj["result"][index]

def find_path(name: str, path: str = None) -> str:
    """
    Recursively looks at parent folders starting from the given path until it finds the given name.
    Returns the path as a Path object if found, or None otherwise.
    """
    # If no path is given, use the current working directory
    if path is None:
        path = os.getcwd()

    # Check if the current directory contains the name
    if name in os.listdir(path):
        path_name = os.path.join(path, name)
        print(f"{name} found: {path_name}")
        return path_name

    # Get the parent directory
    parent_directory = os.path.dirname(path)

    # If the parent directory is the same as the current directory, we've reached the root and stop the search
    if parent_directory == path:
        return None

    # Recursively call the function with the parent directory
    return find_path(name, parent_directory)

def add_comfyui_directory_to_sys_path() -> None:
    """
    Add 'ComfyUI' to the sys.path
    """
    comfyui_path = "/home/kevin/AI/ComfyUI"
    if comfyui_path is not None and os.path.isdir(comfyui_path):
        sys.path.append(comfyui_path)
        print(f"'{comfyui_path}' added to sys.path")

def get_fernet_key_from_encoded_str(encoded_str: str) -> bytes:
    '''
    Derives a 32 byte key from an already salted secret string
    The salt is the first 16 bytes of the string and the rest is the secret
    '''
    salt = encoded_str[:16]
    secret = encoded_str[16:]
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=1200000,
    )
    return base64.urlsafe_b64encode(kdf.derive(secret))


def derive_key(secret: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=1200000,
    )
    return base64.urlsafe_b64encode(kdf.derive(secret.encode('utf-8')))


add_comfyui_directory_to_sys_path()

from nodes import NODE_CLASS_MAPPINGS
import os
import uuid
import shutil

def main():
    # Discover latents
    latents = []
    for root, dirs, files in os.walk(OUTPUT_DIR + LATENTS_DIR):
        for file in files:
            if file.endswith(".latent") and "__decode_processed" not in root:
                latents.append(os.path.join(root, file))
    print('Found ' + str(len(latents)) + ' latents to decode.')

    with torch.inference_mode():
        # Load VAE
        vaeloader = NODE_CLASS_MAPPINGS["VAELoader"]()
        vaeloader_1 = vaeloader.load_vae(vae_name="qwen_image_vae.safetensors")

        for idx, latent in enumerate(latents):
            try:
                print(f'Decoding {idx + 1} of {len(latents)}: `{latent}`', end=" ")

                orig_latent_filename = latent.split('/')[-1]
                # orig_latent_filename_path_rel_to_output = latent.replace(OUTPUT_DIR + '/', "")

                # Make a temporary copy of latent to inputs
                latent_filename = f"decode_{uuid.uuid4()}.latent"
                shutil.copy(latent, os.path.join(INPUT_DIR, latent_filename))

                # Load latent into memory
                loadlatent = NODE_CLASS_MAPPINGS["LoadLatent"]()
                loadlatent_2 = loadlatent.load(latent=latent_filename)

                # Run VAE Decode on latent
                vaedecode = NODE_CLASS_MAPPINGS["VAEDecode"]()
                vaedecode_3 = vaedecode.decode(
                    samples=get_value_at_index(loadlatent_2, 0),
                    vae=get_value_at_index(vaeloader_1, 0),
                )

                # Serialize latent tensor using safetensors
                decoded_tensor: torch.Tensor = get_value_at_index(vaedecode_3, 0)
                serialized_tensor = safetensors.torch.save({"dec": decoded_tensor.contiguous()})

                # Encrypt serialized tensor
                salt = os.urandom(16)
                key = derive_key(TENSOR_ENC_KEY, salt)
                encrypted_tensor = Fernet(key).encrypt(serialized_tensor)

                # Save encrypted tensor to original latent location, and append salt to filename
                # Example: `original_latent_filename.latent.<salt in hex>.enc`
                encrypted_tensor_filename = f"{orig_latent_filename}.{salt.hex()}.enc"
                with open(os.path.join(os.path.dirname(latent), encrypted_tensor_filename), 'wb') as f:
                    f.write(encrypted_tensor)
                
                print(f'-> `{encrypted_tensor_filename}`')
                
                # Delete temporary latent from input
                os.remove(os.path.join(INPUT_DIR, latent_filename))

                # Move original processed latent to ./__decode_processed
                os.makedirs(os.path.join(os.path.dirname(latent), "__decode_processed"), exist_ok=True)
                os.rename(latent, os.path.join(os.path.dirname(latent), "__decode_processed", os.path.basename(latent)))
            except Exception as e:
                print('Error:', e)
    
    print('VAE Decode finished.')

if __name__ == "__main__":
    # Testing only
    os.environ["TENSOR_ENC_KEY"] = "my_test_secret"

    main()