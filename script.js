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
  var job_url_textarea = document.getElementById("job_url");
  console.log("Job URL textarea element:", job_url_textarea);
  // Get the prompt textarea
  var userStoryTextarea = document.getElementById("prompt");
  console.log("User Story textarea element:", userStoryTextarea);

  var modalMessage = document.getElementById("modalMessage"); // 모달 메시지 표시용
  var generatedResumeTextarea = document.getElementById("generated_resume");

  let pollingIntervalId = null; // 폴링 인터벌 ID
  let taskCompletedSuccessfully = false; // 작업 성공 여부 플래그

  if (!btn) {
    console.error("Generate button not found!");
    return;
  }

  if (!job_url_textarea) {
    console.error("Job URL textarea not found!");
    return;
  }

  if (!userStoryTextarea) {
    console.error("User Story textarea not found!");
    return;
  }

  if (!modal) {
    console.error("Modal element not found!");
    return;
  }

  if (!modalMessage) {
    console.error("Modal message element not found!");
    return;
  }

  if (!generatedResumeTextarea) {
    console.error("Generated resume textarea not found!");
    return;
  }

  function showModal(message) {
    modalMessage.innerHTML = message.replace(/\n/g, '<br>');
    modal.style.display = "flex";
  }

  function hideModal() {
    modal.style.display = "none";
    // 모달이 닫힐 때 폴링을 중단하지 않도록 아래 두 줄을 주석 처리 또는 삭제
    // if (pollingIntervalId) {
    //   clearInterval(pollingIntervalId);
    //   pollingIntervalId = null;
    // }
  }

  function requestNotificationPermission() {
    return new Promise((resolve, reject) => {
      if (!('Notification' in window)) {
        console.log("This browser does not support desktop notification");
        return resolve(false);
      }
      if (Notification.permission === "granted") {
        return resolve(true);
      }
      if (Notification.permission !== "denied") {
        Notification.requestPermission().then(permission => {
          if (permission === "granted") {
            return resolve(true);
          }
          resolve(false);
        });
      } else {
        resolve(false);
      }
    });
  }

  function showBrowserNotification(title, body, onClickCallback) {
    requestNotificationPermission().then(granted => {
      if (granted) {
        const notification = new Notification(title, { body });
        notification.onclick = () => {
          window.focus(); // 브라우저 창 포커스
          if (onClickCallback) {
            onClickCallback();
          }
          notification.close();
        };
      }
    });
  }

  function pollTaskStatus(taskId) {
    console.log("Polling for task ID:", taskId);
    taskCompletedSuccessfully = false; // 새 작업 시작 시 초기화
    // 초기 모달은 보여주되, 백그라운드 진행을 위해 사용자가 닫을 수 있도록 함
    let initialModalMessage = "자기소개서를 생성 중입니다... 잠시만 기다려 주세요.\n";
    if (('Notification' in window) && Notification.permission !== 'granted') {
      initialModalMessage += "브라우저 알림을 허용하시면 작업 완료 시 알려드립니다.\n";
    }
    initialModalMessage += "이 창을 닫으셔도 백그라운드에서 계속 진행됩니다.";
    showModal(initialModalMessage);
    generatedResumeTextarea.value = ""; // 이전 내용 초기화

    if (pollingIntervalId) { // 이전 폴링이 있다면 중지
        clearInterval(pollingIntervalId);
    }

    pollingIntervalId = setInterval(function() {
      if (taskCompletedSuccessfully) { // 이미 성공적으로 완료된 작업이면 폴링 중단
          if (pollingIntervalId) {
            clearInterval(pollingIntervalId);
            pollingIntervalId = null;
          }
          return;
      }
      fetch(`http://localhost:8001/tasks/${taskId}`) // CVFactory_Server의 상태 확인 엔드포인트
        .then(response => {
          if (!response.ok) {
            return response.json().then(errData => {
              throw new Error(errData.detail || `Server responded with status: ${response.status}`);
            });
          }
          return response.json();
        })
        .then(data => {
          console.log("Task status:", data);
          if (data.status === "SUCCESS") {
            clearInterval(pollingIntervalId);
            pollingIntervalId = null;
            taskCompletedSuccessfully = true; // 성공 플래그 설정
            let successMessage = "자기소개서 생성이 완료되었습니다!";
            if (data.result && typeof data.result === 'string') {
                generatedResumeTextarea.value = data.result;
            } else if (data.result && data.result.formatted_cover_letter) {
                generatedResumeTextarea.value = data.result.formatted_cover_letter;
            } else {
                 generatedResumeTextarea.value = "생성된 자기소개서 내용을 받아오지 못했습니다.";
                 successMessage = "자기소개서 내용을 받아오는 데 실패했습니다.";
            }
            // 모달을 닫고 브라우저 알림 표시
            hideModal(); // 일단 모달은 닫음
            showBrowserNotification("자기소개서 생성 완료!", successMessage, () => {
                generatedResumeTextarea.focus();
                // 이미 결과가 표시되어 있으므로, 추가적인 모달은 필요 없을 수 있음
                // 필요하다면 여기서 showModal(successMessage) 호출
            });
          } else if (data.status === "FAILURE") {
            clearInterval(pollingIntervalId);
            pollingIntervalId = null;
            let errorMessage = "자기소개서 생성에 실패했습니다.";
            if (data.result && data.result.error) {
                errorMessage += `\n오류: ${data.result.error}`;
            }
            generatedResumeTextarea.value = errorMessage;
            // 실패 시에는 모달을 다시 명확히 보여주는 것이 좋을 수 있음
            showModal(errorMessage);
            showBrowserNotification("자기소개서 생성 실패", errorMessage, () => {
                generatedResumeTextarea.focus();
            });
          } else if (data.status === "PENDING" || data.status === "STARTED" || data.status === "RETRY") {
            // 작업 진행 중, 모달 메시지 업데이트 (선택 사항)
            // 사용자가 모달을 닫았을 수 있으므로, 여기서는 console.log만 남기거나 다른 UI 피드백 고려
            console.log(`Task ${taskId} is still ${data.status}`);
          } else {
            // 알 수 없는 상태
            clearInterval(pollingIntervalId);
            pollingIntervalId = null;
            generatedResumeTextarea.value = `알 수 없는 작업 상태입니다: ${data.status}`;
            showModal(`알 수 없는 작업 상태: ${data.status}`);
          }
        })
        .catch(error => {
          console.error("Polling error:", error);
          clearInterval(pollingIntervalId);
          pollingIntervalId = null;
          generatedResumeTextarea.value = "작업 상태 확인 중 오류가 발생했습니다: " + error.message;
          showModal("작업 상태 확인 중 오류 발생: " + error.message);
        });
    }, 5000); // 5초마다 폴링
  }

  // When the user clicks the button, open the modal
  btn.onclick = function() {
    console.log("Generate button clicked");

    // 브라우저 알림 권한 요청 (이미 허용되었거나 거부된 경우 아무것도 하지 않음)
    requestNotificationPermission().then(granted => {
        if (!granted) {
            console.log("Browser notifications are not granted. Proceeding without them.");
            // 사용자에게 알림이 꺼져있음을 안내하는 UI를 추가할 수 있음
        }
    });

    if (!modal) {
      console.error("Modal element is not available when button is clicked!");
      return;
    }
    modal.style.display = "flex"; // Use flex to center the modal
    console.log("Modal display set to flex");

    // Get the URL from the textarea
    var job_url = job_url_textarea.value;
    console.log("Job URL value:", job_url);
    // Get the user story from the textarea
    var userStory = userStoryTextarea.value;
    console.log("User Story value:", userStory);

    // Validate if the URL is empty
    if (!job_url || job_url.trim() === "") {
      console.error("Job URL is empty. Aborting fetch.");
      alert("공고 URL을 입력해주세요."); // Simple alert for now
      modal.style.display = "none"; // Hide modal if URL is empty
      return; // Stop further execution
    }

    console.log("Preparing to fetch with URL:", job_url, "and User Story:", userStory);

    showModal("자기소개서 생성 요청 중...");
    generatedResumeTextarea.value = ""; // 요청 시 이전 내용 초기화

    // Send the request to the local Docker server
    fetch("http://localhost:8001/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        job_url: job_url,
        prompt: userStory,
      }),
    })
    .then(response => {
      console.log("Initial fetch response received:", response);
      if (!response.ok) {
        // If server response is not ok (e.g., 4xx, 5xx), throw an error to catch it later
        return response.json().then(errData => {
          console.error("Initial fetch response not OK. Error data:", errData);
          throw new Error(errData.detail || `Server responded with status: ${response.status}`);
        });
      }
      return response.json(); // Assuming server responds with JSON
    })
    .then(data => {
      console.log("Initial fetch success. Data:", data);
      if (data.task_id) {
        pollTaskStatus(data.task_id);
      } else {
        throw new Error("Task ID not received from server.");
      }
    })
    .catch((error) => {
      console.error("Initial fetch error:", error);
      // Handle errors (e.g., display error message in the modal or as an alert)
      generatedResumeTextarea.value = "요청 처리 중 오류가 발생했습니다: " + error.message;
      showModal("요청 처리 중 오류 발생: " + error.message);
    });
    console.log("Fetch request initiated");
  }

  if (!span) {
    console.warn("Close button (span) not found!");
  } else {
    // When the user clicks on <span> (x), close the modal
    span.onclick = function() {
      console.log("Close button (span) clicked");
      hideModal();
    }
  }

  // When the user clicks anywhere outside of the modal, close it
  window.onclick = function(event) {
    // console.log("Window clicked. Event target:", event.target);
    if (event.target == modal) {
      console.log("Clicked outside of the modal");
      hideModal();
    }
  }
}); 