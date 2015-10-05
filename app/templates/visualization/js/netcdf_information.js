// netcdf_metadata_list record item names
var netcdfVariableNameString = d3.select(".netcdf_variable_information").text();
// don't know why there are line breaks in the string
// use the following two lines to remove "tap" and line breaks
netcdfVariableNameString = netcdfVariableNameString.replace(/	/g,'');
netcdfVariableNameString = netcdfVariableNameString.replace(/(\r\n|\n|\r)/gm,'');
// remove all the space in name string, without this step
// some variable names will be " aa" not "aa"
netcdfVariableNameString = netcdfVariableNameString.replace(/ /g,'');
var netcdfVariableName = netcdfVariableNameString.split(',');

// set up selectBox
var selectBox= d3.select(".variableSelectBox").append("select")
	.attr("class","variableSelect")
	.attr("id","variableSelectID");

for(var i=0 ; i<netcdfVariableName.length ; i++)
{
	selectBox.append("option").text(netcdfVariableName[i]);
}

var variableDimensionNameList;
var variableDimensionCount;
var variableName;

// this part is used to update webpage
// when users choose an item from the variable select box
d3.select("select")
	.on("click" , function() {
		 updateParagraph();  				
	});

// this part is used to update webpage
// when users choose an item from the variable select box
d3.select("#visualizationMethodSelectBox")
	.on("click" , function() {
		 updateParagraph();  				
	});

function updateParagraph()
{
	// get the item id of the select box
	var clickItemID = document.getElementById('variableSelectID').selectedIndex;
	var visualizationMethodID = document.getElementById('visualizationMethodSelectBox').selectedIndex;
	// visualizationMethodID 0 line chart, 1 map 
	// if users choose line chart 
	if(visualizationMethodID == 0)
	{
		updateParagraphLineChart(clickItemID);
	}
	// if users choose map
	else if(visualizationMethodID == 1)
	{
		updateParagraphMapLatLon(clickItemID);
	}
	else if(visualizationMethodID == 2)
	{
		updateParagraphMapOther(clickItemID);
	}
	else if(visualizationMethodID == 3)
	{
		updateParagraphBarChart(clickItemID);
	}
	else if(visualizationMethodID == 4)
	{
		updateParagraphHistogram(clickItemID);
	}
}

// when users select item from select box and using line chart
// visualization method
function updateParagraphLineChart(clickItemID)
{
	variableName = netcdfVariableName[clickItemID];
	// need to +1 because dimensions in NetCDF does not include variable value itself
	// e.g. temperature has 3 dimensions: lat, lon, time. It does not include temperature 
	variableDimensionCount = parseInt(document.getElementById(variableName+'DimensionCountID').innerHTML) + 1;

	// get variable dimensions name list
	variableDimensionNameList = getVariableDimensionsNameList();

	d3.select(".variableDimensionInformation").text(
	"Name: "+variableName+
	"; Dimension Count: "+variableDimensionCount+
	"; Dimension List: "+variableDimensionNameList+
	","+variableName
    );

	// if choose line chart
	if(variableDimensionCount < 2)
	{
		d3.select(".narrowDownInstructions").text(
		variableName+" has less 2 dimensions. \
		We cannot visualize this variable with line chart");
	}
	else
	{
		d3.select(".narrowDownInstructions").text(
		variableName+" has "+variableDimensionCount+
		" dimensions. Please choose two of them to \
		visualize with line chart. The first is for x axis \
		and the second is for y axis. Please make sure that \
        one of the x axis and y axis should be variable itself!"
		);

		// remove all the old buttons first and then add new ones
		d3.selectAll(".buttonParagraph").remove();
		d3.select(".buttonDiv").append('p')
			.attr("class","buttonParagraph");

		// set up selectBox for x axis
		var xSelectBox= d3.select(".buttonParagraph").append("select")
			.attr("class","xSelect")
			.attr("id","xSelectID");
		for(var i=0 ; i<variableDimensionCount-1 ; i++)
		{
			xSelectBox.append("option").text(variableDimensionNameList[i]);
		}
		xSelectBox.append("option").text(variableName);
		// set up selectBox for y axis
		var ySelectBox= d3.select(".buttonParagraph").append("select")
			.attr("class","ySelect")
			.attr("id","ySelectID");
		for(var i=0 ; i<variableDimensionCount-1 ; i++)
		{
			ySelectBox.append("option").text(variableDimensionNameList[i]);
		}
		ySelectBox.append("option").text(variableName);

		// display button
		var visualizeButton = d3.select(".buttonParagraph")
			.append('input')
			.attr("type","button")
			.attr("value","Next Step")
			.attr("onclick","gotoLineChart()");

	}	
}

