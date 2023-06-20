token = localStorage.getItem("accessToken")

aboutUser = document.getElementById("about_user")

const baseUrl = 'http://127.0.0.1:8000'

const urlParams = new URLSearchParams(window.location.search);
const username = urlParams.get('username');

const getInfoUser = async () => {
  const myHeaders = new Headers();
  myHeaders.append(
    "Authorization",
    `Bearer ${token}`);

  const requestOptions = {
    method: 'GET',
    headers: myHeaders,
    redirect: 'follow'
  };

  const respons = await fetch(`${baseUrl}/api/users/${username}`, requestOptions)
    if (respons.status === 200) {
      result = await respons.json()
      console.log(result);
      aboutUser.innerHTML = ""
      const img = document.createElement('img');
      img.src = result.avatar;
      const avatar = document.createElement('img')
      avatar.src = result.avatar;
      avatar.style.borderRadius = '20%';
      avatar.style.width = '200px';
      avatar.style.height = 'avto';


      const el1 = document.createElement('div')
      el1.className = "col-lg-6 mx-auto mb-4"

      const el2 = document.createElement('div')
      el2.className = "row"

      const avatarDiv = document.createElement('div')
      avatarDiv.className = "col-md-4 themed-grid-col"

      const avatarSpan = document.createElement('span');
      avatarSpan.innerHTML = avatar.outerHTML;
      avatarDiv.appendChild(avatarSpan)

      const aboutUserDdiv = document.createElement('div')
      aboutUserDdiv.className = "col-md-8 themed-grid-col align-items-center"

      const userNameH = document.createElement('h4')
      userNameH.className = "my_display-4 text-body text-center"
      userNameH.textContent = result.username

      aboutUserDdiv.appendChild(userNameH)


      const userInfoUl = document.createElement("ul");
      userInfoUl.style.paddingLeft = "180px";
      const userFirstNameLi = document.createElement("li");
      userFirstNameLi.textContent = `First Name: ${result.first_name}`;
      userFirstNameLi.classList.add("text-left");
      userInfoUl.appendChild(userFirstNameLi)

      const userLastNameLi = document.createElement("li");
      userLastNameLi.textContent = `Last Name: ${result.last_name}`;
      userLastNameLi.classList.add("text-left");
      userInfoUl.appendChild(userLastNameLi)

      const usercreateLi = document.createElement("li");
      const createdAt = new Date(result.created_at);
      const dateOptions = { year: 'numeric', month: 'long', day: 'numeric' };
      const formattedDate = createdAt.toLocaleDateString(undefined, dateOptions);

      usercreateLi.textContent = `Created at: ${formattedDate}`;
      usercreateLi.classList.add("text-left");
      userInfoUl.appendChild(usercreateLi)

      const userImageNumberLi = document.createElement("li");
      userImageNumberLi.textContent = `Number users photos: ${result.number_of_images}`;
      userImageNumberLi.classList.add("text-left");
      userInfoUl.appendChild(userImageNumberLi)

      aboutUserDdiv.appendChild(userInfoUl)
      el2.appendChild(avatarDiv)
      el2.appendChild(aboutUserDdiv)
      el1.appendChild(el2)
      aboutUser.appendChild(el1)

    }
  }
  getInfoUser()
