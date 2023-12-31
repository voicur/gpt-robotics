import speech_recognition as sr
import tempfile
import abc
from openai import OpenAI
from faster_whisper import WhisperModel
import os

class VoiceDetectorRT(abc.ABC):
    def __init__(self):
        self.recognizer = sr.Recognizer()

    @abc.abstractmethod
    def transcribe_audio(self, audio_data):
        pass

    def listen_for_speech(self, microphone, timeout=1):
        with microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            audio_data = self.recognizer.listen(source, timeout=timeout)
        return audio_data

    def automatic_mode(self):
        microphone = sr.Microphone()
        print("Automatic mode is active. Start speaking.")
        while True:
            try:
                audio_data = self.listen_for_speech(microphone)
                if not audio_data or audio_data.get_raw_data() == b'':
                    print("No speech detected, continuing to listen...")
                    continue
                print("Processing speech...")
                transcription = self.transcribe_audio(audio_data)
                print("Transcription:", transcription)
                return transcription
            except sr.WaitTimeoutError:
                print("Listening timed out, no speech detected.")
                continue
            except Exception as e:
                print(f"An error occurred: {e}")
                break

    def manual_mode(self):
        microphone = sr.Microphone()
        input("Press Enter to start recording")
        print("Recording started. Press Enter again to stop.")
        audio_data = self.listen_for_speech(microphone, timeout=None)
        input("Press Enter to stop recording and process speech.")
        print("Processing speech...")
        transcription = self.transcribe_audio(audio_data)
        print("Transcription:", transcription)

# Define the online voice detector subclass
class OnlineVoiceDetector(VoiceDetectorRT):
    def __init__(self, api_key):
        super().__init__()
        self.client = OpenAI(api_key=api_key)

    def transcribe_audio(self, audio_data):
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as fp:
            fp.write(audio_data.get_wav_data())
            fp.flush()  # Ensure all data is written to the file
            temp_filename = fp.name  # Get the name of the temporary file

        # Open the temporary file in "binary" read mode
        with open(temp_filename, 'rb') as audio_file:
            try:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file  # Pass the file object directly
                )
            except Exception as e:
                print(f"An error occurred: {e}")
                return None
            finally:
                os.remove(temp_filename)  # Ensure the temp file is deleted

        return response.text  # Make sure to access the text from the response correctly
    
    def transcribe_file(self, file_path):
        # Open the audio file in binary read mode
        with open(file_path, 'rb') as audio_file:
            try:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file  # Pass the file object directly
                )
            except Exception as e:
                print(f"An error occurred: {e}")
                return None

        return response.text  # Make sure to access the text from the response correctly

# Define the on-device voice detector subclass
class DeviceVoiceDetector(VoiceDetectorRT):
    def __init__(self, model_size="large-v2", device="cpu", compute_type="float32"):
        super().__init__()
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)

    def transcribe_audio(self, audio_data):
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=True) as fp:
            fp.write(audio_data.get_wav_data())
            fp.seek(0)
            segments, _ = self.model.transcribe(fp.name, beam_size=8)
            segments = list(segments)  # The transcription will actually run here.
        return " ".join(segment.text for segment in segments)

    def transcribe_file(self, file_path):
        segments, _ = self.model.transcribe(file_path, beam_size=8)
        segments = list(segments)  # The transcription will actually run here.
        return " ".join(segment.text for segment in segments)
    
# Main execution logic
if __name__ == "__main__":
    choice = input("Choose transcription mode (online/device): ").strip().lower()
    mode = input("Choose mode (automatic/manual): ").strip().lower()

    if choice == "online":
        api_key = "sk-your-key-here"  # Replace with your actual OpenAI API key
        voice_detector = OnlineVoiceDetector(api_key=api_key)
    elif choice == "device":
        voice_detector = DeviceVoiceDetector()
    else:
        print("Invalid transcription mode selected.")
        exit()

    if mode == "automatic":
        voice_detector.automatic_mode()
    elif mode == "manual":
        voice_detector.manual_mode()
    else:
        print("Invalid mode selected.")