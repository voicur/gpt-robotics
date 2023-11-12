import speech_recognition as sr
import tempfile
from faster_whisper import WhisperModel

# Initialize the Whisper model to run on CPU with float32 precision
model = WhisperModel("large-v2", device="cpu", compute_type="float32")

def listen_for_speech(recognizer, microphone, timeout=1):
    """
    Listen for a single phrase from `microphone` and return the audio data.
    :param recognizer: An instance of Recognizer to perform recognition.
    :param microphone: The microphone instance to listen to.
    :param timeout: The amount of silence (in seconds) to wait before considering the end of the phrase.
    :return: The audio data of the detected speech.
    """
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
        audio_data = recognizer.listen(source, timeout=timeout)
    return audio_data

def transcribe_audio(audio_file_path):
    """
    Transcribe the provided audio file.
    :param audio_file_path: The path to the audio file to transcribe.
    :return: The transcription text.
    """
    # Transcribe the audio file using faster-whisper
    segments, _ = model.transcribe(audio_file_path, beam_size=5)
    segments = list(segments)  # The transcription will actually run here.

    # Extract the text from the segments
    transcription = " ".join(segment.text for segment in segments)

    return transcription

def automatic_mode():
    """
    Automatic mode for real-time speech recognition and transcription.
    """
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    print("Automatic mode is active. Start speaking.")
    while True:
        try:
            audio_data = listen_for_speech(recognizer, microphone)
            # If the audio data is empty, continue listening
            if not audio_data or audio_data.get_raw_data() == b'':
                print("No speech detected, continuing to listen...")
                continue
            print("Processing speech...")
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=True) as fp:
                fp.write(audio_data.get_wav_data())
                fp.seek(0)
                transcription = transcribe_audio(fp.name)
            print("Transcription:", transcription)
        except sr.WaitTimeoutError:
            continue
        except Exception as e:
            print(f"An error occurred: {e}")
            break

def manual_mode():
    """
    Manual mode where the user specifies when to start and stop recording.
    """
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    input("Press Enter to start recording")
    print("Recording started. Press Enter again to stop.")
    audio_data = listen_for_speech(recognizer, microphone, timeout=None)
    print("Press Enter to stop recording and process speech.")
    input()
    print("Processing speech...")
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=True) as fp:
        fp.write(audio_data.get_wav_data())
        fp.seek(0)
        transcription = transcribe_audio(fp.name)
    print("Transcription:", transcription)

if __name__ == "__main__":
    mode = input("Choose mode (automatic/manual): ").strip().lower()
    if mode == "automatic":
        automatic_mode()
    elif mode == "manual":
        manual_mode()
    else:
        print("Invalid mode selected.")