// when users select item from select box and using bar chart
// visualization method
function updateParagraphBarChart(clickItemID)
{
	variableName = netcdfVariableName[clickItemID];
	// need to +1 because dimensions in NetCDF does not include variable value itself
	// e.g. temperature has 3 dimensions: lat, lon, time. It does not include temperature 
	variableDimensionCount = parseInt(document.getElementById(variableName+'DimensionCountID').innerHTML) + 1;

	// get variable dimensions name list
	variableDimensionNameList = getVariableDimensionsNameList();

	d3.select(".variableDimensionInformation").text(
	"Name: "+variableName+
	"; Dimension Count: "+variableDimensionCount+
	"; Dimension List: "+variableDimensionNameList+
	","+variableName
    );

	// if choose bar chart
	if(variableDimensionCount < 2)
	{
		d3.select(".narrowDownInstructions").text(
		variableName+" has less 2 dimensions. \
		We cannot visualize this variable with bar chart");
	}
	else
	{
		d3.select(".narrowDownInstructions").text(
		variableName+" has "+variableDimensionCount+
		" dimensions. Please choose two of them to \
		visualize with bar chart. The first is for x axis \
		and the second is for y axis. Please make sure that \
        one of the x axis and y axis should be variable itself!"
		);

		// remove all the old buttons first and then add new ones
		d3.selectAll(".buttonParagraph").remove();
		d3.select(".buttonDiv").append('p')
			.attr("class","buttonParagraph");

		// set up selectBox for x axis
		var xSelectBox= d3.select(".buttonParagraph").append("select")
			.attr("class","xSelect")
			.attr("id","xSelectID");
		for(var i=0 ; i<variableDimensionCount-1 ; i++)
		{
			xSelectBox.append("option").text(variableDimensionNameList[i]);
		}
		xSelectBox.append("option").text(variableName);
		// set up selectBox for y axis
		var ySelectBox= d3.select(".buttonParagraph").append("select")
			.attr("class","ySelect")
			.attr("id","ySelectID");
		for(var i=0 ; i<variableDimensionCount-1 ; i++)
		{
			ySelectBox.append("option").text(variableDimensionNameList[i]);
		}
		ySelectBox.append("option").text(variableName);

		// display button
		var visualizeButton = d3.select(".buttonParagraph")
			.append('input')
			.attr("type","button")
			.attr("value","Next Step")
			.attr("onclick","gotoBarChart()");

	}	
}

// when users select item from select box and using histogram
// visualization method
function updateParagraphHistogram(clickItemID)
{
	variableName = netcdfVariableName[clickItemID];
	// need to +1 because dimensions in NetCDF does not include variable value itself
	// e.g. temperature has 3 dimensions: lat, lon, time. It does not include temperature 
	variableDimensionCount = parseInt(document.getElementById(variableName+'DimensionCountID').innerHTML) + 1;

	// get variable dimensions name list
	variableDimensionNameList = getVariableDimensionsNameList();

	d3.select(".variableDimensionInformation").text(
	"Name: "+variableName+
	"; Dimension Count: "+variableDimensionCount+
	"; Dimension List: "+variableDimensionNameList+
	","+variableName
    );

	// if choose histogram
	if(variableDimensionCount < 2)
	{
		d3.select(".narrowDownInstructions").text(
		variableName+" has less 2 dimensions. \
		We cannot visualize this variable with histogram");
	}
	else
	{
		d3.select(".narrowDownInstructions").text(
		variableName+" has "+variableDimensionCount+
		" dimensions. Please choose one of them. \
		The system will visualize it and with histogram."
		);

		// remove all the old buttons first and then add new ones
		d3.selectAll(".buttonParagraph").remove();
		d3.select(".buttonDiv").append('p')
			.attr("class","buttonParagraph");

		// set up selectBox for x axis
		// this should be one of the dimensions only
		var xSelectBox= d3.select(".buttonParagraph").append("select")
			.attr("class","xSelect")
			.attr("id","xSelectID");
		for(var i=0 ; i<variableDimensionCount-1 ; i++)
		{
			xSelectBox.append("option").text(variableDimensionNameList[i]);
		}

		// add paragraph to explain
		d3.select(".buttonParagraph")
			.append('p')
			.text('please fill the blank. The input value decides how many sections. \
					The minimum section number is 1 and maximum is 100.\
					The default section number is 10.');

		// add input to fill the value
		// minimum section should be 1
		// maximum section num should be 100
		var sectionNum = d3.select(".buttonParagraph")
			.append('input')
			.attr('type','number')
			.attr('id','sectionNumID')
			.attr('min',1)
			.attr('max',100)
			.attr('value',10);

		// display button
		var visualizeButton = d3.select(".buttonParagraph")
			.append('input')
			.attr("type","button")
			.attr("value","Visualize Results")
			.attr("onclick","gotoHistogram()");

	}	
}

