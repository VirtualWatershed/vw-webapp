var variablenameValue = getMetaData('variablename');
var dimensionNumValue = getMetaData('dimensionNum');
var latValue = getMetaData('lat');
var lonValue = getMetaData('lon');
var filenameValue = getMetaData('filename');

var rawData = httpGet('/visualization/'+filenameValue+':'+variablenameValue+':'+dimensionNumValue+':'+latValue+':'+lonValue+':NetCDFMapDataOther');
// convert text into json
rawData = JSON.parse(rawData);
var mapArray = [];
var tempArray = [];
// convert rawData into mapArray
// and find the maximum value of mapArray
var maxValue = rawData['max_value'];
var minValue = rawData['min_value'];
var dataY = rawData['y_num'];
var dataX = rawData['x_num'];
// this timeStamp should be other_dimension_name
var timeStamp = rawData['time'];
// for test
// timeCount should be created with third loop
var timeCount = 0;
for(var i=0 ; i<dataY ; i++)
{
	tempArray = [];
	for(var m=0 ; m<dataX ; m++)
	{

		tempArray.push(rawData['location'][i*dataX+m]['data'][timeCount]);
	}
	mapArray.push(tempArray);
}


// place mapArray into canvas
var canvasHandle = document.getElementById("myCanvas");
var canvas2DContext = [];
var color;
var canvasWidth = d3.select('#myCanvas').attr('width');
var canvasHeight = d3.select('#myCanvas').attr('height');
var width=canvasWidth/dataX;
var height=canvasHeight/dataY;
// TODO this part only works when lat and lon together are rectangular
// Need to create a function to project lat and lon in canvas
for(var m=0 ; m<dataY ; m++)
{
	for(var i=0 ; i<dataX ; i++)
	{
		canvas2DContext.push(canvasHandle.getContext("2d"));
//		canvas2DContext[i].fillStyle = convertValueIntoColor(mapArray[m][i],maxValue);
		canvas2DContext[i].fillStyle = convertValueIntoColor(mapArray[m][i],maxValue,minValue);
		//                          start x,y,width,height
		canvas2DContext[i].fillRect(width*i,height*m,width,height);
	}
}



// need to get lat and lon of the start point from flask server
var imgURL;
var rectLatLngStart = new google.maps.LatLng(rawData['min_lat'], rawData['min_lon']);
var rectLatLngEnd = new google.maps.LatLng(rawData['max_lat'], rawData['max_lon']);
var imgOverlay;
var imageBounds;
var map;

overlayImageOnMap();

// this part is used to overlay an image on a map
// the idea is from https://developers.google.com/maps/documentation/javascript/examples/groundoverlay-simple
function overlayImageOnMap()
{

	// should create map when myCanvas is fully done
    html2canvas(document.getElementById("myCanvas"), 
	{
		onrendered: function(canvas) {
			imgURL = canvas.toDataURL();
			// d3.select("#map-div").append("img")
			//	.attr('src',img);
			google.maps.event.addDomListener(window, 'load', initialize);
			
		}
    });	

}




function initialize() {

  imageBounds = new google.maps.LatLngBounds(
      rectLatLngStart,
      rectLatLngEnd);

  var mapOptions = {
    zoom: 15,
    center: rectLatLngStart,
	mapTypeId: google.maps.MapTypeId.SATELLITE
  };

  map = new google.maps.Map(document.getElementById('map-canvas'),
      mapOptions);

  imgOverlay = new google.maps.GroundOverlay(
      imgURL,
      imageBounds);
  imgOverlay.setMap(map);
}

function addOverlay() {  
	imgOverlay.setMap(map);
}

function removeOverlay() {
	imgOverlay.setMap(null);
}

// this function is used to get the contents of another url
// this is from http://stackoverflow.com/questions/10642289/return-html-content-as-a-string-given-url-javascript-function
function httpGet(theUrl)
{
    if (window.XMLHttpRequest)
    {// code for IE7+, Firefox, Chrome, Opera, Safari
        xmlhttp=new XMLHttpRequest();
    }
    else
    {// code for IE6, IE5
        xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
    }
    xmlhttp.onreadystatechange=function()
    {
        if (xmlhttp.readyState==4 && xmlhttp.status==200)
        {
            return xmlhttp.responseText;
        }
    }
    xmlhttp.open("GET", theUrl, false );
    xmlhttp.send();
	return xmlhttp.responseText;   
}

