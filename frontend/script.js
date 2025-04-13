// config.js 파일 추가 - 환경별 설정 불러오기
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? 'http://localhost:8000' 
    : window.location.origin;

// API 키를 템플릿에서 가져오기
const API_KEY = window.API_KEY;

// 웹 성능 측정
const logCoreWebVitals = () => {
    // 페이지 로딩 성능 측정
    if ('performance' in window && 'getEntriesByType' in window.performance) {
        const pageNav = performance.getEntriesByType('navigation')[0];
        if (pageNav) {
            console.log(`DOM 로드 시간: ${pageNav.domContentLoadedEventEnd - pageNav.startTime}ms`);
            console.log(`페이지 완전 로드 시간: ${pageNav.loadEventEnd - pageNav.startTime}ms`);
        }
    }
    
    // LCP (Largest Contentful Paint) 측정
    if ('PerformanceObserver' in window) {
        try {
            const lcpObserver = new PerformanceObserver((entryList) => {
                const entries = entryList.getEntries();
                const lastEntry = entries[entries.length - 1];
                console.log(`LCP: ${lastEntry.startTime}ms`);
            });
            lcpObserver.observe({ type: 'largest-contentful-paint', buffered: true });
            
            // FID (First Input Delay) 측정
            const fidObserver = new PerformanceObserver((entryList) => {
                const firstInput = entryList.getEntries()[0];
                console.log(`FID: ${firstInput.processingStart - firstInput.startTime}ms`);
            });
            fidObserver.observe({ type: 'first-input', buffered: true });
            
            // CLS (Cumulative Layout Shift) 측정
            let clsValue = 0;
            const clsObserver = new PerformanceObserver((entryList) => {
                for (const entry of entryList.getEntries()) {
                    if (!entry.hadRecentInput) {
                        clsValue += entry.value;
                    }
                }
                console.log(`CLS: ${clsValue}`);
            });
            clsObserver.observe({ type: 'layout-shift', buffered: true });
        } catch (e) {
            console.warn('PerformanceObserver API 사용 중 오류 발생:', e);
        }
    }
};

// 디바운스 함수 - 연속 호출 제한
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// CSRF 토큰 가져오기
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

// 모바일 디바이스 감지 함수
function isMobileDevice() {
    return (window.innerWidth <= 768) || 
           ('ontouchstart' in window) || 
           (navigator.maxTouchPoints > 0) || 
           (navigator.msMaxTouchPoints > 0);
}

// 모바일 최적화 적용 함수
function applyMobileOptimizations() {
    const isMobile = isMobileDevice();
    
    // body에 모바일 클래스 추가
    document.body.classList.toggle('mobile-device', isMobile);
    
    // 텍스트 영역 자동 높이 조정
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        // 모바일에서는 textarea 높이를 자동조정
        if (isMobile) {
            textarea.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = (this.scrollHeight) + 'px';
            });
            
            // iOS에서 스크롤 개선
            textarea.addEventListener('touchstart', function(e) {
                if (this.scrollHeight > this.clientHeight) {
                    e.stopPropagation();
                }
            }, { passive: true });
        }
    });
    
    // 모바일에서 터치 피드백 개선
    if (isMobile) {
        const buttons = document.querySelectorAll('button');
        buttons.forEach(button => {
            button.addEventListener('touchstart', function() {
                this.style.transform = 'scale(0.98)';
            }, { passive: true });
            
            button.addEventListener('touchend', function() {
                this.style.transform = 'scale(1)';
            }, { passive: true });
        });
        
        // 모바일 스크롤 성능 개선
        document.addEventListener('touchmove', function(e) {
            if (e.scale !== 1) { 
                e.preventDefault(); 
            }
        }, { passive: false });
        
        // 텍스트 영역 입력 시 모바일 키보드로 인한 레이아웃 시프트 최소화
        const adjustViewportOnFocus = () => {
            // 현재 포커스된 요소가 텍스트 영역인지 확인
            if (document.activeElement.tagName === 'TEXTAREA' || document.activeElement.tagName === 'INPUT') {
                // iOS에서 메타 뷰포트 조정
                const viewportMeta = document.querySelector('meta[name="viewport"]');
                if (viewportMeta) {
                    viewportMeta.setAttribute('content', 
                        'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0');
                }
                
                // 스크롤 위치 조정
                setTimeout(() => {
                    window.scrollTo({
                        top: document.activeElement.offsetTop - 100,
                        behavior: 'smooth'
                    });
                }, 300);
            }
        };
        
        const resetViewportOnBlur = () => {
            // 포커스가 해제되면 원래 뷰포트 설정 복원
            const viewportMeta = document.querySelector('meta[name="viewport"]');
            if (viewportMeta) {
                viewportMeta.setAttribute('content', 
                    'width=device-width, initial-scale=1.0, maximum-scale=5.0, minimum-scale=1.0, user-scalable=yes, viewport-fit=cover');
            }
        };
        
        // 포커스 이벤트에 핸들러 등록
        document.addEventListener('focus', adjustViewportOnFocus, true);
        document.addEventListener('blur', resetViewportOnBlur, true);
    }
    
    // 화면 방향 감지 및 최적화
    if (window.screen && window.screen.orientation) {
        function handleOrientationChange() {
            const isLandscape = window.screen.orientation.type.includes('landscape');
            document.body.classList.toggle('landscape-mode', isLandscape);
            
            if (isLandscape) {
                // 가로 모드 최적화
                document.querySelector('.prompt-container').style.flexDirection = 'row';
            } else {
                // 세로 모드 최적화
                if (window.innerWidth <= 768) {
                    document.querySelector('.prompt-container').style.flexDirection = 'column';
                }
            }
        }
        
        // 초기 방향 설정
        handleOrientationChange();
        
        // 방향 변경 이벤트 리스너
        window.screen.orientation.addEventListener('change', handleOrientationChange);
    }
}

