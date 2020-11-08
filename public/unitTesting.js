window.addEventListener('DOMContentLoaded', (event) => {
  window.addEventListener('keypress', (keypress) => {
    if(keypress.key == '`' && spotifyApi.getAccessToken().len > 0)
      console.log("we in business");
  });
});
