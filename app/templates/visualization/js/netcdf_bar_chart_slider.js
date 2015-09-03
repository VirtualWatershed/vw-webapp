// obtain dimension name list
var dimensionNameString = d3.select(".SpecifyDimensionNameList").text();
dimensionNameString = dimensionNameString.replace(/	/g,'');
dimensionNameString = dimensionNameString.replace(/(\r\n|\n|\r)/gm,'');
dimensionNameString = dimensionNameString.replace(/ /g,'');
var dimensionNameList = dimensionNameString.split(',');

var dimensionValueList = [];
//this list is used to confirm all the dimension is specifid
var boolDimensionSpecified = [];

// obtain dimension values, which are need to specified
for(var i=0 ; i<dimensionNameList.length ; i++)
{

	// obtain dimension value list
	var paragraphClassName = "."+dimensionNameList[i]+"Paragraph";
	var dimensionValueString = d3.select(paragraphClassName).text();
	dimensionValueString = dimensionValueString.replace('	','');
	dimensionValueString = dimensionValueString.replace(/(\r\n|\n|\r)/gm,'');
	dimensionValueString = dimensionValueString.replace(/ /g,'');
	
	var tempDimensionValueList = dimensionValueString.split(',');
	dimensionValueList.push(tempDimensionValueList);

	boolDimensionSpecified.push(false);

}

// this is used to avoid creating multiple buttons
var boolCreateVisButton = false;
// this is used to record the list index, chosen by users
var dimensionIndexList = new Array();

function updateText(sliderValue, sliderID)
{
	var paragraphID = sliderID.replace("SliderRange","Value");
	var dimensionName = sliderID.replace("SliderRange","");
	var valueParagraph = d3.select("."+paragraphID);
	var listIndex = dimensionNameList.indexOf(dimensionName);
	var valueNumber = parseInt(sliderValue);
	valueParagraph.text(dimensionValueList[listIndex][valueNumber-1]);
	
	dimensionIndexList[listIndex] = valueNumber;

	boolDimensionSpecified[listIndex] = true;
	var boolAllSet = true;
	for(var i=0 ; i<boolDimensionSpecified.length ; i++)
	{
		if(boolDimensionSpecified[i] == false)
		{
			boolAllSet = false;
		}
	}
	// if all the dimension values are specified
	if(boolAllSet==true && boolCreateVisButton==false)
	{
		boolCreateVisButton = true;
		// create visualize button
		d3.select(".visualizationButtonParagraph")
				.append('input')
				.attr("type","button")
				.attr("value","Visualize")
				.attr("onclick","gotoVisualization()");
	}
}

function gotoVisualization()
{
	var dimensionInformation = '';
	for(var i=0 ; i<dimensionNameList.length ; i++)
	{
		dimensionInformation = dimensionInformation + dimensionNameList[i] + ":" + dimensionIndexList[i] + ";";
	}
	dimensionInformation = dimensionInformation + "BarChartNetCDFParameters";
	window.location.href = 'visualization/'+dimensionInformation;
}


