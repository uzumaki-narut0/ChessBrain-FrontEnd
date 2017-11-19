var path = require('path');
var express = require('express');
var app = express();
var http = require('http').Server(app);
var io = require('socket.io')(http);  //socket server which integrates with (mounts on) http server
var hbs = require('express-handlebars');
var mongoose = require('mongoose');
var session = require('express-session');
var morgan  = require('morgan');
var cors = require('cors');

var bodyParser = require('body-parser');
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// app.use(morgan('combined'))
app.use(express.static(__dirname + '/public'));
app.use(session({secret:'sakurasou', saveUninitialized:false, resave:false}));

var portnumber = process.env.PORT || 8080;

app.engine('hbs',hbs({extname: 'hbs', defaultLayout: 'layout', layoutsDir: __dirname+'/views'}));//first argument is engine name which can be anything
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'hbs');


var signupSchema = mongoose.Schema;
var statsSchema = mongoose.Schema;

var signupSchemaObj = new signupSchema({
	username: { type: String, required: true, unique: true },
  	userpassword: { type: String, required: true },
    usermail    		: String
});

var statsSchemaObj = new statsSchema({
	username : { type: String, required: true, unique: true },
	totalGames : Number,
	wins : Number,
	losses : Number,
	draws : Number

});

//creating models
var Signup = mongoose.model('User', signupSchemaObj);
var Stats = mongoose.model('userStats', statsSchemaObj);

//establishing connection
mongoose.connect(process.env.MONGODB_URI, function (error) {
    if (error) 
    	{
    		console.error(error);
    		console.log("error aa rha hai!!");
    	}
    else console.log('mongo connected');
});
// mongoose.connect('mongodb://localhost:27017', { useMongoClient: true });



/*Socket.io PART */
var game_room = {};
var player_white = {};
var player_black = {};

io.on('connection', function(socket){
  console.log('a user connected');
  //when the client emits play, this listenes and executes
  socket.on('create',function(uniquekey, playerWhite){
    game_room[uniquekey] = uniquekey;
    player_white[uniquekey] = playerWhite;
    console.log(playerWhite);
    // console.log(socket.room);
    socket.join(game_room[uniquekey]);

  });

  //when the client emits join, this listenes and executes
  socket.on('join',function(uniquekey, playerBlack){
    socket.room = game_room[uniquekey];
    socket.join(game_room[uniquekey]);
    player_black[uniquekey] = playerBlack;
    //update both players info (name)
    io.sockets.in(game_room[uniquekey]).emit('updatePlayersInfo', playerBlack, player_white[uniquekey]);
    console.log(playerBlack);
  });

  //when the client emits send move, this listenes and executes
  socket.on('sendmove',function(source, target, uniquekey, fen){
    //we tell the client to execute 'updateboard' with the parameters
    io.sockets.in(game_room[uniquekey]).emit('updateboard', source, target);

  });

  //pass chance to next player (server side 'syn' of syn->ack)
  socket.on('triggerPassChance',function(nextplayer, uniquekey){
    io.sockets.in(game_room[uniquekey]).emit('ackPassChance',nextplayer);
  })

  //when the client emits offerdraw-client-syn, this listens and executes
  socket.on('offerdraw-client-syn', function(uniquekey, playerWhoIsOffering){
    io.sockets.in(game_room[uniquekey]).emit('offerdraw-server-ack', uniquekey, playerWhoIsOffering);
  });

  //when the client emits offerresign-client-syn, this listens and executes
  socket.on('offerresign-client-syn', function(uniquekey, playerWhoIsOffering){
    io.sockets.in(game_room[uniquekey]).emit('offerresign-server-ack', uniquekey, playerWhoIsOffering);
  });

  socket.on('client-msg-syn', function(uniquekey, playerWhoSentMsg, message){
    io.sockets.in(game_room[uniquekey]).emit('server-msg-ack', uniquekey, playerWhoSentMsg, message);
  });

  //when the user disonnects... perform this
  socket.on('disonnect',function(){
    socket.leave(socket.room);
  });


});




/* Routing PART*/

app.get('/:userid/home',function(req,res){
  if(req.params.userid == req.session.username)
  {
    Stats.find({username:req.session.username}, function(err, userGameDetails)
    {
      res.render("home",{userDetails : {username : req.session.username}, userGameDetails :userGameDetails[0]});
    });
  }
  else
  {
    //redirect to login page
    res.redirect('/authenticateUser.html');

  }
})