// when users select item from select box and using map
// visualization method
function updateParagraphMapLatLon(clickItemID)
{
	variableName = netcdfVariableName[clickItemID];
	// need to +1 because dimensions in NetCDF does not include variable value itself
	// e.g. temperature has 3 dimensions: lat, lon, time. It does not include temperature 
	variableDimensionCount = parseInt(document.getElementById(variableName+'DimensionCountID').innerHTML) + 1;

	// get variable dimensions name list
	variableDimensionNameList = getVariableDimensionsNameList();

	// so strange, if I delete this part, step one paragraph will not update
	// when I choose an item from step one select box
	d3.select(".variableDimensionInformation").text(
	"Name: "+variableName+
	"; Dimension Count: "+variableDimensionCount+
	"; Dimension List: "+variableDimensionNameList+
	","+variableName
    );


	// if choose map
	// map visualization can just handle 3D or 4D variables
	if((variableDimensionCount!=3) && (variableDimensionCount!=4))
	{
		d3.select(".narrowDownInstructions").text(
		variableName+" does not have 3 or 4 dimensions. \
		We cannot visualize this variable with map");
	}
	else
	{
		d3.select(".narrowDownInstructions").text(
		variableName+" has "+variableDimensionCount+
		" dimensivariableDimensionNameListons. Please choose two of them to \
		be the latitude (x-axis) and longitude (y-axis). The first is for \
		latitude and the second is for longitude."
		);

		// remove all the old buttons first and then add new ones
		d3.selectAll(".buttonParagraph").remove();
		d3.select(".buttonDiv").append('p')
			.attr("class","buttonParagraph");

		// set up selectBox for x axis
		var xSelectBox= d3.select(".buttonParagraph").append("select")
			.attr("class","latSelect")
			.attr("id","latSelectID");
		for(var i=0 ; i<variableDimensionCount-1 ; i++)
		{
			// variable name cannot be lat or lon
			xSelectBox.append("option").text(variableDimensionNameList[i]);
		}
		
		// set up selectBox for y axis
		var ySelectBox= d3.select(".buttonParagraph").append("select")
			.attr("class","lonSelect")
			.attr("id","lonSelectID");
		for(var i=0 ; i<variableDimensionCount-1 ; i++)
		{
			// variable name cannot be lat or lon
			ySelectBox.append("option").text(variableDimensionNameList[i]);
		}

		// display button
		var visualizeButton = d3.select(".buttonParagraph")
			.append('input')
			.attr("type","button")
			.attr("value","Next Step")
			.attr("onclick","gotoMapLatLon()");

	}	
}

