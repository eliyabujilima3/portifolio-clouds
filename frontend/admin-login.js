// Load messages into the dashboard
function getApiBase() {
  return (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
    ? "http://127.0.0.1:5000"
    : "https://portifolio-clouds.onrender.com";
}

async function parseJsonOrText(response) {
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return response.json();
  }

  const text = await response.text();
  try {
    return JSON.parse(text);
  } catch {
    return { message: text || response.statusText };
  }
}

async function loadMessages() {
  const apiBase = getApiBase();

  try {
    const res = await fetch(`${apiBase}/api/messages`, { credentials: 'include' });
    if (!res.ok) {
      const result = await parseJsonOrText(res);
      throw new Error(result.message || JSON.stringify(result));
    }
    const data = await res.json();

    const table = document.getElementById("messagesTable");
    table.innerHTML = "";

    data.forEach(msg => {
      table.innerHTML += `
        <tr>
          <td>${msg.id}</td>
          <td>${msg.name}</td>
          <td>${msg.email}</td>
          <td>${msg.message}</td>
          <td>
            <form class="reply-form" onsubmit="sendReply(event, ${msg.id})">
              <textarea name="replyMessage" placeholder="Type reply..." required></textarea>
              <button type="submit">Send</button>
            </form>
          </td>
        </tr>
      `;
    });
  } catch (error) {
    console.error("Error loading messages:", error);
    alert("Failed to load messages: " + (error.message || error));
  }
}

// Send reply to backend
async function sendReply(event, messageId) {
  event.preventDefault();
  const message = event.target.replyMessage.value;

  const apiBase = getApiBase();

  try {
    const res = await fetch(`${apiBase}/api/reply`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ id: messageId, message })
    });

    if (res.ok) {
      alert("Reply sent successfully!");
      event.target.reset();
    } else {
      const result = await parseJsonOrText(res);
      alert("Error: " + (result.message || result.error || JSON.stringify(result)));
    }
  } catch (error) {
    console.error("Error sending reply:", error);
    alert("Server error while sending reply: " + (error.message || error));
  }
}

// Logout functionality
document.getElementById("logoutBtn").addEventListener("click", async () => {
  const apiBase = getApiBase();

  try {
    await fetch(`${apiBase}/api/logout`, {
      method: "POST",
      credentials: 'include'
    });
    window.location.href = "admin-login.html";
  } catch (error) {
    console.error("Error logging out:", error);
    alert("Logout failed.");
  }
});

// Initialize dashboard
loadMessages();
