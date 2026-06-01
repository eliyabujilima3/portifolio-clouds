document.querySelector("form").addEventListener("submit", async function(e) {
  e.preventDefault();

  const data = {
    name: document.getElementById("name").value,
    email: document.getElementById("email").value,
    message: document.getElementById("message").value
  };

  const apiBase = (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
    ? "http://127.0.0.1:5000"
    : "https://portifolio-clouds.onrender.com";
  // Ensure no trailing slash
  const apiBase = (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
    ? "http://127.0.0.1:5000"
    : "https://portifolio-clouds.onrender.com";

  console.log("📤 Sending message to:", `${apiBase}/api/contact`);
  console.log("📦 Data:", data);

  try {
    const res = await fetch(`${apiBase}/api/contact`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    });

    console.log("📨 Response status:", res.status);
    const result = await res.json();
    console.log("📨 Response:", result);

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
      const replyUrl = apiBase + `/reply-view.html?id=${result.id}`;
      const linkHtml = `${result.message}<br><a href="${replyUrl}" target="_blank">View reply →</a>`;
      document.getElementById("responseMessage").innerHTML = linkHtml;
    } else {
      document.getElementById("responseMessage").innerText = text;
    }
    document.getElementById("responseMessage").style.color =
      res.status === 200 ? "green" : "red";
    
    // Only reset if successful
    if (res.status === 200) {
      this.reset();
      console.log("✅ Message sent successfully!");
    } else {
      console.warn("⚠️ Message may not have been sent properly");
    }
  } catch (error) {
    console.error("❌ Error:", error);
    const msgBox = document.getElementById("responseMessage");
    if (!msgBox) {
      const div = document.createElement("div");
      div.id = "responseMessage";
      div.style.marginTop = "10px";
      document.querySelector("form").appendChild(div);
    }
    document.getElementById("responseMessage").innerText = "❌ Error: " + (error.message || "Network error. Check console logs.");
    document.getElementById("responseMessage").style.color = "red";
  }
});