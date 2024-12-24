/*export class ChatAPI {
    constructor(chatU) {
        // Replace with your ngrok URL
        this.apiUrl = 'https://b5d7-34-85-244-22.ngrok-free.app/chat';
        this.chatUI=chatU;
        this.setupMessageListener();
    }

    setupMessageListener() {
        document.addEventListener('message-sent', async (event) => {
            const message = event.detail;
            try {
                const response = await this.sendMessage(message);
                //const chatUI = document.querySelector('.chat-container').__vue__;
                this.chatUI.addBotMessage(response);
            } catch (error) {
                console.error('Error sending message:', error);
                this.chatUI.addBotMessage('Sorry, I encountered an error processing your request.');
            }
            }
        });
    }

    async sendMessage(message) {
        try {
            const response = await fetch(this.apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            console.log('Received response from backend:', data); 
            return data.response;
        } catch (error) {
            console.error('Error:', error);
            return 'Sorry, I encountered an error processing your request.';
        }
    }
}*/
export class ChatAPI {
    constructor(chatUI) {
        // Replace with your ngrok URL
        this.apiUrl = 'https://ecd8-35-204-162-6.ngrok-free.app/chat';
        this.chatUI = chatUI; // Store the ChatUI instance
        this.setupMessageListener();
    }

    setupMessageListener() {
        document.addEventListener('message-sent', async (event) => {
            const message = event.detail;
            try {
                const response = await this.sendMessage(message);
                this.chatUI.addBotMessage(response); // Use the ChatUI instance
            } catch (error) {
                console.error('Error sending message:', error);
                this.chatUI.addBotMessage('Sorry, I encountered an error processing your request.');
            }
        });
    }

    async sendMessage(message) {
        try {
            const response = await fetch(this.apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message }),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            console.log('Received response from backend:', data);
            return data.response;
        } catch (error) {
            console.error('Error:', error);
            return 'Sorry, I encountered an error processing your request.';
        }
    }
}


