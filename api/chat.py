from http.server import BaseHTTPRequestHandler
import json
import re
from datetime import datetime
import os
import google.generativeai as genai

# Configure Gemini
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash')

# In-memory chat history storage
chat_sessions = {}

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            user_message = data.get('message', '').strip()
            session_id = data.get('session_id', 'default')
            
            # Initialize session if new
            if session_id not in chat_sessions:
                chat_sessions[session_id] = {
                    'history': [],
                    'created_at': datetime.now().isoformat(),
                    'chat': model.start_chat(history=[])
                }
            
            # Validate message topic
            if not self.is_home_repair_related(user_message):
                response = (
                    "I specialize in DIY home repair advice. Please ask about:\n"
                    "- Plumbing (leaks, clogs, toilets)\n"
                    "- Electrical (outlets, wiring)\n"
                    "- Carpentry (furniture, shelves)\n"
                    "- Painting (walls, prep work)\n"
                    "- General home maintenance"
                )
                self.send_json_response(response, session_id)
                return
            
            # Get response from Gemini
            try:
                gemini_response = chat_sessions[session_id]['chat'].send_message(
                    f"Respond as a DIY home repair expert to this question: {user_message}\n"
                    "Provide step-by-step instructions with safety considerations.\n"
                    "Keep responses under 300 characters."
                )
                response = gemini_response.text
            except Exception as e:
                response = self.get_fallback_response(user_message)
            
            # Store conversation
            chat_sessions[session_id]['history'].append({
                'user': user_message,
                'bot': response,
                'timestamp': datetime.now().isoformat()
            })
            
            self.send_json_response(response, session_id)
            
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")

    def send_json_response(self, response, session_id):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({
            'response': response,
            'session_id': session_id
        }).encode())

    def is_home_repair_related(self, message):
        """Basic topic validation"""
        message = message.lower()
        diy_keywords = [
            'repair', 'fix', 'home', 'house', 'diy', 'leak', 'pipe', 
            'electr', 'wire', 'paint', 'drywall', 'wood', 'hammer',
            'nail', 'screw', 'drill', 'tool', 'faucet', 'toilet', 'sink'
        ]
        return any(keyword in message for keyword in diy_keywords)

    def get_fallback_response(self, user_message):
        """Fallback when Gemini fails"""
        simple_responses = {
            r'\bleak|faucet|drip\b': "For leaky faucets: 1) Turn off water 2) Replace washer 3) Reassemble",
            r'\bdrywall|patch|hole\b': "Patch drywall: 1) Cut square 2) Add backing 3) Secure new piece 4) Mud and sand",
            r'\bclog|drain|block\b': "Unclog drains: 1) Use plunger 2) Try baking soda/vinegar 3) Snake if needed",
            r'\bpaint|brush|roller\b': "Painting tips: 1) Clean walls 2) Use tape 3) Cut in edges 4) Roll in W pattern"
        }
        
        for pattern, response in simple_responses.items():
            if re.search(pattern, user_message.lower()):
                return response
                
        return "I can help with plumbing, electrical, painting, and other home repairs. What specifically do you need help with?"
