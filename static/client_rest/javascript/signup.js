console.log("Run")

const baseUrl = 'http://svitlogram.fly.dev'

const form = document.forms[0]

const urlParams = new URLSearchParams(window.location.search);
const message = urlParams.get("message");

returnMessage = document.getElementById("return_message")

if (message) {
    returnMessage.innerHTML = ""
    const returnMessageH = document.createElement('h7')
    returnMessageH.className = "my_display-4 text-body text-center"
    returnMessageH.textContent = message;
    returnMessageH.classList.add("text-center");
    returnMessage.appendChild(returnMessageH)
}

form.addEventListener("submit", async(e) => {
    e.preventDefault()
    const username = form.username.value
    const email = form.email.value
    const first_name = form.first_name.value
    const last_name = form.last_name.value
    const password = form.password.value
    

    const myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/json")

    var raw = JSON.stringify({
        "username": username,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "password": password
      });

    var requestOptions = {
        method: 'POST',
        headers: myHeaders,
        body: raw,
        redirect: 'follow'
      };

    const response = await fetch(
        `${baseUrl}/api/auth/signup`, 
        requestOptions)
    if (response.status == 201) {
        result = await response.json()
        const message = encodeURIComponent(`Congratulations, ${result.user.first_name} ${result.user.last_name}!\nYour registration was successful.\nPlease verify your email address.`)
        window.location = `/static/client_rest/index.html?message=${message}`
    }
    if (response.status == 409){
        const message = encodeURIComponent(`An account with the same email address or username already exists`)
        window.location = `/static/client_rest/signup.html?message=${message}`
    }

})