app.post('/handleSignup',function(req,res){
  // console.log(req.body);
  var result = new Signup(req.body);
  result.save(function(err){
  	if(err)
  	{
  		console.log(err);
  		res.redirect("/authenticateUser.html");
  	}
  	else
  	{
  		var gameStats = new Stats({
  			username : req.body.username,
  			totalGames : 0,
  			wins : 0,
  			losses : 0,
  			draws : 0
  		});
  		gameStats.save(function(err){

  		});
  		console.log(gameStats);
      req.session.username = req.body.username; //storing into session
  		res.render('home',{userDetails : req.body, userGameDetails : gameStats});
  	}
  });
})


app.get('/:userid/home',function(req,res){
  if(req.params.userid == req.session.username)
  {
      Stats.find({username:req.params.userid}, function(err, userGameDetails)
      {
        res.render("home",{userDetails : userDetails[0], userGameDetails :userGameDetails[0]});
      });
  }
  else
  {
    res.redirect("/authenticateUser.html");
  }
});
//logging in.... creating a new session
app.post('/:userid/home',function(req,res){
	Signup.find(req.body, function(err, userDetails){
		if(userDetails.length == 0){
      // res.sendStatus(200);
			res.redirect("/authenticateUser.html");
		}	
		else{
      req.session.username = req.body.username; //storing into session

			console.log(userDetails);
			var x = Stats.find({username:req.body.username}, function(err, userGameDetails)
			{
				res.render("home",{userDetails : userDetails[0], userGameDetails :userGameDetails[0]});
			});
		}
	});
})

app.get('/:userid/:id/:playas',function(req,res){
  // console.log(req.params);

  if(req.params.userid == req.session.username)
  {
      res.render('play', {id: req.params.id,
      playas: req.params.playas,
      userDetails : {
          username : req.session.username,
          gamestate : 'start'
        }
      });  
     
  }
  else
  {
    res.redirect('/authenticateUser.html');
  }
})

app.post('/resultUpdate', function(req, res){
  // console.log(req);
  // res.send("200");
  if(req.body.code == 0)  //draw
  {
    Stats.find({username:req.body.user1}, function(err, userGameDetails)
    {
       let no_of_draw_1 = userGameDetails[0]['draws'] + 1;
       let tot_games = userGameDetails[0]['totalGames'] + 1;
       Stats.findOneAndUpdate({ username: req.body.user1 }, {draws : no_of_draw_1, totalGames : tot_games}, function(err, user) {
          if (err) throw err;
        });
    });
    Stats.find({username:req.body.user2}, function(err, userGameDetails)
    {
       let no_of_draw_2 = userGameDetails[0]['draws'] + 1;
       let tot_games = userGameDetails[0]['totalGames'] + 1;
       Stats.findOneAndUpdate({ username: req.body.user2 }, {draws : no_of_draw_2, totalGames : tot_games}, function(err, user) {
          if (err) throw err;
        });
    });  
  }
  else  //someone won
  {
      console.log(req.body.user1);
      Stats.find({username:req.body.user1}, function(err, userGameDetails)
      {
         console.log('hhhhhhh');
         console.log(userGameDetails);
         let no_of_wins = userGameDetails[0]['wins'] + 1;
         let tot_games = userGameDetails[0]['totalGames'] + 1;
         Stats.findOneAndUpdate({ username: req.body.user1 }, {wins : no_of_wins, totalGames : tot_games}, function(err, user) {
            if (err) throw err;
          });
         
      });
      Stats.find({username:req.body.user2}, function(err, userGameDetails)
      {

         console.log('ggggggg' + req.body.user2);
         console.log(userGameDetails);
         let no_of_losses = userGameDetails[0]['losses'] + 1;
         let tot_games = userGameDetails[0]['totalGames'] + 1;
         Stats.findOneAndUpdate({ username: req.body.user2 }, {losses : no_of_losses, totalGames : tot_games}, function(err, user)
          {
              if (err) throw err;
          });
      });
      
  }
  res.sendStatus(200);  
});

http.listen(portnumber, function () {
  console.log('Example app listening on port!'+portnumber);
})
