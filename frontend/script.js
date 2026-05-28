document.querySelector("form").addEventListener("submit", async function(e) {
  e.preventDefault();

  const data = {
    name: document.getElementById("name").value,
    email: document.getElementById("email").value,
    message: document.getElementById("message").value
  };

  let apiBase;
  if (!window.location.origin || window.location.origin === "null" || window.location.protocol === "file:") {
    apiBase = "http://127.0.0.1:5000";
  } else if (window.location.port && window.location.port !== "5000") {
    apiBase = `${window.location.protocol}//${window.location.hostname}:5000`;
  } else {
    apiBase = window.location.origin;
  }
  const res = await fetch(`${apiBase}/api/contact`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(data)
  });

  const result = await res.json();

  // show message inside page
  const msgBox = document.getElementById("responseMessage");

  if (!msgBox) {
    const div = document.createElement("div");
    div.id = "responseMessage";
    div.style.marginTop = "10px";
    document.querySelector("form").appendChild(div);
  }

  let text = result.message;
  if (result.id) {
    text += ` (Your message ID: ${result.id}) \nView reply: ` + apiBase + `/reply-view.html?id=${result.id}`;
  }
  document.getElementById("responseMessage").innerText = text;
  document.getElementById("responseMessage").style.color =
    res.status === 200 ? "green" : "red";

  this.reset();
});