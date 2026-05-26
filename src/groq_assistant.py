import os
from groq import Groq
from dotenv import load_dotenv

class GroqTutorAssistant:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            print("WARNING: GROQ_API_KEY not found in .env file.")
        
        try:
            self.client = Groq(api_key=self.api_key)
        except Exception as e:
            print(f"Failed to initialize Groq client: {e}")
            self.client = None

        self.model = "llama-3.1-8b-instant"
        self.system_prompt = """You are an expert AI Educational Tutor. 
        Your goal is to guide students, explain learning analytics, and suggest actionable interventions.
        You have access to their risk predictions, engagement scores, and recommendation vectors.
        Be encouraging, professional, and precise. Never make up data; if a metric is low, address it constructively."""

    def get_response(self, user_message: str, chat_history: list = None, student_context: dict = None) -> str:
        """
        Sends context-aware message to Groq.
        """
        if not self.client:
            return "Error: Groq client not initialized. Check your API key."

        messages = [{"role": "system", "content": self.system_prompt}]
        
        #Inject student context into the system prompt if provided
        if student_context:
            context_str = "\n--- CURRENT STUDENT CONTEXT ---\n"
            for k, v in student_context.items():
                context_str += f"{k}: {v}\n"
            messages[0]["content"] += context_str

        #Add history
        if chat_history:
            for msg in chat_history:
                messages.append(msg)
                
        #Add current message
        messages.append({"role": "user", "content": user_message})

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"API Error: {str(e)}"
