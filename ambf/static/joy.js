/**
 * @desc Principal object that draw a joystick, you only need to initialize the object and suggest the HTML container
 * @costructor
 * @param container {String} - HTML object that contains the Joystick
 * @param parameters (optional) - object with following keys:
 */
var JoyStick = function (container, parameters) {
  parameters = parameters || {};
  var title =
      typeof parameters.title === "undefined" ? "joystick" : parameters.title,
    width = typeof parameters.width === "undefined" ? 0 : parameters.width,
    height = typeof parameters.height === "undefined" ? 0 : parameters.height,
    index = typeof parameters.index === "undefined" ? 0 : parameters.index,
    internalFillColor =
      typeof parameters.internalFillColor === "undefined"
        ? "#00AA00"
        : parameters.internalFillColor,
    internalLineWidth =
      typeof parameters.internalLineWidth === "undefined"
        ? 2
        : parameters.internalLineWidth,
    internalStrokeColor =
      typeof parameters.internalStrokeColor === "undefined"
        ? "#003300"
        : parameters.internalStrokeColor,
    externalLineWidth =
      typeof parameters.externalLineWidth === "undefined"
        ? 2
        : parameters.externalLineWidth,
    externalStrokeColor =
      typeof parameters.externalStrokeColor === "undefined"
        ? "#008000"
        : parameters.externalStrokeColor,
    autoReturnToCenter =
      typeof parameters.autoReturnToCenter === "undefined"
        ? true
        : parameters.autoReturnToCenter,
    url =
      typeof parameters.url === "undefined"
        ? "http://192.168.29.148:8000"
        : parameters.url;

  // Create Canvas element and add it in the Container object
  var objContainer = document.getElementById(container);
  var canvas = document.createElement("canvas");
  canvas.id = title;
  if (width === 0) {
    width = objContainer.clientWidth;
  }
  if (height === 0) {
    height = objContainer.clientHeight;
  }
  canvas.width = width;
  canvas.height = height;
  objContainer.appendChild(canvas);
  var context = canvas.getContext("2d");

  var pressed = 0; // Bool - 1=Yes - 0=No
  var circumference = 2 * Math.PI;
  var internalRadius = (canvas.width - (canvas.width / 2 + 10)) / 2;
  var maxMoveStick = internalRadius + 5;
  var externalRadius = internalRadius + 30;
  var centerX = canvas.width / 2;
  var centerY = canvas.height / 2;
  var directionHorizontalLimitPos = canvas.width / 10;
  var directionHorizontalLimitNeg = directionHorizontalLimitPos * -1;
  var directionVerticalLimitPos = canvas.height / 10;
  var directionVerticalLimitNeg = directionVerticalLimitPos * -1;
  // Used to save current position of stick
  var movedX = centerX;
  var movedY = centerY;

  // Check if the device support the touch or not
  if ("ontouchstart" in document.documentElement) {
    canvas.addEventListener("touchstart", onTouchStart, false);
    canvas.addEventListener("touchmove", onTouchMove, false);
    canvas.addEventListener("touchend", onTouchEnd, false);
  } else {
    canvas.addEventListener("mousedown", onMouseDown, false);
    canvas.addEventListener("mousemove", onMouseMove, false);
    canvas.addEventListener("mouseup", onMouseUp, false);
  }
  // Draw the object
  drawExternal();
  drawInternal();

  /******************************************************
   * Private methods
   *****************************************************/

  /**
   * @desc Draw the external circle used as reference position
   */
  function drawExternal() {
    context.beginPath();
    context.arc(centerX, centerY, externalRadius, 0, circumference, false);
    context.lineWidth = externalLineWidth;
    context.strokeStyle = externalStrokeColor;
    context.stroke();
  }

  /**
   * @desc Draw the internal stick in the current position the user have moved it
   */
  function drawInternal() {
    context.beginPath();
    if (movedX < internalRadius) {
      movedX = maxMoveStick;
    }
    if (movedX + internalRadius > canvas.width) {
      movedX = canvas.width - maxMoveStick;
    }
    if (movedY < internalRadius) {
      movedY = maxMoveStick;
    }
    if (movedY + internalRadius > canvas.height) {
      movedY = canvas.height - maxMoveStick;
    }
    context.arc(movedX, movedY, internalRadius, 0, circumference, false);
    // create radial gradient
    var grd = context.createRadialGradient(
      centerX,
      centerY,
      5,
      centerX,
      centerY,
      200
    );
    // Light color
    grd.addColorStop(0, internalFillColor);
    // Dark color
    grd.addColorStop(1, internalStrokeColor);
    context.fillStyle = grd;
    context.fill();
    context.lineWidth = internalLineWidth;
    context.strokeStyle = internalStrokeColor;
    context.stroke();
  }

  /**
   * @desc Events for manage touch
   */

  function onChange() {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", url + "/ambf/apijoy/");
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("action=joystick" + index + "&posx=" + movedX + "&posy=" + movedY);
  }

  function onTouchStart() {
    pressed = 1;
  }

  function onTouchMove(event) {
    // Prevent the browser from doing its default thing (scroll, zoom)
    event.preventDefault();
    if (pressed === 1 && event.targetTouches[0].target === canvas) {
      movedX = event.targetTouches[0].pageX;
      movedY = event.targetTouches[0].pageY;
      // Manage offset
      if (canvas.offsetParent.tagName.toUpperCase() === "BODY") {
        movedX -= canvas.offsetLeft;
        movedY -= canvas.offsetTop;
      } else {
        movedX -= canvas.offsetParent.offsetLeft;
        movedY -= canvas.offsetParent.offsetTop;
      }
      onChange();
      // Delete canvas
      context.clearRect(0, 0, canvas.width, canvas.height);
      // Redraw object
      drawExternal();
      drawInternal();
    }
  }

  function onTouchEnd() {
    pressed = 0;
    // If required reset position store variable
    if (autoReturnToCenter) {
      movedX = centerX;
      movedY = centerY;
    }
    // Delete canvas
    context.clearRect(0, 0, canvas.width, canvas.height);
    onChange();
    // Redraw object
    drawExternal();
    drawInternal();
    //canvas.unbind('touchmove');
  }

  /**
   * @desc Events for manage mouse
   */
  function onMouseDown() {
    pressed = 1;
  }

  function onMouseMove(event) {
    if (pressed === 1) {
      movedX = event.pageX;
      movedY = event.pageY;
      // Manage offset
      if (canvas.offsetParent.tagName.toUpperCase() === "BODY") {
        movedX -= canvas.offsetLeft;
        movedY -= canvas.offsetTop;
      } else {
        movedX -= canvas.offsetParent.offsetLeft;
        movedY -= canvas.offsetParent.offsetTop;
      }

      onChange();
      // Delete canvas
      context.clearRect(0, 0, canvas.width, canvas.height);
      // Redraw object
      drawExternal();
      drawInternal();
    }
  }

  function onMouseUp() {
    pressed = 0;
    // If required reset position store variable
    if (autoReturnToCenter) {
      movedX = centerX;
      movedY = centerY;
    }

    onChange();
    // Delete canvas
    context.clearRect(0, 0, canvas.width, canvas.height);
    // Redraw object
    drawExternal();
    drawInternal();
    //canvas.unbind('mousemove');
  }
};
