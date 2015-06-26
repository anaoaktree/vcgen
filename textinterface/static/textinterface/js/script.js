function saveTextAsFile()
{
	var textToWrite = codeEditor.getValue();
	var textFileAsBlob = new Blob([textToWrite], {type:'text/plain'});
	var fileNameToSaveAs = document.getElementById("inputFileNameToSaveAs").value;

	var downloadLink = document.createElement("a");
	downloadLink.download = fileNameToSaveAs+".imp";
	downloadLink.innerHTML = "Download File";
	if (window.URL != null)
	{
		// Chrome allows the link to be clicked
		// without actually adding it to the DOM.
		downloadLink.href = window.URL.createObjectURL(textFileAsBlob);
	}
	else
	{
		// Firefox requires the link to be added to the DOM
		// before it can be clicked.
		downloadLink.href = window.URL.createObjectURL(textFileAsBlob);
		downloadLink.onclick = destroyClickedElement;
		downloadLink.style.display = "none";
		document.body.appendChild(downloadLink);
	}

	downloadLink.click();
}

function destroyClickedElement(event)
{
	document.body.removeChild(event.target);
}

function loadFileAsText()
{
	var fileToLoad = document.getElementById("fileToLoad").files[0];
	var fileReader = new FileReader();
	fileReader.onload = function(fileLoadedEvent) 
	{
		codeEditor.setValue(fileLoadedEvent.target.result);
	};
	fileReader.readAsText(fileToLoad, "UTF-8");
}

function createRequest() {
  try {
    request = new XMLHttpRequest();
  } catch (trymicrosoft) {
    try {
      request = new ActiveXObject ("Msxml2.XMLHTTP");
  } catch (othermicrosoft) {
    try {
      request = new ActiveXObject("Microsoft.XMLHTTP");
    } catch (failed) {
      request = null;
    }
  }
}

if (request == null)
  alert("Error creating request object!");
return request;
};

function getCookie(name) {
             var cookieValue = null;
             if (document.cookie && document.cookie != '') {
                 var cookies = document.cookie.split(';');
                 for (var i = 0; i < cookies.length; i++) {
                     var cookie = cookies[i].trim();
                     // Does this cookie string begin with the name we want?
                 if (cookie.substring(0, name.length + 1) == (name + '=')) {
                     cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                     break;
                 }
             }
         }
         return cookieValue;
         }

function getResultConds(){
	//ajax request to get conditions
	event.preventDefault();

	var textToWrite = codeEditor.getValue();

    xhr = createRequest();
	xhr.open("POST", "/getconds/", true);
    xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    xhr.onreadystatechange = function(e) {
	  	if (xhr.readyState == 4) {
	  		var resultdiv = document.getElementById('result-div');
	  		var conds = this.responseText;
	  		resultdiv.innerHTML = conds
	  		for(var i=0; i< conds.length; i++){
	  			alert(conds[i])
	  		}
	  		}
	}
	xhr.send(textToWrite);
}

window.onload = function(){
	//checked jsperf.com for perfomance
	document.getElementById("loadFileBtn").addEventListener("click", loadFileAsText);
	document.getElementById("saveAsFileBtn").addEventListener("click", saveTextAsFile);
	document.getElementById("getResult").addEventListener("click", getResultConds);



};