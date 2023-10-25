import pyttsx3

# Initialize the speech engine
engine = pyttsx3.init()

# List available voices
voices = engine.getProperty('voices')
for voice in voices:
    print("Voice:")
    print(" - ID:", voice.id)
    print(" - Name:", voice.name)
    print(" - Languages:", voice.languages)

# Select a voice (replace 'voice_id' with the ID of the desired voice)
voice_id = 'your_desired_portugal'
engine.setProperty('voice', 'portugal')
engine.setProperty('rate',155)



# Test the voice
engine.say("Olá Bernardo")

# Wait for the speech to finish
engine.runAndWait()
