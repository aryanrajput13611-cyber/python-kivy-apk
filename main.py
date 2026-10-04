import threading
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.clock import mainthread

# अपनी Gemini API Key यहाँ डालें
API_KEY = "YOUR_GEMINI_API_KEY_HERE"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

class ChatApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.scroll = ScrollView(size_hint=(1, 0.85))
        self.chat_history = Label(
            text="[b]AI Agent:[/b] नमस्ते! मैं आपकी क्या मदद कर सकता हूँ?\n\n",
            markup=True,
            size_hint_y=None,
            halign='left',
            valign='top'
        )
        self.chat_history.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
        self.chat_history.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
        self.scroll.add_widget(self.chat_history)
        self.layout.add_widget(self.scroll)

        bottom_layout = BoxLayout(size_hint=(1, 0.15), spacing=10)
        self.user_input = TextInput(
            hint_text="अपना सवाल लिखें...",
            multiline=False,
            size_hint=(0.75, 1)
        )
        self.send_button = Button(
            text="Send",
            size_hint=(0.25, 1),
            background_color=(0.2, 0.6, 1, 1)
        )
        self.send_button.bind(on_press=self.send_message)

        bottom_layout.add_widget(self.user_input)
        bottom_layout.add_widget(self.send_button)
        self.layout.add_widget(bottom_layout)

        return self.layout

    def send_message(self, instance):
        prompt = self.user_input.text.strip()
        if not prompt:
            return

        self.chat_history.text += f"[b]You:[/b] {prompt}\n\n"
        self.user_input.text = ""
        self.send_button.disabled = True

        threading.Thread(target=self.call_gemini, args=(prompt,)).start()

    def call_gemini(self, prompt):
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=20)
            if response.status_code == 200:
                result = response.json()
                reply = result['candidates'][0]['content']['parts'][0]['text']
            else:
                reply = f"Error: API status {response.status_code}"
        except Exception as e:
            reply = f"Connection Error: {str(e)}"

        self.update_chat_ui(reply)

    @mainthread
    def update_chat_ui(self, reply):
        self.chat_history.text += f"[b]AI Agent:[/b] {reply.strip()}\n\n"
        self.send_button.disabled = False
        self.scroll.scroll_y = 0

if __name__ == "__main__":
    ChatApp().run()
