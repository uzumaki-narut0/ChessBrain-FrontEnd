var path = require('path');
var express = require('express');
var app = express();
var hbs = require('express-handlebars');
var mongoose = require('mongoose');


var bodyParser = require('body-parser');
app.use(bodyParser.json()); // support json encoded bodies
app.use(bodyParser.urlencoded({ extended: true })); // support encoded bodies
app.use(express.static(__dirname + '/public'));
//app.use(express.static(__dirname + '/public'));

var portnumber = process.env.PORT || 8080;

app.engine('hbs',hbs({extname: 'hbs', defaultLayout: 'layout', layoutsDir: __dirname+'/views'}));//first argument is engine name which can be anything
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'hbs');


var Schema = mongoose.Schema;
var statsSchema = mongoose.Schema;

var userSchema = new Schema({
	username: { type: String, required: true, unique: true },
  	password: { type: String, required: true },
    firstname    		: String,
    lastname     		: String
});

var userStatsSchema = new Schema({
	username : { type: String, required: true, unique: true },
	wins : Number,
	losses : Number,
	draws : Number

});

//creating models
var User = mongoose.model('User', userSchema);
var userStats = mongoose.model('userStats', userStatsSchema);

//establishing connection
mongoose.connect(process.env.MONGODB_URI, function (error) {
    if (error) 
    	{
    		console.error(error);
    		console.log("error aa rha hai!!");
    	}
    else console.log('mongo connected');
});


app.get('/home',function(req,res){
  // console.log(req.params);
  res.render('index'/*, {id: req.params.id, user: req.params.user
  }*/);
  //res.status(200).send(html);
})

app.get('/handleSignup',function(req,res){
  console.log(req.body);
  var result = new User(req.body);
  result.save(function(err){
  	if(err)
  	{
  		//signup unsuccessfull
  		//redirect to same page
  		res.redirect("/new_signup");
  	}
  	else
  	{
  		//signup successfull
  		//redirect to home page
  		// console.log()
  		res.render('/home');
  	}
  });
  
  //res.status(200).send(html);
})

app.get('/handleSignin',function(req,res){
	User.find(function(err, signInDetails){
		if(err){
			//login unsuccessfull
			//redirect to same page
			res.redirect("/new_signup");
		}	
		else{
			//login successful
			//redirect to home page
			res.render("/home");
		}
	});
  //res.status(200).send(html);
})

app.listen(portnumber, function () {
  console.log('Example app listening on port!'+portnumber);
})
