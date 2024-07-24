document
  .getElementById("message-form")
  .addEventListener("submit", async function (event) {
    event.preventDefault();
    const formData = new FormData();
    formData.append("message", document.getElementById("message").value);
    formData.append("photo", document.getElementById("photo").files[0]);

    const response = await fetch("/messages", {
      method: "POST",
      body: formData,
    });

    if (response.ok) {
      alert("Message and photo uploaded successfully");
      loadMessages();
    } else {
      alert("Failed to upload message and photo");
    }
  });

async function loadMessages() {
  const response = await fetch("/messages");
  const messages = await response.json();

  const messagesDiv = document.getElementById("messages");
  messagesDiv.innerHTML = ""; // 清空现有内容
  messages.forEach((message) => {
    const messageElement = document.createElement("div");
    messageElement.innerHTML = `
          <div>
              <p>${message.text}</p>
              <a href="${message.photo_url}" target="_blank"><img src="${message.photo_url}" alt="Photo" width="200"></a>
          </div>
      `;
    messagesDiv.appendChild(messageElement);
  });
}

document.addEventListener("DOMContentLoaded", loadMessages);
