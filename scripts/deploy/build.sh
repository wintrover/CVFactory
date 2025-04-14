#!/usr/bin/env bash
# 오류 발생 시 스크립트 종료
set -o errexit

echo "빌드 스크립트 시작..."

# 파이썬 버전 확인
python --version

# 종속성 설치
echo "종속성 설치 중..."
pip install -r requirements.txt

# 폰트 폴더 생성
echo "폰트 디렉토리 준비 중..."
mkdir -p static/fonts
mkdir -p static_prod/fonts

# 정적 파일 수집
echo "정적 파일 수집 중..."
python manage.py collectstatic --no-input

# 데이터베이스 마이그레이션
echo "데이터베이스 마이그레이션 실행 중..."
python manage.py migrate --no-input

# 필요한 디렉토리 생성
echo "디렉토리 생성 중..."
mkdir -p logs static_dev frontend static_prod

# settings.py 파일 수정 (manifest_strict 설정)
echo "STATICFILES_MANIFEST_STRICT = False 설정 확인 중..."
grep -q "STATICFILES_MANIFEST_STRICT = False" cvfactory/settings.py || echo "STATICFILES_MANIFEST_STRICT = False" >> cvfactory/settings.py

echo "빌드 완료!" 