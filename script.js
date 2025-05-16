document.addEventListener('DOMContentLoaded', function() {
  // Get the modal and the button that opens it
  var modal = document.getElementById("preparingModal");

  // Get the <span> element that closes the modal
  var span = document.getElementsByClassName("close-button")[0];

  // Get the button that triggers the modal
  var btn = document.querySelector(".actions button");
  // Get the job_url textarea
  var jobUrlTextarea = document.getElementById("job_url");

  // When the user clicks the button, open the modal
  btn.onclick = function() {
    modal.style.display = "flex"; // Use flex to center the modal

    // Get the URL from the textarea
    var jobUrl = jobUrlTextarea.value;

    // Validate if the URL is empty
    if (!jobUrl || jobUrl.trim() === "") {
      console.error("Job URL is empty.");
      // Optionally, display an error message to the user in the modal
      // For example, by adding a specific element in your modal HTML and updating its content here
      alert("공고 URL을 입력해주세요."); // Simple alert for now
      modal.style.display = "none"; // Hide modal if URL is empty
      return; // Stop further execution
    }

    console.log("Sending request to CVFactory_Server with URL:", jobUrl);

    // Send the request to the local Docker server
    fetch("http://localhost:8000/process", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        target_url: jobUrl,
        query: "" // Or null, depending on server's expectation for an empty query
      }),
    })
    .then(response => {
      if (!response.ok) {
        // If server response is not ok (e.g., 4xx, 5xx), throw an error to catch it later
        return response.json().then(errData => {
          throw new Error(errData.detail || `Server responded with status: ${response.status}`);
        });
      }
      return response.json(); // Assuming server responds with JSON
    })
    .then(data => {
      console.log("Success:", data);
      // Handle success (e.g., update modal content, display success message)
      // For example, you might want to show the task ID from the response:
      // if(data.task_id) {
      //   alert("Processing started! Task ID: " + data.task_id);
      // }
    })
    .catch((error) => {
      console.error("Error:", error);
      // Handle errors (e.g., display error message in the modal or as an alert)
      alert("요청 처리 중 오류가 발생했습니다: " + error.message);
      // Optionally, hide the modal or show an error message within it
      // modal.style.display = "none"; 
    });
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