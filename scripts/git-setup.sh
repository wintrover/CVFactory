#!/bin/bash

# Git 훅 디렉토리 설정
if [ ! -d .git/hooks ]; then
  echo "'.git/hooks' 디렉토리가 존재하지 않습니다. Git 저장소가 초기화되어 있는지 확인하세요."
  echo "Git 저장소 초기화: git init"
  exit 1
fi

# pre-commit 훅 내용 생성
cat > .git/hooks/pre-commit << 'EOL'
#!/bin/bash

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
EOL

# pre-commit 훅에 실행 권한 부여
chmod +x .git/hooks/pre-commit

echo "✅ Git 보안 설정이 완료되었습니다."
echo "이제 .env 파일이나 민감한 API 키가 실수로 커밋되는 것을 방지합니다." 