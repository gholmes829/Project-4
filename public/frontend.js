
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
        console.log(ratedPlaylist);
        
      }
      var c = document.getElementById("canvas");
var ctx = c.getContext("2d");

const LEFT = 0
const RIGHT = 1

class Node {
    constructor(value) {
        this.value = value
        this.children = []
        this.parent = null
        this.pos = { x: 0, y: 0 }
        this.r = 20
    }

    get left() {
        return this.children[LEFT]
    }

    set left(value) {
        value.parent = this
        this.children[LEFT] = value
    }

    get right() {
        return this.children[RIGHT]
    }

    set right(value) {
        value.parent = this
        this.children[RIGHT] = value
    }

    set position(position) {
        this.pos = position
    }

    get position() {
        return this.pos
    }

    get radius() {
        return this.r
    }

}

class Tree {
    constructor() {
        this.root = null;
        this.startPosition = { x: 600, y: 44 }
        this.axisX = 400
        this.axisY = 50
        
    }

    getPosition({ x, y }, isLeft = false) {
        return { x: isLeft ? x - this.axisX + y : x + this.axisX - y, y: y + this.axisY }
    }

    add(value) {
        const newNode = new Node(value);
        if (this.root == null) {
            newNode.position = this.startPosition
            this.root = newNode
        }
        else {
            let node = this.root
            while (node) {
                if (node.value == value)
                    break;
                if (value > node.value) {
                    if (node.right == null) {
                        newNode.position = this.getPosition(node.position)
                        node.right = newNode
                        break;
                    }
                    node = node.right
                }
                else {
                    if (node.left == null) {
                        newNode.position = this.getPosition(node.position, true)
                        node.left = newNode
                        break;
                    }
                    node = node.left
                }
            }
        }
    }

    all(node) {
        if (node === undefined)
            return
        else {
            console.log(node.value)
            this.all(node.left)
            this.all(node.right)
        }
    }

    getAll() {
        this.all(this.root)
    }

    bfs() {
        console.log("ho")
        const queue = [];
        const black = "#000"

        queue.push(this.root);

        while (queue.length !== 0) {
            const node = queue.shift();
            const { x, y } = node.position

            const color = "#BFBFBF"
            ctx.beginPath();
            ctx.arc(x, y, node.radius, 0, 2 * Math.PI)
            ctx.strokeStyle = black
            ctx.fillStyle = color
            ctx.fill()
            ctx.stroke()
            ctx.strokeStyle = black
            ctx.strokeText(node.value, x-10, y)


            node.children.forEach(child => {

                const { x: x1, y: y1 } = child.position;
                ctx.beginPath();
                ctx.moveTo(x, y + child.radius);
                ctx.lineTo(x1, y1 - child.radius)
                ctx.stroke();
                queue.push(child)
            });

        }
    }
}
const t = new Tree();
for(i = 0; i < selectedPlaylist.items.length;i++)
  {
    s1 = parseFloat(ratedPlaylist[i].songRating.substring(1))
    t.add(s1)
  }
t.bfs()
    },1000);

  }
});


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
  //console.log(playListID);
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
        /**
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
              valence    : features.valence}; */
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


