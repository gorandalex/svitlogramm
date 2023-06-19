console.log("Run")

const baseUrl = 'http://127.0.0.1:8000'

const form = document.forms[0]

const urlParams = new URLSearchParams(window.location.search);
const message = urlParams.get("message");

returnMessage = document.getElementById("return_message")

if (message) {
    console.log(message);
    returnMessage.innerHTML = "";
    
    const lines = message.split("\n"); 
    const returnMessageContainer = document.createElement("div");
    returnMessageContainer.className = "my_display-4 text-body text-center";
    
    lines.forEach((line) => {
        const lineElement = document.createElement("p");
        lineElement.textContent = line;
        returnMessageContainer.appendChild(lineElement);

    });
    
    returnMessage.appendChild(returnMessageContainer);
    returnMessage.classList.add("text-center");
}


form.addEventListener("submit", async(e) => {
    e.preventDefault()
    const username = form.username.value
    const password = form.password.value

    const myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/x-www-form-urlencoded");

    const urlencoded = new URLSearchParams();
    urlencoded.append("username", username);
    urlencoded.append("password", password);

    var requestOptions = {
        method: 'POST',
        headers: myHeaders,
        body: urlencoded,
        redirect: 'follow'
      };

    const response = await fetch(
        `${baseUrl}/api/auth/login`, 
        requestOptions)
    if (response.status == 200) {
        result = await response.json()
        localStorage.setItem("accessToken", result.access_token)
        localStorage.setItem("refreshToken", result.refresh_token)
        window.location = `/static/client_rest/images.html`
    }
})