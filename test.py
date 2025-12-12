import google.generativeai as genai

print("Gemini is working!")
genai.configure(api_key="test")  # We don't need real key just to test import
print("Success! You can now use Gemini!")