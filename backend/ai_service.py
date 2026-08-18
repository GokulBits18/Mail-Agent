import ollama
import json
import re

def process_email_with_ai(email_content: str):
    prompt = f"""
    You are managing the email inbox for Gokul. Read the following email and provide a JSON response. 
    
    You MUST return ONLY a raw JSON object matching this EXACT format:
    {{
        "priority": "Low", 
        "sentiment": "Neutral",
        "draft_reply_1": "Positive reply here",
        "draft_reply_2": "Polite decline here",
        "draft_reply_3": "Ask for details here"
    }}

    RULES:
    1. "priority" MUST be exactly one of: "Low", "Medium", "High", or "Spam". 
       - "Spam": Marketing, newsletters, job alerts, mass promotions.
       - "Low": Purely personal friendly chit-chat (e.g., "Wassup", "Going to trip") OR automated security alerts.
       - "Medium": ANY work-related email (projects, sprints, meetings, scheduling, tasks), EVEN IF the sender uses a friendly or polite tone.
       - "High": Urgent emergencies, server crashes, or time-sensitive crises.
    2. "sentiment" MUST be exactly one word describing the sender's mood (e.g., "Positive", "Neutral", "Urgent", "Friendly").
    3. Match the sender's tone for the replies. Be casual if they are casual.
    
    Email Content:
    {email_content}
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