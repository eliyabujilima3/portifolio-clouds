// Load messages into the dashboard
async function loadMessages() {
  const apiBase = "https://portifolio-clouds.onrender.com";

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
            <form class="reply-form" onsubmit="sendReply(event, '${msg.email}')">
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
async function sendReply(event, email) {
  event.preventDefault();
  const message = event.target.replyMessage.value;

  const apiBase = "https://portifolio-clouds.onrender.com";

  try {
    const res = await fetch(`${apiBase}/api/reply`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ email, message })
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
  const apiBase = "https://portifolio-clouds.onrender.com";

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
