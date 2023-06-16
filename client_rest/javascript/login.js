console.log("Run")

const baseUrl = 'http://127.0.0.1:8000'

const form = document.forms[0]

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
        window.location = "/images.html"
    }
})