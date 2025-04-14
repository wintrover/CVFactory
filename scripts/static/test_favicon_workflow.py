#!/usr/bin/env python
"""
파비콘 생성 및 처리 워크플로우 테스트 스크립트
"""
import os
import sys
import subprocess
import glob
import shutil
from pathlib import Path
import time

# 프로젝트 루트 디렉토리 확인
BASE_DIR = Path(__file__).resolve().parent.parent.parent

def run_fix_favicon():
    """fix_favicon.py 스크립트 실행"""
    print("=== 1. fix_favicon.py 실행 ===")
    
    favicon_script = os.path.join(BASE_DIR, 'scripts', 'static', 'fix_favicon.py')
    try:
        result = subprocess.run(['python', favicon_script], check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except Exception as e:
        print(f"오류 발생: {e}")
        return False

def run_collectstatic():
    """collectstatic 명령 실행"""
    print("\n=== 2. collectstatic 명령 실행 ===")
    
    try:
        # Django 설정 모듈 로드
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cvfactory.settings")
        
        # collectstatic 명령 실행
        result = subprocess.run(['python', 'manage.py', 'collectstatic', '--noinput'], 
                             check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except Exception as e:
        print(f"오류 발생: {e}")
        return False

def copy_favicon_files():
    """파비콘 파일들을 static_prod 디렉토리로 직접 복사"""
    print("\n=== 3. 파비콘 파일 직접 복사 ===")
    
    # 원본 디렉토리와 대상 디렉토리
    static_dir = os.path.join(BASE_DIR, 'static')
    static_prod_dir = os.path.join(BASE_DIR, 'static_prod')
    
    # 파비콘 파일들 (PNG 및 WebP 파일 모두 포함)
    favicon_files = [
        'favicon-16x16.png',
        'favicon-32x32.png',
        'favicon.ico',
        'apple-touch-icon.png',
        'android-chrome-192x192.png',
        'android-chrome-512x512.png',
        'favicon-16x16.webp',
        'favicon-32x32.webp',
        'apple-touch-icon.webp',
        'android-chrome-192x192.webp',
        'android-chrome-512x512.webp'
    ]
    
    # 기존 해시된 파비콘 파일 삭제
    patterns = [
        'favicon*.png', 
        'favicon*.webp',
        'favicon.ico', 
        'android-chrome*.png', 
        'android-chrome*.webp',
        'apple-touch-icon*.png',
        'apple-touch-icon*.webp'
    ]
    
    for pattern in patterns:
        search_pattern = os.path.join(static_prod_dir, pattern)
        for file_path in glob.glob(search_pattern):
            try:
                os.remove(file_path)
                print(f"삭제됨: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"삭제 실패: {os.path.basename(file_path)} - {e}")
    
    # 파일 복사
    for filename in favicon_files:
        src_path = os.path.join(static_dir, filename)
        dst_path = os.path.join(static_prod_dir, filename)
        
        if os.path.exists(src_path):
            try:
                shutil.copy2(src_path, dst_path)
                print(f"복사 완료: {filename}")
            except Exception as e:
                print(f"복사 실패: {filename} - {e}")
        else:
            print(f"원본 파일 없음: {filename}")

def check_transparency():
    """파비콘 이미지의 투명도 확인"""
    print("\n=== 4. 파비콘 투명도 확인 ===")
    
    try:
        # check_transparency.py 스크립트 실행
        transparency_script = os.path.join(BASE_DIR, 'scripts', 'static', 'check_transparency.py')
        result = subprocess.run(['python', transparency_script], check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except Exception as e:
        print(f"오류 발생: {e}")
        return False

def main():
    """전체 워크플로우 실행"""
    print("파비콘 생성 및 처리 워크플로우 테스트 시작...\n")
    
    # 1. fix_favicon.py 실행
    if not run_fix_favicon():
        print("파비콘 생성 실패, 워크플로우 중단")
        return False
    
    # 2. collectstatic 명령 실행
    if not run_collectstatic():
        print("collectstatic 실행 실패, 워크플로우 중단")
        return False
    
    # 3. 파비콘 파일 직접 복사
    copy_favicon_files()
    
    # 4. 투명도 확인
    check_transparency()
    
    print("\n워크플로우 테스트 완료!")
    return True

if __name__ == '__main__':
    success = main()
    if not success:
        sys.exit(1) 