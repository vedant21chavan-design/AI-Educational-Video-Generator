import os
import torch
from diffusers import StableDiffusionPipeline


# ============================================================
# LOCAL MODEL CONFIGURATION
# ============================================================

MODEL_ID = "runwayml/stable-diffusion-v1-5"


# Keep the model loaded in memory after the first load.
# This prevents loading the 5+ GB model again for every image.
_pipeline = None
_device = None


# ============================================================
# LOAD MODEL
# ============================================================

def load_pipeline():
    """
    Load the Stable Diffusion image-generation pipeline.

    The model is loaded only once and reused for
    subsequent image-generation requests.
    """

    global _pipeline, _device

    if _pipeline is not None:
        return _pipeline, _device

    _device = "cuda" if torch.cuda.is_available() else "cpu"

    print("Device:", _device)
    print("Loading image-generation model...")

    print("Model:", MODEL_ID)

    dtype = (
        torch.float16
        if _device == "cuda"
        else torch.float32
    )

    _pipeline = StableDiffusionPipeline.from_pretrained(
        MODEL_ID,
        torch_dtype=dtype
    )

    _pipeline = _pipeline.to(_device)

    print("Model loaded successfully.")

    return _pipeline, _device


# ============================================================
# IMAGE GENERATION
# ============================================================

def generate_image(prompt, output_path):
    """
    Generate an image from a text prompt.

    Parameters:
        prompt (str):
            Description of the image to generate.

        output_path (str):
            Location where the generated image is saved.

    Returns:
        str:
            Path of the generated image.
    """

    # Load or reuse the model.
    pipe, device = load_pipeline()

    print()
    print("Generating image...")
    print("Prompt:", prompt)
    print("Device:", device)

    # Generate image.
    image = pipe(
        prompt,
        height=512,
        width=512,
        num_inference_steps=20
    ).images[0]

    # Create output directory if necessary.
    output_dir = os.path.dirname(output_path)

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Save image.
    image.save(output_path)

    print()
    print("Image generated successfully!")
    print("Saved to:", output_path)

    return output_path


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_prompt = (
        "A clean educational illustration of the solar system, "
        "planets arranged around the Sun, "
        "scientific textbook style, "
        "clear labels, clean composition, "
        "educational diagram"
    )

    output_path = (
        "modules/media_generator/output/"
        "test_solar_system.png"
    )

    generate_image(
        test_prompt,
        output_path
    )