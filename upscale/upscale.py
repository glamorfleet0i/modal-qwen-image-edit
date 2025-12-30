import os
import cv2
import torch
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer

def main():
    """
    Loads the RealESRGAN model and upscales all images from an 'original'
    directory to an 'upscaled' directory.
    """
    # --- Configuration ---
    input_folder = 'original'
    output_folder = 'upscaled'
    model_path = 'RealESRGAN_x4plus_anime_6B.pth'
    
    # Model-specific parameters for RealESRGAN_x4plus_anime_6B
    model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=6, num_grow_ch=32, scale=4)
    netscale = 4 # The upscale factor of the model

    # Determine device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    # --- Initialization ---
    try:
        # Initialize the upscaler
        upsampler = RealESRGANer(
            scale=netscale,
            model_path=model_path,
            model=model,
            tile=0, # Use 0 for no tiling
            tile_pad=10,
            pre_pad=0,
            half=True if device.type == 'cuda' else False, # Use half precision on GPU
            gpu_id=None if device.type == 'cpu' else 0
        )
    except Exception as e:
        print(f"Error initializing RealESRGANer: {e}")
        print("Please ensure 'RealESRGAN_x4plus_anime_6B.pth' is in the current directory.")
        return

    # Create output directory if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # --- Image Processing ---
    image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp'))]

    if not image_files:
        print(f"No images found in the '{input_folder}' directory.")
        return

    print(f"Found {len(image_files)} images to upscale.")

    for filename in image_files:
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        try:
            # Read image
            img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
            if img is None:
                print(f"Warning: Could not read image {filename}. Skipping.")
                continue

            print(f"Processing {filename}...")

            # Upscale the image
            output, _ = upsampler.enhance(img, outscale=netscale)

            # Save the upscaled image
            cv2.imwrite(output_path, output)
            print(f"Saved upscaled image to {output_path}")

        except Exception as error:
            print(f"Error processing file {filename}: {error}")

    print("\nUpscaling complete.")

if __name__ == '__main__':
    main()
