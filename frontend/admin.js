function getApiBase() {
  const isLocal = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
  return isLocal ? "http://127.0.0.1:5000" : "https://portifolio-clouds.onrender.com";
}

// Load messages into the dashboard
async function loadMessages() {
  const apiBase = getApiBase();

  try {
    console.log("🔄 Loading messages from:", `${apiBase}/api/messages`);
    const res = await fetch(`${apiBase}/api/messages`, { credentials: 'include' });
    
    console.log("📨 Response status:", res.status);
    
    if (!res.ok) {
      throw new Error(`Failed to load messages: ${res.status} ${res.statusText}`);
    }
    const data = await res.json();
    console.log("✅ Messages loaded:", data.length, "messages found");

    const table = document.getElementById("messagesTable");
    table.innerHTML = "";

    if (data.length === 0) {
      table.innerHTML = "<tr><td colspan='5' style='text-align:center; padding: 20px;'>📭 No messages yet</td></tr>";
      return;
    }

    data.forEach(msg => {
      const existingReply = msg.reply ? `<div class="existing-reply"><strong>Saved reply:</strong><br>${msg.reply}</div>` : "";
      table.innerHTML += `
        <tr>
          <td>${msg.id}</td>
          <td>${msg.name}</td>
          <td>${msg.email}</td>
          <td>${msg.message}</td>
          <td>
            ${existingReply}
            <form class="reply-form" onsubmit="sendReply(event, ${msg.id})">
              <textarea name="replyMessage" placeholder="Type reply..." required></textarea>
              <button type="submit">Send</button>
            </form>
          </td>
        </tr>
      `;
    });
  } catch (error) {
    console.error("❌ Error loading messages:", error);
    const table = document.getElementById("messagesTable");
    table.innerHTML = `<tr><td colspan='5' style='color:red; text-align:center; padding: 20px;'>⚠️ Error: ${error.message}</td></tr>`;
    alert("Failed to load messages: " + (error.message || error));
  }
}

// Send reply to backend
async function sendReply(event, messageId) {
  event.preventDefault();
  const message = event.target.replyMessage.value;

  const apiBase = getApiBase();

  try {
    console.log("📤 Sending reply for message ID:", messageId);
    const res = await fetch(`${apiBase}/api/reply`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ id: messageId, message })
    });

    console.log("📨 Reply response status:", res.status);

    if (res.ok) {
      alert("✅ Reply saved successfully!");
      event.target.reset();
      loadMessages();
    } else {
      const result = await res.json();
      alert("❌ Error: " + result.message);
    }
  } catch (error) {
    console.error("❌ Error sending reply:", error);
    alert("❌ Server error while sending reply: " + error.message);
  }
}

// Logout functionality
document.getElementById("logoutBtn").addEventListener("click", async () => {
  const apiBase = getApiBase();

  try {
    console.log("🔓 Logging out...");
    await fetch(`${apiBase}/api/logout`, {
      method: "POST",
      credentials: 'include'
    });
    window.location.href = "admin-login.html";
  } catch (error) {
    console.error("❌ Error logging out:", error);
    alert("Logout failed: " + error.message);
  }
});

// Initialize dashboard
console.log("🚀 Initializing admin dashboard...");
loadMessages();