// 페이지 로드 후 실행되는 코드
document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("loading-overlay").style.display = "none";
    
    // 페이지 로드 시 CSRF 토큰 미리 가져오기
    fetchCSRFToken();
    
    // 이미지 최적화 적용
    optimizeImages();
    
    // lottie 스크립트 로드 확인
    checkLottieLoaded();
    
    // 모바일 최적화 적용
    applyMobileOptimizations();
    
    // Core Web Vitals 측정 (개발 모드에서만)
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        setTimeout(logCoreWebVitals, 3000); // 3초 후 성능 측정
    }
    
    // 이벤트 리스너 등록 - 한 번만 호출되도록 보장
    if (!window.eventListenersInitialized) {
        // 화면 크기 변경 시 모바일 최적화 다시 적용
        window.addEventListener('resize', debounce(function() {
            applyMobileOptimizations();
        }, 250));
        
        window.eventListenersInitialized = true;
    }
});

// 이미지 최적화
function optimizeImages() {
    // 현대 브라우저에서 지원하는 경우에만 WebP 이미지 사용
    if ('createImageBitmap' in window && 'avif' in HTMLImageElement.prototype) {
        document.querySelectorAll('img[data-src]').forEach(img => {
            // 원본 이미지 경로
            const originalSrc = img.getAttribute('data-src');
            
            // WebP 지원 시 WebP 버전으로 대체
            if (originalSrc.endsWith('.jpg') || originalSrc.endsWith('.jpeg') || originalSrc.endsWith('.png')) {
                const webpSrc = originalSrc.substring(0, originalSrc.lastIndexOf('.')) + '.webp';
                img.src = webpSrc;
            } else {
                img.src = originalSrc;
            }
            
            // 지연 로딩을 위한 Intersection Observer 사용
            const observer = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        img.src = img.getAttribute('data-src');
                        observer.unobserve(entry.target);
                    }
                });
            });
            
            observer.observe(img);
        });
    }
}

// Lottie 애니메이션 초기화 (최적화 버전)
function initOptimizedLottie(container, animationPath) {
    if (!window.lottie) {
        console.warn('Lottie 라이브러리가 로드되지 않았습니다.');
        return null;
    }
    
    // 애니메이션 경로를 보내는 경우만 처리
    if (!animationPath) {
        console.warn('애니메이션 경로가 제공되지 않았습니다.');
        return null;
    }
    
    // 이미 존재하는 애니메이션 인스턴스가 있다면 제거
    if (container.lottieInstance) {
        container.lottieInstance.destroy();
        container.lottieInstance = null;
    }
    
    try {
        return window.lottie.loadAnimation({
            container: container,
            renderer: 'svg',
            loop: true,
            autoplay: true,
            path: animationPath,
            rendererSettings: {
                progressiveLoad: true,
                preserveAspectRatio: 'xMidYMid meet',
                clearCanvas: false,
                hideOnTransparent: true
            }
        });
    } catch (error) {
        console.error('Lottie 애니메이션 초기화 실패:', error);
        return null;
    }
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

    // 로딩 화면 표시 및 기존 내용 초기화
    const loadingOverlay = document.getElementById("loading-overlay");
    loadingOverlay.style.display = "flex";
    
    // 기존에 실행 중인 Lottie 애니메이션이 있으면 제거
    const animationContainer = document.getElementById("lottie-container");
    if (animationContainer) {
        // 기존 콘텐츠 초기화
        while (animationContainer.firstChild) {
            animationContainer.removeChild(animationContainer.firstChild);
        }
        
        // 기존 인스턴스 제거
        if (animationContainer.lottieInstance) {
            animationContainer.lottieInstance.destroy();
            animationContainer.lottieInstance = null;
        }
        
        // 새 애니메이션 초기화
        const animationPath = animationContainer.getAttribute("data-animation");
        if (animationPath && window.lottie) {
            animationContainer.lottieInstance = initOptimizedLottie(animationContainer, animationPath);
        }
    }

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
            generatedResumeElement.value = resumeText;
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
        if (animationContainer && animationContainer.lottieInstance) {
            animationContainer.lottieInstance.destroy();
            animationContainer.lottieInstance = null;
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
    const temp = document.createElement('div');
    temp.textContent = input;
    return temp.innerHTML;
}

// 쿠키 가져오기 함수
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Lottie 라이브러리 로드 확인
function checkLottieLoaded() {
    if (typeof window.lottie === 'undefined') {
        // Lottie 라이브러리가 로드되지 않았을 때 fallback 처리
        console.warn('Lottie 라이브러리가 로드되지 않았습니다. 기본 로딩 표시를 사용합니다.');
        
        // 대체 로딩 표시 적용
        const lottieContainer = document.getElementById('lottie-container');
        if (lottieContainer) {
            lottieContainer.innerHTML = '<div class="fallback-loading-animation"></div>';
        }
        
        // 지연 로드 시도
        setTimeout(() => {
            if (typeof window.lottie !== 'undefined') {
                console.log('Lottie 라이브러리가 지연 로드되었습니다.');
                const container = document.getElementById('lottie-container');
                if (container) {
                    container.innerHTML = '';
                    const animationPath = container.getAttribute('data-animation');
                    if (animationPath) {
                        initOptimizedLottie(container, animationPath);
                    }
                }
            }
        }, 3000);
    } else {
        // Lottie 라이브러리가 이미 로드되어 있는 경우는 페이지 로드 시에는 초기화하지 않음
        // 실제 로딩 시에만 애니메이션을 시작하기 위해 미리 초기화하지 않음
        console.log('Lottie 라이브러리가 로드되었습니다. 사용 준비 완료.');
    }
} 