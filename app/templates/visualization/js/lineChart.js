//this js now only support the first element of the csv file to be the x axis
//and the first element should be date

//csv_metadata_list record item names
var csv_metadata_string = d3.select(".csv_metadata").text();
//don't know why there are line breaks in the string
//use the following two lines to remove "tap" and line breaks
csv_metadata_string = csv_metadata_string.replace('	','');
csv_metadata_string = csv_metadata_string.replace(/(\r\n|\n|\r)/gm,'');
var csv_metadata_list = csv_metadata_string.split(',');

//this is used to record the x axis information in the input csv file
//and used for offering right information for download file
var xAxisValue = [];
//now just support download x chosen areas
var linechart = new Dygraph(
    document.getElementById("lineChartdiv"),
    "input.csv", // path to CSV file
    {
        width: 1280,
        height: 960,
		xValueFormatter: Dygraph.dateString_,
    	xValueParser: function(x) 
		{ 
				xAxisValue.push(x);
				return Date.parse(x);
    	},
    	xTicker: Dygraph.dateTicker
	}        // options
  );

function change(checkBox) {
	// minus 2, because loop.index is start with 1 not 0 and also the first coloumn
	//is date and it is used for x axis not y axis, therefore should subtract it
	//from the count of y elements
	linechart.setVisibility(String(parseInt(checkBox.id) - 2), checkBox.checked);
}

//this is the original scale
var xScaleStart;
var xScaleEnd;
var xScale;

//when line chart is ready, this function will run
linechart.ready(function() {
	xScaleStart = linechart.xAxisRange()[0];
	xScaleEnd = linechart.xAxisRange()[1];
	xScale = xScaleEnd - xScaleStart;
});


var downloadCSVButton = d3.select(".confirmButton").append("input")
	.attr("type","button")
	.attr("value","downloadCSV")
	.attr("onclick","downloadData()");	



function downloadData()
{
	var xTempScaleStart = linechart.xAxisRange()[0];
	var xTempScaleEnd = linechart.xAxisRange()[1];

	//startElementIndex is the first chosen element index
	var startElementIndex = Math.ceil(linechart.numRows()*(xTempScaleStart - xScaleStart)/xScale);
	var endElementIndex = Math.floor(linechart.numRows()*(xTempScaleEnd - xScaleStart)/xScale);

	//this is for test only
	//d3.select(".confirmButton").append("p")
	//.text('the first element index is ' + startElementIndex + ', the last element index is ' + endElementIndex);

	//this is used to change data into csv file and download it
	var data = [];
	var tempTuple = [];

	//push the lable into csv
	data.push(csv_metadata_list);	

	//double loop, out loop for rows, inner loop for columns
	for(var rowNum = startElementIndex ; rowNum < endElementIndex ; rowNum = rowNum + 1)
	{
		for(var colNum = 0 ; colNum < linechart.numColumns() ; colNum = colNum + 1)
		{
			//this means if the input value is not date
			if(colNum != 0)
				tempTuple.push(linechart.getValue(rowNum,colNum));
			else
				tempTuple.push(xAxisValue[rowNum]);
		}
		data.push(tempTuple);
		tempTuple = [];
	}

	alasql("SELECT * INTO CSV('downloadData.csv') FROM ?",[data]);
}


