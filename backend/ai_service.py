import ollama
import json
import re

def process_email_with_ai(email_content: str):
    """
    Sends email content to the local Llama model to determine priority and draft a reply.
    """
    prompt = f"""
    You are an intelligent email triage assistant. Read the following email and provide a JSON response with exactly three keys:
    1. "priority": Classify the urgency as "Low", "Medium", or "High". (Low = routine/spam, Medium = standard request, High = urgent/angry/important).
    2. "summary": A brief one-sentence summary of the email.
    3. "draft_reply": A professional draft response to the sender.

    Email Content:
    {email_content}
    
    Respond ONLY with valid JSON. Do not include any other text or explanation.
    """
    
    try:
        # ADDED: format='json' forces Ollama to strictly output valid JSON
        response = ollama.chat(model='llama3.2', messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ], format='json')
        
        result_text = response['message']['content'].strip()
        
        # ADDED: Regex search to guarantee we only grab the JSON object, ignoring any stray text
        match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if match:
            result_text = match.group(0)
            
        # Parse the JSON string into a Python dictionary
        parsed_data = json.loads(result_text)
        return parsed_data
        
    except Exception as e:
        print(f"AI Analysis failed: {e}")
        # Fallback if the AI fails
        return {
            "priority": "Medium", 
            "summary": "Manual review required.", 
            "draft_reply": "Thank you for reaching out. We have received your message and will review it shortly."
        }