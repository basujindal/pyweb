var Vwidth = 300,
  Vheight = 300,
  url = "http://10.42.0.1:8000/dvrk/apimg/";
// buffer = new Uint8ClampedArray(width * height * 4),
// vid_canvas = document.getElementById("myCanvas");
var Vcanvas = document.createElement("canvas");
Vcanvas.id = "myCanvas";
Vcanvas.width = Vwidth;
Vcanvas.height = Vheight;
document.body.appendChild(Vcanvas);
var ctx = Vcanvas.getContext("2d");

var idata = ctx.createImageData(Vwidth, Vheight);

function demo() {
  var xhrv = new XMLHttpRequest();
  xhrv.open("GET", url);
  xhrv.setRequestHeader("Accept", "application/octet-stream");
  xhrv.responseType = "arraybuffer";

  xhrv.onload = function () {
    // var arr = xhr.responseText.split(",").map(Number);
    var arr = xhrv.response;
    var pixels = new Uint8ClampedArray(arr);
    // for (var i = 0; i < width * height * 4; i++) {
    // buffer[i] = arr[i];

    var data = idata.data;
    var len = data.length;
    var i = 0;
    var t = 0;

    for (; i < len; i += 4) {
      data[i] = pixels[t]; /// copy RGB data to canvas from custom array
      data[i + 1] = pixels[t + 1];
      data[i + 2] = pixels[t + 2];
      data[i + 3] = 255; /// remember this one with createImageBuffer

      t += 3;
    }
    ctx.putImageData(idata, 0, 0); /// put data to canvas

    console.log("Hello");
    // demo();
  };
  xhrv.send();
}
// demo();

function runner(repeats = 5000) {
  if (repeats > 0) {
    demo();
    setTimeout(() => runner(repeats - 1), 500);
  }
}

runner();
