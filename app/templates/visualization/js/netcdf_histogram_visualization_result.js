var xAxisArrayStr = getMetaData('xAxisArray0');
var yAxisArrayStr = getMetaData('yAxisArray0');
var xAxisArray = xAxisArrayStr.split(',');
var yAxisArray = yAxisArrayStr.split(',');
// convert y from str into float
yAxisArray = changeStrIntoFloatArray(yAxisArray);

var variableName = getMetaData('variableName');

var units = getMetaData('units0');
var standardName = getMetaData('standardName0');
var loadNum = getMetaData('loadNum');

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
	drawBarLineGraph();
/*
	if(totalNum > loadNum)
	{
		drawBarLineGraph();
		var rawData;
		for(i=loadNum ; i<=totalNum ; i++)
		{
			var startStr = i.toString();
			var endStr = (parseInt(i)+1).toString();
			// TODO the xaxis should be dynamically added not hard code 'time', the same for section number not 10
			rawData = httpGet('/visualization/NetCDF/histogram/'+variableName+'/time/10/'+startStr+'/'+endStr+'/histogramVisualization');
			rawData = JSON.parse(rawData);
			d3.select('.netcdfMetadata').append('p')
					.attr('class','xAxisArray'+i)
					.text('1,2,3,4,5,6,7,8,9,0');
			d3.select('.netcdfMetadata').append('p')
					.attr('class','yAxisArray'+i)
					.text('10,9,8,7,6,5,4,3,2,1');

		}
							
	}
	// else
	// the we can visualize them for once
	else
	{
		drawBarLineGraph();
	}
*/
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
            tooltips: xAxisArray
        }
    }).draw();

}

function onClickBarLineChart()
{
//	alert('hello');
}

var loadDataTimes = parseInt(loadNum);
function nextTimeStampDistribution()
{
	// erase the current bar chart 
	// cannont use RGraph.Clear to clear canvas
	// because it does not reset canvas and it will result
	// screenshot part acts strange
	//RGraph.Clear(document.getElementById("histogram"));
	d3.select('#histogram').remove();
	d3.select('.histogramDiv').append('canvas')
		.attr('id','histogram')
		.attr('height',900)
		//.style('border','1px solid #ccc')
		.text('\[No canvas support\]');
	
	d3.select('#histogram').attr('width',80*yAxisArray.length);
	// RGraph.Clear(line.canvas);
	// RGraph.Clear(bar.canvas);
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
	var rawData;
	if(loadDataTimes<=totalNum)
	{
		var startStr = loadDataTimes.toString();
		var endStr = (parseInt(loadDataTimes)+1).toString();
		// TODO the xaxis should be dynamically added not hard code 'time', the same for section number not 10
/*
		rawData = httpGet('/visualization/NetCDF/histogram/'+variableName+'/time/10/'+startStr+'/'+endStr+'/histogramVisualization');
		rawData = JSON.parse(rawData);
		d3.select('.netcdfMetadata').append('p')
				.attr('class','xAxisArray'+startStr)
				.text(rawData['timestamp'][0]['tab_name_list'].toString());
		d3.select('.netcdfMetadata').append('p')
				.attr('class','yAxisArray'+startStr)
				.text(rawData['timestamp'][0]['section_results_number'].toString());

		loadDataTimes = loadDataTimes + 1;
*/
		// use jquery instead of XMLHttpRequest, this makes button reacts when the function runs.
		$.get('/visualization/NetCDF/histogram/'+variableName+'/time/10/'+startStr+'/'+endStr+'/histogramVisualization')
			.done(function(data)
				{
					rawData = JSON.parse(data);
					d3.select('.netcdfMetadata').append('p')
							.attr('class','xAxisArray'+startStr)
							.text(rawData['timestamp'][0]['tab_name_list'].toString());
					d3.select('.netcdfMetadata').append('p')
							.attr('class','yAxisArray'+startStr)
							.text(rawData['timestamp'][0]['section_results_number'].toString());

					loadDataTimes = loadDataTimes + 1;
				});
	}
	//setTimeout(nextTimeStampDistribution,25);
}

var intervalID;
function play()
{
	intervalID = setInterval(function(){nextTimeStampDistribution()},1000);
}

function pause()
{
	clearInterval(intervalID);
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