// when users select item from select box and using map
// visualization method, and it doesn't have lat and lon as dimension
function updateParagraphMapOther(clickItemID)
{
	variableName = netcdfVariableName[clickItemID];
	// need to +1 because dimensions in NetCDF does not include variable value itself
	// e.g. temperature has 3 dimensions: lat, lon, time. It does not include temperature 
	variableDimensionCount = parseInt(document.getElementById(variableName+'DimensionCountID').innerHTML) + 1;

	// get variable dimensions name list
	variableDimensionNameList = getVariableDimensionsNameList();

	// so strange, if I delete this part, step one paragraph will not update
	// when I choose an item from step one select box
	d3.select(".variableDimensionInformation").text(
	"Name: "+variableName+
	"; Dimension Count: "+variableDimensionCount+
	"; Dimension List: "+variableDimensionNameList+
	","+variableName
    );


	// if choose map
	// map visualization can just handle 3D or 4D variables
	if((variableDimensionCount!=3) && (variableDimensionCount!=4))
	{
		d3.select(".narrowDownInstructions").text(
		variableName+" does not have 3 or 4 dimensions. \
		We cannot visualize this variable with map");
	}
	else
	{
		d3.select(".narrowDownInstructions").text(
		variableName+" has "+variableDimensionCount+
		" dimensivariableDimensionNameListons. The first select box is used \
        to confirm the variable for latitude information. The second select \
        box is used to confirm the variable for longitude information."
		);

		// remove all the old buttons first and then add new ones
		d3.selectAll(".buttonParagraph").remove();
		d3.select(".buttonDiv").append('p')
			.attr("class","buttonParagraph");

		// set up selectBox for lat
		var xSelectBox= d3.select(".buttonParagraph").append("select")
			.attr("class","latSelect")
			.attr("id","latSelectID");
		for(var i=0 ; i<netcdfVariableName.length ; i++)
		{
			xSelectBox.append("option").text(netcdfVariableName[i]);
		}
		
		// set up selectBox for lon
		var ySelectBox= d3.select(".buttonParagraph").append("select")
			.attr("class","lonSelect")
			.attr("id","lonSelectID");
		for(var i=0 ; i<netcdfVariableName.length ; i++)
		{
			ySelectBox.append("option").text(netcdfVariableName[i]);
		}

		// display button
		var visualizeButton = d3.select(".buttonParagraph")
			.append('input')
			.attr("type","button")
			.attr("value","Next Step")
			.attr("onclick","gotoMapOther()");

	}	
}


// get variable dimensions name list
function getVariableDimensionsNameList()
{
	var variableDimensionNameListString = d3.select("."+variableName+'DimensionsList').text();
	variableDimensionNameListString = variableDimensionNameListString.replace(/ /g,'');
	variableDimensionNameListString = variableDimensionNameListString.replace(/(\r\n|\n|\r)/gm,'');
	variableDimensionNameListString = variableDimensionNameListString.replace(/	/g,'');
	return variableDimensionNameListString.split(',');
}

function gotoLineChart()
{
	// get chosen item name
	var xclickItemID = parseInt(document.getElementById('xSelectID').selectedIndex);
	var yclickItemID = parseInt(document.getElementById('ySelectID').selectedIndex);
	var xItem;
	var yItem;
    var boolChooseVariableName = false;
	var boolChooseSame = false;

	if(xclickItemID == variableDimensionCount-1)
	{
		xItem = variableName;
        boolChooseVariableName = true;
	}
	else
	{
		xItem = variableDimensionNameList[xclickItemID];
	}
	if(yclickItemID == variableDimensionCount-1)
	{
		yItem = variableName;
        boolChooseVariableName = true;
	}
	else
	{
		yItem = variableDimensionNameList[yclickItemID];
	}
	
	if(xclickItemID == yclickItemID)
	{
		boolChooseSame = true;
	}
	else
	{
		boolChooseSame = false;
	}

	if((boolChooseVariableName==true) && (boolChooseSame==false))
	{
		window.location.href = '/visualization/NetCDF/lineChart/'+variableName
							   +'/'+xItem+'/'+yItem;
	}
	// users must choose variablename as one of the line chart dimensions
	else if(boolChooseVariableName == false)
	{
		alert("Please choose variable as one of the dimensions of the line chart!");
	}
	// users must choose different dimensions for the line chart
	else if(boolChooseSame == true)
	{
		alert("Please choose different dimensions!");
	}
		
}

