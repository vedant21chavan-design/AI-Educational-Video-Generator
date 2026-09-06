"""
Target-length presets for generated videos.

Each scene's on-screen time is driven by how long its actual TTS narration
audio turns out to be (see member4/video_composer.py) - not by a guessed
duration field. That means controlling narration length IS how we control
total video length: no separate "trim the video to X seconds" step is
needed anywhere else in the pipeline.

TTS speaks at a fixed, known rate (see the `rate` setting in
modules/media_generator/tts/generator.py), so a target duration converts
directly into a per-scene word-count budget we can hand to the LLM when
asking it to write each scene's narration.

Caveat: LLMs are only approximate at hitting a requested word count, not
exact, so the resulting video should land roughly near the target -
expect it to vary, not to match to the second.
"""

# Must match the `rate` used in modules/media_generator/tts/generator.py's
# pyttsx3 engine - that setting is roughly this many words per minute.
SPEAKING_RATE_WPM = 160

PRESETS = {
    "short": {
        "label": "Short (~30s)",
        "target_seconds": 30,
        "scene_count": 3,
    },
    "medium": {
        "label": "Medium (~60s)",
        "target_seconds": 60,
        "scene_count": 5,
    },
    "long": {
        "label": "Long (~120s)",
        "target_seconds": 120,
        "scene_count": 8,
    },
}

DEFAULT_PRESET_KEY = "medium"


def get_preset(preset_key):
    """
    Look up a preset by key (e.g. "short"/"medium"/"long"), falling back
    to the default for a missing or unrecognized key rather than raising -
    this only affects roughly how long the video is, never something worth
    failing a whole job over.
    """
    key = (preset_key or "").strip().lower()
    return PRESETS.get(key, PRESETS[DEFAULT_PRESET_KEY])


def words_per_scene(preset):
    """
    Approximate word budget per scene's narration needed to hit this
    preset's target total duration, given the fixed TTS speaking rate.
    """
    words_per_second = SPEAKING_RATE_WPM / 60
    total_words = preset["target_seconds"] * words_per_second
    return max(int(round(total_words / preset["scene_count"])), 8)
