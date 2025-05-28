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

    // 자기소개서 내용을 여기에 직접 삽입합니다.
    const coverLetterContent = `저는 생성형 AI와 LLM 엔지니어로서의 경력을 쌓아오며 다양한 프로젝트
에 참여해 왔습니다. 특히, 대규모 언어 모델의 구조 및 학습, 인퍼런스
에 대한 깊은 이해를 바탕으로 여러 서비스의 기획, 개발, 운영 경험을 
쌓았습니다. Python을 활용한 개발 능력과 LangChain, Lan
gGraph와 같은 LLM 오케스트레이션 툴을 활용한 워크플로우 구성에 
강점이 있습니다. Retrieval-Augmented Generation
(RAG) 기반 서비스 개발 경험도 보유하고 있어, 관련 프로젝트에 기여
할 수 있습니다.

멀티모달 입력 및 에이전트 기반 시스템 설계에 대한 경험도 있습니다. 클
라우드 환경, 특히 AWS와 GCP에서의 AI 모델 운영 및 서비스 배포
 경험이 풍부하여, 클라우드 기반 AI 시스템 구축에 자신 있습니다. 이
미지 처리 알고리즘을 구현하고 다양한 알고리즘을 활용한 경험이 있으며, 
효율적인 코드 작성을 위해 런타임과 메모리 최적화에 힘써 왔습니다.

제가 보유한 기술과 경험을 바탕으로 ㈜바이스벌사의 생성형 AI/LLM 엔
지니어로서의 역할을 충실히 수행할 수 있을 것이라 확신합니다. 저는 새로
운 기술에 대한 끊임없는 탐구와 협동심을 바탕으로 팀과 함께 성장해 나가
고자 합니다. 특히, MCP 기반의 차세대 자동화 구조 기획 및 PoC 
개발과 같은 도전적인 프로젝트에 참여하여 제 역량을 더욱 발전시키고 싶습
니다. 제 경력과 기술이 바이스벌사의 비전과 목표에 기여할 수 있는 좋은
 파트너가 될 것이라 믿습니다.`;
    
    if (generatedResumeTextarea) {
      generatedResumeTextarea.value = coverLetterContent;
    }

    showLoadingState(true);

    fetch(`${API_BASE_URL}/create_cv/`, { // CVFactory_Server의 생성 엔드포인트
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        job_url: job_url_textarea.value,
        prompt: userStoryTextarea.value,
        // is_local_test: true // 로컬 테스트용 플래그 (필요한 경우)
      })
    })
    .then(response => {
      // console.log("Response from /create_cv/ endpoint:", response);
      if (!response.ok) {
        return response.json().then(errData => { // 에러 응답이 JSON 형태일 경우를 대비
          // console.error("Server error response (before throwing):", errData);
          // detail이 객체 형태일 수 있으므로, 문자열로 변환 시도
          let detailMessage = errData.detail;
          if (typeof detailMessage === 'object') {
            detailMessage = JSON.stringify(detailMessage);
          }
          throw new Error(detailMessage || `Server responded with status: ${response.status}`);
        });
      }
      return response.json();
    })
    .then(data => {
      // console.log("Data from /create_cv/ endpoint:", data);
      if (data && data.task_id) {
        // console.log(\`Task ID ${data.task_id} received, starting polling.\`);
        // 폴링 시작 전에 자기소개서 내용을 설정
        // generatedResumeTextarea.value = coverLetterContent; 
        pollTaskStatus(data.task_id);
      } else {
        // console.error("Task ID not found in response data:", data);
        throw new Error("Task ID를 받지 못했습니다.");
      }
    })
    .catch(error => {
      console.error("Error in fetch /create_cv/:", error);
      // console.error(\`Error during fetch: ${error.message}, Stack: ${error.stack}\`);
      statusMessageElement.textContent = "자기소개서 생성 요청에 실패했습니다: " + error.message;
      showLoadingState(false); // 오류 발생 시 로딩 상태 해제
      stopPolling(); // 혹시 폴링이 시작되었다면 중지
    });
  }
}); 