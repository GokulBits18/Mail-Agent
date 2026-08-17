import ollama
import json
import re

def process_email_with_ai(email_content: str):
    prompt = f"""
    You are managing the email inbox for Gokul. Read the following email and provide a JSON response with exactly five keys:
    1. "priority": Classify as "Low", "Medium", "High", or "Spam". (Friends/Security = Low, Work = Medium, Urgent = High, Marketing = Spam).
    2. "sentiment": Analyze the mood of the sender. Use EXACTLY ONE WORD (e.g., "Positive", "Neutral", "Negative", "Frustrated", "Friendly", "Urgent").
    3. "draft_reply_1": A POSITIVE or ACCEPTING natural reply as Gokul.
    4. "draft_reply_2": A POLITE DECLINING or REJECTING natural reply as Gokul.
    5. "draft_reply_3": A NEUTRAL reply asking for more details or clarification as Gokul.

    Keep all replies natural and human-like. MATCH THE SENDER'S TONE. If they are casual, be casual. NEVER use robotic openings like "Dear Sir/Madam".

    Email Content:
    {email_content}
    
    Respond ONLY with valid JSON. Do not include any other text or explanation.
    """
    
    try:
        response = ollama.chat(model='qwen2.5-coder:latest', messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ], format='json')
        
        result_text = response['message']['content'].strip()
        match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if match:
            result_text = match.group(0)
            
        return json.loads(result_text)
        
    except Exception as e:
        print(f"AI Analysis failed: {e}")
        return {
            "priority": "Medium", 
            "sentiment": "Neutral",
            "draft_reply_1": "Sounds good, thank you.",
            "draft_reply_2": "I won't be able to do this right now, sorry.",
            "draft_reply_3": "Could you provide a bit more information?"
        }