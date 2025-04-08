// config.js 파일 추가 - 환경별 설정 불러오기
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? 'http://localhost:8000' 
    : window.location.origin;

// API 키 설정 (실제 환경에서는 보안 저장소에서 가져와야 함)
const API_KEY = 'default-dev-api-key-change-in-production';

function loginWithGoogle() {
    window.location.href = `${API_BASE_URL}/accounts/google/login/`;
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
    
    // 입력값 검증 - URL 형식 확인
    if (!isValidUrl(company_url)) {
        alert("유효한 URL 형식이 아닙니다. http:// 또는 https://로 시작하는 URL을 입력하세요.");
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
    fetch(`${API_BASE_URL}/api/create_resume/`, {
        method: "GET",
        credentials: "include"
    })
    .then(response => response.json())
    .then(() => {
        // CSRF 토큰 가져오기 (GET 요청 후 쿠키에서)
        const csrftoken = getCookie("csrftoken");
        
        // 실제 회사 정보 크롤링 요청
        return fetch(`${API_BASE_URL}/api/fetch_company_info/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken,
                "X-Api-Key": API_KEY  // API 키 추가
            },
            body: JSON.stringify({
                company_url: company_url
            }),
            credentials: "include"
        });
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

    // URL 검증
    if (!isValidUrl(job_url)) {
        alert("유효한 채용 공고 URL이 아닙니다.");
        return;
    }

    // URL 형식 검증 (http:// 또는 https://로 시작하는지)
    if (!job_url.startsWith('http://') && !job_url.startsWith('https://')) {
        job_url = 'https://' + job_url;
        document.getElementById("job_url").value = job_url;
    }

    if (company_url && !isValidUrl(company_url)) {
        alert("유효한 회사 URL이 아닙니다.");
        return;
    }

    if (company_url && !company_url.startsWith('http://') && !company_url.startsWith('https://')) {
        company_url = 'https://' + company_url;
        document.getElementById("company_url").value = company_url;
    }

    // 사용자 입력 정제 (XSS 방지)
    user_story = sanitizeInput(user_story);

    // 로딩 화면 표시
    document.getElementById("loading-overlay").style.display = "flex";

    // Lottie 애니메이션 시도 (실패해도 계속 진행)
    try {
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
    } catch (error) {
        console.warn("Lottie 애니메이션 로드 실패:", error);
        // 애니메이션 실패해도 계속 진행
    }

    // CSRF 토큰 가져오기
    fetch(`${API_BASE_URL}/api/create_resume/`, {
        method: "GET",
        credentials: "include"
    })
    .then(response => response.json())
    .then(() => {
        // CSRF 토큰 가져오기 (GET 요청 후 쿠키에서)
        const csrftoken = getCookie("csrftoken");
        
        // 실제 자기소개서 생성 요청
        return fetch(`${API_BASE_URL}/api/create_resume/`, {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken,
                "X-Api-Key": API_KEY  // API 키 추가
            },
            body: JSON.stringify({
                recruitment_notice_url: job_url,
                target_company_url: company_url,
                user_story: user_story
            }),
            credentials: "include"
        });
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

        // 애니메이션 종료 (있는 경우에만)
        try {
            let animationContainer = document.getElementById("lottie-container");
            if (animationContainer && animationContainer.lottieInstance) {
                animationContainer.lottieInstance.destroy();
            }
        } catch (error) {
            console.warn("Lottie 애니메이션 종료 실패:", error);
        }
    });
}

// URL 유효성 검사 함수
function isValidUrl(string) {
    try {
        new URL(string);
        return true;
    } catch (_) {
        return false;
    }
}

// 사용자 입력 정제 함수 (XSS 방지)
function sanitizeInput(input) {
    if (!input) return "";
    
    // HTML 태그 제거
    const doc = new DOMParser().parseFromString(input, 'text/html');
    return doc.body.textContent || "";
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