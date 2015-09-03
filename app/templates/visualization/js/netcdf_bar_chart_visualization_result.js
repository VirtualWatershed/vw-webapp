var xAxisArrayStr = getMetaData('xAxisArray');
var yAxisArrayStr = getMetaData('yAxisArray');
var xAxisArray = xAxisArrayStr.split(',');
var yAxisArray = yAxisArrayStr.split(',');
xAxisArray = changeStrIntoFloatArray(xAxisArray);
yAxisArray = changeStrIntoFloatArray(yAxisArray);
var xLabel = getMetaData('xAxisLabel');
var yLabel = getMetaData('yAxisLabel');

d3.select('#barchart').attr('width',30*yAxisArray.length);

// run the function when dom is fully loaded
// and then draw a bar graph
// the library is from http://www.rgraph.net/docs/bar.html
window.onload = function ()
{

    var bar = new RGraph.Bar({
        id: 'barchart',
        data: yAxisArray,
        options: {
            labels: xAxisArray,
			gutter: {
				left: 45
			},
			background: {
				barcolor1: 'white',
				barcolor2: 'white',
				grid: true
			},
			colors: ['red']
        }
    }).draw()
};



function screenShot()
{
	// select line chart div
    html2canvas(document.getElementById("barchart"), 
	{
		onrendered: function(canvas) {
			var img = canvas.toDataURL()
			window.open(img);
		}
    });	
}

// get flask server input data from html
function getMetaData(metaDataClass)
{
	var variableDimensionNameListString = d3.select("."+metaDataClass).text();
	variableDimensionNameListString = variableDimensionNameListString.replace(/	/g,'');
	variableDimensionNameListString = variableDimensionNameListString.replace(/(\r\n|\n|\r)/gm,'');
	variableDimensionNameListString = variableDimensionNameListString.replace(/ /g,'');
	return variableDimensionNameListString;
}

function changeStrIntoFloatArray(inputArray)
{
	var floatArray = [];
	for(i=0 ; i<inputArray.length ; i++)
	{
		floatArray.push(parseFloat(inputArray[i]));
	}
	return floatArray;
}
