import torch
from diffusers import StableDiffusionPipeline

MODEL_ID = "runwayml/stable-diffusion-v1-5"

device = "cuda" if torch.cuda.is_available() else "cpu"

print("Device:", device)

pipe = StableDiffusionPipeline.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.float16
)

pipe = pipe.to(device)

prompt = "A clean educational illustration of the solar system, planets arranged around the Sun, scientific textbook style"

image = pipe(
    prompt,
    height=512,
    width=512,
    num_inference_steps=20
).images[0]

image.save("test_solar_system.png")

print("Image generated successfully!")
print("Saved as: test_solar_system.png")