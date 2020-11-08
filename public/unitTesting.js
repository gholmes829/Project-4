window.addEventListener('DOMContentLoaded', (event) => {
  window.addEventListener('keypress', (keypress) => {
    if(keypress.key == '`' && window.location.href.includes("#access_token"))
      document.getElementById("profile-container").style.visibility = "hidden";
      document.getElementById("playlist-container").style.visibility = "hidden";
      document.getElementById("graph-container").style.visibility = "hidden";
      window.location.href = "/runTests";
  });
});
