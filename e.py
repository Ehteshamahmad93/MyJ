import os
import requests
import speech_recognition as sr
import webbrowser

# Speak output
def speak(text):
    print("Jarvis:", text)
    os.system(f'espeak "{text}"')

# Flag to store last command to avoid repetition
last_command = ""

# Take voice or text input
def take_command():
    global last_command  # Reference to the global last_command variable
    try:
        r = sr.Recognizer()

        # Set up the microphone and adjust for ambient noise
        with sr.Microphone(device_index=0) as source:
            r.adjust_for_ambient_noise(source)  # Adjusts for background noise
            print("Listening...")
            audio = r.listen(source)
            print("Recognizing...")

            # Use recognize_google without the timeout parameter
            query = r.recognize_google(audio, language='en')  # Without timeout
            print(f"You said: {query}")

            # Check if the command is the same as the last one
            if query.lower() == last_command:  # If the command is the same as last one, skip
                print("Same command repeated, ignoring.")
                return None  # Or return something to indicate the command was ignored

            last_command = query.lower()  # Update the last command
            return query.lower()

    except sr.UnknownValueError:
        print("Sorry, I could not understand the audio.")
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Voice failed, switching to text.")
        text_input = input("You (text): ").lower()  # Get text input if voice fails

        # Check if the text input is the same as the last command
        if text_input == last_command:  # If text input is the same as the last command, skip
            print("Same command repeated, ignoring.")
            return None  # Or return something to indicate the command was ignored

        last_command = text_input  # Update the last command
        return text_input

# Open a website based on the voice or text command
def open_website(command):
    websites = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "facebook": "https://www.facebook.com",
        "twitter": "https://www.twitter.com",
        "wikipedia": "https://www.wikipedia.org",
        "instagram": "https://www.instagram.com",
    }

    for site, url in websites.items():
        # Print debug to see if the site name is being recognized
        print(f"Checking if '{site}' is in the command...")

        if site in command:
            print(f"Found match! Opening {site}...")
            webbrowser.open(url)
            speak(f"Opening {site}")
            return True
    # Debug to see if no match was found
    print("No website command matched.")
    return False

# Chat using Hugging Face Inference API
def chat(query):
    print("Command received:", query)
    print("Starting chat...")

    url = "https://api-inference.huggingface.co/models/google/flan-t5-small"
    headers = {"Authorization": f"Bearer your_api_key_here"}  # Replace with your Hugging Face API key
    payload = {"inputs": query}

    try:
        # Make the POST request to Hugging Face API
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            try:
                output = response.json()
                if isinstance(output, list) and "generated_text" in output[0]:
                    reply = output[0]["generated_text"]
                else:
                    reply = str(output)
                speak(reply)
            except Exception as e:
                speak("Sorry, something went wrong parsing the response.")
                print("Parse Error:", e)
        else:
            speak("Failed to get response from AI.")
            print("Error:", response.text)
    except requests.exceptions.RequestException as e:
        speak("Failed to make a request to the API.")
        print(f"Request Error: {e}")

# Main loop
def main():
    speak("Hello, I am Jarvis. How can I help you?")
    print("Hello from Jarvis!")
    last_query = ""
    is_chat_mode = False

    while True:
        query = take_command()
        if not query or query == last_query:
            continue  # Ignore empty or repeated input

        query = query.strip().lower()
        last_query = query

        if query in ["exit", "quit", "bye"]:
            speak("Goodbye!")
            break

        elif "chat" in query:
            is_chat_mode = True
            speak("Entering chat mode. Say 'exit chat' to leave.")
            continue

        elif "exit chat" in query:
            is_chat_mode = False
            speak("Exiting chat mode.")
            continue

        # Handle website opening commands
        if open_website(query):
            continue

        if is_chat_mode:
            chat(query)
        else:
            if "hi" in query or "hello" in query:
                speak("Hello! I am Jarvis. How can I help you?")
            else:
                speak(f"I heard '{query}', but I don't understand it yet.")

if __name__ == "__main__":
    main()