from http.server import BaseHTTPRequestHandler
import json
import openai

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        
        user_message = data.get('message', '')
        
        # In a real deployment, you'd use your OpenAI API key here
        # For Vercel, you should set this as an environment variable
        # openai.api_key = os.environ.get('OPENAI_API_KEY')
        
        # For this example, we'll use a simple response system
        # since we can't rely on OpenAI API in this basic setup
        response = self.generate_response(user_message)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'response': response}).encode())
    
    def generate_response(self, user_message):
        # This is a simple rule-based response system
        # In a real app, you'd use the OpenAI API or another AI service
        
        user_message = user_message.lower()
        
        responses = {
            "leak": "For a leaky faucet, first turn off the water supply. Then, disassemble the faucet to inspect the washer and O-rings. Replace any worn parts and reassemble.",
            "leaky": "For a leaky faucet, first turn off the water supply. Then, disassemble the faucet to inspect the washer and O-rings. Replace any worn parts and reassemble.",
            "faucet": "For a leaky faucet, first turn off the water supply. Then, disassemble the faucet to inspect the washer and O-rings. Replace any worn parts and reassemble.",
            "drywall": "To patch drywall: 1) Cut a square around the damaged area. 2) Install a backing. 3) Cut a new piece of drywall to fit. 4) Secure it with screws. 5) Apply joint compound. 6) Sand smooth when dry.",
            "patch": "To patch drywall: 1) Cut a square around the damaged area. 2) Install a backing. 3) Cut a new piece of drywall to fit. 4) Secure it with screws. 5) Apply joint compound. 6) Sand smooth when dry.",
            "clog": "To unclog a drain: 1) Try a plunger first. 2) If that doesn't work, use a drain snake. 3) For kitchen sinks, you can try a mixture of baking soda and vinegar followed by hot water. Avoid chemical drain cleaners as they can damage pipes.",
            "drain": "To unclog a drain: 1) Try a plunger first. 2) If that doesn't work, use a drain snake. 3) For kitchen sinks, you can try a mixture of baking soda and vinegar followed by hot water. Avoid chemical drain cleaners as they can damage pipes.",
            "paint": "For painting a room: 1) Clean and repair walls. 2) Apply painter's tape. 3) Use a primer if needed. 4) Cut in edges with a brush. 5) Roll the main areas. 6) Apply second coat if necessary. 7) Remove tape before paint fully dries.",
            "electrical": "For basic electrical work: Always turn off power at the breaker first. Use a voltage tester to confirm power is off. If you're not comfortable with electrical work, it's best to hire a licensed electrician.",
            "toilet": "For a running toilet: 1) Check the flapper valve - it may need cleaning or replacement. 2) Adjust the float if water level is too high. 3) Check the fill valve for leaks or malfunctions.",
            "squeak": "For squeaky floors: 1) Locate the squeak by walking around. 2) From below (if accessible), drive screws through the subfloor into the joists. 3) From above, use special squeak-reduction screws or apply talcum powder between boards.",
            "window": "For drafty windows: 1) Apply weatherstripping around the frame. 2) Use window insulator kits in winter. 3) For older windows, consider adding storm windows or eventually replacing them with energy-efficient models."
        }
        
        for keyword in responses:
            if keyword in user_message:
                return responses[keyword]
        
        # Default response if no keyword matches
        return "I can help with various home repair topics like plumbing, electrical, drywall, painting, and more. Could you please provide more details about your specific home repair issue?"
