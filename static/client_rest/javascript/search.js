token = localStorage.getItem("accessToken")

const baseUrl = 'http://127.0.0.1:8000'

const searchParams = new URLSearchParams(window.location.search);
const searchValue = searchParams.get('search');
console.log(searchValue);

searchList = document.getElementById("search_list")
console.log(searchList);

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
  
    const respons = await fetch(`${baseUrl}/api/users/users_id/${user_id}`, requestOptions)
    if (respons.status === 200) {
      result = await respons.json()
      return result;
    }
  }

const getSearch = async () => {
    const myHeaders = new Headers();
    myHeaders.append(
        "Authorization",
        `Bearer ${token}`);

    const requestOptions = {
        method: 'GET',
        headers: myHeaders,
        redirect: 'follow'
    };

    const respons = await fetch(`${baseUrl}/api/users/search_all/?data=${searchValue}`, requestOptions)
    if (respons.status === 200) {
        result = await respons.json()
        searchList = document.getElementById("search_list")
        searchList.innerHTML = ""
        if (result.users.length > 0) {
            console.log(result.users);
        }
        if (result.images.length > 0) {
            const images = document.createElement("div")
            images.className = "col-lg-6 mx-auto mb-4"
            for (const image of result.images) {
                const img = document.createElement('img');
                img.src = image.url;
                const user = image.user_id ? await getUserById(image.user_id) : null;

                const avatar = document.createElement('img');
                avatar.src = user.avatar;
                avatar.style.borderRadius = '20%';
                avatar.style.width = '30px';
                avatar.style.height = '30px';

                const el = document.createElement('div');
                el.className = 'modal-content rounded-4 shadow';

                const avatarUserNameDiv = document.createElement('div');
                avatarUserNameDiv.className = "author mb-2 mt-2"
                const avatarSpan = document.createElement('span');
                avatarSpan.innerHTML = avatar.outerHTML;


                const authorLink = document.createElement('a');
                authorLink.className = 'author';
                authorLink.textContent = user.username;
                authorLink.href = `user_profile.html?username=${user.username}`
                avatarUserNameDiv.appendChild(avatarSpan);
                avatarUserNameDiv.appendChild(authorLink);

                const photoDiv = document.createElement('div');
                const photoLink = document.createElement('a');
                photoLink.className = 'photo';
                photoLink.innerHTML = img.outerHTML;
                photoDiv.appendChild(photoLink);

                const imagesDescriptionDiv = document.createElement('div');
                imagesDescriptionDiv.className = "some_class mb-2"
                const descriptionSpan = document.createElement('span');
                descriptionSpan.textContent = image.description;
                imagesDescriptionDiv.appendChild(descriptionSpan)

                const imageRatingDiv = document.createElement('div');
                const imageRating = document.createElement('a');
                imageRating.textContent = `Rating: ${image.avg_rating}`
                imageRatingDiv.appendChild(imageRating)
                imagesDescriptionDiv.appendChild(imageRatingDiv)

                const topicsDiv = document.createElement('div');
                topicsDiv.className = 'node__topics';
                topicsDiv.textContent = 'Tags: ';

                for (const tag of image.tags) {
                    const tagLink = document.createElement('a');
                    tagLink.className = 'btn mb-2 mb-md-0 btn-outline-danger btn-sm';
                    tagLink.textContent = tag.name;
                    topicsDiv.appendChild(tagLink);
                }
                imagesDescriptionDiv.appendChild(topicsDiv)

                el.appendChild(avatarUserNameDiv);
                el.appendChild(photoDiv);
                el.appendChild(imagesDescriptionDiv);
                images.appendChild(el)
            }
            searchList.appendChild(images)
        }
    }
}
getSearch()