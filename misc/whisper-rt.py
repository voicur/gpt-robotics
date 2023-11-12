import speech_recognition as sr
import time
from openai import OpenAI
import os
import tempfile

# Initialize the OpenAI client
client = OpenAI(api_key="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")


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

def transcribe_audio(audio_data, model="whisper-1"):
    """
    Transcribe the provided audio data.
    :param audio_data: The audio data to transcribe.
    :param model: The Whisper model to use.
    :return: The transcription text.
    """
    # Save the audio data to a temporary file in a supported format
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as fp:
        fp.write(audio_data.get_wav_data())
        temp_filename = fp.name
    
    # Read the temporary file for sending to the API
    with open(temp_filename, 'rb') as audio_file:
        # Send the audio file to the API for transcription
        try:
            response = client.audio.transcriptions.create(
                model=model,
                file=audio_file
            )
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
    
    # Extract the text from the response
    transcription = response.text
    
    # Delete the temporary file
    os.remove(temp_filename)
    
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
                continue
            print("Processing speech...")
            transcription = transcribe_audio(audio_data)
            print("Transcription:", transcription)
        except sr.WaitTimeoutError:
            # Timeout reached, no speech detected
            continue
        except Exception as e:
            print(f"An error occurred: {e}")
            break;

def manual_mode():
    """
    Manual mode where the user specifies when to start and stop recording.
    """
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    input("Press Enter to start recording")
    print("Recording started. Press Enter again to stop.")
    audio_data = listen_for_speech(recognizer, microphone, timeout=None)
    input("Press Enter to stop recording and process speech.")
    print("Processing speech...")
    transcription = transcribe_audio(audio_data)
    print("Transcription:", transcription)

if __name__ == "__main__":
    mode = input("Choose mode (automatic/manual): ").strip().lower()
    if mode == "automatic":
        automatic_mode()
    elif mode == "manual":
        manual_mode()
    else:
        print("Invalid mode selected.")