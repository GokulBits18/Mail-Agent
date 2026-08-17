import ollama
import json
import re

def process_email_with_ai(email_content: str):
    """
    Sends email content to the local Llama model to determine priority and draft a reply.
    """
    prompt = f"""
    You are managing the email inbox for Gokul. Read the following email and provide a JSON response with exactly three keys:
    1. "priority": Classify the urgency as "Low", "Medium", "High", or "Spam". 
       - Spam = Marketing, newsletters, promotions, automated bot replies, or system bounce-backs.
       - Low = Casual conversations with friends, short personal check-ins, or routine notifications. NEVER mark emails from real human friends as Spam.
       - Medium = Standard work requests or questions requiring a thoughtful reply.
       - High = Urgent, angry, or time-sensitive emergencies.
    2. "summary": A brief one-sentence summary of the email.
    3. "draft_reply": Write a natural, human-like reply as Gokul. MATCH THE SENDER'S TONE. If they are casual (e.g., "Wassup", "Hey"), be casual and friendly back (e.g., "Hey! Not much, what's up with you?"). If they are formal, be professional. NEVER use robotic openings like "Dear Sir/Madam", and NEVER state that you are an AI. Write exactly what a real person would say.

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