#!/usr/bin/env python
"""
하나의 파비콘 파일만 복사하는 간단한 스크립트
"""
import os
import shutil
import sys

# 복사할 파일 지정
if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    filename = "android-chrome-192x192.png"  # 기본값

# 프로젝트 루트 디렉토리
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 원본 디렉토리와 대상 디렉토리
STATIC_DIR = os.path.join(BASE_DIR, 'static')
STATIC_PROD_DIR = os.path.join(BASE_DIR, 'static_prod')

src_path = os.path.join(STATIC_DIR, filename)
dst_path = os.path.join(STATIC_PROD_DIR, filename)

print(f"복사: {filename}")
print(f"소스: {src_path}")
print(f"대상: {dst_path}")

if os.path.exists(src_path):
    try:
        shutil.copy2(src_path, dst_path)
        print(f"복사 완료: {filename}")
    except Exception as e:
        print(f"복사 실패: {e}")
else:
    print(f"원본 파일이 존재하지 않습니다: {src_path}") 