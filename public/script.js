document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const typingIndicator = document.getElementById('typingIndicator');
    const quickQuestions = document.querySelectorAll('.quick-question');
    
    // Add a message to the chat
    function addMessage(content, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        const contentP = document.createElement('p');
        contentP.textContent = content;
        
        contentDiv.appendChild(contentP);
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to the bottom of the chat
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Show typing indicator
    function showTypingIndicator() {
        typingIndicator.style.display = 'flex';
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Hide typing indicator
    function hideTypingIndicator() {
        typingIndicator.style.display = 'none';
    }
    
    // Send message to the API
   // Replace the sendMessage function with this:
async function sendMessage(message) {
    showTypingIndicator();
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                message: message,
                session_id: 'user_' + Math.random().toString(36).substr(2, 9) // Simple session ID
            }),
        });
        
        if (!response.ok) throw new Error('Network error');
        const data = await response.json();
        hideTypingIndicator();
        addMessage(data.response, false);
    } catch (error) {
        hideTypingIndicator();
        addMessage("Sorry, I'm having trouble connecting. Try again later.", false);
    }
}
    
    // Handle user input
    function handleUserInput() {
        const message = userInput.value.trim();
        if (message) {
            addMessage(message, true);
            userInput.value = '';
            sendMessage(message);
        }
    }
    
    // Event listeners
    sendButton.addEventListener('click', handleUserInput);
    
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleUserInput();
        }
    });
    
    // Quick question buttons
    quickQuestions.forEach(button => {
        button.addEventListener('click', function() {
            const question = this.textContent;
            addMessage(question, true);
            sendMessage(question);
        });
    });
    
    // Initial greeting (already in HTML)
});
