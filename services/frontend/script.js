let userName = '';
let userEmail = '';

function startChat() {
    userName = document.getElementById('name').value;
    userEmail = document.getElementById('email').value;
    
    if (!userName || !userEmail) {
        alert('Please enter both name and email');
        return;
    }
    
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('chatWindow').style.display = 'block';
    
    addMessage('Bot', `Hello ${userName}! I'm powered by AWS Bedrock Agent. Try asking: "Get me posts from r/Python"`);
}

function sendMessage() {
    const input = document.getElementById('userInput');
    const message = input.value;
    
    if (!message) return;
    
    addMessage('You', message);
    input.value = '';
    
    // Call Bedrock Agent via public API
    callBedrockAgent(message);
}

async function callBedrockAgent(message) {
    addMessage('Bot', '🤖 AWS Bedrock Agent is thinking...');
    
    try {
        console.log('Sending message to API:', message);
        
        // Call the public API
        const response = await fetch('https://xl3q8bwqm9.execute-api.us-east-1.amazonaws.com/prod/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message
            })
        });
        
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);
        
        if (response.ok) {
            const data = await response.json();
            console.log('Response data:', data);
            addMessage('Bot', `🤖 ${data.message}`);
        } else {
            const errorText = await response.text();
            console.error('API Error:', response.status, errorText);
            addMessage('Bot', `Sorry, API returned error ${response.status}: ${errorText}`);
        }
    } catch (error) {
        console.error('Fetch Error:', error);
        addMessage('Bot', `Sorry, I had trouble connecting to AWS Bedrock Agent: ${error.message}`);
    }
}

function addMessage(sender, message) {
    const messagesDiv = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = sender === 'You' ? 'user-message' : 'bot-message';
    messageDiv.innerHTML = `<strong>${sender}:</strong> ${message}`;
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}
