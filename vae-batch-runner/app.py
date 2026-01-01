import os
import shutil
import uuid
import json
import requests
import copy

LATENTS_DIR = "/home/kevin/AI/ComfyUI/output/latents"
INPUT_DIR = "/home/kevin/AI/ComfyUI/input"
COMFYUI_URL = "http://localhost:8188"

prompt = json.load(open("prompt.json", "r"))

# Walk through LATENTS_DIR and get all latents.
# Ignore any latents that are directly in a "processed" directory
latents = []
for root, dirs, files in os.walk(LATENTS_DIR):
    for file in files:
        if file.endswith(".latent") and "processed" not in root:
            latents.append(os.path.join(root, file))

# Process each latent recursively
for latent in latents:
    # Copy latent to INPUT_DIR and rename to vae_decode_current unix timestamp.latent
    latent_filename = f"vae_decode_{uuid.uuid4()}.latent"
    shutil.copy(latent, os.path.join(INPUT_DIR, latent_filename))

    print("Decoding latent: " + latent + " (" + latent_filename + ")")

    # Send latent to ComfyUI (POST /prompt)
    req = copy.deepcopy(prompt)
    req["prompt"]["2"]["inputs"]["latent"] = latent_filename
    response = requests.post(COMFYUI_URL + "/prompt", json=req)
    if response.status_code != 200:
        raise Exception("Failed to decode latent")
    
    # Remove latent from INPUT_DIR
    # os.remove(os.path.join(INPUT_DIR, latent_filename))

    # Move original latent to a processed directory within its original folder
    os.makedirs(os.path.join(os.path.dirname(latent), "processed"), exist_ok=True)
    os.rename(latent, os.path.join(os.path.dirname(latent), "processed", os.path.basename(latent)))
