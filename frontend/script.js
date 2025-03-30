function loginWithGoogle() {
    window.location.href = "http://127.0.0.1:8000/accounts/google/login/";
}

function saveInput(id) {
    let element = document.getElementById(id);
    
    if (!element) {  // ID가 없으면 오류 방지
        console.error(`ID가 ${id}인 요소를 찾을 수 없습니다.`);
        return;
    }
    
    localStorage.setItem(id, element.value);
    alert("저장되었습니다!");
}

// 페이지 로드 후 강제로 로딩 오버레이 숨기기 (혹시 CSS 적용이 안될 경우 대비)
document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("loading-overlay").style.display = "none";
});

// 회사 정보 크롤링 함수
function fetchCompanyInfo() {
    let company_url = document.getElementById("company_url").value.trim();
    
    if (!company_url) {
        alert("회사 URL을 입력하세요.");
        return;
    }
    
    // URL 형식 검증 (http:// 또는 https://로 시작하는지)
    if (!company_url.startsWith('http://') && !company_url.startsWith('https://')) {
        company_url = 'https://' + company_url;
        document.getElementById("company_url").value = company_url;
    }
    
    // 로딩 화면 표시
    document.getElementById("loading-overlay").style.display = "flex";
    
    let animationContainer = document.getElementById("lottie-container");
    let animationPath = animationContainer.getAttribute("data-animation");
    
    // 기존 애니메이션이 있다면 제거 후 새로 실행
    if (animationContainer.lottieInstance) {
      animationContainer.lottieInstance.destroy();
    }
    
    animationContainer.lottieInstance = lottie.loadAnimation({
      container: animationContainer,
      renderer: "svg",
      loop: true,
      autoplay: true,
      path: animationPath
    });
    
    // CSRF 토큰 가져오기
    const csrftoken = getCookie("csrftoken");
    
    fetch("http://127.0.0.1:8000/api/fetch_company_info/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken
        },
        body: JSON.stringify({
            company_url: company_url
        }),
        credentials: "include"
    })
    .then(response => response.json())
    .then(data => {
        console.log("서버 응답:", data);
        
        if (data.company_info) {
            // 회사 정보를 추가 정보 영역에 표시
            alert("회사 정보를 성공적으로 가져왔습니다!");
        } else {
            alert("회사 정보를 가져오지 못했습니다: " + (data.error || "알 수 없는 오류"));
        }
    })
    .catch(error => {
        console.error("에러 발생:", error);
        alert("서버 요청 중 오류가 발생했습니다.");
    })
    .finally(() => {
        // 로딩 화면 숨김
        document.getElementById("loading-overlay").style.display = "none";
        
        // 애니메이션 종료
        if (animationContainer.lottieInstance) {
            animationContainer.lottieInstance.destroy();
        }
    });
}

function generateResume() {
    let job_url = document.getElementById("job_url").value.trim();
    let company_url = document.getElementById("company_url").value.trim();
    let user_story = document.getElementById("user_story").value.trim();

    if (!job_url || !user_story) {
        alert("공고 URL과 자기소개 내용을 입력하세요.");
        return;
    }

    // URL 형식 검증 (http:// 또는 https://로 시작하는지)
    if (company_url && !company_url.startsWith('http://') && !company_url.startsWith('https://')) {
        company_url = 'https://' + company_url;
        document.getElementById("company_url").value = company_url;
    }

    // 로딩 화면 표시
    document.getElementById("loading-overlay").style.display = "flex";

    let animationContainer = document.getElementById("lottie-container");
    let animationPath = animationContainer.getAttribute("data-animation");

    // 기존 애니메이션이 있다면 제거 후 새로 실행
    if (animationContainer.lottieInstance) {
      animationContainer.lottieInstance.destroy();
    }

    animationContainer.lottieInstance = lottie.loadAnimation({
      container: animationContainer,
      renderer: "svg",
      loop: true,
      autoplay: true,
      path: animationPath
    });

    // CSRF 토큰 가져오기
    const csrftoken = getCookie("csrftoken");

    fetch("http://127.0.0.1:8000/api/create_resume/", {
        method: "POST",
        headers: { 
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken  // CSRF 토큰 추가
        },
        body: JSON.stringify({
            recruitment_notice_url: job_url,
            target_company_url: company_url,
            user_story: user_story
        }),
        credentials: "include"  // 쿠키 인증 포함
    })
    .then(response => response.json())
    .then(data => {
        console.log("서버 응답:", data);  

        let generatedResumeElement = document.getElementById("generated_resume");

        if (generatedResumeElement) {
            generatedResumeElement.value = data.generated_resume || "자기소개서 생성에 실패했습니다.";
        } else {
            console.error("generated_resume 요소를 찾을 수 없습니다.");
        }
    })
    .catch(error => {
      console.error("에러 발생:", error);
      alert("서버 요청 중 오류가 발생했습니다.");
    })
    .finally(() => {
      // 로딩 화면 숨김
      document.getElementById("loading-overlay").style.display = "none";

      // 애니메이션 종료
      if (animationContainer.lottieInstance) {
        animationContainer.lottieInstance.destroy();
      }
    });
}

// CSRF 토큰을 가져오는 함수
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
} 