var path = require('path');
var express = require('express');
var app = express();
var http = require('http').Server(app);
var io = require('socket.io')(http);  //socket server which integrates with (mounts on) http server
var hbs = require('express-handlebars');
var mongoose = require('mongoose');


var bodyParser = require('body-parser');
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static(__dirname + '/public'));

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



/*Socket.io PART */
var game_room = {};
var users = {}; //users list

io.on('connection', function(socket){
  console.log('a user connected');

  //when the client emits play, this listenes and executes
  socket.on('create',function(uniquekey){

    socket.uniquekey = uniquekey; //a unique key corresponding to this game

    game_room[uniquekey] = uniquekey;
    socket.room = game_room[uniquekey];
    console.log(socket.room);

    //send client to room game_room[uniquekey]
    socket.join(game_room[uniquekey]);

    //echo to client they have connected!
    socket.emit('updatechat','SERVER','You have connected to room' + game_room[uniquekey]);

    //echo to room1 that a person has connected to room1
    socket.broadcast.to(game_room[uniquekey]).emit('updatechat','SERVER',"user_name" + 'has created this room');

    //socket.emit('updaterooms',rooms,'room1');

  });



  //when the client emits join, this listenes and executes
  socket.on('join',function(uniquekey){

    //stores the username in socket session for this client
    console.log(uniquekey);
  //  socket.username = user_name;
    //send client to room1
    socket.room = game_room[uniquekey];
    socket.join(game_room[uniquekey]);
    console.log(socket.room);

    //echo to client they have connected!
    socket.emit('updatechat','SERVER','You have connected to '+ game_room[uniquekey]);

    //echo to room1 that a person has connected to room1

    socket.broadcast.to(game_room[uniquekey]).emit('updatechat','SERVER',"user_name" + 'has joined this room');

  //  socket.emit('updaterooms',rooms,'room1');

  });


  //when the client emits send move, this listenes and executes
  socket.on('sendmove',function(source, target, uniquekey){

    //we tell the client to execute 'updateboard' with the parameters
    console.log(source + " " + target);
   // console.log(game_room[uniquekey]);
    io.sockets.in(game_room[uniquekey]).emit('updateboard', source, target);

  });


  socket.on('whosechance',function(currplayer, uniquekey){
    console.log('in whose chance');
    io.sockets.in(game_room[uniquekey]).emit('flipchance',currplayer);
  })

  socket.on('sendchat',function(msg, uniquekey){
    io.sockets.in(game_room[uniquekey]).emit('updatechatui',msg);
  });

  //when the user disonnects... perform this
  socket.on('disonnect',function(){
    //echo globally that this client has left
    socket.broadcast.emit('updatechat','SERVER', " disonnected");
    socket.leave(socket.room);
  });


});




/* Routing PART*/

app.get('/home',function(req,res){
  res.render('home'/*, {id: req.params.id, user: req.params.user
  }*/);
})

app.post('/handleSignup',function(req,res){
  console.log(req.body);
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
  		res.render('home',{userDetails : req.body, userGameDetails : gameStats});
  	}
  });
})

app.post('/handleSignin',function(req,res){
	Signup.find(req.body, function(err, userDetails){
		if(err){
			res.redirect("/authenticateUser.html");
		}	
		else{
			console.log(userDetails);
			var x = Stats.find({username:req.body.username}, function(err, userGameDetails)
			{
				res.render("home",{userDetails : userDetails[0], userGameDetails :userGameDetails[0]});
			});
		}
	});
})

app.get('/:id/:playas',function(req,res){
  console.log(req.params);
  res.render('play', {id: req.params.id,
    playas: req.params.playas
  });
  //res.status(200).send(html);
})

http.listen(portnumber, function () {
  console.log('Example app listening on port!'+portnumber);
})
