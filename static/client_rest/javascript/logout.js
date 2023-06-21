token = localStorage.getItem("accessToken")

async function logout() {
    const url = `${baseUrl}/api/logout`;
    const token = localStorage.getItem("accessToken");

    const requestOptions = {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    };

    try {
        const response = await fetch(url, requestOptions);
        const data = await response.json();
        window.location.href = "logout.html";
    } catch (error) {
        console.log("Error:", error);
    }
}
