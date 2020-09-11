function configureFirebaseLogin() {
      
    // [START gae_python_state_change]
    firebase.auth().onAuthStateChanged(function(user) {
      if (user) {
        var name = user.displayName;
        
        /* If the provider gives a display name, use the name for the
        personal welcome message. Otherwise, use the user's email. */
        var welcomeName = user.email;

        user.getIdToken().then(function(idToken) {
          userIdToken = idToken;
          user_name = name;
          user_email = welcomeName;
          var data = {user_email:user_email}
          $.ajax({
            type: "POST",
            url: "/login",
            dataType: "json",
            contentType: "application/json;charset=UTF-8;",
            data: JSON.stringify(data)
          })
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
    var uiConfig = {
        'signInFlow': 'redirect',
        'signInSuccessUrl': '/teacher_home',
        'signInOptions': [
        // Leave the lines as is for the providers you want to offer your users.
        firebase.auth.GoogleAuthProvider.PROVIDER_ID,
        ],
        // Terms of service url
        // 'tosUrl': '<your-tos-url>',
    };

    var ui = new firebaseui.auth.AuthUI(firebase.auth());
    ui.start('#firebaseui-auth-container', uiConfig);
    }


