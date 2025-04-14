#!/usr/bin/env python
"""
staticfiles.json 파일 내용을 확인하는 스크립트
특정 파일의 매핑 상태를 확인합니다.
"""
import os
import json
import sys

# 프로젝트 루트 디렉토리
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_staticfiles_json():
    manifest_path = os.path.join(BASE_DIR, 'static_prod', 'staticfiles.json')
    if not os.path.exists(manifest_path):
        print('staticfiles.json 파일이 존재하지 않습니다.')
        return
    
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    paths = manifest.get('paths', {})
    
    # 패턴별로 확인할 파일 목록
    patterns = [
        'favicon*.png',
        'favicon.ico',
        'android-chrome*.png',
        'apple-touch-icon*.png',
        'og-image*.png',
        'og-image*.webp',
        'twitter-card*.png',
        'twitter-card*.webp',
    ]
    
    # 패턴에 맞는 파일 찾기
    interesting_files = []
    for key in paths.keys():
        filename = os.path.basename(key)
        for pattern in patterns:
            if pattern.replace('*', '') in filename:
                interesting_files.append(key)
                break
    
    # 매핑된 파일 정보 출력
    print('=== staticfiles.json 파일 분석 ===')
    print(f'총 {len(paths)} 개의 파일 매핑이 존재합니다.')
    print(f'관심 있는 파일 수: {len(interesting_files)}')
    print('\n=== 관심 있는 파일의 매핑 정보 ===')
    
    for key in sorted(interesting_files):
        value = paths[key]
        print(f'"{key}" -> "{value}"')
    
if __name__ == '__main__':
    check_staticfiles_json() 