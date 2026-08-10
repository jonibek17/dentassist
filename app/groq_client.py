import json
from typing import Optional
from groq import Groq
from app.config import config
from app.prompts import SYSTEM_PROMPT


class GroqClient:
    def __init__(self):
        self.client = Groq(api_key=config.GROQ_API_KEY) if config.GROQ_API_KEY else None
        self.model = config.GROQ_MODEL
    
    async def get_clinic_context(self) -> str:
        """Load clinic data from JSON file."""
        try:
            with open(config.CLINIC_DATA_PATH, "r", encoding="utf-8") as f:
                clinic_data = json.load(f)
            return json.dumps(clinic_data, ensure_ascii=False)
        except Exception:
            return "{}"
    
    async def ask_question(self, user_question: str) -> str:
        """Ask a question to Groq AI."""
        if not self.client:
            return self._get_fallback_response()
        
        try:
            clinic_context = await self.get_clinic_context()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"{SYSTEM_PROMPT}\n\nДанные клиники:\n{clinic_context}"},
                    {"role": "user", "content": user_question}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content or self._get_fallback_response()
        
        except Exception:
            return self._get_fallback_response()
    
    def _get_fallback_response(self) -> str:
        """Return fallback response when Groq is unavailable."""
        return (
            "К сожалению, я не могу ответить на ваш вопрос прямо сейчас. "
            "Пожалуйста, запишитесь на консультацию, и администратор поможет вам."
        )


groq_client = GroqClient()
