from math import e
import os
import random
import sys
from typing import Sequence, Mapping, Any, Union
import torch

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

add_comfyui_directory_to_sys_path()

from nodes import NODE_CLASS_MAPPINGS
import os
import uuid
import shutil
from pathlib import Path
from PIL import Image
from PIL.PngImagePlugin import PngInfo
from safetensors import safe_open

OUTPUT_DIR="/home/kevin/AI/ComfyUI/output"
LATENTS_DIR="/latents"
INPUT_DIR="/home/kevin/AI/ComfyUI/input"

def main():
    # Discover latents
    latents = []
    for root, dirs, files in os.walk(OUTPUT_DIR + LATENTS_DIR):
        for file in files:
            if file.endswith(".latent") and "processed" not in root:
                latents.append(os.path.join(root, file))
      
    print('Found ' + str(len(latents)) + ' latents to decode.')
    with torch.inference_mode():
        vaeloader = NODE_CLASS_MAPPINGS["VAELoader"]()
        vaeloader_1 = vaeloader.load_vae(vae_name="qwen_image_vae.safetensors")

        for idx, latent in enumerate(latents):
            try:
                print(f'Decoding {idx + 1} of {len(latents)}: `{latent}`', end=" ")

                orig_latent_filename_path_rel_to_output = latent.replace(OUTPUT_DIR + '/', "")

                # Move latent to inputs
                latent_filename = f"vae_decode_{uuid.uuid4()}.latent"
                shutil.copy(latent, os.path.join(INPUT_DIR, latent_filename))

                # Load latent from input
                loadlatent = NODE_CLASS_MAPPINGS["LoadLatent"]()
                loadlatent_2 = loadlatent.load(latent=latent_filename)

                # Run VAE Decode
                vaedecode = NODE_CLASS_MAPPINGS["VAEDecode"]()
                saveimage = NODE_CLASS_MAPPINGS["SaveImage"]()

                vaedecode_3 = vaedecode.decode(
                    samples=get_value_at_index(loadlatent_2, 0),
                    vae=get_value_at_index(vaeloader_1, 0),
                )

                saveimage_4 = saveimage.save_images(
                    filename_prefix=orig_latent_filename_path_rel_to_output,
                    images=get_value_at_index(vaedecode_3, 0),
                )

                try:
                    # Rename file to replace .latent_00001_.png with .latent.png
                    # Ex. ComfyUI_00001_.latent_00001_.png -> ComfyUI_00001_.latent.png
                    out_file = saveimage_4['ui']['images'][0]['filename']
                    out_file_path = OUTPUT_DIR + LATENTS_DIR + '/' + out_file
                    out_file_renamed_path = out_file_path.replace('.latent_00001_.png', '.latent.png')

                    # If the file already exists, leave it alone as duplicates are already enumerated
                    if not os.path.exists(out_file_renamed_path):
                        os.rename(out_file_path, out_file_renamed_path)
                except Exception as e:
                    out_file = 'unknown file'
                    print(f'Image name not found', end=" ")
                
                print(f'-> `{out_file}`')

                # Copy latent metadata to output image
                with safe_open(latent, framework="pt", device="cpu") as f:
                    latent_metadata = f.metadata()
                if latent_metadata is not None:
                    real_out_file_renamed_path = Path(out_file_renamed_path)
                    image = Image.open(real_out_file_renamed_path)
                    img_metadata = PngInfo()
                    for x in latent_metadata:
                        img_metadata.add_text(x, latent_metadata[x])
                    image.save(real_out_file_renamed_path, pnginfo=img_metadata)
                
                # Delete latent from input
                os.remove(os.path.join(INPUT_DIR, latent_filename))

                # Move processed latent
                os.makedirs(os.path.join(os.path.dirname(latent), "processed"), exist_ok=True)
                os.rename(latent, os.path.join(os.path.dirname(latent), "processed", os.path.basename(latent)))
            except Exception as e:
                print('Error:', e)
    
    print('VAE Decode finished.')

if __name__ == "__main__":
    main()