<!DOCTYPE html>
<html>
<head>
<!-- include jquery from CDN -->
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
<script>
	function fetchAppdataSummary() {
		$('#appdata').html("Loading...");
		console.log("loading...");
		var url = '/flask/api/applications/allFaculties'
		$.getJSON(url,onAppdataSuccess);
	}
	
	function onAppdataSuccess(data) {
		$('#appdata').html('Reply...');
		console.log("got reply");
		outtext = "Faculties";
		for(var k in data['totals']) {
			outtext += "\n"+k+" => "+data['totals'][k];
			ppObj("data["+k+"]:",data[k])
		}
		$('#appdata').text(outtext);
		formatResponse(data);
	}
	
	function formatResponse(data) {
		var categories = ["FirmOffer","CondOffer","Pending","Waiting","Other","total"];
		// handle totals
		var ltext = "<br><b>Totals:</b> "
		var totals = data['totals'];
		//ppObj("totals=",totals);
		for(var i in categories) {
			var c = categories[i];
			if(totals[c] != null) {
				ltext += c+"="+totals[c]["total"]+"; ";
			} else {
				ltext += c+"=None; ";
			}
		}
		// iterate over faculties
		faculties = data['faculties'];
		ppObj("faculties=",faculties);
		for(var fcode in faculties) {
			f = faculties[fcode];
			var fname = f[1] ;
			ltext += "<br>"+fcode+": "+fname+"<br>";
			ftotals = f[2];
			for(var i in categories) {
				var c = categories[i];
				if(ftotals[c] != null) {
					ltext += c+"="+ftotals[c]["total"]+"; ";
				} else {
					ltext += c+"=None; ";
				}
			}
		}
		$("#summary-data").html(ltext);
	}
	
	function updateDiv() {
		var aDiv = $('#appdata');
		console.log("div: "+aDiv);
		var oldtext = $('#appdata').text();
		console.log("oldtext: "+oldtext);
		$('#appdata').text("This is new text...");
	}
	
	function dumpObj(s,o) {
		var ltext = s;
		for(var k in o) {
			ltext += k + "=>" + o +","
		}
		console.log(ltext);
	}
	
	function ppObj(s,o) {
		console.log(s+JSON.stringify(o),null,'\t')
	}
</script>
</head>
<body>
	<a href='javascript:fetchAppdataSummary();'>get data...</a><br/>
	<a href='javascript:updateDiv();'>update div...</a>
	<div id='appdata'>
		Nothing here...
	</div>
	<div id='summary-data'>
		
	</div>
</body>
</html>