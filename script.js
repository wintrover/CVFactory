document.addEventListener('DOMContentLoaded', function() {
  console.log("DOM fully loaded and parsed");

  // Get the modal and the button that opens it
  var modal = document.getElementById("preparingModal");
  console.log("Modal element:", modal);

  // Get the <span> element that closes the modal
  var span = document.getElementsByClassName("close-button")[0];
  console.log("Close button element:", span);

  // Get the button that triggers the modal
  var btn = document.querySelector(".actions button");
  console.log("Generate button element:", btn);
  // Get the job_url textarea
  var jobUrlTextarea = document.getElementById("job_url");
  console.log("Job URL textarea element:", jobUrlTextarea);

  if (!btn) {
    console.error("Generate button not found!");
    return;
  }

  if (!jobUrlTextarea) {
    console.error("Job URL textarea not found!");
    return;
  }

  // When the user clicks the button, open the modal
  btn.onclick = function() {
    console.log("Generate button clicked");

    if (!modal) {
      console.error("Modal element is not available when button is clicked!");
      return;
    }
    modal.style.display = "flex"; // Use flex to center the modal
    console.log("Modal display set to flex");

    // Get the URL from the textarea
    var jobUrl = jobUrlTextarea.value;
    console.log("Job URL value:", jobUrl);

    // Validate if the URL is empty
    if (!jobUrl || jobUrl.trim() === "") {
      console.error("Job URL is empty. Aborting fetch.");
      alert("공고 URL을 입력해주세요."); // Simple alert for now
      modal.style.display = "none"; // Hide modal if URL is empty
      return; // Stop further execution
    }

    console.log("Preparing to fetch with URL:", jobUrl);

    // Send the request to the local Docker server
    fetch("http://localhost:8001/process", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        target_url: jobUrl,
      }),
    })
    .then(response => {
      console.log("Fetch response received:", response);
      if (!response.ok) {
        // If server response is not ok (e.g., 4xx, 5xx), throw an error to catch it later
        return response.json().then(errData => {
          console.error("Fetch response not OK. Error data:", errData);
          throw new Error(errData.detail || `Server responded with status: ${response.status}`);
        });
      }
      return response.json(); // Assuming server responds with JSON
    })
    .then(data => {
      console.log("Fetch success. Data:", data);
      // Handle success (e.g., update modal content, display success message)
      // For example, you might want to show the task ID from the response:
      // if(data.task_id) {
      //   alert("Processing started! Task ID: " + data.task_id);
      // }
    })
    .catch((error) => {
      console.error("Fetch error:", error);
      // Handle errors (e.g., display error message in the modal or as an alert)
      alert("요청 처리 중 오류가 발생했습니다: " + error.message);
      // Optionally, hide the modal or show an error message within it
      // modal.style.display = "none"; 
    });
    console.log("Fetch request initiated");
  }

  if (!span) {
    console.warn("Close button (span) not found!");
  } else {
    // When the user clicks on <span> (x), close the modal
    span.onclick = function() {
      console.log("Close button (span) clicked");
      if(modal) modal.style.display = "none";
    }
  }

  // When the user clicks anywhere outside of the modal, close it
  window.onclick = function(event) {
    // console.log("Window clicked. Event target:", event.target);
    if (event.target == modal) {
      console.log("Clicked outside of the modal");
      if(modal) modal.style.display = "none";
    }
  }
}); 