// change 2D map based on the 
function goToNextTime()
{
	MaxIndex = rawData['time'].length;
	timeCount = (timeCount+1) % MaxIndex;
	canvas2DContext = [];
	mapArray = [];

	for(var i=0 ; i<dataY ; i++)
	{
		tempArray = [];
		for(var m=0 ; m<dataX ; m++)
		{

			tempArray.push(rawData['location'][i*dataX+m]['data'][timeCount]);
		}
		mapArray.push(tempArray);
	}

	// clear canvas
	context = canvasHandle.getContext("2d");
	context.clearRect(0, 0, canvasWidth, canvasHeight);

	for(var m=0 ; m<dataY ; m++)
	{
		for(var i=0 ; i<dataX ; i++)
		{
			canvas2DContext.push(canvasHandle.getContext("2d"));
	//		canvas2DContext[i].fillStyle = convertValueIntoColor(mapArray[m][i],maxValue);
			canvas2DContext[i].fillStyle = convertValueIntoColor(mapArray[m][i],maxValue,minValue);
			//                          start x,y,width,height
			canvas2DContext[i].fillRect(width*i,height*m,width,height);
		}
	}
// changing overlay on a map is not working now
/*
	// clear the overlay first
	imgOverlay.setMap(null);
	// add a new overlay
	// should create map when myCanvas is fully done
    html2canvas(document.getElementById("myCanvas"), 
	{
		//onrendered: function(canvas) {
		function(canvas) {
			imgURL = canvas.toDataURL();			
		}
		//}
	});	
	imgOverlay = new google.maps.GroundOverlay(
		imgURL,
		imageBounds);
	imgOverlay.setMap(map);
*/
}

//function convertValueIntoColor(inputValue, maxArrayValue)
function convertValueIntoColor(inputValue, maxArrayValue, minArrayValue)
{

	// black white 2D map
	var colorNum = 255;
	colorNum = parseInt(colorNum * (inputValue-minArrayValue) / (maxArrayValue-minArrayValue));
	var colorStr;

	//if color num < 16 then when you change it into string it will be just one letter not "0f"
	if(colorNum == 0)
		colorStr = "00";
	else if(colorNum < 16)
		colorStr = "0" + colorNum.toString(16);
	else
		colorStr = colorNum.toString(16);

    return "#" + colorStr + colorStr + colorStr;

/*

	// green + red method
	var greenNum = 255;
	var redNum = Math.floor(greenNum - (greenNum*inputValue/maxArrayValue));
	var tempHexString;
	greenNum = Math.floor(greenNum*inputValue/maxArrayValue);
	var greenString;
	var redString;

	//if red num < 16 then when you change it into string it will be just one letter not "0f"
	if(redNum == 0)
		redString = "00";
	else if(redNum < 16)
		redString = "0" + redNum.toString(16);
	else
		redString = redNum.toString(16);

	if(greenNum == 0)
		greenString = "00";
	else if(greenNum < 16)
		greenString = "0" + greenNum.toString(16);
	else
		greenString = greenNum.toString(16);

    return tempHexString = "#" + redString + greenString + "00";

	// normalize three colors method
	// 16777215 is #FFFFFF
	colorValue = 16777215*(inputValue-minArrayValue) / (maxArrayValue-minArrayValue);
	colorStr = '#' + ('00000' + (colorValue | 0).toString(16)).substr(-6); 
	return colorStr;
*/

}

// get flask server input data from html
function getMetaData(metaDataClass)
{
	var variableDimensionNameListString = d3.select("."+metaDataClass).text();
	variableDimensionNameListString = variableDimensionNameListString.replace('	','');
	variableDimensionNameListString = variableDimensionNameListString.replace(/(\r\n|\n|\r)/gm,'');
	variableDimensionNameListString = variableDimensionNameListString.replace(/ /g,'');
	return variableDimensionNameListString;
}


