# 프로젝트 루트 디렉토리 확인
$projectRoot = git rev-parse --show-toplevel 2>$null
if (-not $projectRoot) {
    Write-Host "❌ 오류: Git 저장소를 찾을 수 없습니다." -ForegroundColor Red
    Write-Host "이 스크립트는 Git 저장소의 루트 디렉토리에서 실행해야 합니다." -ForegroundColor Yellow
    exit 1
}

# Git Bash 확인
$gitBashPath = (Get-Command "git").Source -replace "cmd\\git\.exe$", "bin\bash.exe"
if (-not (Test-Path $gitBashPath)) {
    Write-Host "❌ 오류: Git Bash를 찾을 수 없습니다." -ForegroundColor Red
    Write-Host "Git for Windows가 올바르게 설치되어 있는지 확인하세요." -ForegroundColor Yellow
    exit 1
}

# Git 훅 디렉토리 설정
$hooksDir = Join-Path $projectRoot ".git\hooks"
if (-not (Test-Path $hooksDir)) {
    Write-Host "'.git/hooks' 디렉토리가 존재하지 않습니다. Git 저장소가 초기화되어 있는지 확인하세요." -ForegroundColor Red
    Write-Host "Git 저장소 초기화: git init" -ForegroundColor Yellow
    exit 1
}

# pre-commit 훅 내용 생성
$preCommitContent = @'
#!/bin/sh

# Git이 설치된 디렉토리 찾기
GIT_DIR=$(dirname $(dirname $(which git)))

# 필수 명령어 확인
if ! command -v grep >/dev/null 2>&1; then
    if [ -f "$GIT_DIR/usr/bin/grep" ]; then
        PATH="$GIT_DIR/usr/bin:$PATH"
    else
        echo "❌ 오류: grep 명령어를 찾을 수 없습니다."
        exit 1
    fi
fi

# 민감한 파일 체크
echo "🔍 민감한 파일 검사중..."

# .env 파일 체크
if git diff --cached --name-only | grep -E "\.env$" | grep -v ".env.example"; then
    echo "❌ 오류: .env 파일이 커밋되려고 합니다."
    exit 1
fi

# 민감한 토큰과 키 체크
SENSITIVE_PATTERNS=(
    "api[-_]?key['\"]?\s*[:=]\s*['\"]?[A-Za-z0-9_]+"
    "secret['\"]?\s*[:=]\s*['\"]?[A-Za-z0-9_]+"
    "password['\"]?\s*[:=]\s*['\"]?[A-Za-z0-9_]+"
    "token['\"]?\s*[:=]\s*['\"]?[A-Za-z0-9_.]+"
    "client[-_]?(id|secret)['\"]?\s*[:=]\s*['\"]?[A-Za-z0-9_-]+"
)

CHECK_FILES=$(git diff --cached --name-only | grep -E "\.(py|js|json|yml|yaml|sh|txt|ini|env|example)$")

for FILE in $CHECK_FILES; do
    if [ -f "$FILE" ]; then
        for PATTERN in "${SENSITIVE_PATTERNS[@]}"; do
            if git diff --cached "$FILE" | grep -E "$PATTERN" | grep -v "EXAMPLE|YOUR_|PLACEHOLDER"; then
                echo "❌ 오류: $FILE 파일에 민감한 정보가 포함되어 있습니다."
                exit 1
            fi
        done
    fi
done

echo "✅ 민감한 정보 검사 통과"
exit 0
'@

# pre-commit 훅 파일 생성 (UTF-8 without BOM으로 저장)
$preCommitPath = Join-Path $hooksDir "pre-commit"
[System.IO.File]::WriteAllText($preCommitPath, $preCommitContent, [System.Text.UTF8Encoding]::new($false))

Write-Host "✅ Git 보안 설정이 완료되었습니다." -ForegroundColor Green
Write-Host "이제 .env 파일이나 민감한 API 키가 실수로 커밋되는 것을 방지합니다." -ForegroundColor Green 