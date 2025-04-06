#!/bin/bash

# 환경 전환 스크립트
# 사용법: ./switch_env.sh [development|production|local]

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 기본 환경은 development
ENV=${1:-development}

if [ "$ENV" != "development" ] && [ "$ENV" != "production" ] && [ "$ENV" != "local" ]; then
    echo -e "${RED}사용법: ./switch_env.sh [development|production|local]${NC}"
    echo "  development: 개발 환경 (DEBUG=True, 로컬 설정)"
    echo "  production: 배포 환경 (DEBUG=False, 보안 설정 활성화)"
    echo "  local: 로컬 개발 환경 (현재 .env 파일 유지, API 키만 업데이트)"
    exit 1
fi

echo -e "${BLUE}환경을 $ENV 모드로 전환합니다...${NC}"

# 필요한 환경 파일 확인 및 생성
if [ "$ENV" != "local" ] && [ ! -f .env.$ENV ]; then
    echo -e "${YELLOW}경고: .env.$ENV 파일이 없습니다. .env.example에서 생성합니다.${NC}"
    
    if [ ! -f .env.example ]; then
        echo -e "${RED}오류: .env.example 파일도 없습니다. 먼저 .env.example 파일을 생성해주세요.${NC}"
        exit 1
    fi
    
    cp .env.example .env.$ENV
    
    # 개발/배포 환경에 따라 기본값 설정
    if [ "$ENV" = "development" ]; then
        sed -i.bak 's/DEBUG=False/DEBUG=True/g' .env.$ENV
        sed -i.bak 's/ALLOWED_HOSTS=.*/ALLOWED_HOSTS=localhost,127.0.0.1/g' .env.$ENV
        rm -f .env.$ENV.bak
    elif [ "$ENV" = "production" ]; then
        sed -i.bak 's/DEBUG=True/DEBUG=False/g' .env.$ENV
        sed -i.bak 's/CSRF_COOKIE_SECURE=False/CSRF_COOKIE_SECURE=True/g' .env.$ENV
        sed -i.bak 's/SESSION_COOKIE_SECURE=False/SESSION_COOKIE_SECURE=True/g' .env.$ENV
        rm -f .env.$ENV.bak
    fi
    
    echo -e "${GREEN}.env.$ENV 파일이 생성되었습니다. API 키와 비밀 정보를 직접 입력해주세요.${NC}"
fi

# API 키 추출 함수
extract_api_keys() {
    local env_file=$1
    local output_file=$2
    
    # API 키와 민감한 정보를 추출하여 임시 파일에 저장
    grep -E "API_KEY|SECRET|TOKEN|PASSWORD|CLIENT_ID|CLIENT_SECRET" $env_file > $output_file
}

# local 모드가 아닌 경우에만 환경 파일 전환
if [ "$ENV" != "local" ]; then
    # .env 파일 백업
    if [ -f .env ]; then
        BACKUP_FILE=".env.backup.$(date +%Y%m%d%H%M%S)"
        echo -e "${BLUE}기존 .env 파일을 $BACKUP_FILE으로 백업합니다...${NC}"
        cp .env $BACKUP_FILE
        
        # 기존 환경에서 API 키 추출
        API_KEYS_FILE=".env.api_keys.tmp"
        extract_api_keys .env $API_KEYS_FILE
    fi
    
    # 환경별 설정 파일 복사
    echo -e "${BLUE}.env.$ENV 파일을 .env로 복사합니다...${NC}"
    cp .env.$ENV .env
    
    # API 키 복원 (기존 키가 있는 경우)
    if [ -f $API_KEYS_FILE ]; then
        echo -e "${BLUE}API 키와 민감한 정보를 복원합니다...${NC}"
        while IFS= read -r line; do
            key=$(echo $line | cut -d= -f1)
            # .env 파일에서 같은 키를 가진 줄을 찾아 바꿈
            sed -i.bak "s/^$key=.*/$line/g" .env
        done < $API_KEYS_FILE
        
        # 임시 파일 삭제
        rm -f $API_KEYS_FILE
        rm -f .env.bak
    fi
else
    echo -e "${GREEN}로컬 모드: 현재 .env 파일을 유지합니다.${NC}"
    
    # DEBUG 모드 활성화 
    sed -i.bak 's/DEBUG=False/DEBUG=True/g' .env
    rm -f .env.bak
    
    echo -e "${YELLOW}주의: DEBUG=True로 설정되었습니다. 개발 목적으로만 사용하세요.${NC}"
fi

# 환경 전환 완료 메시지
echo -e "${GREEN}완료! 이제 $ENV 환경에서 실행됩니다.${NC}"

# 현재 환경 설정 요약 출력
echo -e "${BLUE}현재 환경 설정 요약:${NC}"
grep -E "DEBUG=|ALLOWED_HOSTS=|CORS_" .env | sort

echo -e "${YELLOW}주의: 실제 API 키는 보안을 위해 출력하지 않습니다.${NC}"

# 서버 재시작 안내
echo -e "${BLUE}변경사항을 적용하려면 서버를 재시작하세요:${NC}"
echo "  python manage.py runserver" 