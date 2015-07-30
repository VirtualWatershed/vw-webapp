var variablenameValue = getMetaData('variablename');
var dimensionNumValue = getMetaData('dimensionNum');
var latValue = getMetaData('lat');
var lonValue = getMetaData('lon');
var filenameValue = getMetaData('filename');

var rawData = httpGet('/visualization/'+filenameValue+':'+variablenameValue+':'+dimensionNumValue+':'+latValue+':'+lonValue+':NetCDFMapData');
// convert text into json
rawData = JSON.parse(rawData);
var mapArray = [];
var tempArray = [];
// convert rawData into mapArray
// and find the maximum value of mapArray
var maxValue = 0;
var minValue = 100000000000000000000000000000000;
var dataY = rawData.length;
for(var i=0 ; i<dataY ; i++)
{
	tempArray = rawData[i].data.split(',');
	if(maxValue < Math.max.apply(null, tempArray))
	{
		maxValue = Math.max.apply(null, tempArray);
	}
	if(minValue > Math.min.apply(null, tempArray))
	{
		minValue = Math.min.apply(null, tempArray);
	}
	mapArray.push(tempArray);
}
var dataX = tempArray.length;

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

/*
      function initialize() {
        var mapCanvas = document.getElementById('map-div');
        var mapOptions = {
          center: new google.maps.LatLng(44.5403, -78.5463),
          zoom: 8,
          mapTypeId: google.maps.MapTypeId.ROADMAP
        }
        var map = new google.maps.Map(mapCanvas, mapOptions)
      }
      google.maps.event.addDomListener(window, 'load', initialize);

*/


// this part is used to display canvas on a google map
// https://github.com/brendankenny/CanvasLayer
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
var rectLatLng = new google.maps.LatLng(40, -95);
var rectWidth = 10;

var resolutionScale = window.devicePixelRatio || 1;

function init() 
{
	// initialize the map
	var mapOptions = {
		zoom: 4,
		center: new google.maps.LatLng(39.3, -95.8),
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
	heightGoogleMap=rectWidth/dataY;

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
	var worldPoint = mapProjection.fromLatLngToPoint(rectLatLng);

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

