#!/usr/bin/env python
"""
이미지 파일을 static 폴더에서 static_prod 폴더로 직접 복사하는 스크립트
이미지 파일의 투명도 문제를 해결하기 위한 가장 단순한 방법입니다.
"""
import os
import shutil
import glob
import sys

# 프로젝트 루트 디렉토리
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 원본 디렉토리와 대상 디렉토리
STATIC_DIR = os.path.join(BASE_DIR, 'static')
STATIC_PROD_DIR = os.path.join(BASE_DIR, 'static_prod')

print(f"BASE_DIR: {BASE_DIR}")
print(f"STATIC_DIR: {STATIC_DIR}")
print(f"STATIC_PROD_DIR: {STATIC_PROD_DIR}")
print(f"STATIC_DIR exists: {os.path.exists(STATIC_DIR)}")
print(f"STATIC_PROD_DIR exists: {os.path.exists(STATIC_PROD_DIR)}")

def copy_images():
    """이미지 파일을 static 폴더에서 static_prod 폴더로 직접 복사합니다."""
    print("=== 이미지 파일 복사 시작 ===")
    
    # 복사할 파일 목록 (복사하려는 모든 파일을 여기에 추가)
    image_files = [
        # 파비콘 파일
        'favicon-16x16.png',
        'favicon-32x32.png',
        'favicon.ico',
        'apple-touch-icon.png',
        'android-chrome-192x192.png',
        'android-chrome-512x512.png',
        # OG 및 트위터 카드 이미지
        'og-image.png',
        'twitter-card.png'
    ]
    
    try:
        # 삭제 부분은 건너뛰고 바로 복사 진행
        print("\n파일 복사 진행 중...")
        for filename in image_files:
            src_path = os.path.join(STATIC_DIR, filename)
            dst_path = os.path.join(STATIC_PROD_DIR, filename)
            
            print(f"  파일: {filename}")
            print(f"  소스 경로: {src_path}")
            print(f"  대상 경로: {dst_path}")
            print(f"  소스 존재: {os.path.exists(src_path)}")
            
            if os.path.exists(src_path):
                try:
                    shutil.copy2(src_path, dst_path)
                    print(f"  복사 완료: {filename}")
                except Exception as e:
                    print(f"  복사 실패: {filename} - {e}")
                    print(f"  오류 유형: {type(e)}")
            else:
                print(f"  원본 파일 없음: {filename}")
        
        print("\n=== 이미지 파일 복사 완료 ===")
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        copy_images()
    except Exception as e:
        print(f"치명적 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 