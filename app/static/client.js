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
      el('result-1-photo').innerHTML = `<img src='${response['hat_1_photo']}'>`;
      el('result-1-url').innerHTML = `<br><a href="${response['hat_1_link']}">${response['hat_1_info']}</a>`;
      el('result-1-free').innerHTML = `<br>Free pattern? ${response['hat_1_free']}`;
      el('result-2-photo').innerHTML = `<br><img src='${response['hat_2_photo']}'>`;
      el('result-2-url').innerHTML = `<br><a href="${response['hat_2_link']}">${response['hat_2_info']}</a>`;
      el('result-2-free').innerHTML = `<br>Free pattern? ${response['hat_2_free']}`;
      el('result-3-photo').innerHTML = `<br><img src='${response['hat_3_photo']}'>`;
      el('result-3-url').innerHTML = `<br><a href="${response['hat_3_link']}">${response['hat_3_info']}</a>`;
      el('result-3-free').innerHTML = `<br>Free pattern? ${response['hat_3_free']}`;
    }
    el('analyze-button').innerHTML = 'Analyze';
};

  var fileData = new FormData();
  fileData.append("file", uploadFiles[0]);
  xhr.send(fileData);
}