document.querySelector("form").addEventListener("submit", async function(e) {
  e.preventDefault();

  const data = {
    name: document.getElementById("name").value,
    email: document.getElementById("email").value,
    message: document.getElementById("message").value
  };

  const res = await fetch("https://portifolio-clouds.onrender.com/api/contact", {
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

  document.getElementById("responseMessage").innerText = result.message;
  document.getElementById("responseMessage").style.color =
    res.status === 200 ? "green" : "red";

  this.reset();
});