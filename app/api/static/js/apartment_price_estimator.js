// creating map
var mymap = L.map('mapid').setView([52.06883124080639, 19.479736645844262], 5);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
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
    $('#lat')
        .val(e.latlng.lat.toString())
    $('#lng')
        .val(e.latlng.lng.toString())
}

mymap.on('click', onMapClick);

// Example starter JavaScript for disabling form submissions if there are invalid fields and adding spinner
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
$('#form').on('change', function() {
  $(".btn").click(function() {
    // disable button
    // $(this).prop("disabled", true);
    // add spinner to button
    $('#spinner').html(
      `<div class="d-flex align-items-center">
        <strong>Loading...</strong>
        <div class="spinner-border ml-auto" role="status" aria-hidden="true"></div>
      </div>`
    );
  });
});
