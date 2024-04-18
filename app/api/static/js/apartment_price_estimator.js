// creating map
var mymap = L.map('mapid').setView([52.06883124080639, 19.479736645844262], 5);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  maxZoom: 18,
  tileSize: 256,
  zoomOffset: 0,
  }).addTo(mymap);

// adding marker to map
var marker = L.marker();

function onMapClick(e) {
    marker
        .setLatLng(e.latlng)
        // .setContent("You clicked the map at " + e.latlng.toString())
        .addTo(mymap);

    var roundedLat = e.latlng.lat.toFixed(6);
    var roundedLng = e.latlng.lng.toFixed(6);
    
    $('#lat').val(roundedLat);
    $('#lng').val(roundedLng);
}

mymap.on('click', onMapClick);

// Example starter JavaScript for disabling form submissions if there are invalid fields
(function() {
  'use strict';
  window.addEventListener('load', function() {
    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    var forms = document.getElementsByClassName('needs-validation');
    // Loop over them and prevent submission
    var validation = Array.prototype.filter.call(forms, function(form) {
      form.addEventListener('submit', function(event) {
        if (form.checkValidity() === false) {
          event.preventDefault();
          event.stopPropagation();
        }
        form.classList.add('was-validated');

      }, false);

    });

  }, false);

})();

// spinner
document.addEventListener("DOMContentLoaded", function () {
  var form = document.getElementById("form");
  var spinner = document.getElementById("spinner");

  form.addEventListener("submit", function (event) {

    // Check if the form is valid
    if (!form.checkValidity()) {
      // If the form is invalid, do not proceed with the submission
      return;
    }

    // Replace the submit button with the spinner
    var submitButton = form.querySelector('button[type="submit"]');
    submitButton.style.display = "none";
    spinner.innerHTML = '<button class="btn btn-success" type="button" disabled><span class="spinner-border spinner-border-sm" aria-hidden="true"></span><span role="status"> Loading...</span></button>';

    xhr.onerror = function () {
      // Hide the spinner on error
      spinner.innerHTML = '';
      submitButton.style.display = "block";

      console.error("Request failed");
    };
    xhr.send(formData);
  });
});
