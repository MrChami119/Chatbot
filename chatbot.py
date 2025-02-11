import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
from huggingface_hub import InferenceClient
from typing import Optional

class ChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Chatbot")
        self.root.geometry("600x800")
        
        # Initialize the Hugging Face client
        # Replace with your API key
        self.api_key = "xxxxxxxxxxxxx"
        self.client = InferenceClient(api_key=self.api_key)
        
        self.setup_gui()
        
    def setup_gui(self):
        # Create main container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(
            main_container,
            wrap=tk.WORD,
            width=50,
            height=30
        )
        self.chat_display.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.chat_display.config(state='disabled')
        
        # User input field
        self.user_input = ttk.Entry(
            main_container,
            width=40
        )
        self.user_input.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        self.user_input.bind("<Return>", self.send_message)
        
        # Send button
        send_button = ttk.Button(
            main_container,
            text="Send",
            command=self.send_message
        )
        send_button.grid(row=1, column=1, sticky=(tk.E))
        
        # Configure grid weights
        main_container.columnconfigure(0, weight=3)
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(0, weight=1)
        
        # Loading indicator
        self.loading_label = ttk.Label(main_container, text="")
        self.loading_label.grid(row=2, column=0, columnspan=2)
        
    def update_chat_display(self, message: str, is_user: bool = True):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, f"{'You' if is_user else 'Bot'}: {message}\n\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state='disabled')
        
    def get_bot_response(self, user_message: str) -> Optional[str]:
        try:
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_message
                        }
                    ]
                }
            ]
            
            completion = self.client.chat.completions.create(
                model="meta-llama/Llama-3.2-11B-Vision-Instruct",
                messages=messages,
                max_tokens=500
            )
            
            return completion.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"
            
    def send_message(self, event=None):
        user_message = self.user_input.get().strip()
        if not user_message:
            return
            
        # Clear input field
        self.user_input.delete(0, tk.END)
        
        # Display user message
        self.update_chat_display(user_message, is_user=True)
        
        # Show loading indicator
        self.loading_label.config(text="Bot is typing...")
        
        # Get bot response in a separate thread
        def get_response():
            response = self.get_bot_response(user_message)
            self.root.after(0, self.handle_response, response)
            
        threading.Thread(target=get_response, daemon=True).start()
        
    def handle_response(self, response):
        # Hide loading indicator
        self.loading_label.config(text="")
        
        # Display bot response
        self.update_chat_display(response, is_user=False)

def main():
    root = tk.Tk()
    app = ChatbotGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()