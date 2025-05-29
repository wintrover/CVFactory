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

  let eventSource = null; // SSE EventSource 객체

  // 요소 존재 여부 확인
  if (!generateButtonElement || !buttonText || !spinner || !job_url_textarea || !userStoryTextarea || !generatedResumeTextarea || !statusMessageElement) {
    console.error("One or more essential UI elements are missing!");
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

  function startTaskStreaming(taskId) {
    console.log("Starting SSE connection for task ID:", taskId);
    showLoadingState(true);
    
    let initialMessage = "자기소개서 생성을 시작합니다... 잠시만 기다려 주세요.";
    if (('Notification' in window) && Notification.permission !== 'granted') {
      initialMessage += " 브라우저 알림을 허용하시면 작업 완료 시 알려드립니다.";
    }
    statusMessageElement.textContent = initialMessage;
    generatedResumeTextarea.value = ""; // 이전 결과 비우기

    if (eventSource) {
        eventSource.close(); // 이전 EventSource가 있다면 닫기
    }

    eventSource = new EventSource(API_BASE_URL + "/stream-task-status/" + taskId);

    eventSource.onopen = function() {
        console.log("SSE connection opened for task " + taskId + ".");
        statusMessageElement.textContent = "서버와 연결되었습니다. 작업 진행 상황을 곧 받아옵니다...";
    };

    eventSource.onmessage = function(event) {
      // console.log("SSE message received:", event.data);
      try {
        const data = JSON.parse(event.data);
        // console.log("Parsed SSE data:", data);

        let statusText = data.status;
        if (data.current_step) {
            statusText = data.current_step + " (상태: " + data.status + ")";
        }
        statusMessageElement.textContent = "진행 상황: " + statusText;

        if (data.status === "SUCCESS") {
          console.log("SSE Task SUCCESS:", data);
          showLoadingState(false);
          let displayedMessage = "자기소개서 생성이 완료되었습니다!";
          let cvContent = "";

          if (data.result && typeof data.result === 'object') {
            if (data.result.full_cover_letter_text) { // FastAPI의 TaskStatusResponse.result.full_cover_letter_text
                cvContent = data.result.full_cover_letter_text;
            } else if (data.result.result && data.result.result.full_cover_letter_text) { // FastAPI의 TaskStatusResponse.result.result.full_cover_letter_text (중첩된 경우)
                cvContent = data.result.result.full_cover_letter_text;
            } else if (data.result.message) { // 다른 메시지 필드가 있는 경우
                cvContent = data.result.message;
                displayedMessage = data.result.message;
            } else {
                cvContent = "생성된 자기소개서 내용을 분석하는 데 실패했습니다. (서버 응답 형식 오류)";
                displayedMessage = "자기소개서 내용 분석 실패.";
                console.warn("SSE SUCCESS but result object structure is unexpected:", data.result);
            }
          } else if (data.result && typeof data.result === 'string') {
             cvContent = "자기소개서 결과 처리 중 오류가 발생했습니다. (잘못된 응답 형식)";
             displayedMessage = "자기소개서 결과 처리 오류.";
             console.warn("SSE SUCCESS but result is a string:", data.result);
          } else {
             cvContent = "생성된 자기소개서 내용을 받아오지 못했습니다. (결과 없음)";
             displayedMessage = "자기소개서 내용을 받아오는 데 실패했습니다.";
             console.warn("SSE SUCCESS but result is null or unexpected type:", data.result);
          }
          
          generatedResumeTextarea.value = cvContent;
          statusMessageElement.textContent = displayedMessage; // 최종 성공 메시지
          logDisplayedCvToBackend(cvContent);

          let notificationMessage = displayedMessage.split('\n')[0];
          if (cvContent && cvContent.length > 50 && displayedMessage.startsWith("자기소개서 생성")) {
               notificationMessage = "자기소개서가 성공적으로 생성되었습니다!";
          }
          showBrowserNotification("자기소개서 생성 완료!", notificationMessage, () => {
              generatedResumeTextarea.focus();
          });
          eventSource.close(); // 성공 시 연결 종료
          console.log("SSE connection closed on SUCCESS.");

        } else if (data.status === "FAILURE" || data.status === "ERROR_INTERNAL" || data.status === "ERROR_SETUP" || data.status === "ERROR_STREAM" || data.status === "ERROR_SERIALIZATION" || data.status === "ERROR_UNEXPECTED_STREAM") {
          console.error("SSE Task FAILURE or ERROR:", data);
          showLoadingState(false);
          let errorMessage = "자기소개서 생성에 실패했습니다.";
          if (data.result && data.result.error) {
              errorMessage += " 오류: " + data.result.error;
          } else if (data.result && typeof data.result === 'string') { // 실패 시 result가 문자열일 경우
              errorMessage += " 오류: " + data.result;
          } else if (data.message) { // FastAPI 에러 메시지
              errorMessage = data.message;
          }
          
          let currentStepInfo = data.current_step ? " (단계: " + data.current_step + ")" : "";
          statusMessageElement.textContent = errorMessage + currentStepInfo;
          
          showBrowserNotification("자기소개서 생성 실패", errorMessage.replace(/\n/g, ' ') + currentStepInfo);
          eventSource.close(); // 실패 시 연결 종료
          console.log("SSE connection closed on FAILURE or ERROR.");

        } else if (data.status === "PENDING" || data.status === "STARTED" || data.status === "RETRY" || data.status === "PROGRESS") {
          // 진행 중 상태 업데이트 (이미 위에서 statusMessageElement 업데이트 됨)
          console.log("SSE Task " + taskId + " status: " + data.status + ", step: " + (data.current_step || 'N/A'));
        } else {
          // 알 수 없는 상태
          console.warn("SSE Unknown task status for " + taskId + ": " + JSON.stringify(data));
          statusMessageElement.textContent = "알 수 없는 작업 상태: " + (data.status || 'N/A');
          // 알 수 없는 상태라도 일단은 연결 유지, 서버에서 종료해주길 기대
        }
      } catch (e) {
        console.error("Error parsing SSE message or updating UI:", e, "Raw data:", event.data);
        statusMessageElement.textContent = "데이터 처리 중 오류가 발생했습니다.";
        // 파싱 오류 시에는 연결을 유지할 수도, 닫을 수도 있음. 여기서는 일단 유지.
      }
    };

    eventSource.onerror = function(err) {
      console.error("EventSource failed:", err);
      showLoadingState(false);
      statusMessageElement.textContent = "서버와 연결 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.";
      eventSource.close(); // 에러 발생 시 명시적으로 연결 종료
      console.log("SSE connection closed on ERROR.");
    };
  }

  function logDisplayedCvToBackend(textToLog) {
    // console.log(`Logging displayed CV to backend. Length: ${textToLog ? textToLog.length : 0}`);
    const payload = {
      displayed_text: textToLog || ""
    };
  
    fetch(API_BASE_URL + "/log-displayed-cv", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })
    .then(response => {
      if (!response.ok) {
        console.warn("Backend logging failed with status: " + response.status);
        return response.json().then(errData => { throw new Error(errData.detail || 'Unknown error'); });
      }
      return response.json();
    })
    .then(data => {
      // console.log('Backend logging successful:', data.message);
    })
    .catch(error => {
      console.error('Error logging displayed CV to backend:', error);
    });
  }
  
  generateButtonElement.addEventListener('click', function() {
    // console.log("Generate button clicked.");
    var url = job_url_textarea.value.trim();
    var userPrompt = userStoryTextarea.value.trim();
    // console.log(\`URL: \${url}, Prompt: \${userPrompt ? 'Provided' : 'Not provided'}\`);

    if (!url) {
      // console.log("URL is empty. Alerting user.");
      alert("채용 공고 URL을 입력해주세요.");
      return;
    }

    // console.log("Calling showLoadingState(true)");
    showLoadingState(true);
    statusMessageElement.textContent = "자기소개서 생성 요청 중..."; // 초기 메시지
    generatedResumeTextarea.value = ""; // 이전 결과 지우기

    const payload = {
      job_posting_url: url,
      user_prompt: userPrompt || null // user_prompt가 없으면 null로 설정
    };

    // console.log("Payload for POST request:", payload);

    fetch(API_BASE_URL + "/", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json', // Content-Type 변경
      },
      body: JSON.stringify(payload), // FormData 대신 JSON 페이로드 사용
    })
    .then(response => {
      // console.log("Raw response from /:", response);
      if (!response.ok) {
        // console.error("Server responded with an error:", response.status);
        showLoadingState(false);
        return response.json().then(errData => {
            // console.error("Error data from server:", errData);
            let detailMessage = "알 수 없는 오류";
            if (errData && errData.detail) {
                if (typeof errData.detail === 'string') {
                    detailMessage = errData.detail;
                } else if (Array.isArray(errData.detail) && errData.detail.length > 0 && errData.detail[0].msg && Array.isArray(errData.detail[0].loc)) {
                    // FastAPI 유효성 검사 오류 형식 처리
                    detailMessage = errData.detail.map(d => d.loc.join('.') + " - " + d.msg).join(', ');
                } else if (typeof errData.detail === 'object') {
                    detailMessage = JSON.stringify(errData.detail);
                }
            }
            throw new Error(detailMessage);
        });
      }
      return response.json();
    })
    .then(data => {
      // console.log("Successfully received task ID:", data);
      if (data.task_id) {
        statusMessageElement.textContent = "작업이 시작되었습니다 (ID: " + data.task_id + "). 잠시 후 결과가 표시됩니다.";
        startTaskStreaming(data.task_id); // SSE 스트리밍 시작
      } else {
        // console.error("Task ID not found in response data:", data);
        showLoadingState(false);
        statusMessageElement.textContent = "작업 ID를 받지 못했습니다.";
        generatedResumeTextarea.value = "오류: 서버에서 작업 ID를 반환하지 않았습니다.";
      }
    })
    .catch(error => {
      console.error("Error during fetch operation:", error);
      showLoadingState(false);
      statusMessageElement.textContent = "자기소개서 생성 요청에 실패했습니다: " + error.message;
      generatedResumeTextarea.value = "오류로 인해 자기소개서를 생성할 수 없습니다: " + error.message;
    });
  });
}); 