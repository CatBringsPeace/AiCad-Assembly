"""
AI handler - Gemini API integration for assembly instruction parsing
"""

import os
import json
from dotenv import load_dotenv

try:
    import google.generativeai as genai
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        client = genai.GenerativeModel("gemini-2.0-flash")
    else:
        client = None
except Exception:
    client = None


class AIHandler:
    def __init__(self):
        self.client = client
    
    def generate(self, user_input: str, rule_result: dict = None):
        """
        Generate assembly instructions using Gemini AI.
        
        Args:
            user_input: User's assembly instruction
            rule_result: Previous rule-based parse result (optional)
        
        Returns:
            dict with commands and metadata
        """
        if not self.client:
            return {
                "method": "ai_error",
                "commands": rule_result.get("commands", []) if rule_result else [],
                "confidence": 0.0,
                "error": "Gemini not configured"
            }
        
        prompt = f"""Parse this assembly instruction into JSON commands.

Valid command types: INSERT, ROTATE, ALIGN, DUPLICATE, STACK, FASTEN, OFFSET

Return ONLY this JSON format:
{{
    "commands": [
        {{"type": "INSERT", "obj_a": "screw", "depth": 20, "unit": "mm", "obj_b": "hole_A"}},
        {{"type": "ROTATE", "obj_a": "part", "degrees": 90, "axis": "Z"}}
    ]
}}

User instruction: "{user_input}"

Previous rule parse: {json.dumps(rule_result) if rule_result else 'None'}

Return ONLY JSON, no explanation."""

        try:
            response = self.client.generate_content(prompt)
            text = response.text.strip()
            
            # Extract JSON
            if text.startswith("{"):
                data = json.loads(text)
            else:
                # Try extracting from markdown
                import re
                match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
                if match:
                    data = json.loads(match.group(1))
                else:
                    data = {"commands": []}
            
            return {
                "method": "ai_only",
                "commands": data.get("commands", []),
                "confidence": 0.9,
                "raw": text
            }
        
        except Exception as e:
            return {
                "method": "ai_error",
                "commands": rule_result.get("commands", []) if rule_result else [],
                "confidence": 0.0,
                "error": str(e)
            }