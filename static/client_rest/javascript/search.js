token = localStorage.getItem("accessToken")

const baseUrl = 'http://svitlogram.fly.dev'

const searchParams = new URLSearchParams(window.location.search);
const searchValue = searchParams.get('search');

searchList = document.getElementById("search_list")

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
        console.log(result);
        searchList = document.getElementById("search_list")
        searchList.innerHTML = ""
        if (result.users.length > 0) {
            const usersInfo = document.createElement("div")
            usersInfo.className = "col-lg-6 mx-auto mb-4"
            console.log(result.users);
            for (const user of result.users) {

                const img = document.createElement('img');
                img.src = user.avatar;
                const avatar = document.createElement('img')
                avatar.src = user.avatar;
                avatar.style.borderRadius = '20%';
                avatar.style.width = '200px';
                avatar.style.height = 'avto';


                //const el1 = document.createElement('div')
                //el1.className = "col-lg-6 mx-auto mb-4"

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
                userNameH.textContent = user.username

                aboutUserDdiv.appendChild(userNameH)


                const userInfoUl = document.createElement("ul");
                userInfoUl.style.paddingLeft = "180px";
                const userFirstNameLi = document.createElement("li");
                userFirstNameLi.textContent = `First Name: ${user.first_name}`;
                userFirstNameLi.classList.add("text-left");
                userInfoUl.appendChild(userFirstNameLi)

                const userLastNameLi = document.createElement("li");
                userLastNameLi.textContent = `Last Name: ${user.last_name}`;
                userLastNameLi.classList.add("text-left");
                userInfoUl.appendChild(userLastNameLi)

                const usercreateLi = document.createElement("li");
                console.log(user.created_at);
                const createdAt = new Date(user.created_at);
                const dateOptions = { year: 'numeric', month: 'long', day: 'numeric' };
                const formattedDate = createdAt.toLocaleDateString(undefined, dateOptions);

                //usercreateLi.textContent = `Created at: ${formattedDate}`;
                //usercreateLi.classList.add("text-left");
                //userInfoUl.appendChild(usercreateLi)

                //const userImageNumberLi = document.createElement("li");
                //userImageNumberLi.textContent = `Number users photos: ${user.number_of_images}`;
                //userImageNumberLi.classList.add("text-left");
                //userInfoUl.appendChild(userImageNumberLi)

                aboutUserDdiv.appendChild(userInfoUl)
                el2.appendChild(avatarDiv)
                el2.appendChild(aboutUserDdiv)
                usersInfo.appendChild(el2)
            }
            searchList.appendChild(usersInfo)
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