
var spotifyApi;

var userID;
var selectedSong;
var selectedSongid;
var selectedPlaylist;
var selected_playlist_name;
var playListID;
var ratedPlaylist;

window.addEventListener('DOMContentLoaded', (event) => {
  spotifyApi = new SpotifyWebApi();
  let html_access_token = document.getElementById("access");
  if(html_access_token.innerHTML.length > 0)
  {
    spotifyApi.setAccessToken(html_access_token.innerHTML);
    console.log("cashe loaded");
    getUser();
  }
  if(window.location.href.includes("&playList="))
  {
    let location = window.location.href;
    location = decodeURIComponent(location);
    let start = (location.indexOf("&playList=")+10),
        stop = location.indexOf("&playlistID=") - start;
    playListID = location.substring(location.indexOf("&playlistID=")+12);
    showTracks(playListID);
    setTimeout(() => {
      let newPlaylist = location.substr(start,stop);
      let colin = newPlaylist.indexOf(':');
      let comma = 0;
      let newId = newPlaylist.substr(1,colin-comma-1);
      let newRating = newPlaylist.slice(colin, newPlaylist.indexOf(',',comma+1));
      tempObj = {
        ID : newId,
        songRating : newRating
      }
      ratedPlaylist = [tempObj];
      for(i = 1; i < selectedPlaylist.items.length;i++)
      {
        colin = newPlaylist.indexOf(':',colin+1);
        comma = newPlaylist.indexOf(',',comma+1);
        newId = newPlaylist.substr(comma+1,colin-comma-1);
        newRating = newPlaylist.slice(colin, newPlaylist.indexOf(',',comma+1));
        tempObj = {
          ID : newId,
          songRating : newRating
        }
        ratedPlaylist.push(tempObj);
      }
      removeMisMatched();
    },1000);

  }
});

/**
* This function updates the users information on screen while also setting the initial state to pick a playlist
*/
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
      playListID = oldDataId;
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
              selectedSongid = data.items[i].track.id;
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

/**
* This creates a JSON dictionary of songs and their respective features.
* @param {JSON} data This takes a JSON object representing a playlist
*/
function createPlaylistDictionary(data)
{
  let length = data.items.length;
  var playListDictionary = {"Playlist" : []};
  var tempFeatures = null;
  var tempID = "";
  misMatchURL = document.getElementById("generate-remove");
  console.log(playListID);
  for(let i = 0;i<length;i++)
  {
    tempID = data.items[i].track.id;
    spotifyApi.getAudioFeaturesForTrack(tempID,null).then(
      function (features) {
        tempFeatures = {ID : i,
              danceability: features.danceability,
              energy       : features.energy,
              key        : features.key,
              tempo      : features.tempo,
              valence    : features.valence};
        playListDictionary.Playlist.push(tempFeatures);
        data_str = encodeURIComponent(JSON.stringify(playListDictionary));
        misMatchURL.href = '/misMatch/?somevalue=' + data_str + "&access_token=" + spotifyApi.getAccessToken() + "&playlistID=" + playListID;
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

/**
* This function is a reaction function when the user clicks the remove song button
*/
function removeSong()
  {
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
        selectedSongid = selectedPlaylist.items[i].track.id;
        updateIframe(selectedSongid)};
        element.appendChild(newButton);
      }
      else if (i==selectedSong){
        console.log("Splice");
        temp = i;
        offset = true;
      }
      else if(offset)
      {
        console.log("Adding selected song " + i);
        var newButton = document.createElement("button");
        var node = document.createTextNode(selectedPlaylist.items[i].track.name);
        newButton.appendChild(node);
        var element = document.getElementById("trackList");
        newButton.onclick = function(){selectedSong = i-1;
        selectedSongid = selectedPlaylist.items[i-1].track.id;
        updateIframe(selectedSongid);
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
}

/**
* This function takes a specific song to remove from the playlist
* @param {int} specificSong A integer representing a song to remove
*/
function removeSpecific(specificSong)
{
  let temp = 0;
  let offset = false;
  for(let i=0;i<selectedPlaylist.items.length;i++)
  {
    if (i != specificSong && !offset)
    {
      var newButton = document.createElement("button");
      var node = document.createTextNode(selectedPlaylist.items[i].track.name);
      newButton.appendChild(node);
      var element = document.getElementById("trackList");
      newButton.onclick = function(){selectedSong = i;
      selectedSongid = selectedPlaylist.items[i].track.id;
      updateIframe(selectedSongid)};
      element.appendChild(newButton);
    }
    else if (i==specificSong){
      console.log("Splice");
      temp = i;
      offset = true;
    }
    else if(offset)
    {
      var newButton = document.createElement("button");
      var node = document.createTextNode(selectedPlaylist.items[i].track.name);
      newButton.appendChild(node);
      var element = document.getElementById("trackList");
      newButton.onclick = function(){selectedSong = i-1;
      selectedSongid = selectedPlaylist.items[i-1].track.id;
      updateIframe(selectedSongid);
      };
      element.appendChild(newButton);
    }
  }
  selectedPlaylist.items.splice(temp,1);
  for(let x=0;x<selectedPlaylist.items.length+1;x++)
  {
    var element = document.getElementById("trackList");
    element.removeChild(element.childNodes[0]);

  }
}

/**
* This runs through the playlist and removes songs that are outside a certain range
*/
function removeMisMatched()
{
  removeSpecific(1);
  console.log("Testing Mismatched");
}

/**
* This function updates the iframe that lets a user play a specific song
*/
function updateIframe(id)
{
  var url = "https://open.spotify.com/embed/track/" + id
  document.getElementById("playButton").src = url;

}
