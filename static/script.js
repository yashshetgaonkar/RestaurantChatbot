
const chatArea = document.getElementById("chatArea");
const messageInput = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");

function addMessage(text, sender, intent = null, confidence = null) {
    const message = document.createElement("div");
    message.className = `message ${sender}`;

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = sender === "bot" ? "🤖" : "👤";

    const content = document.createElement("div");

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = text;

    content.appendChild(bubble);

    if (sender === "bot" && intent) {
        const label = document.createElement("span");
        label.className = "intent-label";
        label.textContent = `Intent: ${intent} | Confidence: ${confidence}`;
        content.appendChild(label);
    }

    message.appendChild(avatar);
    message.appendChild(content);
    chatArea.appendChild(message);

    chatArea.scrollTop = chatArea.scrollHeight;
}

function showTyping() {
    const typing = document.createElement("div");
    typing.className = "typing";
    typing.id = "typingIndicator";
    typing.textContent = "🤖 Fast-Food Service is thinking...";
    chatArea.appendChild(typing);
    chatArea.scrollTop = chatArea.scrollHeight;
}

function removeTyping() {
    const typing = document.getElementById("typingIndicator");
    if (typing) typing.remove();
}

async function sendMessage() {
    const message = messageInput.value.trim();

    if (!message) return;

    const welcome = document.getElementById("welcome");
    if (welcome) welcome.remove();

    addMessage(message, "user");

    messageInput.value = "";
    sendButton.disabled = true;
    showTyping();

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();
        removeTyping();

        if (!response.ok) {
            addMessage(data.response || "Something went wrong.", "bot");
        } else {
            addMessage(
                data.response,
                "bot",
                data.intent,
                data.confidence
            );
        }

    } catch (error) {
        removeTyping();
        addMessage(
            "Unable to connect to the server. Please make sure Flask is running.",
            "bot"
        );
    } finally {
        sendButton.disabled = false;
        messageInput.focus();
    }
}

function sendQuickMessage(message) {
    messageInput.value = message;
    sendMessage();
}

function resetChat() {
    chatArea.innerHTML = `
        <div class="welcome" id="welcome">
            <div class="welcome-icon">🍕</div>
            <h1>Welcome to Fast-Food Service!</h1>
            <p>Your personal food assistant. Craving something delicious? Let's find it.</p>
            <div class="suggestions">
                <button onclick="sendQuickMessage('Show me the menu')">🍽️ Explore menu</button>
                <button onclick="sendQuickMessage('Recommend me some food')">⭐ Recommend food</button>
                <button onclick="sendQuickMessage('How much is a burger?')">💰 Check prices</button>
                <button onclick="sendQuickMessage('I want to order food')">🛒 Place an order</button>
            </div>
        </div>
    `;
    messageInput.value = "";
    messageInput.focus();
}

// Send message when Enter is pressed
messageInput.addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});

// Initial focus
messageInput.focus();
