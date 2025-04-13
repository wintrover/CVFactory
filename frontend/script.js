// config.js 파일 추가 - 환경별 설정 불러오기
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? 'http://localhost:8000' 
    : window.location.origin;

// API 키를 템플릿에서 가져오기
const API_KEY = window.API_KEY;

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
    
    // 페이지 로드 시 CSRF 토큰 미리 가져오기
    fetchCSRFToken();
    
    // Lottie 스크립트 지연 로딩
    if (typeof lottie === 'undefined') {
        const lottieScript = document.createElement('script');
        lottieScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.9.6/lottie.min.js';
        lottieScript.defer = true;
        document.head.appendChild(lottieScript);
    }
});

// CSRF 토큰 미리 가져오기
function fetchCSRFToken() {
    fetch(`${API_BASE_URL}/api/create_resume/`, {
        method: "GET",
        credentials: "include"
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`CSRF 토큰 요청 실패: ${response.status}`);
        }
        return response.json();
    })
    .then(() => {
        console.log("CSRF 토큰 가져오기 성공");
    })
    .catch(error => {
        console.error("CSRF 토큰 가져오기 실패:", error);
    });
}

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
    const csrftoken = getCookie("csrftoken");
    if (!csrftoken) {
        console.log("CSRF 토큰이 없습니다. 토큰을 가져온 후 다시 시도합니다.");
        fetchCSRFToken();
        setTimeout(() => {
            const retryToken = getCookie("csrftoken");
            if (retryToken) {
                console.log("CSRF 토큰을 성공적으로 가져왔습니다. 요청을 계속합니다.");
                fetchCompanyInfo();
            } else {
                alert("CSRF 토큰을 가져올 수 없습니다. 페이지를 새로고침해주세요.");
                document.getElementById("loading-overlay").style.display = "none";
            }
        }, 1000);
        return;
    }
    
    // 실제 회사 정보 크롤링 요청
    fetch(`${API_BASE_URL}/api/fetch_company_info/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,
            "X-Api-Key": API_KEY,
            "X-Requested-With": "XMLHttpRequest"
        },
        body: JSON.stringify({
            company_url: company_url
        }),
        credentials: "include"
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
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

// Lottie 애니메이션 로드 함수
function loadLottieAnimation() {
    if (typeof lottie === 'undefined') {
        console.log('Lottie 라이브러리 로딩 중...');
        const lottieScript = document.createElement('script');
        lottieScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.9.6/lottie.min.js';
        lottieScript.onload = function() {
            console.log('Lottie 라이브러리 로드 완료');
            initLottieAnimation();
        };
        document.head.appendChild(lottieScript);
    } else {
        initLottieAnimation();
    }
}

// Lottie 애니메이션 초기화
function initLottieAnimation() {
    let animationContainer = document.getElementById("lottie-container");
    
    if (!animationContainer) {
        console.error('애니메이션 컨테이너를 찾을 수 없습니다.');
        return;
    }
    
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
        path: animationPath,
        rendererSettings: {
            progressiveLoad: true
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

    // Lottie 애니메이션 로드
    loadLottieAnimation();

    // CSRF 토큰 가져오기
    const csrftoken = getCookie("csrftoken");
    if (!csrftoken) {
        console.log("CSRF 토큰이 없습니다. 토큰을 가져온 후 다시 시도합니다.");
        fetchCSRFToken();
        setTimeout(() => {
            const retryToken = getCookie("csrftoken");
            if (retryToken) {
                console.log("CSRF 토큰을 성공적으로 가져왔습니다. 요청을 계속합니다.");
                generateResume();
            } else {
                alert("CSRF 토큰을 가져올 수 없습니다. 페이지를 새로고침해주세요.");
                document.getElementById("loading-overlay").style.display = "none";
            }
        }, 1000);
        return;
    }

    // 폼 데이터 생성
    const requestData = {
        recruitment_notice_url: job_url,
        target_company_url: company_url,
        user_story: user_story
    };
    
    // 자기소개서 생성 요청
    fetch(`${API_BASE_URL}/api/create_resume/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,
            "X-Requested-With": "XMLHttpRequest"
        },
        body: JSON.stringify(requestData),
        credentials: "include"
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log("서버 응답:", data);  

        let generatedResumeElement = document.getElementById("generated_resume");

        if (generatedResumeElement) {
            const resumeText = data.generated_resume || "자기소개서 생성에 실패했습니다.";
            const timestamp = new Date().toISOString();
            console.log(`[${timestamp}] 자기소개서 생성 완료 및 DOM에 렌더링 시작. 길이: ${resumeText.length}자`);
            generatedResumeElement.value = resumeText;
            console.log(`[${timestamp}] 자기소개서가 DOM에 렌더링 완료됨`);
            
            // 콘솔에 앞부분 미리보기 출력 (디버깅용)
            if (resumeText.length > 0) {
                console.log(`자기소개서 미리보기 (앞부분 50자): ${resumeText.substring(0, 50)}...`);
            }
        } else {
            console.error("generated_resume 요소를 찾을 수 없습니다.");
        }
    })
    .catch(error => {
        console.error("에러 발생:", error);
        alert("서버 요청 중 오류가 발생했습니다: " + error.message);
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

// 이미지 최적화 헬퍼 함수들

/**
 * 이미지에 지연 로딩 적용
 * 페이지 성능 향상을 위해 모든 이미지에 지연 로딩 속성 추가
 */
function optimizeImages() {
    const images = document.querySelectorAll('img:not([loading])');
    
    images.forEach(img => {
        // 지연 로딩 속성 추가
        img.setAttribute('loading', 'lazy');
        
        // 이미지 크기가 설정되어 있지 않은 경우 처리
        if (!img.hasAttribute('width') && !img.hasAttribute('height')) {
            // 이미지가 로드된 후 크기 설정
            img.onload = function() {
                // 이미지가 이미 로드된 후에만 크기 설정
                if (img.naturalWidth > 0 && img.naturalHeight > 0) {
                    img.setAttribute('width', img.naturalWidth);
                    img.setAttribute('height', img.naturalHeight);
                }
            };
            
            // 이미지가 이미 로드된 경우 바로 크기 설정
            if (img.complete && img.naturalWidth > 0) {
                img.setAttribute('width', img.naturalWidth);
                img.setAttribute('height', img.naturalHeight);
            }
        }
        
        // alt 속성이 없는 경우 빈 alt 추가 (접근성 개선)
        if (!img.hasAttribute('alt')) {
            img.setAttribute('alt', '');
        }
    });
}

/**
 * 반응형 이미지 생성 헬퍼 함수
 * 일반 이미지 태그를 반응형 picture 요소로 변환
 * @param {string} imgSelector - 이미지 선택자
 * @param {object} options - 설정 옵션
 */
function createResponsiveImage(imgSelector, options = {}) {
    const img = document.querySelector(imgSelector);
    if (!img) return;
    
    const defaults = {
        smallBreakpoint: 768,
        mediumBreakpoint: 1024,
        webpSupport: true,
        lazy: true,
        sizes: '100vw'
    };
    
    const settings = { ...defaults, ...options };
    
    // 원래 이미지 경로에서 파일 확장자 추출
    const imgSrc = img.getAttribute('src');
    const extension = imgSrc.split('.').pop();
    const baseSrc = imgSrc.substring(0, imgSrc.lastIndexOf('.'));
    
    // alt 텍스트 가져오기
    const altText = img.getAttribute('alt') || '';
    
    // picture 요소 생성
    const picture = document.createElement('picture');
    
    // WebP 지원하는 경우 WebP 소스 추가
    if (settings.webpSupport) {
        // 모바일용 WebP
        const sourceSmallWebp = document.createElement('source');
        sourceSmallWebp.setAttribute('srcset', `${baseSrc}-small.webp`);
        sourceSmallWebp.setAttribute('media', `(max-width: ${settings.smallBreakpoint}px)`);
        sourceSmallWebp.setAttribute('type', 'image/webp');
        picture.appendChild(sourceSmallWebp);
        
        // 태블릿용 WebP
        const sourceMediumWebp = document.createElement('source');
        sourceMediumWebp.setAttribute('srcset', `${baseSrc}-medium.webp`);
        sourceMediumWebp.setAttribute('media', `(max-width: ${settings.mediumBreakpoint}px)`);
        sourceMediumWebp.setAttribute('type', 'image/webp');
        picture.appendChild(sourceMediumWebp);
        
        // 데스크톱용 WebP
        const sourceWebp = document.createElement('source');
        sourceWebp.setAttribute('srcset', `${baseSrc}.webp`);
        sourceWebp.setAttribute('type', 'image/webp');
        picture.appendChild(sourceWebp);
    }
    
    // 원본 포맷 소스 추가
    
    // 모바일용
    const sourceSmall = document.createElement('source');
    sourceSmall.setAttribute('srcset', `${baseSrc}-small.${extension}`);
    sourceSmall.setAttribute('media', `(max-width: ${settings.smallBreakpoint}px)`);
    picture.appendChild(sourceSmall);
    
    // 태블릿용
    const sourceMedium = document.createElement('source');
    sourceMedium.setAttribute('srcset', `${baseSrc}-medium.${extension}`);
    sourceMedium.setAttribute('media', `(max-width: ${settings.mediumBreakpoint}px)`);
    picture.appendChild(sourceMedium);
    
    // 새 이미지 요소 생성
    const newImg = document.createElement('img');
    newImg.setAttribute('src', imgSrc);
    newImg.setAttribute('alt', altText);
    
    if (settings.lazy) {
        newImg.setAttribute('loading', 'lazy');
    }
    
    if (img.hasAttribute('width')) {
        newImg.setAttribute('width', img.getAttribute('width'));
    }
    
    if (img.hasAttribute('height')) {
        newImg.setAttribute('height', img.getAttribute('height'));
    }
    
    // sizes 속성 설정
    newImg.setAttribute('sizes', settings.sizes);
    
    // 이미지를 picture 요소에 추가
    picture.appendChild(newImg);
    
    // 원래 이미지를 picture 요소로 교체
    img.parentNode.replaceChild(picture, img);
    
    return picture;
}

// 페이지 로드 시 이미지 최적화 실행
document.addEventListener('DOMContentLoaded', function() {
    // 기존 코드...
    
    // 이미지 최적화 적용
    optimizeImages();
}); 