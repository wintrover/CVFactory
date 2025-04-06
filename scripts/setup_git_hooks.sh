#!/bin/bash

# scripts 디렉토리 생성 (이미 생성되어 있을 수 있음)
mkdir -p scripts

# .git/hooks 디렉토리 확인
if [ ! -d .git/hooks ]; then
  echo "'.git/hooks' 디렉토리가 존재하지 않습니다. Git 저장소가 초기화되어 있는지 확인하세요."
  echo "Git 저장소 초기화: git init"
  exit 1
fi

# pre-commit 훅에 실행 권한 부여
chmod +x scripts/pre-commit

# pre-commit 훅 설치
cp scripts/pre-commit .git/hooks/
echo "✅ Git pre-commit 훅이 설치되었습니다."

# 설치 확인
if [ -f .git/hooks/pre-commit ]; then
  echo "✅ 훅 설치 확인 완료: .git/hooks/pre-commit"
else
  echo "❌ 훅 설치 실패. 수동으로 scripts/pre-commit 파일을 .git/hooks/ 디렉토리로 복사하세요."
fi

echo "민감한 정보 보호를 위한 Git 훅 설정이 완료되었습니다."
echo "이제 .env 파일이나 민감한 API 키가 실수로 커밋되는 것을 방지합니다." 