function gotoBarChart()
{
	// get chosen item name
	var xclickItemID = parseInt(document.getElementById('xSelectID').selectedIndex);
	var yclickItemID = parseInt(document.getElementById('ySelectID').selectedIndex);
	var xItem;
	var yItem;
    var boolChooseVariableName = false;
	var boolChooseSame = false;

	if(xclickItemID == variableDimensionCount-1)
	{
		xItem = variableName;
        boolChooseVariableName = true;
	}
	else
	{
		xItem = variableDimensionNameList[xclickItemID];
	}
	if(yclickItemID == variableDimensionCount-1)
	{
		yItem = variableName;
        boolChooseVariableName = true;
	}
	else
	{
		yItem = variableDimensionNameList[yclickItemID];
	}
	
	if(xclickItemID == yclickItemID)
	{
		boolChooseSame = true;
	}
	else
	{
		boolChooseSame = false;
	}

	if((boolChooseVariableName==true) && (boolChooseSame==false))
	{
		window.location.href = '/visualization/NetCDF/barChart/'+variableName
							   +'/'+xItem+'/'+yItem;
	}
	// users must choose variablename as one of the bar chart dimensions
	else if(boolChooseVariableName == false)
	{
		alert("Please choose variable as one of the dimensions of the bar chart!");
	}
	// users must choose different dimensions for the bar chart
	else if(boolChooseSame == true)
	{
		alert("Please choose different dimensions!");
	}
		
}

function gotoHistogram()
{
	// get chosen dimension name
	var xclickItemID = parseInt(document.getElementById('xSelectID').selectedIndex);
	var xItem = variableDimensionNameList[xclickItemID];
	// deicide if sectionNum is int
	var sectionNumber = parseFloat(document.getElementById('sectionNumID').value);
	var boolInt = (sectionNumber%1 === 0);

	if(boolInt && sectionNumber>=1 && sectionNumber<=100)
	{
		// initial step start frame is 0 and end frame is 0
		window.location.href = '/visualization/NetCDF/histogram/'+variableName
							   +'/'+xItem+'/'+sectionNumber.toString()+'/0/0/histogramVisualization';
	}
	else if(sectionNumber<1 || sectionNumber>100)
	{
		alert("Input value should between 1 and 100!");
	}
	else
	{
		alert("Input value is not integer!");
	}
		
}

function gotoMapLatLon()
{
	// get chosen item name
	var xclickItemID = parseInt(document.getElementById('latSelectID').selectedIndex);
	var yclickItemID = parseInt(document.getElementById('lonSelectID').selectedIndex);
	var xItem;
	var yItem;
	var boolChooseSame = false;
	variableDimensionCount = parseInt(document.getElementById(variableName+'DimensionCountID').innerHTML) + 1;	

	xItem = variableDimensionNameList[xclickItemID];
	yItem = variableDimensionNameList[yclickItemID];

	
	if(xclickItemID == yclickItemID)
	{
		boolChooseSame = true;
	}
	else
	{
		boolChooseSame = false;
	}

	// users must choose different dimensions for the line chart
	if(boolChooseSame == true)
	{
		alert("Please choose different dimensions!");
	}
	else
	{
		// /filename:variablename:3:x_dimension:y_dimension:NetCDFMapData or
		// /filename:variablename:4:x_dimension:y_dimension:NetCDFMapData
		window.location.href = '/visualization/NetCDF/'+variableName+":"+variableDimensionCount
							   +":"+xItem+":"+yItem+'/2DMapVisualizationLatLon';
	}
		
}

function gotoMapOther()
{
	// get chosen item name
	var xclickItemID = parseInt(document.getElementById('latSelectID').selectedIndex);
	var yclickItemID = parseInt(document.getElementById('lonSelectID').selectedIndex);
	var xItem;
	var yItem;
	var boolChooseSame = false;
	variableDimensionCount = parseInt(document.getElementById(variableName+'DimensionCountID').innerHTML) + 1;	

	xItem = netcdfVariableName[xclickItemID];
	yItem = netcdfVariableName[yclickItemID];

	
	if(xclickItemID == yclickItemID)
	{
		boolChooseSame = true;
	}
	else
	{
		boolChooseSame = false;
	}

	// users must choose different dimensions for the line chart
	if(boolChooseSame == true)
	{
		alert("Please choose different dimensions!");
	}
	else
	{
		// /filename:variablename:3:x_dimension:y_dimension:NetCDFMapData or
		// /filename:variablename:4:x_dimension:y_dimension:NetCDFMapData
		window.location.href = '/visualization/NetCDF/'+variableName+":"+variableDimensionCount
							   +":"+xItem+":"+yItem+'/2DMapVisualizationOther';
	}
		
}

