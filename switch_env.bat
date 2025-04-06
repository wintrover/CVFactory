@echo off
setlocal enabledelayedexpansion

:: 환경 전환 스크립트 - Windows 버전
:: 사용법: switch_env.bat [development|production|local]

:: 색상 정의
set RED=[91m
set GREEN=[92m
set YELLOW=[93m
set BLUE=[94m
set NC=[0m

:: 기본 환경은 development
set ENV=%1
if "%ENV%"=="" set ENV=development

if "%ENV%" NEQ "development" if "%ENV%" NEQ "production" if "%ENV%" NEQ "local" (
    echo %RED%사용법: switch_env.bat [development^|production^|local]%NC%
    echo   development: 개발 환경 ^(DEBUG=True, 로컬 설정^)
    echo   production: 배포 환경 ^(DEBUG=False, 보안 설정 활성화^)
    echo   local: 로컬 개발 환경 ^(현재 .env 파일 유지, API 키만 업데이트^)
    exit /b 1
)

echo %BLUE%환경을 %ENV% 모드로 전환합니다...%NC%

:: 필요한 환경 파일 확인 및 생성
if "%ENV%" NEQ "local" (
    if not exist .env.%ENV% (
        echo %YELLOW%경고: .env.%ENV% 파일이 없습니다. .env.example에서 생성합니다.%NC%
        
        if not exist .env.example (
            echo %RED%오류: .env.example 파일도 없습니다. 먼저 .env.example 파일을 생성해주세요.%NC%
            exit /b 1
        )
        
        copy .env.example .env.%ENV% > nul
        
        :: 개발/배포 환경에 따라 기본값 설정
        if "%ENV%"=="development" (
            powershell -Command "(Get-Content .env.%ENV%) -replace 'DEBUG=False', 'DEBUG=True' | Set-Content .env.%ENV%"
            powershell -Command "(Get-Content .env.%ENV%) -replace 'ALLOWED_HOSTS=.*', 'ALLOWED_HOSTS=localhost,127.0.0.1' | Set-Content .env.%ENV%"
        ) else if "%ENV%"=="production" (
            powershell -Command "(Get-Content .env.%ENV%) -replace 'DEBUG=True', 'DEBUG=False' | Set-Content .env.%ENV%"
            powershell -Command "(Get-Content .env.%ENV%) -replace 'CSRF_COOKIE_SECURE=False', 'CSRF_COOKIE_SECURE=True' | Set-Content .env.%ENV%"
            powershell -Command "(Get-Content .env.%ENV%) -replace 'SESSION_COOKIE_SECURE=False', 'SESSION_COOKIE_SECURE=True' | Set-Content .env.%ENV%"
        )
        
        echo %GREEN%.env.%ENV% 파일이 생성되었습니다. API 키와 비밀 정보를 직접 입력해주세요.%NC%
    )
)

:: 임시 파일 생성 및 API 키 추출 함수
if "%ENV%" NEQ "local" (
    :: .env 파일 백업
    if exist .env (
        set BACKUP_FILE=.env.backup.%DATE:~0,4%%DATE:~5,2%%DATE:~8,2%%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%
        set BACKUP_FILE=!BACKUP_FILE: =0!
        echo %BLUE%기존 .env 파일을 !BACKUP_FILE!으로 백업합니다...%NC%
        copy .env !BACKUP_FILE! > nul
        
        :: 기존 환경에서 API 키 추출
        set API_KEYS_FILE=.env.api_keys.tmp
        powershell -Command "Get-Content .env | Select-String -Pattern 'API_KEY|SECRET|TOKEN|PASSWORD|CLIENT_ID|CLIENT_SECRET' | Out-File -FilePath %API_KEYS_FILE%"
    )
    
    :: 환경별 설정 파일 복사
    echo %BLUE%.env.%ENV% 파일을 .env로 복사합니다...%NC%
    copy .env.%ENV% .env > nul
    
    :: API 키 복원 (기존 키가 있는 경우)
    if exist %API_KEYS_FILE% (
        echo %BLUE%API 키와 민감한 정보를 복원합니다...%NC%
        for /f "tokens=*" %%A in (%API_KEYS_FILE%) do (
            for /f "tokens=1,* delims==" %%B in ("%%A") do (
                powershell -Command "(Get-Content .env) -replace '^%%B=.*', '%%A' | Set-Content .env"
            )
        )
        
        :: 임시 파일 삭제
        del %API_KEYS_FILE%
    )
) else (
    echo %GREEN%로컬 모드: 현재 .env 파일을 유지합니다.%NC%
    
    :: DEBUG 모드 활성화 
    powershell -Command "(Get-Content .env) -replace 'DEBUG=False', 'DEBUG=True' | Set-Content .env"
    
    echo %YELLOW%주의: DEBUG=True로 설정되었습니다. 개발 목적으로만 사용하세요.%NC%
)

:: 환경 전환 완료 메시지
echo %GREEN%완료! 이제 %ENV% 환경에서 실행됩니다.%NC%

:: 현재 환경 설정 요약 출력
echo %BLUE%현재 환경 설정 요약:%NC%
powershell -Command "Get-Content .env | Select-String -Pattern 'DEBUG=|ALLOWED_HOSTS=|CORS_' | Sort-Object"

echo %YELLOW%주의: 실제 API 키는 보안을 위해 출력하지 않습니다.%NC%

:: 서버 재시작 안내
echo %BLUE%변경사항을 적용하려면 서버를 재시작하세요:%NC%
echo   python manage.py runserver

endlocal 