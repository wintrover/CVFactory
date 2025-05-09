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
            // console.log(`DOM 로드 시간: ${pageNav.domContentLoadedEventEnd - pageNav.startTime}ms`); // 로그 삭제
            // console.log(`페이지 완전 로드 시간: ${pageNav.loadEventEnd - pageNav.startTime}ms`); // 로그 삭제
        }
    }
    
    // LCP (Largest Contentful Paint) 측정
    if ('PerformanceObserver' in window) {
        try {
            const lcpObserver = new PerformanceObserver((entryList) => {
                const entries = entryList.getEntries();
                const lastEntry = entries[entries.length - 1];
                // console.log(`LCP: ${lastEntry.startTime}ms`); // 로그 삭제
            });
            lcpObserver.observe({ type: 'largest-contentful-paint', buffered: true });
            
            // FID (First Input Delay) 측정
            const fidObserver = new PerformanceObserver((entryList) => {
                const firstInput = entryList.getEntries()[0];
                // console.log(`FID: ${firstInput.processingStart - firstInput.startTime}ms`); // 로그 삭제
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
                // console.log(`CLS: ${clsValue}`); // 로그 삭제
            });
            clsObserver.observe({ type: 'layout-shift', buffered: true });
        } catch (e) {
            console.warn('PerformanceObserver API 사용 중 오류 발생:', e);
        }
    }
};

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
    
    // 디버깅용 로그 추가
    // console.log('모바일 디바이스 감지:', isMobile); // 로그 삭제
    
    // body에 모바일 클래스 추가
    document.body.classList.toggle('mobile-device', isMobile);
    
    // 문서 전체에 터치 이벤트 개선
    if (isMobile) {
        // body와 html에 스크롤 관련 속성 설정
        document.documentElement.style.height = '100%';
        document.documentElement.style.overflowY = 'auto';
        document.documentElement.style.webkitOverflowScrolling = 'touch';
        document.body.style.height = '100%';
        document.body.style.overflowY = 'auto';
        document.body.style.webkitOverflowScrolling = 'touch';
        
        // main 요소 직접 스크롤 가능하도록 설정
        const mainElement = document.querySelector('main');
        if (mainElement) {
            // console.log('main 요소 발견, 스크롤 설정 적용'); // 로그 삭제
            
            // 스크롤 가능하다는 것을 시각적으로 표시 (디버깅용)
            mainElement.setAttribute('data-scrollable', 'true');
            
            mainElement.style.overflowY = 'auto';
            mainElement.style.webkitOverflowScrolling = 'touch';
            mainElement.style.touchAction = 'pan-y';
            mainElement.style.position = 'relative';
            mainElement.style.zIndex = '1';
            
            // 기존 터치 이벤트 리스너 제거 후 새로 추가
            mainElement.removeEventListener('touchstart', mainTouchStartHandler);
            mainElement.removeEventListener('touchmove', mainTouchMoveHandler);
            mainElement.removeEventListener('touchend', mainTouchEndHandler);
            
            // 터치 이벤트 디버깅용 로그 추가
            let touchStartY = 0;
            let touchMoveCount = 0;
            
            function mainTouchStartHandler(e) {
                touchStartY = e.touches[0].clientY;
                touchMoveCount = 0;
                // console.log('MAIN TOUCH START:', { 
                //     y: touchStartY,
                //     time: new Date().getTime(),
                //     target: e.target.tagName,
                //     scrollTop: mainElement.scrollTop,
                //     scrollHeight: mainElement.scrollHeight,
                //     clientHeight: mainElement.clientHeight 
                // });
            }
            
            function mainTouchMoveHandler(e) {
                touchMoveCount++;
                const currentY = e.touches[0].clientY;
                const deltaY = touchStartY - currentY;
                
                // 10px 이상 움직였을 때만 로그
                if (touchMoveCount % 5 === 0 || Math.abs(deltaY) > 10) {
                    // console.log('MAIN TOUCH MOVE:', { 
                    //     deltaY: deltaY, 
                    //     moveCount: touchMoveCount,
                    //     currentScrollTop: mainElement.scrollTop,
                    //     canScrollUp: mainElement.scrollTop > 0,
                    //     canScrollDown: mainElement.scrollTop + mainElement.clientHeight < mainElement.scrollHeight
                    // });
                }
            }
            
            function mainTouchEndHandler(e) {
                // console.log('MAIN TOUCH END:', { 
                //     moveCount: touchMoveCount,
                //     finalScrollTop: mainElement.scrollTop
                // });
            }
            
            // 이벤트 리스너 추가
            mainElement.addEventListener('touchstart', mainTouchStartHandler, { passive: true });
            mainElement.addEventListener('touchmove', mainTouchMoveHandler, { passive: true });
            mainElement.addEventListener('touchend', mainTouchEndHandler, { passive: true });
            
            // 스크롤 이벤트 모니터링
            mainElement.addEventListener('scroll', function(e) {
                // console.log('MAIN SCROLL:', { 
                //     scrollTop: mainElement.scrollTop,
                //     timestamp: new Date().getTime()
                // });
            }, { passive: true });
            
            // 프롬프트 컨테이너도 스크롤 가능하도록 설정
            const promptContainer = document.querySelector('.prompt-container');
            if (promptContainer) {
                promptContainer.style.overflowY = 'auto';
                promptContainer.style.webkitOverflowScrolling = 'touch';
                promptContainer.style.touchAction = 'pan-y';
                promptContainer.style.position = 'relative';
                promptContainer.style.zIndex = '2';
            }
        } else {
            // console.warn('main 요소를 찾을 수 없음');
        }
        
        // 터치 이벤트 디버깅용 글로벌 핸들러
        document.addEventListener('touchstart', function(e) {
            // console.log('DOCUMENT TOUCH START: ', e.target.tagName);
        }, { passive: true });
    }
    
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
        
        // 모바일 스크롤과 탭 상호작용 개선
        // main 요소와 그 내부의 요소들의 터치 이벤트 처리 개선
        const mainElement = document.querySelector('main');
        if (mainElement) {
            // 터치 동작 최적화
            mainElement.style.touchAction = 'manipulation';
            
            // 클릭/터치 이벤트가 제대로 동작하도록 설정
            mainElement.addEventListener('touchstart', function(e) {
                // 스크롤 가능한 영역에서는 이벤트 전파 유지
            }, { passive: true });
            
            // textarea 요소의 터치 이벤트 최적화
            const textareas = mainElement.querySelectorAll('textarea');
            textareas.forEach(textarea => {
                textarea.style.touchAction = 'pan-y';
                textarea.style.webkitOverflowScrolling = 'touch'; // iOS 스크롤 가속
            });
            
            // 커스텀 스크롤을 보장하는 요소 선택
            const scrollableElements = mainElement.querySelectorAll('.chat-box, .large-prompt, .large-textarea');
            scrollableElements.forEach(element => {
                element.style.webkitOverflowScrolling = 'touch'; // iOS에서 부드러운 스크롤
                element.style.touchAction = 'pan-y'; // 수직 스크롤만 허용
            });
        }
        
        // 텍스트 영역 입력 시 모바일 키보드로 인한 레이아웃 시프트 최소화
        const adjustViewportOnFocus = () => {
            // 현재 포커스된 요소가 텍스트 영역인지 확인
            if (document.activeElement.tagName === 'TEXTAREA' || document.activeElement.tagName === 'INPUT') {
                // iOS에서 메타 뷰포트 조정 (모바일에서 줌인/줌아웃 방지)
                const viewportMeta = document.querySelector('meta[name="viewport"]');
                if (viewportMeta) {
                    viewportMeta.setAttribute('content', 
                        'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0');
                }
                
                // 스크롤 위치 조정 - 포커스 요소가 키보드에 가려지지 않도록
                setTimeout(() => {
                    window.scrollTo({
                        top: document.activeElement.offsetTop - 100,
                        behavior: 'smooth'
                    });
                }, 300);
            }
        };
        
        const resetViewportOnBlur = () => {
            // 포커스가 해제되면 원래 뷰포트 설정 복원 (모바일에서 줌인/줌아웃 허용)
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

// 디바운스 함수 - 성능 최적화
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
        // console.log("CSRF 토큰 가져오기 성공");
    })
    .catch(error => {
        // console.error("CSRF 토큰 가져오기 실패:", error);
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
    
    // 최적화된 로티 애니메이션 초기화
    let animationContainer = document.getElementById("lottie-container");
    let animationPath = animationContainer.getAttribute("data-animation");
    
    try {
        animationContainer.lottieInstance = initOptimizedLottie(animationContainer, animationPath);
    } catch (error) {
        // console.warn("Lottie 애니메이션 로드 실패:", error);
        // 애니메이션 실패해도 계속 진행
    }
    
    // CSRF 토큰 가져오기
    const csrftoken = getCookie("csrftoken");
    if (!csrftoken) {
        // console.log("CSRF 토큰이 없습니다. 토큰을 가져온 후 다시 시도합니다.");
        fetchCSRFToken();
        setTimeout(() => {
            const retryToken = getCookie("csrftoken");
            if (retryToken) {
                // console.log("CSRF 토큰을 성공적으로 가져왔습니다. 요청을 계속합니다.");
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
        // console.log("서버 응답:", data);
        
        if (data.company_info) {
            // 회사 정보를 추가 정보 영역에 표시
            alert("회사 정보를 성공적으로 가져왔습니다!");
        } else {
            alert("회사 정보를 가져오지 못했습니다: " + (data.error || "알 수 없는 오류"));
        }
    })
    .catch(error => {
        // console.error("에러 발생:", error);
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

// 이미지 최적화 적용
function optimizeImages() {
    // 이미지 지연 로딩 적용
    const images = document.querySelectorAll('img[data-src]');
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    if (img.dataset.srcset) {
                        img.srcset = img.dataset.srcset;
                    }
                    img.onload = () => {
                        img.removeAttribute('data-src');
                        img.removeAttribute('data-srcset');
                    };
                    observer.unobserve(img);
                }
            });
        });
        
        images.forEach(img => {
            imageObserver.observe(img);
        });
    } else {
        // 폴백 - 인터섹션 옵저버 지원하지 않는 경우
        images.forEach(img => {
            img.src = img.dataset.src;
            if (img.dataset.srcset) {
                img.srcset = img.dataset.srcset;
            }
        });
    }
    
    // 배경 이미지 최적화
    const withBgImages = document.querySelectorAll('[style*="background-image"]');
    withBgImages.forEach(el => {
        // 배경 이미지는 IntersectionObserver로 지연 로딩 고려
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    // 화면에 들어오면 배경 이미지 로드
                    observer.unobserve(entry.target);
                }
            });
        }, {
            rootMargin: '200px' // 화면에 들어오기 전 미리 로드
        });
        
        observer.observe(el);
    });
}

