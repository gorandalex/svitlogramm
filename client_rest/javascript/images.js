token = localStorage.getItem("accessToken")

images = document.getElementById("images")

const getUserById = async (user_id) => {
  const myHeaders = new Headers();
  myHeaders.append(
    "Authorization",
    `Bearer ${token}`);

  const requestOptions = {
    method: 'GET',
    headers: myHeaders,
    redirect: 'follow'
  };

  const respons = await fetch(`http://127.0.0.1:8000/api/users/users_id/${user_id}`, requestOptions)
  if (respons.status === 200) {
    result = await respons.json()
    console.log(result.username)
    return result;
  }
}

const getImeges = async () => {
  const myHeaders = new Headers();
  myHeaders.append(
    "Authorization",
    `Bearer ${token}`);

  const requestOptions = {
    method: 'GET',
    headers: myHeaders,
    redirect: 'follow'
  };

  const respons = await fetch("http://127.0.0.1:8000/api/images", requestOptions)
  if (respons.status === 200) {
    result = await respons.json()
    images.innerHTML = ""
    for (image of result) {
      const img = document.createElement('img')
      img.src = image.url
      user = await getUserById(image.user_id)
      const avatar = document.createElement('img')
      avatar.src = user.avatar
      console.log(avatar.outerHTML);
      //<li class="list-group-item">An item</li>
      el = document.createElement("li")
      el.className = "modal-content rounded-4 shadow mb-4"
      el.innerHTML = `${avatar.outerHTML}User: ${user.username}<br>${img.outerHTML}<br>Description: ${image.description}<br>Rating: `
      images.appendChild(el)
    }
  }
}

getImeges()