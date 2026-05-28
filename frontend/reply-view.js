function getApiBase() {
  if (!window.location.origin || window.location.origin === "null" || window.location.protocol === "file:") {
    return "http://127.0.0.1:5000";
  }
  const port = window.location.port;
  if (port && port !== "5000") {
    return `${window.location.protocol}//${window.location.hostname}:5000`;
  }
  return window.location.origin;
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