/*

// this part is used to display canvas on a google map
// https://github.com/brendankenny/CanvasLayer
var TILE_SIZE = 256;
var map;
var canvasLayer;
var context;
// these variables are for map overlay
var canvasHandleGoogleMap;
var canvas2DContextGoogleMap = [];
var colorGoogleMap;
var canvasWidthGoogleMap;
var canvasHeightGoogleMap;
var widthGoogleMap;
var heightGoogleMap;
////////////////////////////////////////////////////////
var rectLatLngStart = new google.maps.LatLng(43.732738, -116.14286);
var rectLatLngEnd = new google.maps.LatLng(43.729389, -116.13766);

var rectWidth;
var rectHeight;

var resolutionScale = window.devicePixelRatio || 1;

function bound(value, opt_min, opt_max) {
  if (opt_min != null) value = Math.max(value, opt_min);
  if (opt_max != null) value = Math.min(value, opt_max);
  return value;
}

function degreesToRadians(deg) {
  return deg * (Math.PI / 180);
}

function radiansToDegrees(rad) {
  return rad / (Math.PI / 180);
}


// constructor
function MercatorProjection() {
  this.pixelOrigin_ = new google.maps.Point(TILE_SIZE / 2,
      TILE_SIZE / 2);
  this.pixelsPerLonDegree_ = TILE_SIZE / 360;
  this.pixelsPerLonRadian_ = TILE_SIZE / (2 * Math.PI);
}

MercatorProjection.prototype.fromLatLngToPoint = function(latLng,
    opt_point) {
  var me = this;
  var point = opt_point || new google.maps.Point(0, 0);
  var origin = me.pixelOrigin_;

  point.x = origin.x + latLng.lng() * me.pixelsPerLonDegree_;

  // Truncating to 0.9999 effectively limits latitude to 89.189. This is
  // about a third of a tile past the edge of the world tile.
  var siny = bound(Math.sin(degreesToRadians(latLng.lat())), -0.9999,
      0.9999);
  point.y = origin.y + 0.5 * Math.log((1 + siny) / (1 - siny)) *
      -me.pixelsPerLonRadian_;
  return point;
};

MercatorProjection.prototype.fromPointToLatLng = function(point) {
  var me = this;
  var origin = me.pixelOrigin_;
  var lng = (point.x - origin.x) / me.pixelsPerLonDegree_;
  var latRadians = (point.y - origin.y) / -me.pixelsPerLonRadian_;
  var lat = radiansToDegrees(2 * Math.atan(Math.exp(latRadians)) -
      Math.PI / 2);
  return new google.maps.LatLng(lat, lng);
};


function init() 
{
	// initialize the map
	var mapOptions = {
		zoom: 8,
		center: rectLatLngStart,
		mapTypeId: google.maps.MapTypeId.ROADMAP,
		styles: [
		{
		  stylers: [{saturation: -85}]
		}, {
		  featureType: "water",
		  elementType: "geometry",
		  stylers: [
			{ lightness: -20 }
		  ]
		}
		]
	};
	var mapDiv = document.getElementById('map-div');
	map = new google.maps.Map(mapDiv, mapOptions);

	// initialize the canvasLayer
	var canvasLayerOptions = {
		map: map,
		resizeHandler: resize,
		animate: false,
		updateHandler: update,
		resolutionScale: resolutionScale
	};
	canvasLayer = new CanvasLayer(canvasLayerOptions);
	canvasHandleGoogleMap = canvasLayer.canvas;
	// context is the graphic handler for the whole canvas
	context = canvasHandleGoogleMap.getContext('2d');
	for(var m=0 ; m<dataY ; m++)
	{
		for(var i=0 ; i<dataX ; i++)
		{
			canvas2DContextGoogleMap.push(canvasHandleGoogleMap.getContext("2d"));			
		}
	}
	// get rec width and height
	var numTiles = 1 << map.getZoom();
	var projection = new MercatorProjection();
	var worldCoordinateStart = projection.fromLatLngToPoint(rectLatLngStart);
	var pixelCoordinateStart = new google.maps.Point(
		worldCoordinateStart.x * numTiles,
		worldCoordinateStart.y * numTiles);
	var worldCoordinateEnd = projection.fromLatLngToPoint(rectLatLngEnd);
	var pixelCoordinateEnd = new google.maps.Point(
		worldCoordinateEnd.x * numTiles,
		worldCoordinateEnd.y * numTiles);
	rectWidth = pixelCoordinateEnd.x - pixelCoordinateStart.x;
	rectHeight = pixelCoordinateEnd.y - pixelCoordinateStart.y;
}

function resize() {
// nothing to do here
}

function update()
{
	// clear previous canvas contents
	canvasWidthGoogleMap = canvasHandleGoogleMap.width;
	canvasHeightGoogleMap = canvasHandleGoogleMap.height;
	widthGoogleMap=rectWidth/dataX;
	heightGoogleMap=rectHeight/dataY;


	// TODO this part only works when lat and lon together are rectangular
	// Need to create a function to project lat and lon in canvas
	context.clearRect(0, 0, canvasWidthGoogleMap, canvasHeightGoogleMap);


    
	// We need to scale and translate the map for current view.
	// see https://developers.google.com/maps/documentation/javascript/maptypes#MapCoordinates
	var mapProjection = map.getProjection();

	
	// Clear transformation from last update by setting to identity matrix.
	// Could use context.resetTransform(), but most browsers don't support
	// it yet.
	context.setTransform(1, 0, 0, 1, 0, 0);
    
	// scale is just 2^zoom
	// If canvasLayer is scaled (with resolutionScale), we need to scale by
	// the same amount to account for the larger canvas.
	var scale = Math.pow(2, map.zoom) * resolutionScale;
	context.scale(scale, scale);

	// If the map was not translated, the topLeft corner would be 0,0 in
	// world coordinates. Our translation is just the vector from the
	// world coordinate of the topLeft corder to 0,0.
	//
	var offset = mapProjection.fromLatLngToPoint(canvasLayer.getTopLeft());
	context.translate(-offset.x, -offset.y);

	// project rectLatLng to world coordinates and draw
	var worldPoint = mapProjection.fromLatLngToPoint(rectLatLngStart);

	for(var m=0 ; m<dataY ; m++)
	{
		for(var i=0 ; i<dataX ; i++)
		{
			canvas2DContextGoogleMap[i].fillStyle = convertValueIntoColor(mapArray[m][i],maxValue,minValue);
			//                          start x,y,width,height
			canvas2DContextGoogleMap[i].fillRect(worldPoint.x+widthGoogleMap*i,worldPoint.y+heightGoogleMap*m,widthGoogleMap,heightGoogleMap);
		}
	}
}	

document.addEventListener('DOMContentLoaded', init, false);
// "canvas on google part" ends here
*/











