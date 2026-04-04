(function () {
  "use strict";

  const chatMessages = document.getElementById("chatMessages");
  const chatContainer = document.getElementById("chatContainer");
  const chatForm = document.getElementById("chatForm");
  const messageInput = document.getElementById("messageInput");
  const sendBtn = document.getElementById("sendBtn");

  const SESSION_KEY = "vet_clinic_session_id";

  function getSessionId() {
    let id = sessionStorage.getItem(SESSION_KEY);
    if (!id) {
      id = crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(36) + Math.random().toString(36).slice(2);
      sessionStorage.setItem(SESSION_KEY, id);
    }
    return id;
  }

  function scrollToBottom() {
    requestAnimationFrame(function () {
      chatContainer.scrollTop = chatContainer.scrollHeight;
    });
  }

  function renderMarkdown(text) {
    if (typeof marked !== "undefined" && marked.parse) {
      return marked.parse(text);
    }
    return text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\n/g, "<br>");
  }

  function addMessage(text, role) {
    var wrapper = document.createElement("div");
    wrapper.className = "message " + (role === "user" ? "user-message" : "bot-message");

    var bubble = document.createElement("div");
    bubble.className = "message-bubble";

    if (role === "user") {
      bubble.textContent = text;
    } else {
      bubble.innerHTML = renderMarkdown(text);
    }

    wrapper.appendChild(bubble);
    chatMessages.appendChild(wrapper);
    scrollToBottom();
  }

  function showTypingIndicator() {
    var wrapper = document.createElement("div");
    wrapper.className = "message bot-message";
    wrapper.id = "typingIndicator";

    var bubble = document.createElement("div");
    bubble.className = "message-bubble typing-indicator";
    bubble.innerHTML = "<span></span><span></span><span></span>";

    wrapper.appendChild(bubble);
    chatMessages.appendChild(wrapper);
    scrollToBottom();
  }

  function removeTypingIndicator() {
    var el = document.getElementById("typingIndicator");
    if (el) el.remove();
  }

  function setLoading(loading) {
    sendBtn.disabled = loading;
    messageInput.disabled = loading;
    if (!loading) messageInput.focus();
  }

  async function sendMessage() {
    var text = messageInput.value.trim();
    if (!text) return;

    addMessage(text, "user");
    messageInput.value = "";
    setLoading(true);
    showTypingIndicator();

    try {
      var response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          session_id: getSessionId(),
        }),
      });

      removeTypingIndicator();

      if (!response.ok) {
        var errData = await response.json().catch(function () {
          return { detail: "Something went wrong. Please try again." };
        });
        addMessage(errData.detail || errData.reply || "An error occurred.", "bot");
      } else {
        var data = await response.json();
        addMessage(data.reply, "bot");
      }
    } catch (err) {
      removeTypingIndicator();
      addMessage("Unable to reach the server. Please check your connection and try again.", "bot");
    } finally {
      setLoading(false);
    }
  }

  chatForm.addEventListener("submit", function (e) {
    e.preventDefault();
    sendMessage();
  });

  messageInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
})();
