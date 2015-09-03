var xAxisArrayStr = getMetaData('xAxisArray0');
var yAxisArrayStr = getMetaData('yAxisArray0');
var xAxisArray = xAxisArrayStr.split(',');
var yAxisArray = yAxisArrayStr.split(',');
// convert y from str into float
yAxisArray = changeStrIntoFloatArray(yAxisArray);

var units = getMetaData('units0');
var standardName = getMetaData('standardName0');

// this variable records how many elements in the list
var totalNum = parseInt(getMetaData('elementNum'));
// this variable records the current timestamp
var currentNum = 0;
// this the handle of bar chart
var bar;
// this the handle of line chart
var line;

d3.select('#histogram').attr('width',80*yAxisArray.length);

// run the function when dom is fully loaded
// and then draw a bar graph
// the library is from http://www.rgraph.net/docs/bar.html
window.onload = function ()
{

	drawBarLineGraph()

};

function drawBarLineGraph()
{
	bar = new RGraph.Bar({
        id: 'histogram',
        data: yAxisArray,
        options: {
            labels: xAxisArray,
            ylabels: false,
			eventsClick: onClickBarLineChart,
            background: {
                grid: {
                    vlines: false
                }
            },
            strokestyle: 'rgba(0,0,0,0)',
			colors: ['red'],
            gutter: {
                left: 45
            }
        }
    });
	bar.set('text.angle', 10);
	bar.set('text.size', 8);
	//bar.set('titleSize', 12);
	//bar.set('titleXaxisSize', 12);
	bar.draw();

    line = new RGraph.Line({
        id: 'histogram',
        data: yAxisArray,
        options: {
			title: 'Pixcel Count of Timestep-'+currentNum+' '+standardName,
			titleXaxis: units,
			titleYaxis: 'Pixcel Counts',
			titleSize: 12,
			titleXaxisSize: 10,
			titleYaxisSize: 10,
			eventsClick: onClickBarLineChart,
			//titleXaxisPos: 0.125,
			//titleYaxisPos: 0.125,
            spline: true,
            shadow: true,
            tickmarks: 'endsquare',
            background: {
                grid: {
                    vlines: false
                }
            },
            gutter: {
                left: 45
            },
			colors: ['blue'],
			// it works when elementNum == 1
			// TODO
			// debugging when elementNum!=1
            //tooltips: xAxisArray
        }
    }).draw();

}

function onClickBarLineChart()
{
	
}

function nextTimeStampDistribution()
{
	// erase the current bar chart 
	RGraph.Clear(document.getElementById("histogram"));
	//canvasHandle = document.getElementById("histogram").getContext('2d');
	//canvasHandle.clearRect(0,0,80*yAxisArray.length,900);
	// currentNum+1 mod totalNum
	currentNum = (currentNum + 1)%totalNum;

	xAxisArrayStr = getMetaData('xAxisArray'+currentNum);
	yAxisArrayStr = getMetaData('yAxisArray'+currentNum);
 
	xAxisArray = xAxisArrayStr.split(',');
	yAxisArray = yAxisArrayStr.split(',');
	// convert y from str into float
	yAxisArray = changeStrIntoFloatArray(yAxisArray);

	// units = getMetaData('units'+currentNum);
	// standardName = getMetaData('standardName'+currentNum);

	drawBarLineGraph();
	//setTimeout(nextTimeStampDistribution,25);
}

function screenShot()
{
	// select line chart div
    html2canvas(document.getElementById("histogram"), 
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
