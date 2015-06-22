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

function getResultConds(){
	//ajax request to get conditions
	document.getElementById("result-div").innerHTML = codeEditor.getValue();
}

window.onload = function(){
	//checked jsperf.com for perfomance
	document.getElementById("loadFileBtn").addEventListener("click", loadFileAsText);
	document.getElementById("saveAsFileBtn").addEventListener("click", saveTextAsFile);
	document.getElementById("getResult").addEventListener("click", getResultConds);



};