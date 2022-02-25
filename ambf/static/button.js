
var Joy1 = new JoyStick('joy1Div');

document.getElementById('buttonf').addEventListener('click', function(){loadText("Forward")});
document.getElementById('buttonb').addEventListener('click', function(){loadText("Backward")});
document.getElementById('buttonr').addEventListener('click', function(){loadText("Reset")});
var output = document.getElementById("value");
output.innerHTML = 0;


var url = 'http://192.168.29.148:8000'
function loadText(direction){
  var xhr = new XMLHttpRequest();
  xhr.open('POST', url + '/ambf/api/');
  xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhr.onload = function(){
	output.innerHTML = xhr.responseText;
  }; 
  xhr.send("action=" + direction );
}