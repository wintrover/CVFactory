#!/usr/bin/env python
"""
이미지 파일을 static 폴더에서 static_prod 폴더로 직접 복사하는 스크립트
먼저 static_prod 디렉토리를 초기화하고, 투명도가 보존된 이미지를 복사합니다.
frontend 디렉토리의 이미지도 처리할 수 있는 옵션이 추가되었습니다.
"""
import os
import shutil
import sys
import argparse
from PIL import Image

# 프로젝트 루트 디렉토리
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 원본 디렉토리와 대상 디렉토리
STATIC_DIR = os.path.join(BASE_DIR, 'static')
STATIC_PROD_DIR = os.path.join(BASE_DIR, 'static_prod')
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')  # frontend 디렉토리 추가

# 이미지 목록 파일 경로
IMAGE_LIST_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'image_list.txt')

def clean_static_prod():
    """static_prod 디렉토리의 모든 내용을 삭제합니다."""
    print("=== static_prod 디렉토리 초기화 시작 ===")
    
    if not os.path.exists(STATIC_PROD_DIR):
        os.makedirs(STATIC_PROD_DIR)
        print("static_prod 디렉토리가 존재하지 않아 새로 생성했습니다.")
        return
    
    # django가 생성한 staticfiles.json은 유지해야 함
    staticfiles_json = os.path.join(STATIC_PROD_DIR, 'staticfiles.json')
    has_staticfiles_json = os.path.exists(staticfiles_json)
    
    if has_staticfiles_json:
        # staticfiles.json 파일 임시 저장
        temp_json_content = None
        try:
            with open(staticfiles_json, 'r', encoding='utf-8') as f:
                temp_json_content = f.read()
            print("staticfiles.json 파일 백업 완료")
        except Exception as e:
            print(f"staticfiles.json 파일 백업 실패: {e}")
    
    # 모든 파일 삭제
    for item in os.listdir(STATIC_PROD_DIR):
        item_path = os.path.join(STATIC_PROD_DIR, item)
        try:
            if os.path.isfile(item_path):
                os.unlink(item_path)
                print(f"파일 삭제: {item}")
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"디렉토리 삭제: {item}")
        except Exception as e:
            print(f"삭제 실패: {item} - {e}")
    
    # staticfiles.json 복원
    if has_staticfiles_json and temp_json_content:
        try:
            with open(staticfiles_json, 'w', encoding='utf-8') as f:
                f.write(temp_json_content)
            print("staticfiles.json 파일 복원 완료")
        except Exception as e:
            print(f"staticfiles.json 파일 복원 실패: {e}")
    
    print("=== static_prod 디렉토리 초기화 완료 ===")

def read_image_list():
    """이미지 목록 파일에서 복사할 파일 목록을 읽어옵니다."""
    if os.path.exists(IMAGE_LIST_FILE):
        with open(IMAGE_LIST_FILE, 'r', encoding='utf-8') as f:
            # 주석과 빈 줄 제외하고 각 줄을 이미지 파일 이름으로 사용
            return [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
    else:
        print(f"경고: 이미지 목록 파일({IMAGE_LIST_FILE})을 찾을 수 없습니다.")
        # 기본 이미지 목록 (파일이 없을 경우 대비)
        return [
            'favicon-16x16.png',
            'favicon-32x32.png',
            'favicon.ico',
            'apple-touch-icon.png',
            'android-chrome-192x192.png',
            'android-chrome-512x512.png',
            'og-image.png',
            'twitter-card.png'
        ]

def copy_images():
    """이미지 파일을 static 폴더에서 static_prod 폴더로 직접 복사합니다."""
    print("=== 이미지 파일 복사 시작 ===")
    
    # 이미지 목록 파일에서 복사할 파일 목록 읽기
    image_files = read_image_list()
    print(f"복사할 이미지 파일 수: {len(image_files)}")
    
    try:
        for filename in image_files:
            src_path = os.path.join(STATIC_DIR, filename)
            dst_path = os.path.join(STATIC_PROD_DIR, filename)
            
            # WebP 변환 대상인지 확인 (PNG 파일만)
            webp_dst_path = None
            if filename.lower().endswith('.png'):
                webp_dst_path = os.path.join(STATIC_PROD_DIR, os.path.splitext(filename)[0] + '.webp')
            
            print(f"  파일: {filename}")
            print(f"  소스 경로: {src_path}")
            print(f"  대상 경로: {dst_path}")
            
            if os.path.exists(src_path):
                try:
                    # 원본 파일 복사
                    shutil.copy2(src_path, dst_path)
                    print(f"  복사 완료: {filename}")
                    
                    # PNG 파일인 경우 WebP 버전도 생성 (투명도 유지)
                    if webp_dst_path:
                        try:
                            img = Image.open(src_path)
                            img.save(
                                webp_dst_path, 
                                format="WebP", 
                                lossless=True,  # 무손실 압축으로 투명도 보존
                                quality=100
                            )
                            print(f"  WebP 생성 완료: {os.path.basename(webp_dst_path)}")
                        except Exception as e:
                            print(f"  WebP 생성 실패: {filename} - {e}")
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

# 새로 추가: frontend 디렉토리의 WebP 생성 함수
def create_frontend_webp():
    """frontend 디렉토리의 PNG 파일에서 투명도가 보존된 WebP 파일을 생성합니다."""
    print("=== frontend 디렉토리 WebP 생성 시작 ===")
    
    # frontend 디렉토리의 PNG 파일 목록
    png_files = [
        "favicon-16x16.png",
        "favicon-32x32.png",
        "apple-touch-icon.png",
        "android-chrome-192x192.png",
        "android-chrome-512x512.png",
        "og-image.png",
        "twitter-card.png"
    ]
    
    for filename in png_files:
        src_path = os.path.join(FRONTEND_DIR, filename)
        webp_path = os.path.join(FRONTEND_DIR, os.path.splitext(filename)[0] + ".webp")
        
        print(f"  파일: {filename}")
        print(f"  PNG 경로: {src_path}")
        print(f"  WebP 경로: {webp_path}")
        
        if os.path.exists(src_path):
            try:
                # WebP 변환 (투명도 유지)
                img = Image.open(src_path)
                img.save(
                    webp_path, 
                    format="WebP", 
                    lossless=True,  # 무손실 압축으로 투명도 보존
                    quality=100
                )
                print(f"  WebP 생성 완료: {os.path.basename(webp_path)}")
            except Exception as e:
                print(f"  WebP 생성 실패: {filename} - {e}")
        else:
            print(f"  원본 파일 없음: {filename}")
    
    print("\n=== frontend 디렉토리 WebP 생성 완료 ===")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="정적 이미지 파일 처리 스크립트")
    parser.add_argument("--clean", action="store_true", help="static_prod 디렉토리 초기화")
    parser.add_argument("--frontend", action="store_true", help="frontend 디렉토리 WebP 생성")
    
    args = parser.parse_args()
    
    try:
        # frontend 모드
        if args.frontend:
            create_frontend_webp()
        else:
            # 기존 모드: static_prod 처리
            if args.clean:
                clean_static_prod()
            copy_images()
    except Exception as e:
        print(f"치명적 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 