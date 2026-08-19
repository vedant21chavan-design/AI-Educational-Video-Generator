import os
import pyttsx3


def get_voices():
    """
    Get all voices available on the Windows system.

    Returns:
        list: Available voice objects.
    """

    engine = pyttsx3.init()

    voices = engine.getProperty("voices")

    print("\nAvailable voices:")

    for index, voice in enumerate(voices):
        print(
            f"{index}: "
            f"{voice.name} | "
            f"{voice.id}"
        )

    engine.stop()

    return voices


def generate_tts(
    text,
    output_path,
    voice_index=0,
    rate=160,
    volume=1.0
):
    """
    Generate speech from text using offline Windows TTS.

    Parameters:
        text (str):
            Text to convert into speech.

        output_path (str):
            Location where the audio file will be saved.

        voice_index (int):
            Index of the Windows voice to use.

        rate (int):
            Speech speed.

        volume (float):
            Volume from 0.0 to 1.0.

    Returns:
        str:
            Path of the generated audio file.
    """

    print("\nGenerating speech...")
    print("Text:", text)

    # Create output directory
    output_directory = os.path.dirname(output_path)

    if output_directory:
        os.makedirs(
            output_directory,
            exist_ok=True
        )

    # Initialize Windows TTS engine
    engine = pyttsx3.init()

    # Get installed voices
    voices = engine.getProperty("voices")

    if not voices:
        engine.stop()

        raise RuntimeError(
            "No Windows TTS voices were found."
        )

    # Make sure voice index is valid
    if voice_index < 0 or voice_index >= len(voices):
        print(
            f"Invalid voice index {voice_index}. "
            f"Using voice 0 instead."
        )

        voice_index = 0

    # Select voice
    selected_voice = voices[voice_index]

    engine.setProperty(
        "voice",
        selected_voice.id
    )

    # Speech speed
    engine.setProperty(
        "rate",
        rate
    )

    # Volume
    engine.setProperty(
        "volume",
        volume
    )

    print(
        "Voice:",
        selected_voice.name
    )

    print(
        "Saving audio to:",
        output_path
    )

    # Generate speech
    engine.save_to_file(
        text,
        output_path
    )

    engine.runAndWait()

    engine.stop()

    # Verify output
    if not os.path.exists(output_path):
        raise RuntimeError(
            "TTS generation failed. "
            "Audio file was not created."
        )

    file_size = os.path.getsize(output_path)

    if file_size == 0:
        raise RuntimeError(
            "TTS generation failed. "
            "Generated audio file is empty."
        )

    print("\nSpeech generated successfully!")
    print("Saved to:", output_path)
    print("File size:", file_size, "bytes")

    return output_path


if __name__ == "__main__":

    test_text = (
        "The solar system consists of the Sun "
        "and all the objects that orbit around it. "
        "These include eight planets, dwarf planets, "
        "moons, asteroids, and comets."
    )

    output_path = (
        "modules/media_generator/"
        "output/test_solar_system.wav"
    )

    generate_tts(
        text=test_text,
        output_path=output_path,
        voice_index=0,
        rate=160,
        volume=1.0
    )