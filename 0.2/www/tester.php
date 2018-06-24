<!DOCTYPE html>
<html>
    <head>
        <!-- Required meta tags -->
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

        <!-- jquery from CDN -->
        <script src='https://code.jquery.com/jquery-2.2.4.js'></script>

        <!-- Bootstrap CSS -->
        <link href="//maxcdn.bootstrapcdn.com/bootstrap/3.3.0/css/bootstrap.min.css" rel="stylesheet" id="bootstrap-css">
        <link href="css/styles.css" rel="stylesheet" id="bootstrap-css">
        <script src="//maxcdn.bootstrapcdn.com/bootstrap/3.3.0/js/bootstrap.min.js"></script>
        
        <!-- own styles -->
        <style>
            .preformatted {
                font-family: monospace;
                white-space: pre;
            }
        </style>
        <script>
            $(document).ready(function (){
               $('#sendreq').click(function(e){
                   var ept = $('#endpoint').val();
                   var json = $('#jsonreq').val();
                   console.log("clicked: "+ept+" -> "+json);
                   
                   $.ajax({
                        type: "POST",
                        url: ept,
                        dataType: 'json',
                        contentType: 'application/json',
                        async: false,
                        data: json,
                        success: function (e) {
                            console.log("success, e="+JSON.stringify(e)); 
                            $('#jsonrsp').text(JSON.stringify(e,null,4));
                        }
                    });
                   
                   return false;
               });

               $('#login').click(function(e){
                   var user = $('#username').val();
                   var pass = $('#password').val();
                   json = JSON.stringify({"action":"login","userId":user,"pwd":pass});
                   console.log("login: "+json);
                   
                   $.ajax({
                        type: "POST",
                        url: "/api/ascholar/0.2/login",
                        dataType: 'json',
                        contentType: 'application/json',
                        async: false,
                        data: json,
                        success: function (e) {
                            console.log("success, e="+JSON.stringify(e)); 
                            $('#loginrsp').text(JSON.stringify(e,null,4));
                            if(e.status > 0) {
                                login_token = e.logToken;
                                $('#logintoken').text(login_token);
                            }
                        }
                    });
                   
                   return false;
                });

                $('#select_action').change(function(e){
                    console.log("onChange:");
                    // get the selected method name
                    var selact = $('#select_action')[0];
                    var actName = selact.options[selact.selectedIndex].text;
                    var req_tmp = {"token":login_token,"action":actName} ;
                    console.log("req_tmp:"+JSON.stringify(req_tmp));
                    $('#jsonreq').val(JSON.stringify(req_tmp,null,4));
                })

            });
        </script>
    </head>
    <body>
<div class='container'>
    
<h3>API Tester</h3>
<form>
<div>
<h3>Login / get authtoken</h3>
Username: <input type='text' id='username' name='username' value='aUser'/>
Password: <input type='password' id='password' name='password' value='aSecret'/>
<button id='login'>Get login token:</button>
<span id='logintoken'>...</span>
</div>
<div id='loginrsp' class='preformatted'>
    
</div>
<hr>
<h3>API request</h3>
<div>
        Endpoint: <input id='endpoint' name='endpoint' value='/api/ascholar/0.2/main'/>
        <select id='select_action'>
            <option>...</option>
            <option>getInstitutionId</option>
            <option>getCollegeId</option>
            <option>getCollegeFacultiesId</option>
            <option>getFacultyDisciplinesId</option>
            <option>getDisciplineProgrammesId</option>
            <option>getProgrammeStudents</option>
            <option>getStudentProgrammeRegistrations</option>
            <option>getStudentFinalCourseResults</option>
            <option>getAssessmentResults</option>
            <option>getStudentBioData</option>
        </select>
</div>    
        <textarea id='jsonreq' name='jsonreq' rows='10' cols='72'>
{
	"token" : "1234567890",
	"action" : "getCollegeId"
}
        </textarea>
<div>
<button id='sendreq'>Send request</button>    
</div>
</form>
<hr>
<div id='jsonrsp' class='preformatted'>
    
</div>
    
</div><!-- container -->
    </body>

</html>