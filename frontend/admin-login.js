// Load messages into the dashboard
function getApiBase() {
  return (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
    ? "http://127.0.0.1:5000"
    : "https://portifolio-clouds.onrender.com";
}

async function loadMessages() {
  const apiBase = getApiBase();

  try {
    const res = await fetch(`${apiBase}/api/messages`, { credentials: 'include' });
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
    alert("Failed to load messages.");
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
      const result = await res.json();
      alert("Error: " + result.message);
    }
  } catch (error) {
    console.error("Error sending reply:", error);
    alert("Server error while sending reply.");
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
