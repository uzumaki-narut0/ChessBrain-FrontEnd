var express = require('express')
var app = express()

app.use(express.static('public'))

//app.use(express.static(__dirname + '/public'));

var portnumber = process.env.PORT || 8080;

app.listen(portnumber, function () {
  console.log('Example app listening on port 3000!')
})
