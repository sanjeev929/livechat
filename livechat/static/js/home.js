var currentusername="{{name}}"
    function showUserProfile(userName, userBio, userProfile,followbtn) {
        var userDetails = document.getElementById('user-details');
        var userNameElement = document.getElementById('user-name');
        var userBioElement = document.getElementById('user-bio');
        var profilePicture = document.getElementById('profile-picture');
        var followButton = document.getElementById('follow-button');
        var unfollowButton = document.getElementById('unfollow-button');
        if (followbtn) {
            followButton.style.display = 'block'; 
            unfollowButton.style.display = 'none'; 
        }
        else{
            followButton.style.display = 'none'; 
            unfollowButton.style.display = 'block'; 
        }
        // Set user details and show the section
        userNameElement.textContent = userName;
        userBioElement.textContent = userBio;
        profilePicture.src = userProfile;
        userDetails.style.display = 'block';
    }

function updateNotificationDetails(users) {
    var chatUsersList = document.querySelector('.followerchat-users-list');
    chatUsersList.innerHTML = '';
    var totalFollowerCount = 0;
    users.forEach(profile => {

        var followerItem = document.createElement('li');
        followerItem.className = 'followerchat-user-item';
        
        var userImg = document.createElement('img');
        if(profile.profile_url=== "Not"){
            userImg.src =profileImageUrl;
        }
        else{
            userImg.src = "data:image;base64," +profile.profile_url;
        }
        
        userImg.alt = profile.username;
        userImg.className = 'followerprofile-picture';
        followerItem.appendChild(userImg);

        var userName = document.createElement('span');
        userName.className = 'followerchat-user-name';
        userName.textContent = profile.username;
        followerItem.appendChild(userName);

        var followerButtons = document.createElement('div');
        followerButtons.className = 'follower-buttons';

        var acceptButton = document.createElement('button');
        acceptButton.textContent = 'Accept';
        acceptButton.className = 'followerchat-user-action';
        // Add event listener for accept button
        acceptButton.addEventListener('click', function() {
            submitAction(profile.username, 'accept');
            acceptButton.style.display='none'

        });
        followerButtons.appendChild(acceptButton);

        var declineButton = document.createElement('button');
        declineButton.textContent = 'Decline';
        declineButton.className = 'followerchat-user-action';
        // Add event listener for decline button
        declineButton.addEventListener('click', function() {
            submitAction(profile.username, 'decline');
            declineButton.style.display='none'

        });
        followerButtons.appendChild(declineButton);

        followerItem.appendChild(followerButtons);

        chatUsersList.appendChild(followerItem);
        totalFollowerCount++;
    });

    document.getElementById('notification-count').textContent = totalFollowerCount;
    
}

// window.onload = function() {
//         var userNameElement = document.querySelector('.followerchat-user-name');
//         console.log(userNameElement)
//         if (userNameElement.textContent.trim() !== '') {
//             document.getElementById('notification-detailsall').style.display = 'block';
//         }
//     };
function submitAction(username, action) {

    var data = JSON.stringify({ username: username, action: action });
    var csrftoken = getCookie('csrftoken');
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/accept-decline-follow/', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('X-CSRFToken', csrftoken);
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            console.log(xhr.responseText);
        }
    };
    xhr.send(data);
}

function friendslist(users) {
    var chatUsersList = document.querySelector('.friendslist-users-list');
    chatUsersList.innerHTML = '';
    var totalFollowerCount = 0;
    console.log("==========",users)
    users.forEach(profile => {

        var followerItem = document.createElement('li');
        followerItem.className = 'friendslist-user-item';
        
        var userImg = document.createElement('img');
        console.log(profile.profile_url)
        if(profile.profile_url=== "Not"){
            userImg.src =profileImageUrl;
        }
        else{
            userImg.src = "data:image;base64," +profile.profile_url;
        }
        var path = userImg.src.split(window.location.origin)[1];
        console.log("helo",path)
        userImg.alt = profile.username;
        userImg.className = 'friendslistprofile-picture';
        followerItem.appendChild(userImg);

        var userName = document.createElement('span');
        userName.className = 'friendslist-user-name';
        userName.textContent = profile.username;
        followerItem.appendChild(userName);

        var followerButtons = document.createElement('div');
        followerButtons.className = 'friendslist-buttons';

        var acceptButton = document.createElement('button');
        acceptButton.textContent = 'Message';
        acceptButton.className = 'friendslist-user-action';
        // Add event listener for accept button
        acceptButton.addEventListener('click', function() {
            submitAction(profile.username, 'accept');
            acceptButton.style.display='none'

        });
        followerButtons.appendChild(acceptButton);

        followerItem.appendChild(followerButtons);

        chatUsersList.appendChild(followerItem);
        totalFollowerCount++;
    });

    document.getElementById('friends-count').textContent = totalFollowerCount;
    
}

