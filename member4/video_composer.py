import json
import os
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont

# Windows ships Arial by default, which is enough to render captions without
# needing any extra font install. Override with the VGP_CAPTION_FONT env var
# if a different machine doesn't have this file.
CAPTION_FONT = os.environ.get(
    "VGP_CAPTION_FONT",
    r"C:\\Windows\\Fonts\\arial.ttf",
)


def load_vgp(vgp_path):
    with open(vgp_path, "r", encoding="utf-8") as file:
        vgp = json.load(file)

    return vgp


def get_scenes(vgp):
    return vgp["scenes"]


def get_scene_durations(scenes):
    durations = [scene["duration"] for scene in scenes]

    for duration in durations:
        if duration <= 0:
            raise ValueError("Scene duration must be greater than 0")

    return durations


def get_scene_images(job_id, scenes):
    return [
        f"assets/{job_id}/scene_{scene['scene_id']}.png"
        for scene in scenes
    ]


def get_scene_audio(job_id, scenes):
    return [
        f"assets/{job_id}/scene_{scene['scene_id']}.wav"
        for scene in scenes
    ]


def validate_assets(image_paths, audio_paths):
    for image_path, audio_path in zip(image_paths, audio_paths):
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio not found: {audio_path}")

    return True


# ================================================================
# CAPTIONS
# ================================================================
#
# Earlier attempts used MoviePy's TextClip + CompositeVideoClip to overlay
# captions, sized and positioned using TextClip's own reported width/height.
# That kept producing bottom-of-frame cutoffs on longer (3-4 line) captions
# even after several fixes, which means the reported dimensions from that
# code path can't be trusted for placement.
#
# This version sidesteps that entirely: it burns the caption directly onto
# the scene's image pixels with PIL, measuring line widths/heights with the
# *exact same* PIL font object used to draw them. There is no cross-library
# guessing involved, so placement is correct by construction - the y
# position is computed directly from the measured text block height.

def _wrap_text_to_width(draw, text, font, max_width):
    """Word-wrap `text` so no line exceeds `max_width` pixels, measured
    with the actual font/draw context that will render it."""
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        candidate = f"{current_line} {word}".strip()
        left, top, right, bottom = draw.textbbox((0, 0), candidate, font=font)
        if (right - left) <= max_width or not current_line:
            current_line = candidate
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


def _burn_caption_onto_image(image_path, caption_text, output_path, font_size=26):
    """Draw `caption_text` onto a copy of the scene image, word-wrapped and
    centered near the bottom, guaranteed to stay inside the frame. Returns
    the path of the new (captioned) image."""
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    side_margin = 20
    bottom_margin = 20
    max_text_width = image.width - (side_margin * 2)
    max_block_height = int(image.height * 0.5)

    font = ImageFont.truetype(CAPTION_FONT, font_size)
    lines = _wrap_text_to_width(draw, caption_text, font, max_text_width)

    def _measure_block(lines, font):
        ascent, descent = font.getmetrics()
        line_height = ascent + descent
        line_spacing = int(line_height * 0.3)
        block_height = len(lines) * line_height + max(len(lines) - 1, 0) * line_spacing
        return line_height, line_spacing, block_height

    line_height, line_spacing, block_height = _measure_block(lines, font)

    # If the caption is too tall to fit (an unusually long narration
    # sentence), shrink the font instead of letting it overflow the frame.
    while block_height > max_block_height and font_size > 12:
        font_size -= 2
        font = ImageFont.truetype(CAPTION_FONT, font_size)
        lines = _wrap_text_to_width(draw, caption_text, font, max_text_width)
        line_height, line_spacing, block_height = _measure_block(lines, font)

    y = image.height - block_height - bottom_margin
    y = max(y, side_margin)  # final safety clamp, top edge

    for line in lines:
        left, top, right, bottom = draw.textbbox((0, 0), line, font=font)
        line_width = right - left
        x = max((image.width - line_width) / 2, side_margin)
        draw.text(
            (x, y),
            line,
            font=font,
            fill="white",
            stroke_width=2,
            stroke_fill="black",
        )
        y += line_height + line_spacing

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    image.save(output_path)
    return output_path


def create_video(
    image_paths,
    audio_paths,
    durations,
    output_path,
    fps=24,
    captions=None,
):
    """
    Create a video from a list of images.

    Parameters:
        image_paths: list of image file paths
        output_path: path where the video will be saved
        duration_per_image: duration of each image in seconds
        fps: video frame rate
        captions: optional list of strings, one per scene (e.g. each
            scene's narration), burned onto the video as text overlays.
    """

    clips = []
    validate_assets(image_paths, audio_paths)

    if len(image_paths) != len(audio_paths):
        raise ValueError("Number of images and audio files must match")

    if captions is not None and len(captions) != len(image_paths):
        raise ValueError("Number of captions must match number of scenes")

    # NOTE: `durations` (the VGP's LLM-guessed scene length) is accepted for
    # backward compatibility but is NOT used for timing anymore. The LLM's
    # guess frequently does not match how long the generated narration audio
    # actually is, which made scenes sit on screen in silence after the
    # narration finished. We now size each scene to the real audio length.
    for index, (image_path, audio_path) in enumerate(zip(image_paths, audio_paths)):
        audio_clip = AudioFileClip(audio_path)

        frame_source = image_path
        if captions:
            try:
                captioned_path = f"{image_path}.captioned.png"
                frame_source = _burn_caption_onto_image(
                    image_path, captions[index], captioned_path
                )
            except Exception as caption_error:
                # Don't let a missing font (or any renderer quirk) take
                # down the whole video - fall back to the plain image.
                print(
                    f"Caption rendering failed for scene {index + 1}, "
                    f"continuing without captions: {caption_error}"
                )
                frame_source = image_path

        image_clip = ImageClip(frame_source).with_duration(audio_clip.duration)
        video_clip = image_clip.with_audio(audio_clip)
        clips.append(video_clip)

    final_video = concatenate_videoclips(clips, method="compose")

    final_video.write_videofile(
        output_path,
        fps=fps
    )

    final_video.close()

    for clip in clips:
        clip.close()


if __name__ == "__main__":

    vgp = load_vgp("../output/JOB_010_vgp.json")

    scenes = get_scenes(vgp)

    images = get_scene_images(vgp["job_id"], scenes)

    durations = get_scene_durations(scenes)

    audio_paths = get_scene_audio(vgp["job_id"], scenes)

    create_video(
        images,
        audio_paths,
        durations,
        "assets/vgp_audio_scene_test.mp4"
    )
