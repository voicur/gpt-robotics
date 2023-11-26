import csv
import os
import time
from whisper_rt import OnlineVoiceDetector
from whisper_rt import DeviceVoiceDetector

# Ensure the data directory exists
data_directory = "data"
os.makedirs(data_directory, exist_ok=True)
data_file_path = os.path.join(data_directory, "voice_recognition_test_results.csv")

# List of audio files for testing
audio_files = [
    "DRONE_VOICE_1.wav",
    "DRONE_VOICE_2.wav",
    "DRONE_VOICE_3.wav",
    "DRONE_VOICE_4.wav",
]

# Define a function to test voice recognition
def test_voice_recognition(voice_detector, audio_files):
    results = []

    for file_path in audio_files:
        for _ in range(15):  # Run each file 15 times
            start_time = time.time()
            transcription = voice_detector.transcribe_file(file_path)
            end_time = time.time()
            time_taken = end_time - start_time

            results.append({
                "file_path": file_path,
                "time_taken": time_taken,
                "transcription": transcription
            })

    return results

# Define a function to write results to a CSV file
def write_results_to_csv(results, file_path):
    with open(file_path, 'w', newline='') as csvfile:
        fieldnames = ['file_path', 'time_taken', 'transcription']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for result in results:
            writer.writerow(result)

# Main execution logic
if __name__ == "__main__":
    # Test both online and on-device transcription
    api_key = "sk-your-key-here"  # Replace with your actual OpenAI API key
    online_voice_detector = OnlineVoiceDetector(api_key=api_key)
    device_voice_detector = DeviceVoiceDetector()

    # Test online transcription
    online_results = test_voice_recognition(online_voice_detector, audio_files)
    write_results_to_csv(online_results, os.path.join(data_directory, "online_voice_recognition_test_results.csv"))

    # Test on-device transcription
    device_results = test_voice_recognition(device_voice_detector, audio_files)
    write_results_to_csv(device_results, os.path.join(data_directory, "device_voice_recognition_test_results.csv"))

    print(f"Online test results written to {os.path.join(data_directory, 'online_voice_recognition_test_results.csv')}")
    print(f"Device test results written to {os.path.join(data_directory, 'device_voice_recognition_test_results.csv')}")