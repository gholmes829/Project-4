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
    tests = location.substring(location.indexOf("&tests=")+8);
    tests =tests.replaceAll("'","");
    tests = tests.replaceAll("]","");
    console.log(tests);
    output = tests.split(',');
    console.log(output);
    testDiv = document.getElementById("Tests");
    testDiv.style.visibility = "visible";
    let count = 0;
    for (i = 0; i < output.length; i++)
    {
      var newTest = document.createElement("h1");
      newTest.style.visibility = "visibile";
      newTest.style.color = " #BFBFBF";
      var node = document.createTextNode("Test " + count + ":" + output[i]);
      newTest.append(node);
      testDiv.append(newTest);
      count++;
    }
    spotifyApi.getPlaylistTracks("37i9dQZEVXbLRQDuF5jeBp").then(
    function (data) {

        console.log("Here");
        if(createPlaylistDictionary(data))
        {
          var newTest = document.createElement("h1");
          newTest.style.visibility = "visibile";
          newTest.style.color = " #BFBFBF";
          var node = document.createTextNode("Test " + count + ": Created playList Dictionary: PASSED");
          newTest.append(node);
          testDiv.append(newTest);
          count++;
        }
        showTracks('37i9dQZEVXbLRQDuF5jeBp');
        setTimeout(() => {
          if(selectedPlaylist.href == data.href)
          {
            var newTest = document.createElement("h1");
            newTest.style.visibility = "visibile";
            newTest.style.color = " #BFBFBF";
            var node = document.createTextNode("Test " + count + ": showTracks creating correct playList: PASSED");
            newTest.append(node);
            testDiv.append(newTest);
            count++;
          }
          else {
            console.log(data);
            console.log(selectedPlaylist);
          }
        },200);
        setTimeout(() => {
          if (removeSpecific(0) == 0)
          {
            var newTest = document.createElement("h1");
            newTest.style.visibility = "visibile";
            newTest.style.color = " #BFBFBF";
            var node = document.createTextNode("Test " + count + ": removeSpecific: PASSED");
            newTest.append(node);
            testDiv.append(newTest);
            count++;
          }
          else
          {
            console.log("No workie");
          }
        },200);
      },
        function (err) {
          console.error(err);
          });
  }
  window.addEventListener('keypress', (keypress) => {
    if(keypress.key == '`' && window.location.href.includes("#access_token"))
      document.getElementById("profile-container").style.visibility = "hidden";
      document.getElementById("playlist-container").style.visibility = "hidden";
      document.getElementById("graph-container").style.visibility = "hidden";
      window.location.href = "/runTests/" + "?access_token=" + spotifyApi.getAccessToken();
  });
});

function testCreatePlaylist()
{

}
