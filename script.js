// Force refresh - script.js
document.addEventListener('DOMContentLoaded', function() {
  console.log("DOM fully loaded and parsed");

  // Get the modal and the button that opens it
  var modal = document.getElementById("preparingModal");
  console.log("Modal element:", modal);

  // Get the <span> element that closes the modal
  var span = document.getElementsByClassName("close-button")[0];
  console.log("Close button element:", span);

  // "생성하기" 버튼 및 내부 요소 가져오기
  var generateButtonElement = document.getElementById("generateButton");
  console.log("Generate button element:", generateButtonElement);
  var buttonText = generateButtonElement ? generateButtonElement.querySelector(".button-text") : null;
  var spinner = generateButtonElement ? generateButtonElement.querySelector(".spinner") : null;
  
  // Get the job_url textarea
  var job_url_textarea = document.getElementById("job_url");
  console.log("Job URL textarea element:", job_url_textarea);
  // Get the prompt textarea
  var userStoryTextarea = document.getElementById("prompt");
  console.log("User Story textarea element:", userStoryTextarea);

  // 기본 프롬프트 내용 설정
  const defaultPromptText = `채용 공고 내용과 다음 사용자 프롬프트를 기반으로 자기소개서를 작성해 주세요.
    자기소개서는 한국어로, 전문적이고 회사와 직무에 맞춰 작성되어야 합니다.
    사용자 프롬프트에서 관련 있는 기술과 경험을 강조하고, 이를 채용 공고의 요구 사항과 연결해야 합니다.

    **매우 중요 지침: 출력은 반드시 제출 가능한 순수 자기소개서 본문 그 자체여야 합니다.
    어떠한 추가 설명, 주석, 메모, 지시사항 또는 "[귀하의 이름]"이나 "(참고)"와 같은 자리 표시자를 절대 포함하지 마십시오.
    생성되는 텍스트는 자기소개서의 첫 문장으로 바로 시작해서 마지막 문장으로 끝나야 합니다.
    머리글, "OOO님께"와 같은 서두, 또는 "진심으로, [귀하의 이름]"과 같은 맺음말을 포함하지 마십시오.**

    어투는 자신감 있고 열정적이어야 합니다.
    단순히 기술을 나열하는 것이 아니라 사용자 프롬프트를 자기소개서에 자연스럽게 통합해야 합니다.
    만약 사용자 프롬프트가 제공되지 않았다면, 채용 공고 내용만을 기반으로 자기소개서를 생성하되, 
    사용자가 자신의 특정 경험을 추가해야 할 부분을 '여기에 경험을 추가하세요'처럼 명시적으로 언급하지 않고, 
    자기소개서 내용 안에서 미묘하게 암시하도록 작성해 주세요.`;

  if (userStoryTextarea) {
    userStoryTextarea.value = defaultPromptText;
    console.log("Default prompt text set to textarea.");
  } else {
    console.error("Prompt textarea not found, could not set default text.");
  }

  var modalMessage = document.getElementById("modalMessage"); // 모달 메시지 표시용
  var generatedResumeTextarea = document.getElementById("generated_resume");

  let pollingIntervalId = null; // 폴링 인터벌 ID
  let taskCompletedSuccessfully = false; // 작업 성공 여부 플래그

  // 요소 존재 여부 확인
  if (!generateButtonElement || !buttonText || !spinner) {
    console.error("Generate button or its inner elements not found!");
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

  function showLoadingState(isLoading) {
    console.log(`Setting loading state to: ${isLoading}`);
    if (isLoading) {
      buttonText.style.display = 'none';
      spinner.style.display = 'inline-block';
      generateButtonElement.disabled = true;
    } else {
      buttonText.style.display = 'inline-block';
      spinner.style.display = 'none';
      generateButtonElement.disabled = false;
    }
    console.log(`Generate button disabled: ${generateButtonElement.disabled}, Spinner display: ${spinner.style.display}`);
  }

  function showModal(message) {
    modalMessage.innerHTML = message.replace(/\n/g, '<br>');
    modal.style.display = "flex";
  }

  function hideModal() {
    modal.style.display = "none";
  }

  function requestNotificationPermission() {
    return new Promise((resolve) => {
      if (!('Notification' in window)) {
        console.log("This browser does not support desktop notification");
        return resolve(false);
      }
      if (Notification.permission === "granted") {
        return resolve(true);
      }
      if (Notification.permission !== "denied") {
        Notification.requestPermission().then(permission => {
          resolve(permission === "granted");
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
      console.log(`Fetching status for task ${taskId}...`);
      fetch(`https://cvfactory-server-627721457878.asia-northeast3.run.app/tasks/${taskId}`) // CVFactory_Server의 상태 확인 엔드포인트
        .then(response => {
          if (!response.ok) {
            return response.json().then(errData => {
              throw new Error(errData.detail || `Server responded with status: ${response.status}`);
            });
          }
          return response.json();
        })
        .then(data => {
          console.log("Task status data received:", data);
          if (data.status === "SUCCESS") {
            console.log("Task SUCCESS: Clearing interval and setting taskCompletedSuccessfully to true.");
            clearInterval(pollingIntervalId);
            pollingIntervalId = null;
            taskCompletedSuccessfully = true; // 성공 플래그 설정
            let successMessage = "자기소개서 생성이 완료되었습니다!";
            console.log("Task SUCCESS: Updating textarea.");
            if (data.result && typeof data.result === 'string') {
                generatedResumeTextarea.value = data.result;
            } else if (data.result && data.result.formatted_cover_letter) {
                generatedResumeTextarea.value = data.result.formatted_cover_letter;
            } else {
                 generatedResumeTextarea.value = "생성된 자기소개서 내용을 받아오지 못했습니다.";
                 successMessage = "자기소개서 내용을 받아오는 데 실패했습니다.";
            }
            console.log("Task SUCCESS: Textarea updated. Calling showLoadingState(false).");
            showLoadingState(false);
            console.log("Task SUCCESS: showLoadingState(false) called.");
            
            hideModal(); // 일단 모달은 닫음
            showBrowserNotification("자기소개서 생성 완료!", successMessage, () => {
                generatedResumeTextarea.focus();
                // 이미 결과가 표시되어 있으므로, 추가적인 모달은 필요 없을 수 있음
                // 필요하다면 여기서 showModal(successMessage) 호출
            });
          } else if (data.status === "FAILURE") {
            console.error("Task FAILURE: Clearing interval.", data.result ? data.result.error : 'No error details');
            clearInterval(pollingIntervalId);
            pollingIntervalId = null;
            showLoadingState(false);
            let errorMessage = "자기소개서 생성에 실패했습니다.";
            if (data.result && data.result.error) {
                errorMessage += `\n오류: ${data.result.error}`;
            }
            generatedResumeTextarea.value = errorMessage;
            // 실패 시에는 모달을 다시 명확히 보여주는 것이 좋을 수 있음
            showModal(errorMessage);
            showBrowserNotification("자기소개서 생성 실패", errorMessage.replace(/\n/g, ' '), () => {
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
            showLoadingState(false);
            generatedResumeTextarea.value = `알 수 없는 작업 상태입니다: ${data.status}`;
            showModal(`알 수 없는 작업 상태: ${data.status}`);
          }
        })
        .catch(error => {
          console.error("Polling error:", error);
          clearInterval(pollingIntervalId);
          pollingIntervalId = null;
          showLoadingState(false);
          generatedResumeTextarea.value = "작업 상태 확인 중 오류가 발생했습니다: " + error.message;
          showModal("작업 상태 확인 중 오류 발생: " + error.message);
        });
    }, 5000); // 5초마다 폴링
  }

  // When the user clicks the button, open the modal
  generateButtonElement.onclick = function() {
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
      modalMessage.textContent = "채용 공고 URL을 입력해 주세요.";
      generatedResumeTextarea.value = ""; // Clear previous resume
      // btn.textContent = "자기소개서 생성"; // Reset button text if needed
      // btn.disabled = false; // Re-enable button if needed
      return; // Stop execution if URL is empty
    }
    // 사용자 프롬프트가 비어있거나 기본 프롬프트와 정확히 일치하는 경우, 빈 문자열로 처리 (선택적)
    // if (!userStory || userStory.trim() === "" || userStory.trim() === defaultPromptText.trim()) {
    //   userStory = ""; 
    // }

    // Show loading message
    modalMessage.textContent = "자기소개서 생성을 요청하는 중...";
    generatedResumeTextarea.value = ""; // Clear previous resume before new generation
    // btn.textContent = "생성 중..."; // Change button text to indicate loading
    // btn.disabled = true; // Disable button to prevent multiple clicks

    // Show loading state
    showLoadingState(true);

    // Send the POST request to the server
    // 서버 URL 수정: /generate_resume 제거
    fetch('https://cvfactory-server-627721457878.asia-northeast3.run.app/', { // 수정된 URL
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
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