// Function to update chat users list
function updateChatUsersList(users) {
    var chatUsersList = document.querySelector('.chat-users-list');
    chatUsersList.innerHTML = '';
    users.forEach(user => {
        // Skip adding the current user's profile
        if (user.follower_profiles || user.followers_profile){
            return;
        }
        
        if (user.name === currentusername) {
            return;
        }
        
        var listItem = document.createElement('li');
        listItem.className = 'chat-user-item';
        listItem.onclick = function() {
            if (user.profile === "Not") {
                showUserProfile(user.name, user.bio, profileImageUrl,user.followbtn);
            }
            else{
                showUserProfile(user.name, user.bio,  "data:image;base64,"+user.profile,user.followbtn);
            }
        };
        var userImg = document.createElement('img');
        if (user.profile === "Not") {
            userImg.src=profileImageUrl;
        }
        else{
            userImg.src = "data:image;base64," + user.profile;
        }
        
        userImg.alt = user.name;
        userImg.className = 'chat-user-img';
        listItem.appendChild(userImg);

        var userName = document.createElement('span');
        userName.className = 'chat-user-name';
        userName.textContent = user.name;
        listItem.appendChild(userName);

        chatUsersList.appendChild(listItem);
    });
}


function showProfileForm() {
    var editProfile = document.getElementById('edit-profile');
    if (editProfile.style.display === 'block') {
        editProfile.style.display = 'none'; // Close the form if it's already open
    } else {
        editProfile.style.display = 'block'; // Otherwise, open the form
    }
}

function showNotifications() {
    var editProfile = document.getElementById('notification-detailsall');
    if (editProfile.style.display === 'block') {
        editProfile.style.display = 'none'; // Close the form if it's already open
    } else {
        var userNameElement = document.querySelector('.followerchat-user-name');
        console.log(userNameElement)
        if (userNameElement.textContent.trim() !== '') {
            document.getElementById('notification-detailsall').style.display = 'block';
            editProfile.style.display = 'block'; 
        }
    }
}

function showfriends() {
    var editProfile = document.getElementById('friends-detailsall');
    if (editProfile.style.display === 'block') {
        editProfile.style.display = 'none'; // Close the form if it's already open
    } else {
        var userNameElement = document.querySelector('.friendslist-user-name');
        console.log(userNameElement)
        if (userNameElement.textContent.trim() !== '') {
            document.getElementById('friends-detailsall').style.display = 'block';
            editProfile.style.display = 'block'; 
        }
    }
}

$.ajax({
    url: '/get_user_details/',  // Replace '/your-url/' with the actual URL endpoint
    type: 'GET',
    success: function(response) {
        var userData = response.user_data;
        var followData = response.follow_data;
        var friends = response.friends;
        console.log("ok",friends)
        friendslist(friends)
        updateChatUsersList(userData)
        updateNotificationDetails(followData)
        // Process userData and followData as needed
    },
    error: function(xhr, status, error) {
        // Handle errors here
        console.error('Error:', error);
    }
});

document.addEventListener("DOMContentLoaded", function() {
    var followButton = document.getElementById('follow-button');
    var unfollowButton = document.getElementById('unfollow-button');

    // Function to handle follow/unfollow action
    function handleFollowAction(button) {
        // Extract necessary data
        var accountName = document.getElementById('user-name').textContent;
        var followResponse = button.textContent.trim(); // Get the current button text
        
        // Toggle button text
        button.textContent = followResponse === 'Follow' ? 'Un Follow' : 'Follow';
        console.log(followResponse)
        // Get CSRF token
        var csrftoken = getCookie('csrftoken');

        // Send data to the backend using AJAX
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/follow/', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.setRequestHeader('X-CSRFToken', csrftoken); // Include CSRF token in headers
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                // Handle response from the server if needed
                console.log('Follow/unfollow request sent successfully');
            }
        };
        var data = JSON.stringify({ accountName: accountName, followResponse: followResponse });
        xhr.send(data);
    }

    // Event listener for follow button
    followButton.addEventListener('click', function(event) {
        event.preventDefault(); // Prevent default form submission behavior
        handleFollowAction(followButton);
    });

    // Event listener for unfollow button
    unfollowButton.addEventListener('click', function(event) {
        event.preventDefault(); // Prevent default form submission behavior
        handleFollowAction(unfollowButton);
    });
});

// Function to retrieve CSRF token from cookies
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function previewImage(event) {

    const preview = document.getElementById('profile-picture-preview');
    const file = event.target.files[0];
    const reader = new FileReader();

    reader.onloadend = function () {
        preview.src = reader.result;
    }

    if (file) {
        reader.readAsDataURL(file);
    } else {
        preview.src = "";
    }
}
document.addEventListener('dblclick', function(event) {
    // Close all open containers
    var notificationProfile = document.getElementById('notification-detailsall');
    var freindsProfile = document.getElementById('friends-detailsall');
    var editProfile = document.getElementById('edit-profile');
    var userdetails = document.getElementById('user-details');
    
    // Check if the elements are found before trying to hide them
    if (notificationProfile) {
        notificationProfile.style.display = 'none';
    }
    if (editProfile) {
        editProfile.style.display = 'none';
    }
    if (userdetails) {
        userdetails.style.display = 'none';
    }
    if (freindsProfile) {
        freindsProfile.style.display = 'none';
    }
});


document.addEventListener("DOMContentLoaded", function() {
    // Get the container that holds both buttons
    var container = document.querySelector('.follower-buttons');

    // Function to hide the notification container
    function hideNotificationContainer() {
        var notificationContainer = document.getElementById('notification-detailsall');
        notificationContainer.style.display = 'none';
    }
    
    // Add event listener for the buttons container
    container.addEventListener('click', function() {
        hideNotificationContainer();
    });
});