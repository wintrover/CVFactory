#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
이미지 최적화 스크립트
- PNG 이미지 압축 및 WebP 변환
- 모든 이미지 파일에 대해 압축 작업 수행
- 원본 대비 압축 비율 출력
"""

import os
import sys
from pathlib import Path
from PIL import Image, ImageOps
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 기본 설정
QUALITY = 85  # WebP 및 JPEG 품질 (0-100)
PNG_OPTIMIZE = True  # PNG 최적화 옵션

# 무시할 파일 목록
IGNORE_FILES = ['.DS_Store', 'Thumbs.db']


def get_size_format(b, factor=1024, suffix="B"):
    """
    파일 크기를 사람이 읽기 쉬운 형식으로 변환합니다.
    """
    for unit in ["", "K", "M", "G", "T"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}P{suffix}"


def optimize_image(input_path, output_dir=None, quality=QUALITY, webp=True):
    """
    이미지 파일을 최적화하고 WebP 버전도 생성합니다.
    """
    try:
        # 입출력 경로 설정
        img_path = Path(input_path)
        img_name = img_path.stem
        img_ext = img_path.suffix.lower()
        
        # 출력 디렉토리가 없으면 원본과 동일한 디렉토리 사용
        output_dir = output_dir or img_path.parent
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 원본 파일 크기
        original_size = os.path.getsize(input_path)
        
        # 이미지 열기
        with Image.open(input_path) as img:
            # 원본 이미지 최적화
            if img_ext in ['.png']:
                # PNG 최적화
                optimized_output = output_dir / f"{img_name}{img_ext}"
                img.save(optimized_output, optimize=PNG_OPTIMIZE, format="PNG")
            elif img_ext in ['.jpg', '.jpeg']:
                # JPEG 최적화
                optimized_output = output_dir / f"{img_name}{img_ext}"
                img.save(optimized_output, quality=quality, optimize=True, format="JPEG")
            else:
                # 기타 이미지 형식
                optimized_output = output_dir / f"{img_name}{img_ext}"
                img.save(optimized_output)
            
            # WebP 버전 생성
            if webp:
                webp_output = output_dir / f"{img_name}.webp"
                img.save(webp_output, quality=quality, format="WEBP")
        
        # 최적화된 이미지 크기
        optimized_size = os.path.getsize(optimized_output)
        compression = 100 - (optimized_size / original_size * 100)
        
        # 로그 출력
        logger.info(f"최적화 완료: {input_path}")
        logger.info(f"  원본 크기: {get_size_format(original_size)}")
        logger.info(f"  최적화 크기: {get_size_format(optimized_size)}")
        logger.info(f"  압축률: {compression:.1f}%")
        
        if webp:
            webp_size = os.path.getsize(webp_output)
            webp_compression = 100 - (webp_size / original_size * 100)
            logger.info(f"  WebP 크기: {get_size_format(webp_size)}")
            logger.info(f"  WebP 압축률: {webp_compression:.1f}%")
        
        return {
            "status": "success",
            "original": input_path,
            "optimized": str(optimized_output),
            "webp": str(webp_output) if webp else None,
            "original_size": original_size,
            "optimized_size": optimized_size,
            "compression": compression,
            "webp_size": webp_size if webp else None,
            "webp_compression": webp_compression if webp else None
        }
    
    except Exception as e:
        logger.error(f"이미지 최적화 실패: {input_path} - {str(e)}")
        return {
            "status": "error",
            "original": input_path,
            "error": str(e)
        }


def process_directory(input_dir, output_dir=None, quality=QUALITY, webp=True):
    """
    디렉토리 내 모든 이미지 파일을 처리합니다.
    """
    input_dir = Path(input_dir)
    output_dir = output_dir or input_dir
    output_dir = Path(output_dir)
    
    # 통계 변수
    total_original = 0
    total_optimized = 0
    total_webp = 0
    file_count = 0
    error_count = 0
    
    # 이미지 확장자 목록
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    
    logger.info(f"디렉토리 처리 시작: {input_dir}")
    
    # 모든 이미지 파일 찾기
    for img_path in input_dir.glob('**/*'):
        if img_path.is_file() and img_path.suffix.lower() in image_extensions:
            if img_path.name in IGNORE_FILES:
                continue
            
            # 이미지 최적화
            result = optimize_image(img_path, output_dir, quality, webp)
            
            if result["status"] == "success":
                file_count += 1
                total_original += result["original_size"]
                total_optimized += result["optimized_size"]
                if webp and result["webp_size"]:
                    total_webp += result["webp_size"]
            else:
                error_count += 1
    
    # 최종 통계 출력
    if file_count > 0:
        total_compression = 100 - (total_optimized / total_original * 100)
        total_webp_compression = 100 - (total_webp / total_original * 100) if total_webp > 0 else 0
        
        logger.info(f"처리 완료: {file_count}개 파일 ({error_count}개 오류)")
        logger.info(f"총 원본 크기: {get_size_format(total_original)}")
        logger.info(f"총 최적화 크기: {get_size_format(total_optimized)}")
        logger.info(f"총 압축률: {total_compression:.1f}%")
        
        if webp:
            logger.info(f"총 WebP 크기: {get_size_format(total_webp)}")
            logger.info(f"총 WebP 압축률: {total_webp_compression:.1f}%")
    else:
        logger.warning(f"처리된 이미지 파일이 없습니다.")
    
    return {
        "file_count": file_count,
        "error_count": error_count,
        "total_original": total_original,
        "total_optimized": total_optimized,
        "total_webp": total_webp,
    }


def main():
    """
    메인 함수 - 커맨드라인 인터페이스 제공
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='이미지 최적화 도구')
    parser.add_argument('input', help='입력 이미지 또는 디렉토리 경로')
    parser.add_argument('-o', '--output', help='출력 디렉토리 경로 (기본값: 입력과 동일)')
    parser.add_argument('-q', '--quality', type=int, default=QUALITY, help=f'이미지 품질 (0-100, 기본값: {QUALITY})')
    parser.add_argument('--no-webp', action='store_true', help='WebP 변환을 건너뜁니다')
    
    args = parser.parse_args()
    
    # 입력이 디렉토리인지 파일인지 확인
    input_path = Path(args.input)
    if input_path.is_dir():
        # 디렉토리 처리
        process_directory(input_path, args.output, args.quality, not args.no_webp)
    elif input_path.is_file():
        # 단일 파일 처리
        optimize_image(input_path, args.output, args.quality, not args.no_webp)
    else:
        logger.error(f"입력 경로가 존재하지 않습니다: {args.input}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 