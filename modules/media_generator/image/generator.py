import os
import torch
from diffusers import StableDiffusionPipeline


MODEL_ID = "stable-diffusion-v1-5/stable-diffusion-v1-5"


def load_pipeline():
    """
    Load the Stable Diffusion image-generation pipeline.
    """

    device = "cuda" if torch.cuda.is_available() else "cpu"

    print("Device:", device)

    pipe = StableDiffusionPipeline.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32
    )

    pipe = pipe.to(device)

    return pipe, device


def generate_image(prompt, output_path):
    """
    Generate an image from a text prompt.

    Parameters:
        prompt (str): Description of the image to generate.
        output_path (str): Location where the generated image is saved.

    Returns:
        str: Path of the generated image.
    """

    pipe, device = load_pipeline()

    print("Generating image...")
    print("Prompt:", prompt)

    image = pipe(
        prompt,
        height=512,
        width=512,
        num_inference_steps=20
    ).images[0]

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    image.save(output_path)

    print("Image generated successfully!")
    print("Saved to:", output_path)

    return output_path


if __name__ == "__main__":

    test_prompt = (
        "A clean educational illustration of the solar system, "
        "planets arranged around the Sun, scientific textbook style"
    )

    output_path = "modules/media_generator/output/test_solar_system.png"

    generate_image(
        test_prompt,
        output_path
    )