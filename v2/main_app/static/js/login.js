function setup_firebase(auth_config){
  firebase.initializeApp(auth_config);
  configureFirebaseLogin();
  configureFirebaseLoginWidget();
}

function configureFirebaseLogin() {
    // Used in the initial login page
    firebase.auth().onAuthStateChanged(function(user) {
      if (user) {
        let name = user.displayName;
        /* If the provider gives a display name, use the name for the
        personal welcome message. Otherwise, use the user's email. */
        let welcomeName = user.email;

        user.getIdToken().then(function(idToken) {
          userIdToken = idToken;
          user_name = name;
          user_email = welcomeName;
          //alert("Logged in");
          
          $('#user').text(welcomeName);
          $('#logged-in').show();

        });

      } else {
        $('#logged-in').hide();
        $('#login_container').show();

      }
    });
    // [END gae_python_state_change]
}

function configureFirebaseLoginWidget() {
    let uiConfig = {
        callbacks: {
          signInSuccessWithAuthResult: function(authResult, redirectUrl){
            document.getElementById('loader').style.display = 'block';
            let data = {user_email: authResult.user.email};
            $.ajax({
              type: "POST",
              url: "/login",
              dataType: "json",
              contentType: "application/json;charset=UTF-8;",
              data: JSON.stringify(data),
              success: function(result){
                location.href=result['redirect'];
              },
              error: function(e){
                console.log(e);
              }
            })
            return false;
          },
          uiShown: function() {
              document.getElementById('loader').style.display = 'none';
          }
        },
        'signInFlow': 'redirect',
        'signInSuccessUrl': '/home',
        'signInOptions': [
            // Leave the lines as is for the providers you want to offer your users.
            firebase.auth.GoogleAuthProvider.PROVIDER_ID,
            {
              provider: firebase.auth.EmailAuthProvider.PROVIDER_ID,
              requireDisplayName: true,
            },
        ],
    };
    let ui = new firebaseui.auth.AuthUI(firebase.auth());
    ui.start('#firebaseui-auth-container', uiConfig);
}
function enable_signout(){
  //Enables signout button after successful login
  let signOutBtn = $('#sign-out');
  signOutBtn.prop('disabled', false);
  signOutBtn.prop('hidden', false);
  signOutBtn.click(function(event) {
    event.preventDefault();
    $.ajax({
      type: "POST",
      url: "/logout",
      success: function(){
        firebase.auth().signOut().then(function() {
          console.log("Sign out successful");
          window.location.href = "/login";
        }, function(error) {
          console.log(error);
        });
      }
    });
  });
}
function initApp(authConfig){
  //Initialize firebase app with API key, domain, and GCP project
  firebase.initializeApp(authConfig);
  return new Promise(function(resolve, reject){
    firebase.auth().onAuthStateChanged((user) => {
      if (user){
        // get user auth level
        $.ajax({
          type: "GET",
          url: "/api/user",
          success: function(data){
            let json = $.parseJSON(data)
            let ret_data = {
              "email": "",
              "admin": "",
              "student": "",
              "instructor": "",
              "display_name": user.displayName
            }
            ret_data['email'] = user.email;
            if (json['admin'] === true){
              ret_data['admin'] = true;
            }
            if (json['student'] === true){
              ret_data['student'] = true;
            }
            if (json['instructor'] === true){
              ret_data['instructor'] = true;
            }
            resolve(ret_data);
          }
        });
      }
    });
  });
}
