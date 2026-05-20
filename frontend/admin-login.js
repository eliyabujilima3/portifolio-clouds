document.querySelector("#loginForm").addEventListener("submit", async function(e) {
  e.preventDefault();

  const data = {
    username: document.getElementById("username").value,
    password: document.getElementById("password").value
  };

  try {
    const res = await fetch("https://portifolio-clouds.onrender.com/api/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    });

    const result = await res.json();

    if (res.status === 200) {
      window.location.href = "admin.html";
    } else {
      alert(result.message);
    }

  } catch (error) {
    console.log(error);
    alert("Server error");
  }
});