function getApiBase() {
  return (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
    ? "http://127.0.0.1:5000"
    : "https://portifolio-clouds.onrender.com";
}

function getQueryParam(name) {
  const params = new URLSearchParams(window.location.search);
  return params.get(name);
}

async function loadReply() {
  const id = getQueryParam('id');
  const area = document.getElementById('messageArea');
  if (!id) {
    area.innerText = 'No message id provided in URL.';
    return;
  }

  const apiBase = getApiBase();
  try {
    const res = await fetch(`${apiBase}/api/message/${id}`);
    if (!res.ok) {
      area.innerText = 'Message not found.';
      return;
    }
    const data = await res.json();
    area.innerHTML = `
      <p><strong>From:</strong> ${data.name} &lt;${data.email}&gt;</p>
      <p><strong>Message:</strong><br>${data.message}</p>
      <p><strong>Admin reply:</strong><br>${data.reply ? '<div class="reply">' + data.reply + '</div>' : '<em>No reply yet</em>'}</p>
    `;
  } catch (err) {
    area.innerText = 'Failed to load message.';
  }
}

loadReply();