// 최적화된 로티 애니메이션 초기화
function initOptimizedLottie(container, animationPath) {
    if (!container || !animationPath) {
        // console.warn("로티 애니메이션 초기화 실패: 컨테이너 또는 경로 누락");
        return null;
    }
    
    // 이미 인스턴스가 있으면 재사용
    if (container.lottieInstance) {
        return container.lottieInstance;
    }
    
    // 로티 객체가 로드되었는지 확인
    if (typeof lottie === 'undefined') {
        // console.warn("로티 라이브러리가 로드되지 않았습니다");
        
        // 로티 로드 이벤트 등록
        document.addEventListener('lottieReady', () => {
            // console.log("로티 지연 로드 완료, 애니메이션 초기화 시도");
            initOptimizedLottie(container, animationPath);
        }, { once: true });
        
        return null;
    }
    
    try {
        // 성능 최적화 옵션 설정
        const animationOptions = {
            container: container,
            renderer: 'svg',
            loop: true,
            autoplay: true,
            path: animationPath,
            rendererSettings: {
                progressiveLoad: true,
                preserveAspectRatio: 'xMidYMid slice',
                clearCanvas: false,
                hideOnTransparent: true
            }
        };
        
        // 모바일 디바이스에서는 더 낮은 품질로 설정
        if (isMobileDevice()) {
            animationOptions.rendererSettings.clearCanvas = true;
            animationOptions.rendererSettings.progressiveLoad = true;
        }
        
        // 애니메이션 성능 모니터링
        const startTime = performance.now();
        const animation = lottie.loadAnimation(animationOptions);
        
        // 애니메이션 로드 완료 시 성능 측정
        animation.addEventListener('DOMLoaded', () => {
            const loadTime = performance.now() - startTime;
            // console.log(`로티 애니메이션 로드 시간: ${loadTime.toFixed(2)}ms`);
            
            // 너무 느리면 품질 저하 고려
            if (loadTime > 500 && isMobileDevice()) {
                animation.setQuality('low');
            }
        });
        
        return animation;
        
    } catch (error) {
        // console.error("로티 애니메이션 초기화 중 오류:", error);
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

    // 로딩 화면 표시
    document.getElementById("loading-overlay").style.display = "flex";

    // 최적화된 Lottie 애니메이션 시도 (실패해도 계속 진행)
    try {
        let animationContainer = document.getElementById("lottie-container");
        let animationPath = animationContainer.getAttribute("data-animation");
        
        // 최적화된 로티 애니메이션 초기화
        animationContainer.lottieInstance = initOptimizedLottie(animationContainer, animationPath);
    } catch (error) {
        // console.warn("Lottie 애니메이션 로드 실패:", error);
        // 애니메이션 실패해도 계속 진행
    }

    // CSRF 토큰 가져오기
    const csrftoken = getCookie("csrftoken");
    if (!csrftoken) {
        // console.log("CSRF 토큰이 없습니다. 토큰을 가져온 후 다시 시도합니다.");
        fetchCSRFToken();
        setTimeout(() => {
            const retryToken = getCookie("csrftoken");
            if (retryToken) {
                // console.log("CSRF 토큰을 성공적으로 가져왔습니다. 요청을 계속합니다.");
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
        // console.log("서버 응답:", data);  

        let generatedResumeElement = document.getElementById("generated_resume");

        if (generatedResumeElement) {
            let resumeText = "자기소개서 생성에 실패했습니다."; // 기본값 설정
            
            // 상세 디버깅 로그 추가 (조건 분리 로깅)
            const hasData = !!data;
            const hasResumeKey = hasData && data.hasOwnProperty('resume');
            const resumeValue = hasResumeKey ? data.resume : undefined;
            const isString = typeof resumeValue === 'string';
            const trimmedValue = isString ? resumeValue.trim() : undefined;
            const trimmedLength = isString ? trimmedValue.length : undefined;
            const isLengthPositive = trimmedLength > 0;

            // console.log(`[Debug] Detailed Check:`, {
            //     hasData: hasData,
            //     hasResumeKey: hasResumeKey,
            //     resumeType: typeof resumeValue,
            //     isString: isString,
            //     resumeValueSnippet: isString ? resumeValue.substring(0, 100) + '...' : 'N/A',
            //     trimmedValueSnippet: isString ? trimmedValue.substring(0, 100) + '...' : 'N/A',
            //     trimmedLength: trimmedLength,
            //     isLengthPositive: isLengthPositive
            // });

            // data.resume가 존재하고, 비어있지 않은 문자열인지 명시적으로 확인
            if (hasData && hasResumeKey && isString && isLengthPositive) {
                resumeText = resumeValue;
                // console.log("[Debug] Condition passed. Using data.resume.");
            } else {
                // console.warn("[Debug] Condition failed. Using default failure message.");
                // console.warn("data.resume가 없거나 비어있습니다. 기본 실패 메시지를 사용합니다.");
            }
            
            const timestamp = new Date().toISOString();
            // console.log(`[${timestamp}] 자기소개서 생성 완료 및 DOM에 렌더링 시작. 길이: ${resumeText.length}자`);
            generatedResumeElement.value = resumeText;
            // console.log(`[${timestamp}] 자기소개서가 DOM에 렌더링 완료됨`);
            
            // 콘솔에 앞부분 미리보기 출력 (디버깅용)
            if (resumeText.length > 0) {
                // console.log(`자기소개서 미리보기 (앞부분 50자): ${resumeText.substring(0, 50)}...`);
            }
        } else {
            // console.error("generated_resume 요소를 찾을 수 없습니다.");
        }
    })
    .catch(error => {
        // console.error("에러 발생:", error);
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
            // console.warn("Lottie 애니메이션 종료 실패:", error);
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

/**
 * lottie 라이브러리가 로드되었는지 확인하는 함수
 * 정해진 시간 내에 로드되지 않으면 경고 출력
 */
function checkLottieLoaded() {
    let checkAttempts = 0;
    const maxAttempts = 10;
    
    const checkInterval = setInterval(() => {
        if (typeof lottie !== 'undefined') {
            // console.log('Lottie 라이브러리가 정상적으로 로드되었습니다.'); // 로그 삭제
            clearInterval(checkInterval);
            return;
        }
        
        checkAttempts++;
        if (checkAttempts >= maxAttempts) {
            // console.warn('Lottie 라이브러리 로드 실패. 애니메이션이 작동하지 않을 수 있습니다.');
            clearInterval(checkInterval);
        }
    }, 500); // 500ms 간격으로 확인
} 