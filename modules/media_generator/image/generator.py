import os
import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler


# ============================================================
# LOCAL MODEL CONFIGURATION
# ============================================================

MODEL_PATH = (
    r"C:\Users\DEMEERA\.cache\huggingface\hub"
    r"\models--runwayml--stable-diffusion-v1-5"
    r"\snapshots\451f4fe16113bff5a5d2269ed5ad43b0592e9a14"
)

# Appended to every prompt to nudge Stable Diffusion toward sharper,
# cleaner output instead of its default average.
QUALITY_SUFFIX = ", detailed illustration, clean composition, high quality"

# Told to Stable Diffusion as what to AVOID. This is one of the single
# biggest levers for output quality on SD1.5 - without it, the model has
# no signal steering it away from its common failure modes (blurry,
# distorted anatomy, garbled text, watermarks, low detail).
NEGATIVE_PROMPT = (
    "blurry, low quality, low detail, distorted, deformed, disfigured, "
    "extra limbs, mutated, watermark, signature, text, letters, words, "
    "jpeg artifacts, grainy, out of frame, cropped"
)

# 20 steps was fast but left visible artifacts. 35 is still a couple of
# seconds per image on a GPU but noticeably sharper and more coherent.
NUM_INFERENCE_STEPS = 35


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

    print("Model path:", MODEL_PATH)

    dtype = (
        torch.float16
        if _device == "cuda"
        else torch.float32
    )

    _pipeline = StableDiffusionPipeline.from_pretrained(
    MODEL_PATH,
    torch_dtype=dtype,
    local_files_only=True
    )

    # DPM-Solver++ converges to a cleaner result in the same (or fewer)
    # steps than SD1.5's default scheduler - a straightforward quality
    # upgrade with no extra cost.
    _pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
        _pipeline.scheduler.config
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

    full_prompt = prompt + QUALITY_SUFFIX

    print()
    print("Generating image...")
    print("Prompt:", full_prompt)
    print("Device:", device)

    # Generate image.
    image = pipe(
        full_prompt,
        negative_prompt=NEGATIVE_PROMPT,
        height=512,
        width=512,
        num_inference_steps=NUM_INFERENCE_STEPS
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
