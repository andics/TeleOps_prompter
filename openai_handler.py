"""
OpenAI API Handler
Handles communication with OpenAI's GPT-4o Vision API
"""
import base64
import os
import sys
import traceback
from datetime import datetime
from openai import OpenAI

# Global log file handle
_log_file = None

def get_log_file(log_folder):
    """Get or create the log file handle"""
    global _log_file
    if log_folder:
        os.makedirs(log_folder, exist_ok=True)
        log_path = os.path.join(log_folder, "openai_requests.log")
        if _log_file is None or _log_file.name != log_path:
            if _log_file:
                _log_file.close()
            _log_file = open(log_path, "a", encoding="utf-8", buffering=1)  # Line buffered
            print(f"[LOG FILE] Opened log file: {log_path}", flush=True)
    return _log_file


def log_message(log_folder, message):
    """Log a message to both console and log file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    formatted = f"[{timestamp}] {message}"
    
    # Always print to console
    print(formatted, flush=True)
    sys.stdout.flush()
    
    # Also write to log file if folder specified
    if log_folder:
        f = get_log_file(log_folder)
        if f:
            f.write(formatted + "\n")
            f.flush()


class OpenAIHandler:
    """Handles OpenAI API interactions for vision analysis"""
    
    def __init__(self, api_key=None):
        """
        Initialize OpenAI handler
        
        Args:
            api_key: OpenAI API key (uses environment variable if not provided)
        """
        print("=" * 80, flush=True)
        print("[OpenAIHandler] INITIALIZING", flush=True)
        
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        
        if not self.api_key:
            print("[OpenAIHandler] WARNING: OpenAI API key NOT PROVIDED", flush=True)
            print("[OpenAIHandler] Checked api_key parameter: None", flush=True)
            print(f"[OpenAIHandler] Checked OPENAI_API_KEY env var: {os.environ.get('OPENAI_API_KEY', 'NOT SET')}", flush=True)
            self.client = None
        else:
            print(f"[OpenAIHandler] API key found: {self.api_key[:8]}...{self.api_key[-4:]}", flush=True)
            print("[OpenAIHandler] Creating OpenAI client...", flush=True)
            self.client = OpenAI(api_key=self.api_key)
            print(f"[OpenAIHandler] OpenAI client created: {self.client}", flush=True)
        
        print("=" * 80, flush=True)
    
    def encode_image(self, image_path):
        """
        Encode image to base64
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded string
        """
        print(f"[encode_image] Reading file: {image_path}", flush=True)
        print(f"[encode_image] File exists: {os.path.exists(image_path)}", flush=True)
        
        with open(image_path, "rb") as image_file:
            data = image_file.read()
            print(f"[encode_image] Read {len(data)} bytes", flush=True)
            encoded = base64.b64encode(data).decode('utf-8')
            print(f"[encode_image] Encoded to {len(encoded)} chars", flush=True)
            return encoded
    
    def evaluate_image(self, image_path, prompt, log_folder=None, filter_id=None):
        """
        Evaluate an image against a prompt using GPT-4o Vision
        
        Args:
            image_path: Path to the image file
            prompt: The filter prompt/question
            log_folder: Optional folder path to log requests
            filter_id: Optional filter ID for logging
            
        Returns:
            String response from GPT, or None if error
        """
        log_message(log_folder, "=" * 80)
        log_message(log_folder, f"[evaluate_image] START")
        log_message(log_folder, f"[evaluate_image] filter_id: {filter_id}")
        log_message(log_folder, f"[evaluate_image] image_path: {image_path}")
        log_message(log_folder, f"[evaluate_image] prompt: {prompt}")
        log_message(log_folder, f"[evaluate_image] log_folder: {log_folder}")
        log_message(log_folder, f"[evaluate_image] client exists: {self.client is not None}")
        
        if not self.client:
            log_message(log_folder, "[evaluate_image] ERROR: OpenAI client is None - API key missing")
            log_message(log_folder, "=" * 80)
            return None
        
        # Check if image exists
        log_message(log_folder, f"[evaluate_image] Checking if image exists...")
        log_message(log_folder, f"[evaluate_image] os.path.exists(image_path) = {os.path.exists(image_path)}")
        
        if not os.path.exists(image_path):
            log_message(log_folder, f"[evaluate_image] ERROR: Image file does not exist: {image_path}")
            log_message(log_folder, "=" * 80)
            return None
        
        # Encode the image
        log_message(log_folder, "[evaluate_image] Encoding image to base64...")
        base64_image = self.encode_image(image_path)
        log_message(log_folder, f"[evaluate_image] Image encoded, length: {len(base64_image)}")
        
        # Build the request
        log_message(log_folder, "[evaluate_image] Building request payload...")
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
        
        log_message(log_folder, f"[evaluate_image] Request payload built")
        log_message(log_folder, f"[evaluate_image] Message role: {messages[0]['role']}")
        log_message(log_folder, f"[evaluate_image] Content items: {len(messages[0]['content'])}")
        
        # Make the API call - NO TRY/EXCEPT, let errors propagate
        log_message(log_folder, "[evaluate_image] CALLING OpenAI API...")
        log_message(log_folder, "[evaluate_image] Model: gpt-4o")
        log_message(log_folder, "[evaluate_image] max_tokens: 150")
        log_message(log_folder, "[evaluate_image] temperature: 0")
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=150,
            temperature=0
        )
        
        log_message(log_folder, f"[evaluate_image] API RESPONSE RECEIVED")
        log_message(log_folder, f"[evaluate_image] Response object: {response}")
        log_message(log_folder, f"[evaluate_image] Response type: {type(response)}")
        log_message(log_folder, f"[evaluate_image] Choices count: {len(response.choices)}")
        
        # Extract response text
        result_text = response.choices[0].message.content.strip()
        
        log_message(log_folder, f"[evaluate_image] RESULT: {result_text}")
        log_message(log_folder, "=" * 80)
        
        return result_text
    
    def chat(self, message, image_path=None):
        """
        General chat function with optional image
        
        Args:
            message: Chat message
            image_path: Optional path to image
            
        Returns:
            Response text or None if error
        """
        print(f"[chat] Called with message: {message}", flush=True)
        print(f"[chat] image_path: {image_path}", flush=True)
        
        if not self.client:
            print("[chat] ERROR: OpenAI client not initialized", flush=True)
            return "OpenAI client not initialized"
        
        content = [{"type": "text", "text": message}]
        
        if image_path and os.path.exists(image_path):
            print(f"[chat] Adding image to request", flush=True)
            base64_image = self.encode_image(image_path)
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            })
        
        print(f"[chat] Calling OpenAI API...", flush=True)
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": content
                }
            ],
            max_tokens=500
        )
        
        result = response.choices[0].message.content
        print(f"[chat] Result: {result}", flush=True)
        
        return result
