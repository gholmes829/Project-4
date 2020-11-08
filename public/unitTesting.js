window.addEventListener('DOMContentLoaded', (event) => {
  if(window.location.href.includes("&tests="))
  {
    document.getElementById("profile-container").style.visibility = "hidden";
    document.getElementById("playlist-container").style.visibility = "hidden";
    document.getElementById("graph-container").style.visibility = "hidden";

    let location = window.location.href;
    location = decodeURIComponent(location);
    let start = (location.indexOf("&tests=")+10),
        stop = location.indexOf("&tests=") - start;
    tests = location.substring(location.indexOf("&tests=")+7);
    console.log(tests);
  }
  window.addEventListener('keypress', (keypress) => {
    if(keypress.key == '`' && window.location.href.includes("#access_token"))
      document.getElementById("profile-container").style.visibility = "hidden";
      document.getElementById("playlist-container").style.visibility = "hidden";
      document.getElementById("graph-container").style.visibility = "hidden";
      window.location.href = "/runTests/" + "?access_token=" + spotifyApi.getAccessToken();
  });
});
