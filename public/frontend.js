
var spotifyApi;

var userID;
var selectedSong;
var selectedSongid;
var selectedPlaylist;
var selected_playlist_name;
var playListID;
var ratedPlaylist;
var misMatchedSongs;
var misMatchFlag = false;
var sliderValue;

window.addEventListener('DOMContentLoaded', (event) => {
  var x = document.getElementById("remove_song");
  x.style.display = "none";
  spotifyApi = new SpotifyWebApi();
  let html_access_token = document.getElementById("access");
  if(html_access_token.innerHTML.length > 0)
  {
    spotifyApi.setAccessToken(html_access_token.innerHTML);
    getUser();

  }
  if(window.location.href.includes("&playList="))
  {
    let location = window.location.href;
    location = decodeURIComponent(location);
	 //console.log(location);
    let start = (location.indexOf("&playList=")+10),
        stop = location.indexOf("&playlistID=") - start;
    playListID = location.substring(location.indexOf("&playlistID=")+12);
    document.getElementById("remove_song").style.visibility = "visible";
    showTracks(playListID);
    setTimeout(() => {
      let newPlaylist = location.substr(start,stop);
      //console.log(newPlaylist);
      let colin = newPlaylist.indexOf(':');
      let comma = 0;
      let newId = newPlaylist.substr(1,colin-comma-1);
      let newRating = newPlaylist.slice(colin, newPlaylist.indexOf(',',comma+1));
      tempObj = {
        ID : newId,
        songRating : newRating
      }
      ratedPlaylist = [tempObj];
      //console.log(selectedPlaylist);
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
      showGraph();
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
    });
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
          newButton.onclick = function()
          {
            var x = document.getElementById("remove_song");
            x.style.display = "block";
            selectedSong =i;
            selectedSongid = data.items[i].track.id;
            updateIframe(selectedSongid);
            console.log(data);};
          element.appendChild(newButton);
      }},
      function (err) {
        console.error(err);
        });
}

var data_str;

function goBack()
{
  window.location.href = "/#access_token=" + spotifyApi.getAccessToken();
  location.reload()
}
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
  console.log(misMatchedSongs);
  setTimeout(() => {
  for(i = 0; i < selectedPlaylist.items.length;i++)
  {
    finalPlaylist.push(selectedPlaylist.items[i].track.uri);
  }
  let j = 0;
  while(j < misMatchedSongs.length)
  {
    finalPlaylist.splice(misMatchedSongs[j],1);
    for(y =0; y<misMatchedSongs.length;y++)
    {
      misMatchedSongs[y] = misMatchedSongs[y] -1;
    }
    j++;
  }
  console.log(finalPlaylist);
},250);

  setTimeout(() => {
    spotifyApi.createPlaylist(userID,{name:"Flow Created Playlist"}).then(
      function (data) {
        spotifyApi.addTracksToPlaylist(data.id,finalPlaylist,null).then(
          function(newPlaylist){
            console.log(newPlaylist);
            window.location.href = "/#access_token=" + spotifyApi.getAccessToken();
            location.reload();
          },
          function(err){
            console.log(err);
          });
      },
      function (err) {
        console.error(err);
      });
  },2000);

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
        newButton.onclick = function()
        {
          var x = document.getElementById("remove_song");
          x.style.display = "block";
          selectedSong = i;
        selectedSongid = selectedPlaylist.items[i].track.id;
        updateIframe(selectedSongid)};
        element.appendChild(newButton);
      }
      else if (i==selectedSong){
        temp = i;
        offset = true;
      }
      else if(offset)
      {
        var newButton = document.createElement("button");
        var node = document.createTextNode(selectedPlaylist.items[i].track.name);
        newButton.appendChild(node);
        var element = document.getElementById("trackList");
        newButton.onclick = function(){
          var x = document.getElementById("remove_song");
            x.style.display = "block";
            selectedSong = i-1;
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
    var x = document.getElementById("remove_song");
    x.style.display = "none";
    if(ratedPlaylist.length > 0)
    {
      console.log("remove");
      showGraph();
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
  let removed = "";
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
      removed = i;
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
  return removed;
}

function updateSlider()
{
  sliderValue = document.getElementById("range").value;
  document.getElementById("UpdateSlider").innerHTML = sliderValue;
  console.log(sliderValue);
  showGraph();

}

/**
* This function updates the iframe that lets a user play a specific song
*/
function updateIframe(id)
{
  var url = "https://open.spotify.com/embed/track/" + id
  document.getElementById("playButton").src = url;

}

function showGraph()
{
  var c = document.getElementById("canvas");
      var ctx = c.getContext("2d");
      ctx.canvas.width  = window.innerWidth;
      ctx.canvas.height = selectedPlaylist.items.length*50;
      const black = "#ffffff"
      var j=0;
      var other = 0;
      misMatchedSongs = [];
      console.log(selectedPlaylist.items.length);
      for(i = 0; i < selectedPlaylist.items.length;i++)
      {

        if(i%4==0)
        {
          j= j+1;
          other = 0;
        }
        ctx.beginPath();
        ctx.arc(90+other*150, 150*j+30, 60, 0, 2 * Math.PI);
        s1 = parseFloat(ratedPlaylist[i].songRating.substring(1))
        //console.log(ratedPlaylist);
        if(sliderValue <=s1)
        {
          ctx.fillStyle = "red";
          misMatchedSongs.push(i);
        }
        else
        {
          ctx.fillStyle = "blue";
        }

        ctx.fill();
        ctx.stroke();
        ctx.strokeStyle = black;
        ctx.strokeText(selectedPlaylist.items[i].track.name, 40+other*150, 150*j+30)
        other = other+1;
      }
}
