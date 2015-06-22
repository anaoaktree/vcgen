var editor = CodeMirror.fromTextArea(document.getElementById("inputTextToSave"), {
      lineNumbers: true,
      mode: "text/html",
      matchBrackets: true
    });