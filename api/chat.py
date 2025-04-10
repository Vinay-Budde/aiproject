from http.server import BaseHTTPRequestHandler
import json
import re
from datetime import datetime
import os

# In-memory chat history storage (for demo - replace with database in production)
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
                    'created_at': datetime.now().isoformat()
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
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'response': response,
                    'session_id': session_id
                }).encode())
                return
            
            # Generate response
            response = self.generate_response(user_message, session_id)
            
            # Store conversation
            chat_sessions[session_id]['history'].append({
                'user': user_message,
                'bot': response,
                'timestamp': datetime.now().isoformat()
            })
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'response': response,
                'session_id': session_id
            }).encode())
            
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")

    def is_home_repair_related(self, message):
        """Check if message is related to home repair topics"""
        message = message.lower()
        
        diy_keywords = [
            'repair', 'fix', 'home', 'house', 'diy', 'leak', 'pipe', 'plumb',
            'electr', 'wire', 'paint', 'drywall', 'wood', 'hammer', 'nail',
            'screw', 'drill', 'tool', 'faucet', 'toilet', 'sink', 'drain',
            'clog', 'window', 'door', 'lock', 'hinge', 'tile', 'floor', 'wall'
        ]
        
        off_topic_keywords = [
            'movie', 'sport', 'game', 'music', 'politic', 'weather',
            'celebrity', 'stock', 'finance', 'programming', 'code'
        ]
        
        # Must contain at least one DIY keyword and no off-topic keywords
        has_diy_keyword = any(keyword in message for keyword in diy_keywords)
        no_off_topic = not any(keyword in message for keyword in off_topic_keywords)
        
        return has_diy_keyword and no_off_topic

    def generate_response(self, message, session_id):
        """Generate context-aware response"""
        message = message.lower()
        history = chat_sessions[session_id]['history']
        
        # Handle greetings
        if any(word in message for word in ['hi', 'hello', 'hey']):
            return "Hello! I'm your DIY Home Repair Assistant. What project are you working on today?"
        
        # Handle thanks
        if any(word in message for word in ['thank', 'thanks', 'appreciate']):
            return "You're welcome! Let me know if you have any other home repair questions."
        
        # Context-aware responses
        last_question = next(
            (msg['user'] for msg in reversed(history) if '?' in msg['user']),
            None
        )
        
        # Enhanced response database
        response_db = {
            r'\b(leak|leaky|faucet|drip)\b': self.get_faucet_advice(last_question),
            r'\b(drywall|patch|hole|wall)\b': self.get_drywall_advice(),
            r'\b(clog|drain|block|sink)\b': self.get_drain_advice(),
            r'\b(paint|brush|roller|wall)\b': self.get_painting_advice(),
            r'\b(electr|wire|outlet|switch|breaker)\b': self.get_electrical_advice(),
            r'\b(toilet|flush|running|clog)\b': self.get_toilet_advice(),
            r'\b(window|draft|insulate|glass)\b': self.get_window_advice(),
            r'\b(tool|equipment|safety|gear)\b': (
                "Safety first! Always wear:\n"
                "- Safety goggles\n"
                "- Work gloves\n"
                "- Dust mask when needed\n"
                "Inspect tools before use."
            )
        }
        
        # Find matching response pattern
        for pattern, response in response_db.items():
            if re.search(pattern, message):
                return response
        
        # Default response
        return (
            "For DIY home repairs, I can help with:\n"
            "1. Plumbing issues (leaks, clogs)\n"
            "2. Electrical basics (outlets, switches)\n"
            "3. Drywall repair\n"
            "4. Painting techniques\n"
            "5. Furniture assembly\n\n"
            "What specific project are you working on?"
        )

    # Domain-specific response generators
    def get_faucet_advice(self, last_question):
        steps = [
            "1. Turn off water supply under sink",
            "2. Disassemble faucet handle",
            "3. Check washer and O-rings for wear",
            "4. Replace damaged parts (take old parts to hardware store for matching)",
            "5. Reassemble and test"
        ]
        if last_question and "shower" in last_question.lower():
            steps.insert(1, "For shower faucets: Remove handle cover first with flathead screwdriver")
        return "Fixing a leaky faucet:\n" + "\n".join(steps)
    
    def get_drywall_advice(self):
        return (
            "Drywall repair:\n"
            "1. Cut out damaged area in square/rectangle shape\n"
            "2. Install wood backing strips inside wall\n"
            "3. Cut new drywall piece to fit hole\n"
            "4. Secure with drywall screws (don't overtighten)\n"
            "5. Apply joint compound with putty knife\n"
            "6. Add fiberglass mesh tape for strength\n"
            "7. Sand smooth when dry (wear dust mask!)\n"
            "8. Prime before painting"
        )
    
    def get_drain_advice(self):
        return (
            "Unclogging drains:\n"
            "1. Try a plunger first (cover overflow drain if present)\n"
            "2. For sink drains: Remove and clean P-trap\n"
            "3. Use drain snake for deeper clogs\n"
            "4. Natural solution: 1/2 cup baking soda + 1/2 cup vinegar\n"
            "5. Flush with boiling water after 15 minutes\n"
            "⚠️ Avoid chemical drain cleaners - they damage pipes"
        )
    
    def get_painting_advice(self):
        return (
            "Professional painting tips:\n"
            "1. Clean walls with TSP cleaner\n"
            "2. Repair cracks/holes with spackle\n"
            "3. Use blue painter's tape for edges\n"
            "4. 'Cut in' edges with angled brush first\n"
            "5. Roll walls in 'W' pattern for even coverage\n"
            "6. Maintain 'wet edge' to avoid lap marks\n"
            "7. Remove tape when paint is slightly tacky\n"
            "8. Wait 4+ hours between coats"
        )
    
    def get_electrical_advice(self):
        return (
            "⚠️ Electrical Safety First ⚠️\n"
            "1. ALWAYS turn off power at breaker\n"
            "2. Verify power is off with non-contact tester\n"
            "3. Only DIY-safe projects:\n"
            "   - Replacing outlets/switches (same type)\n"
            "   - Installing light fixtures\n"
            "4. Never work on:\n"
            "   - Main panel\n"
            "   - Aluminum wiring\n"
            "   - Any unsure project"
        )
    
    def get_toilet_advice(self):
        return (
            "Toilet repairs:\n"
            "Running toilet? Check:\n"
            "1. Flapper valve (replace if worn)\n"
            "2. Float adjustment (water 1\" below overflow)\n"
            "3. Fill valve (replace if leaking)\n\n"
            "Clogged? Use flange plunger or closet auger"
        )
    
    def get_window_advice(self):
        return (
            "Window solutions:\n"
            "Drafty windows?\n"
            "1. Apply self-stick weatherstripping\n"
            "2. Use interior window insulator kit in winter\n"
            "3. Caulk exterior gaps with silicone\n\n"
            "Sticking windows? Clean tracks and apply silicone spray"
        )
