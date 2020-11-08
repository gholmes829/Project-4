
var express = require('express');
var request = require('request');
var cors = require('cors');
var querystring = require('querystring');
var cookieParser = require('cookie-parser');
var fs = require('fs');

// server code
var client_id = '9586133394724f65b7fc986b34fa1a2c';
var client = 'c0b7e24f80c54b5e92c2109c31d58eaf';
var redirect_uri = 'http://localhost:8888/callback';
var access;

/**
 * Generates a random string containing numbers and letters
 * @param  {number} length The length of the string
 * @return {string} The generated string
 */
var generateRandomString = function(length) {
  var text = '';
  var possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';

  for (var i = 0; i < length; i++) {
    text += possible.charAt(Math.floor(Math.random() * possible.length));
  }
  return text;
};

var stateKey = 'spotify_auth_state';

var app = express();

app.use(express.static(__dirname + '/public'))
   .use(cors())
   .use(cookieParser());

app.get('/login', function(req, res) {
  var state = generateRandomString(16);
  res.cookie(stateKey, state);

  // your application requests authorization
  var scope = 'user-read-private user-read-email playlist-modify-private playlist-read-private playlist-modify-public';
  res.redirect('https://accounts.spotify.com/authorize?' +
    querystring.stringify({
      response_type: 'code',
      client_id: client_id,
      scope: scope,
      redirect_uri: redirect_uri,
      state: state
    }));
});

/**
* This detects mismatched song
*/
app.get('/callback', function(req, res) {

  // your application requests refresh and access tokens
  // after checking the state parameter
  var code = req.query.code || null;
  var state = req.query.state || null;
  var storedState = req.cookies ? req.cookies[stateKey] : null;

  if (state === null || state !== storedState) {
    res.redirect('/#' +
      querystring.stringify({
        error: 'state_mismatch'
      }));
  } else {
    res.clearCookie(stateKey);
    var authOptions = {
      url: 'https://accounts.spotify.com/api/token',
      form: {
        code: code,
        redirect_uri: redirect_uri,
        grant_type: 'authorization_code'
      },
      headers: {
        'Authorization': 'Basic ' + (new Buffer(client_id + ':' + client).toString('base64'))
      },
      json: true
    };
    request.post(authOptions, function(error, response, body) {
      if (!error && response.statusCode === 200) {

        var access_token = body.access_token,
            refresh_token = body.refresh_token;
        access = access_token;
        var options = {
          url: 'https://api.spotify.com/v1/me',
          headers: { 'Authorization': 'Bearer ' + access_token },
          json: true
        };

        // we can also pass the token to the browser to make requests from there
        res.redirect('/#' +
          querystring.stringify({
            access_token: access_token,
            refresh_token: refresh_token
          }));
      } else {
        res.redirect('/#' +
          querystring.stringify({
            error: 'invalid_token'
          }));
      }
    });
  }
});

var spawn = require("child_process").spawn;
var fs = require('fs');

var textChunk = "";
function check(playList,access_token,id,res)
{
  setTimeout(() => {
        if(textChunk.includes("Done!"))
        {
          let start = textChunk.indexOf("{"),
              stop  = textChunk.indexOf("}");
          textChunk = textChunk.substr(start,stop+1);
          redirectBack(playList,access_token,id,res);
        }
        else {
          var process = spawn('python',["-u","./backend/__main__.py",playList]);

          process.stdout.on('data',function(chunk){

              textChunk = chunk.toString('utf8');// buffer to string
              });
          check(playList,access_token,id,res);
        }
      },1000);
}
function redirectBack(playList,access_token,id,res)
{
  res.redirect('/#' +
      querystring.stringify({
            access_token: access_token,
            playList    : textChunk,
            playlistID  : id
      }));
}

app.get('/misMatch', function(req, res) {
    check(req.query.somevalue,req.query.access_token,req.query.playlistID,res);
    });

function runTests(req,res)
{
  setTimeout(() => {
        if(textChunk.includes("Done!"))
        {
          let start = textChunk.indexOf("["),
              stop  = textChunk.indexOf("]");
          textChunk = textChunk.substr(start,stop+1);
          console.log(textChunk);
          redirectTests(req,res,textChunk);
        }
        else {
          var process = spawn('python',["-u","./backend/testing.py"]);

          process.stdout.on('data',function(chunk){

              textChunk = chunk.toString('utf8');// buffer to string
              });
          runTests(req,res);
        }
      },1000);
}

function redirectTests(req,res,textChunk)
{
  res.redirect('/#' +
      querystring.stringify({
            access_token: req.query.access_token,
            tests    : textChunk
      }));
}
app.get('/runTests', function(req,res) {
  console.log("run tests");
  runTests(req,res);
  });
app.listen(8888);
