document.addEventListener('DOMContentLoaded', function() {
  // Get the modal and the button that opens it
  var modal = document.getElementById("preparingModal");

  // Get the <span> element that closes the modal
  var span = document.getElementsByClassName("close-button")[0];

  // Get the button that triggers the modal
  var btn = document.querySelector(".actions button");

  // When the user clicks the button, open the modal
  btn.onclick = function() {
    modal.style.display = "flex"; // Use flex to center the modal
  }

  // When the user clicks on <span> (x), close the modal
  span.onclick = function() {
    modal.style.display = "none";
  }

  // When the user clicks anywhere outside of the modal, close it
  window.onclick = function(event) {
    if (event.target == modal) {
      modal.style.display = "none";
    }
  }
}); 