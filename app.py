import os
from flask import Flask, request, jsonify, render_template_string
from werkzeug.serving import make_server
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

app = Flask(__name__)

# Control flag for Graceful shutdown
stop_flag = False

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Vet Clinic Chatbot</title>
    <style>
        body { font-family: sans-serif; max-width: 600px; margin: 40px auto; }
        #chatbox { height: 400px; border: 1px solid #ccc; padding: 10px; overflow-y: scroll; margin-bottom: 10px; }
        .message { margin-bottom: 10px; padding: 10px; border-radius: 5px; }
        .user { background-color: #e3f2fd; text-align: right; }
        .bot { background-color: #f1f8e9; }
        #msg, #session_id { width: 100%; box-sizing: border-box; margin-bottom: 10px; padding: 8px;}
        button { padding: 10px 20px; }
    </style>
</head>
<body>
    <h2>ENAE25 Vet Clinic Assistant</h2>
    <div>
        <label for="session_id">Session ID (for memory):</label>
        <input type="text" id="session_id" value="default-session">
    </div>
    <div id="chatbox"></div>
    <input type="text" id="msg" placeholder="Type your message here..." onkeypress="handleKeyPress(event)">
    <button onclick="sendMessage()">Send</button>

    <script>
        function addMessage(sender, text, className) {
            const chatbox = document.getElementById('chatbox');
            const msgDiv = document.createElement('div');
            msgDiv.className = 'message ' + className;
            msgDiv.innerHTML = `<strong>${sender}:</strong> ${text}`;
            chatbox.appendChild(msgDiv);
            chatbox.scrollTop = chatbox.scrollHeight;
        }

        async function sendMessage() {
            const msgInput = document.getElementById('msg');
            const sessionInput = document.getElementById('session_id');
            const msgValue = msgInput.value.trim();
            const sessionValue = sessionInput.value.trim();
            
            if (!msgValue) {
                addMessage('System', 'Please enter a message.', 'bot');
                return;
            }

            addMessage('You', msgValue, 'user');
            msgInput.value = '';

            try {
                const formData = new FormData();
                formData.append('msg', msgValue);
                formData.append('session_id', sessionValue || 'default');

                const response = await fetch('/ask_bot', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                addMessage('Bot', data.msg, 'bot');
            } catch (error) {
                addMessage('Error', error.message, 'bot');
            }
        }

        function handleKeyPress(e) {
            if (e.keyCode === 13) {
                sendMessage();
            }
        }
    </script>
</body>
</html>
"""

_SYSTEM_PROMPT = (
    "You are a cautious, friendly assistant for a small preventive-medicine "
    "veterinary clinic. The clinic ONLY provides dog and cat sterilisation "
    "(neutering/spaying), vaccinations, and microchip identification.\n\n"
    "Hard rules:\n"
    "- Do NOT give emergency or general-illness advice. If the animal seems ill "
    "or it is an emergency, clearly tell the owner to contact a full-service "
    "veterinary clinic or emergency hospital.\n"
    "- Do NOT make specific medical promises, diagnoses, or detailed scheduling "
    "commitments. Keep guidance high-level and conservative.\n"
    "- You DO NOT have access to clinic calendars, booking systems, tools, or RAG.\n"
    "- Base your instructions strictly on the following guidelines:\n"
    "   * Cats can be operated while in heat. Dogs MUST NOT be operated while in heat "
    "     (schedule 2 months after heat to avoid false pregnancy).\n"
    "   * Animals over 6 years old require a mandatory pre-op blood test.\n"
    "   * Fasting: no food 8-12 hours before surgery, water allowed until 1-2 hours before.\n"
    "   * Arrival: Cats must arrive in a rigid carrier without exception. Dogs must be on a lead.\n"
    "   * Pick-up: Dogs around 12:00, Cats around 15:00.\n"
    "   * Complications: Warn that vomiting on the surgery day is normal. Contact the clinic "
    "     by WhatsApp if there is active bleeding or no response to stimuli 8 hours after surgery.\n\n"
    "What you CAN do in this version:\n"
    "- Answer basic questions about preparation (fasting/carriers).\n"
    "- Refer the user to call the clinic for bookings and exact pricing.\n"
    "Keep answers short and conversational."
)

_store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """Return the message history for a given session id."""
    if session_id not in _store:
        _store[session_id] = ChatMessageHistory()
    return _store[session_id]

# Initialize LLM and Chain only if API key is present
def build_bot_chain():
    if not os.environ.get("OPENAI_API_KEY"):
        return None
        
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    prompt = ChatPromptTemplate.from_messages([
        ("system", _SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])
    
    chain = prompt | llm
    
    with_message_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )
    return with_message_history

# Lazy initialization fallback
_bot_chain = build_bot_chain()

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route("/ask_bot", methods=["POST"])
def ask_bot():
    """
    Read user message and session_id. Pass session_id in config so the chain
    can load and update the correct conversation history.
    """
    data = request.form
    user_msg = (data.get("msg") or "").strip()
    session_id = (data.get("session_id") or "default").strip()
    
    if not user_msg:
        return jsonify({"msg": "Please send a non-empty message."}), 400
        
    # Attempt lazy init just in case env variable got set after module load
    global _bot_chain
    if _bot_chain is None:
        _bot_chain = build_bot_chain()
        if _bot_chain is None:
            return jsonify({"msg": "OPENAI_API_KEY is not set. Please set it to use the chatbot."}), 500
            
    try:
        config = {"configurable": {"session_id": session_id}}
        response = _bot_chain.invoke({"input": user_msg}, config=config)
        bot_msg = response.content if hasattr(response, "content") else str(response)
        return jsonify({"msg": bot_msg})
    except Exception as e:
        return jsonify({"msg": "Error: " + str(e)}), 500

def run_server():
    server = make_server("0.0.0.0", 5000, app)
    server.timeout = 1
    print("Starting Vet Clinic server at http://0.0.0.0:5000")
    while not stop_flag:
        server.handle_request()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
