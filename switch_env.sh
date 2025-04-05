#!/bin/bash

# 환경 전환 스크립트
# 사용법: ./switch_env.sh [development|production]

# 기본 환경은 development
ENV=${1:-development}

if [ "$ENV" != "development" ] && [ "$ENV" != "production" ]; then
    echo "사용법: ./switch_env.sh [development|production]"
    exit 1
fi

echo "환경을 $ENV 모드로 전환합니다..."

# .env 파일 백업
if [ -f .env ]; then
    echo "기존 .env 파일 백업 중..."
    cp .env .env.bak
fi

# 환경별 설정 파일 복사
echo ".env.$ENV 파일을 .env로 복사 중..."
cp .env.$ENV .env

# 환경 전환 완료 메시지
echo "완료! 이제 $ENV 환경에서 실행됩니다."
echo "주의: 실제 API 키는 직접 .env 파일에 입력해야 합니다." 