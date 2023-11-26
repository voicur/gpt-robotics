class Command:
    def __init__(self, app):
        self.app = app

    def marker(self, marker_id):
        print(f"Reached marker {marker_id}")

        # Capture the current image
        image_b64 = self.app.get_wait_for_b64_image()
        if image_b64 is None:
            print("Failed to capture image at marker.")
            return

        # Send updated context to the AI model
        prompt = f"Marker #{marker_id} reached"
        response = self.app.ask(prompt, b64_image_or_url=image_b64)

        # Extract and execute new commands
        new_commands = self.app.extract_python_code(response)
        if new_commands:
            print(new_commands)
            self.app.execute_commands(new_commands)