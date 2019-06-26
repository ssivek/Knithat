var el = x => document.getElementById(x);

function showPicker() {
  el("file-input").click();
}

function showPicked(input) {
  el("upload-label").innerHTML = input.files[0].name;
  var reader = new FileReader();
  reader.onload = function(e) {
    el("image-picked").src = e.target.result;
    el("image-picked").className = "";
  };
  reader.readAsDataURL(input.files[0]);
}

function analyze() {
  var uploadFiles = el("file-input").files;
  if (uploadFiles.length !== 1) alert("Please select a file to analyze!");

  el("analyze-button").innerHTML = "Analyzing...";
  var xhr = new XMLHttpRequest();
  var loc = window.location;
  xhr.open("POST", `${loc.protocol}//${loc.hostname}:${loc.port}/analyze`,
    true);
  xhr.onerror = function() {
    alert(xhr.responseText);
  };
  xhr.onload = function(e) {
    if (this.readyState === 4) {
        const response = JSON.parse(e.target.responseText);
        const patt1 = response.slice(0);
        const patt2 = response.slice(1);
        const patt3 = response.slice(2)
        el('result-label').innerHTML = `
          Result in ugly format: <br>${response['result']}
          <what about const and slice? get pattern 1 info ${patt1.info}
          OLD EFFORTS THAT DON'T WORK:
          <br>Try for a pattern name:  ${response['result'][0].info}
          <br>And a link:  ${response['result'][0].link}
          <br>And a photo URL: ${response['result'][0].photo}
          <br>And a free indicator: ${response['result'][0].free}
          <br>Happy knitting!<br>
        `;
    }
    el('analyze-button').innerHTML = 'Analyze';
};

  var fileData = new FormData();
  fileData.append("file", uploadFiles[0]);
  xhr.send(fileData);
}

