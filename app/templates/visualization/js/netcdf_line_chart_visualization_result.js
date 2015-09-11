var csvString = d3.select(".csvString").text();
// remove all the taps
csvString = csvString.replace(/	/g,'');
csvString = csvString.replace(/(\r\n|\n|\r)/gm,'');
csvString = csvString.replace(/ /g,'');
var csvStringList = csvString.split('\\n');
// have to create csvVisStr not use csvString
// coz I don't know why csvString does not work
// I used {{csv_string}} in html and line chart works fine
var csvVisStr = ''
// recreate csv file
for(var i=0 ; i<csvStringList.length ; i++)
{
	csvVisStr = csvVisStr + csvStringList[i] + '\n';
}

netcdfVisLineChart = new Dygraph(

    // containing div
    document.getElementById("graphdiv"),
    csvVisStr

);

function screenShot()
{
	// select line chart div
    html2canvas(document.getElementById("graphdiv"), 
	{
		onrendered: function(canvas) {
			var img = canvas.toDataURL()
			window.open(img);
		}
    });	
}


