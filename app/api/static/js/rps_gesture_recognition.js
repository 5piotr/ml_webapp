// file size validation
$('#form').on('change', function() {
  var fileSize = $('#formFile')[0].files[0].size; // File size in bytes
  var maxSize = 4 * 1024 * 1024; // 4MB in bytes

  if (fileSize > maxSize) {
    alert('File size exceeds the maximum limit of 4MB.');
    return false; // Prevent form submission
  }
});

// spinner
$(document).ready(function() {
  $('#form').submit(function() {
    // Replace submit button with loading spinner
    var $submitButton = $(this).find('button[type="submit"]');
    $submitButton.replaceWith('<button class="btn btn-success" type="button" disabled><span class="spinner-border spinner-border-sm" aria-hidden="true"></span><span role="status"> Loading...</span></button>');
  });
});
