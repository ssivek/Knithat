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
        var response = JSON.parse(e.target.responseText);
        var res1photo = response['hat_1_photo'];

        el('result-1-info').innerHTML = `${response['hat_1_info']}`;
        el('result-1-url').setAttribute('href', response['hat_1_link']);
        el('result-1-free').innerHTML = `Free pattern? ${response['hat_1_free']}`;
    
        document.getElementById('hat-1-image').innerHTML = res1photo;
        
        el('all-result').innerHTML = `            
          Your first pattern recommendation is ${response['hat_1_info']}
          You can find it at: ${response['hat_1_link']}`;
    }

    el('analyze-button').innerHTML = 'Analyze';
};

  var fileData = new FormData();
  fileData.append("file", uploadFiles[0]);
  xhr.send(fileData);
}