"""
VLM API Handler - With verbose logging
"""
import base64
import os
from datetime import datetime
from openai import OpenAI


def vlm_log(msg, log_folder=None):
    """Log with VLM prefix to console and file"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [VLM] {msg}"
    print(line, flush=True)
    
    if log_folder:
        try:
            with open(os.path.join(log_folder, "teleops.log"), "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except:
            pass


class OpenAIHandler:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        
        if self.api_key:
            vlm_log(f"API key found: {self.api_key[:8]}...{self.api_key[-4:]}")
            self.client = OpenAI(api_key=self.api_key)
            vlm_log("OpenAI client created successfully")
        else:
            vlm_log("WARNING: No API key provided!")
            self.client = None
    
    def evaluate_image(self, image_path, prompt, log_folder=None, filter_id=None):
        """Evaluate image with VLM, log everything to shared folder"""
        
        vlm_log("=" * 60, log_folder)
        vlm_log(f"EVALUATION START", log_folder)
        vlm_log(f"  Filter ID: {filter_id}", log_folder)
        vlm_log(f"  Image: {image_path}", log_folder)
        vlm_log(f"  Prompt: {prompt}", log_folder)
        
        if not self.client:
            vlm_log("ERROR: No VLM client available!", log_folder)
            return None
        
        if not os.path.exists(image_path):
            vlm_log(f"ERROR: Image file not found: {image_path}", log_folder)
            return None
        
        # Get file info
        file_size = os.path.getsize(image_path)
        vlm_log(f"  Image size: {file_size} bytes", log_folder)
        
        # Encode image
        vlm_log("Encoding image to base64...", log_folder)
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode('utf-8')
        vlm_log(f"  Base64 length: {len(b64)} chars", log_folder)
        
        # Call API
        vlm_log("Calling OpenAI GPT-4o API...", log_folder)
        vlm_log("  Model: gpt-4o", log_folder)
        vlm_log("  Max tokens: 150", log_folder)
        vlm_log("  Temperature: 0", log_folder)
        
        start_time = datetime.now()
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                ]
            }],
            max_tokens=150,
            temperature=0
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        vlm_log(f"API response received in {duration:.2f}s", log_folder)
        vlm_log(f"  Response ID: {response.id}", log_folder)
        vlm_log(f"  Model used: {response.model}", log_folder)
        vlm_log(f"  Finish reason: {response.choices[0].finish_reason}", log_folder)
        
        if hasattr(response, 'usage'):
            vlm_log(f"  Tokens - prompt: {response.usage.prompt_tokens}, completion: {response.usage.completion_tokens}", log_folder)
        
        result = response.choices[0].message.content.strip()
        
        vlm_log(f"RESULT: '{result}'", log_folder)
        vlm_log(f"  Result length: {len(result)} chars", log_folder)
        vlm_log(f"  Result lowercase: '{result.lower()}'", log_folder)
        vlm_log(f"  Contains 'true': {'true' in result.lower()}", log_folder)
        vlm_log(f"  Contains 'false': {'false' in result.lower()}", log_folder)
        vlm_log("=" * 60, log_folder)
        
        return result
