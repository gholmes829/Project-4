var spotifyApi = new SpotifyWebApi();

let html_access_token = document.getElementById("access");
if(html_access_token.innerHTML.length > 0)
{
  spotifyApi.setAccessToken(html_access_token.innerHTML);
  console.log("cashe loaded");
  getUser();
}
else {
  html_access_token.addEventListener('change', (event) => {
    spotifyApi.setAccessToken(html_access_token.innerHTML);
    console.log("event loaded");
  });
}


var userID;
var selectedSong;
var selectedSongid;
var selectedPlaylist;
var selected_playlist_name;


function getUser()
{
  spotifyApi.getMe(null).then(
      function (data) {
        callGetUserPlayerList(data);
        userID = data.id;
        document.getElementById("profile-userName").innerHTML = "Username: " + data.display_name;
        document.getElementById("profile-userID").innerHTML = ("userID: " + data.id);
        document.getElementById("profile-pic").src = data.images[0].url;
      },
      function (err) {
        console.error(err);
      });
  }

    /**
     * makes playlists into button options and calls a function that gets tracks in playlist
     * @param {object} oldData data of all the user playlists
     */
    function callGetUserPlayerList(oldData)
    {
      spotifyApi.getUserPlaylists(oldData.id).then(
        function (data) {
          document.getElementById("header").innerHTML = "Choose a Playlist to be Edited";
          for (let i = 0; i<data.items.length;i++)
          {
              let newButton = document.createElement("button");
              var node = document.createTextNode(data.items[i].name);
              newButton.appendChild(node);
              var element = document.getElementById("playList");
              newButton.onclick = function(){showTracks(data.items[i].id);
              selected_playlist_name = data.items[i].name;};
              element.appendChild(newButton);
          }
        },
        function (err) {
          console.error(err);
        }
      );
    }
    /**
     * displays track names after being edited
     * @param {string} oldDataId id of the playlist selected
     */
    function showTracks(oldDataId){
      document.getElementById("playList").style.display = "none";
      spotifyApi.getPlaylistTracks(oldDataId).then(
        function (data) {
          createPlaylistDictionary(data);
          selectedPlaylist = data;
          document.getElementById("header").innerHTML = "Choose a Track to play";
          for (let i = 0; i<data.items.length;i++)
          {
              var newButton = document.createElement("button");
              var node = document.createTextNode(data.items[i].track.name);

              newButton.appendChild(node);
              var element = document.getElementById("trackList");
              newButton.onclick = function(){
              selectedSong =i;
              selectedSongid = data.items[i].track.id
              updateIframe(selectedSongid);
              console.log(data);};
              element.appendChild(newButton);

          }

        },
        function (err) {
          console.error(err);
        }
      );
    }

var data_str;
function createPlaylistDictionary(data)
{
  let length = data.items.length;
  var playListDictionary = {"Playlist" : []};
  var tempFeatures = null;
  var tempID = "";
  misMatchURL = document.getElementById("generate-remove");
  for(let i = 0;i<length;i++)
  {
    tempID = data.items[i].track.id;
    spotifyApi.getAudioFeaturesForTrack(tempID,null).then(
      function (features) {
        tempFeatures = {ID : i,
              acousticness : features.acousticness,
              danceability: features.danceability,
              energy       : features.energy,
              instrumentalness: features.instrumentalness,
              key        : features.key,
              liveness   : features.liveness,
              loudness   : features.loudness,
              speechiness: features.speechiness,
              tempo      : features.tempo,
              valence    : features.valence};
        playListDictionary.Playlist.push(tempFeatures);
        data_str = encodeURIComponent(JSON.stringify(playListDictionary));
        misMatchURL.href = '/misMatch/?somevalue=' + data_str;
      },
      function (err) {
        console.error(err);
      });
  }
}



/**
* This function takes the current selected playlist and creates a clone of it on spotify
*/
function finishPlaylist()
{
  var finalPlaylist = [];
  console.log(selected_playlist_name);
  for(i = 0; i < selectedPlaylist.items.length;i++)
  {
    finalPlaylist[i] = (selectedPlaylist.items[i].track.uri).toString();
  }

  spotifyApi.createPlaylist(userID,{name:"clone of " + selected_playlist_name}).then(
    function (data) {
      spotifyApi.addTracksToPlaylist(data.id,finalPlaylist,null).then(
        function(newPlaylist){
          console.log(newPlaylist);
          location.reload();
        },
        function(err){
          console.log(err);
        });
    },
    function (err) {
      console.error(err);
    });
  }
function removeSong()
  {
    console.log(selectedSong);
    let temp = 0;
    let offset = false;
    for(let i=0;i<selectedPlaylist.items.length;i++)
    {
      if (i != selectedSong && !offset)
      {
        console.log("Adding selected song " + i);
        var newButton = document.createElement("button");
        var node = document.createTextNode(selectedPlaylist.items[i].track.name);
        newButton.appendChild(node);
        var element = document.getElementById("trackList");
        newButton.onclick = function(){selectedSong = i;
        updateIframe(selectedSongid)};
        element.appendChild(newButton);
      }
      else if (i==selectedSong){
        console.log("Splice");
        temp = i;
        offset = true;
        //delete selectedPlaylist.items[i];
        //selectedPlaylist.items.length = selectedPlaylist.items.length-1;
      }
      else if(offset)
      {
        console.log("Adding selected song " + i);
        var newButton = document.createElement("button");
        var node = document.createTextNode(selectedPlaylist.items[i].track.name);
        newButton.appendChild(node);
        var element = document.getElementById("trackList");
        newButton.onclick = function(){selectedSong = i-1;
        };
        element.appendChild(newButton);
        console.log("Incorrect");
      }
    }
    selectedPlaylist.items.splice(temp,1);
    for(let x=0;x<selectedPlaylist.items.length+1;x++)
    {
      console.log("delete " + x);
      var element = document.getElementById("trackList");
      element.removeChild(element.childNodes[0]);

    }
    console.log(selectedSong);
    console.log(selectedPlaylist.items.length);
}


function removeMisMatched()
{
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
  if (this.readyState == 4 && this.status == 200) {
    document.getElementById("demo").innerHTML = this.responseText;
  }};
  xhttp.open("POST","../flow.js",true);
  xhttp.send();
}
function updateIframe(id)
{
  var url = "https://open.spotify.com/embed/track/" + id
  document.getElementById("playButton").src = url;

}
