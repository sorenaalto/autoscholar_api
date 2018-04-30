<html>
<head>
<!-- include jquery from CDN -->
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
<script>
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
	
	function showResponse(data) {
		var rspstr = JSON.stringify(data,null,4);
		$('#response').text(rspstr);
	}
	
	var urlbase = "/api/autoscholar";
	
	function doQualList() {
		console.log("doQualList");
		year = 2017;
		fcode = '35';
		year = $('#1year').val();
		ppObj("year=",year);
		fcode = $('#1fcode').val();
		url = urlbase + "/QualificationList/"+year+"/"+fcode ;		
		$('#call').text(url);
		$('#response').text('...');
		$.getJSON(url,showResponse);
		return false;
	}

	function doQualReg() {
		console.log("doQualReg");
		year = $('#2year').val();
		qcode = $('#2qual').val();
		url = urlbase + "/StudentsRegisteredInQual/"+year+"/"+qcode ;		
		$('#call').text(url);
		$('#response').text('...');
		$.getJSON(url,showResponse);
		return false;
	}

	function doStudBio() {
		console.log("doStudBio");
		var slist = $('#3slist').val();
		var url = urlbase + "/StudentBioList?snums="+slist ;		
		$('#call').text(url);
		$('#response').text('...');
		$.getJSON(url,showResponse);
		return false;
	}

	function doStudFinRes() {
		console.log("doStudFinRes");
		var slist = $('#4slist').val();
		var url = urlbase + "/StudentFinalResults?snums="+slist ;		
		$('#call').text(url);
		$('#response').text('...');
		$.getJSON(url,showResponse);
		return false;
	}

	function doSubjInfo() {
		console.log("doSubjInfo");
		var year = $('#5year').val();
		var slist = $('#5slist').val();
		var url = urlbase + "/SubjectInfo/"+year+"?subjcodes="+slist ;		
		$('#call').text(url);
		$('#response').text('...');
		$.getJSON(url,showResponse);
		return false;
	}
	
	function doStudAssRes() {
		console.log("doStudAssRes");
		var slist = $('#6slist').val();
		var url = urlbase + "/StudentAssessmentResults?snums="+slist ;		
		$('#call').text(url);
		$('#response').text('...');
		$.getJSON(url,showResponse);
		return false;
	}

	//catch buttons
	$().ready(function() {
		$("#btnQualList").click(doQualList);
		$("#btnQualReg").click(doQualReg);
		$("#btnStudBio").click(doStudBio);
		$("#btnStudFinRes").click(doStudFinRes);
		$("#btnSubjInfo").click(doSubjInfo);
		$("#btnStudAssRes").click(doStudAssRes);
		console.log("buttons hooked up");
	});
</script>
<style>
	.demoitem { background-color: #F0F0F0; border: solid black 1px; margin-top: 20px;}
	.itemlabel { background-color: #C0C0C0;}
	.rightbtn { float: right }
	.output { 
		font-family: courier, monospace ;
		white-space: pre;
		background-color: #E0E0F0 ;
		border: solid black 2px;
	};
</style>
</head>
<body>
<?php $urlbase = '/api/autoscholar/'; ?>
<h2>Autoscholar data integration API / examples:</h2>
	<form>
<div class='demoitem'>
	<div class='itemlabel'>
		<b>Endpoint:</b> <tt><?php echo($urlbase)?>/QualificationsList</tt>
	</div>
	/QualificationsList/
	<input type=text id='1year' value='2017'/>/
	<select id='1fcode'>
		<option value='31'>31 : Arts and Design</option>
		<option value='32'>32 : Accounting and Informatics</option>
		<option value='33'>33 : Management Sciences</option>
		<option value='34'>34 : Applied Sciences</option>
		<option value='35'>35 : Engineering and the Built Environment</option>
		<option value='36'>36 : Health Sciences</option>
	</select>
	<button type='button' class='rightbtn' id='btnQualList'>Call endpoint</button>
</div>

<div class='demoitem'>
	<div class='itemlabel'>
		<b>Endpoint:</b> <tt><?php echo($urlbase)?>/StudentsRegisteredInQual</tt>
	</div>
	/StudentsRegisteredInQual/
	<input type=text id='2year' value='2017'/>/
	<input type=text id='2qual' value='NDINS1'/>
	<button type='button' class='rightbtn' id='btnQualReg'>Call endpoint</button>
</div>

<div class='demoitem'>
	<div class='itemlabel'>
		<b>Endpoint:</b> <tt><?php echo($urlbase)?>/StudentBioList</tt>
	</div>
	/StudentsBioList?snums=
	<textarea id='3slist' rows='1' cols='50'>[21416314,21416315,21416316]</textarea>
	<button type='button' class='rightbtn' id='btnStudBio'>Call endpoint</button>
</div>

<div class='demoitem'>
	<div class='itemlabel'>
		<b>Endpoint:</b> <tt><?php echo($urlbase)?>/StudentFinalResults</tt>
	</div>
	/StudentsFinalResults?snums=
	<textarea id='4slist' rows='1' cols='50'>[21416314,21416315,21416316]</textarea>
	<button type='button' class='rightbtn' id='btnStudFinRes'>Call endpoint</button>
</div>

<div class='demoitem'>
	<div class='itemlabel'>
		<b>Endpoint:</b> <tt><?php echo($urlbase)?>/SubjectInfo</tt>
	</div>
	/SubjectInfo/
	<input type=text id='5year' value='2017'/>
	?subjcodes=
	<textarea id='5slist' rows='1' cols='50'>["IPRO201","DSFW202","DSFW212","DSFW222"]</textarea>
	<button type='button' class='rightbtn' id='btnSubjInfo'>Call endpoint</button>
</div>

<div class='demoitem'>
	<div class='itemlabel'>
		<b>Endpoint:</b> <tt><?php echo($urlbase)?>/StudentAssessmentResults</tt>
	</div>
	/StudentsAssessmentResults?snums=
	<textarea id='6slist' rows='1' cols='50'>[21416314,21416315,21416316]</textarea>
	<button type='button' class='rightbtn' id='btnStudAssRes'>Call endpoint</button>
</div>



	</form>
<br>
<b>Request URL:</b>
<div class='output' id='call'>...</div>
<b>Response JSON:</b>
<div class='output' id='response'>...</div>	
	
</body>
</html>