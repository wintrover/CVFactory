// Force refresh - script.js
const IS_LOCAL = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
const API_BASE_URL = IS_LOCAL ? "http://localhost:8001" : "https://cvfactory-server-627721457878.asia-northeast3.run.app";

document.addEventListener('DOMContentLoaded', function() {
  // console.log("DOM fully loaded and parsed");

  // "생성하기" 버튼 및 내부 요소 가져오기
  var generateButtonElement = document.getElementById("generateButton");
  // console.log("Generate button element:", generateButtonElement);
  var buttonText = generateButtonElement ? generateButtonElement.querySelector(".button-text") : null;
  var spinner = generateButtonElement ? generateButtonElement.querySelector(".spinner") : null;
  
  // Get the job_url textarea
  var job_url_textarea = document.getElementById("job_url");
  // console.log("Job URL textarea element:", job_url_textarea);
  // Get the prompt textarea
  var userStoryTextarea = document.getElementById("prompt");
  // console.log("User Story textarea element:", userStoryTextarea);

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
    // console.log("Default prompt text set to textarea.");
  } else {
    console.error("Prompt textarea not found, could not set default text.");
  }

  var generatedResumeTextarea = document.getElementById("generated_resume");
  var statusMessageElement = document.getElementById("statusMessage"); // 상태 메시지 요소 가져오기

  let pollingIntervalId = null; // 폴링 인터벌 ID
  let isPolling = false; // 현재 폴링 중인지 여부를 나타내는 플래그

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
  if (!generatedResumeTextarea) {
    console.error("Generated resume textarea not found!");
    return;
  }
  if (!statusMessageElement) { // statusMessageElement 존재 여부 확인
    console.error("Status message element not found!");
    return;
  }

  showLoadingState(false); // 페이지 로드 시 스피너 숨김 및 버튼 텍스트 표시
  statusMessageElement.textContent = ""; // 초기 상태 메시지 없음

  function showLoadingState(isLoading) {
    // console.log(`Setting loading state to: ${isLoading}`);
    if (isLoading) {
      buttonText.style.display = 'none';
      spinner.style.display = 'inline-block';
      generateButtonElement.disabled = true;
    } else {
      buttonText.style.display = 'inline-block';
      spinner.style.display = 'none';
      generateButtonElement.disabled = false;
    }
    // console.log(`Generate button disabled: ${generateButtonElement.disabled}, Spinner display: ${spinner.style.display}`);
  }

  function requestNotificationPermission() {
    return new Promise((resolve) => {
      if (!('Notification' in window)) {
        // console.log("This browser does not support desktop notification");
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

  function stopPolling() {
    if (pollingIntervalId) {
      clearInterval(pollingIntervalId);
      pollingIntervalId = null;
    }
    isPolling = false;
    showLoadingState(false); // 폴링 중지 시 항상 로딩 상태 해제
  }

  function pollTaskStatus(taskId) {
    // console.log("Polling for task ID:", taskId);
    isPolling = true; // 폴링 시작
    showLoadingState(true); // 폴링 시작 시 로딩 상태 표시

    let initialMessage = "자기소개서를 생성 중입니다... 잠시만 기다려 주세요.";
    if (('Notification' in window) && Notification.permission !== 'granted') {
      initialMessage += " 브라우저 알림을 허용하시면 작업 완료 시 알려드립니다.";
    }
    statusMessageElement.textContent = initialMessage;
    generatedResumeTextarea.value = ""; // 자기소개서 영역은 비워둠
    // console.log(initialMessage);

    if (pollingIntervalId) { // 이전 폴링이 있다면 중지
        clearInterval(pollingIntervalId);
    }

    pollingIntervalId = setInterval(function() {
      if (!isPolling) { // isPolling이 false이면 폴링 중단 (예: stopPolling 호출 시)
          return;
      }
      // console.log(`Fetching status for task ${taskId}...`);
      fetch(`${API_BASE_URL}/tasks/${taskId}`) // CVFactory_Server의 상태 확인 엔드포인트
        .then(response => {
          if (!response.ok) {
            return response.json().then(errData => {
              throw new Error(errData.detail || `Server responded with status: ${response.status}`);
            });
          }
          return response.json();
        })
        .then(data => {
          // console.log("Task status data received:", data);
          if (data.status === "SUCCESS") {
            // console.log("Task SUCCESS: Clearing interval.");
            stopPolling(); 
            let displayedMessage = "자기소개서 생성이 완료되었습니다!";
            let cvContent = "";

            if (data.result && typeof data.result === 'object') {
                // data.result는 백엔드의 final_pipeline_result 객체여야 합니다.
                if (data.result.status === "SUCCESS" && data.result.cover_letter_preview) {
                    cvContent = data.result.cover_letter_preview;
                    // displayedMessage는 기본 메시지 유지
                } else if (data.result.status === "NO_CONTENT_FOR_COVER_LETTER" && data.result.message) {
                    cvContent = data.result.message; 
                    displayedMessage = data.result.message;
                } else if (data.result.message) { 
                    cvContent = data.result.message; // 메시지만 있는 경우 (예: 파일 경로만 반환 시)
                    displayedMessage = data.result.message;
                     if (data.result.cover_letter_preview) { // 혹시 preview가 message와 같이 있다면 preview 우선
                        cvContent = data.result.cover_letter_preview;
                        displayedMessage = "자기소개서 생성이 완료되었습니다!";
                    }
                } else { // 예상치 못한 객체 구조
                    cvContent = "생성된 자기소개서 내용을 분석하는 데 실패했습니다. (서버 응답 형식 오류)";
                    displayedMessage = "자기소개서 내용 분석 실패.";
                    console.warn("Task SUCCESS but result object structure is unexpected:", data.result);
                }
            } else if (data.result && typeof data.result === 'string') { 
                // 이 경우는 process_job_posting_pipeline의 반환값(루트 태스크 ID)이 그대로 온 경우일 수 있음.
                // main.py 수정으로 이 경우는 거의 없어야 하지만, 방어 코드.
                cvContent = "자기소개서 결과 처리 중 오류가 발생했습니다. (잘못된 응답 형식)";
                displayedMessage = "자기소개서 결과 처리 오류.";
                console.warn("Task SUCCESS but result is a string:", data.result);
            } else { // data.result가 null이거나 예상치 못한 타입
                cvContent = "생성된 자기소개서 내용을 받아오지 못했습니다. (결과 없음)";
                displayedMessage = "자기소개서 내용을 받아오는 데 실패했습니다.";
                console.warn("Task SUCCESS but result is null or unexpected type:", data.result);
            }
            
            generatedResumeTextarea.value = cvContent;
            statusMessageElement.textContent = displayedMessage;
            showLoadingState(false);
            
            let notificationMessage = displayedMessage.split('\n')[0]; // 알림은 첫 줄만, 또는 간결한 메시지
            if (cvContent && cvContent.length > 50 && displayedMessage.startsWith("자기소개서 생성")) { // 내용이 있고 성공 메시지면
                 notificationMessage = "자기소개서가 성공적으로 생성되었습니다!";
            }

            showBrowserNotification("자기소개서 생성 완료!", notificationMessage, () => {
                generatedResumeTextarea.focus();
            });

          } else if (data.status === "FAILURE") {
            console.error("Task FAILURE: Clearing interval.", data.result ? (data.result.error || data.result) : 'No error details');
            stopPolling(); 
            let errorMessage = "자기소개서 생성에 실패했습니다.";
            if (data.result && data.result.error) {
                errorMessage += ` 오류: ${data.result.error}`;
            } else if (data.result && typeof data.result === 'string') {
                errorMessage += ` 오류: ${data.result}`;
            }
            
            let currentStepInfo = data.current_step ? ` (단계: ${data.current_step})` : "";
            statusMessageElement.textContent = errorMessage + currentStepInfo;
            
            showBrowserNotification("자기소개서 생성 실패", errorMessage.replace(/\n/g, ' ') + currentStepInfo, () => {
                // 실패 시에는 굳이 포커스하지 않아도 될 수 있음
            });
          } else if (data.status === "PENDING" || data.status === "STARTED" || data.status === "RETRY" || data.status === "PROGRESS") { 
            let currentStepMessage = data.current_step || data.status; 
            statusMessageElement.textContent = `자기소개서 생성 중... (${currentStepMessage})`;
          } else {
            // 알 수 없는 상태
            stopPolling(); // 알 수 없는 상태 시 폴링 중지 및 로딩 상태 해제
            // generatedResumeTextarea.value = `알 수 없는 작업 상태입니다: ${data.status}`;
            statusMessageElement.textContent = `알 수 없는 작업 상태입니다: ${data.status}`;
          }
        })
        .catch(error => {
          console.error("Polling error:", error);
          stopPolling(); // 오류 시 폴링 중지 및 로딩 상태 해제
          // generatedResumeTextarea.value = "작업 상태 확인 중 오류가 발생했습니다: " + error.message;
          statusMessageElement.textContent = "작업 상태 확인 중 오류가 발생했습니다: " + error.message;
        });
    }, 5000); // 5초마다 폴링
  }

  // When the user clicks the button
  generateButtonElement.onclick = function() {
    // console.log("Generate button clicked");

    if (isPolling) {
      // console.log("Already polling, ignoring click.");
      alert("이미 자기소개서 생성 작업이 진행 중입니다.\n완료될 때까지 기다려 주십시오.");
      return;
    }

    requestNotificationPermission().then(granted => {
        if (!granted) {
            // console.log("Browser notifications are not granted. Proceeding without them.");
        }
    });

    var job_url = job_url_textarea.value;
    // console.log("Job URL value:", job_url);
    var userStory = userStoryTextarea.value;
    // console.log("User Story value:", userStory);

    if (!job_url || job_url.trim() === "") {
      console.error("Job URL is empty. Aborting fetch.");
      alert("채용 공고 URL을 입력해 주세요.");
      // generatedResumeTextarea.value = ""; 
      statusMessageElement.textContent = "채용 공고 URL을 입력해 주세요.";
      return; 
    }

    // generatedResumeTextarea.value = "자기소개서 생성을 요청하는 중...";
    statusMessageElement.textContent = "자기소개서 생성을 요청하는 중...";
    generatedResumeTextarea.value = ""; // 자기소개서 영역 초기화
    showLoadingState(true);

    fetch(`${API_BASE_URL}/`, {
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
      // console.log("Initial fetch response received:", response);
      if (!response.ok) {
        return response.json().then(errData => {
          // console.error("Initial fetch response not OK. Error data:", errData);
          throw new Error(errData.detail || `Server responded with status: ${response.status}`);
        });
      }
      return response.json();
    })
    .then(data => {
      // console.log("Initial fetch success. Data:", data);
      if (data.task_id) {
        pollTaskStatus(data.task_id);
      } else {
        throw new Error("Task ID not received from server.");
      }
    })
    .catch((error) => {
      console.error("Initial fetch error:", error);
      // generatedResumeTextarea.value = "요청 처리 중 오류가 발생했습니다: " + error.message;
      statusMessageElement.textContent = "요청 처리 중 오류가 발생했습니다: " + error.message;
      showLoadingState(false); // 오류 발생 시 로딩 상태 해제
      alert("요청 처리 중 오류 발생: " + error.message);
    });
    // console.log("Fetch request initiated");
  }
}); 