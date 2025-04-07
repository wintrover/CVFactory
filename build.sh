#!/usr/bin/env bash
# 오류 발생 시 스크립트 종료
set -o errexit

# 파이썬 의존성 설치
pip install -r requirements.txt

# 정적 파일 수집
python manage.py collectstatic --no-input

# 데이터베이스 마이그레이션
python manage.py migrate 