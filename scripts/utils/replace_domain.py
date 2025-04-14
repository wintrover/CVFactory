#!/usr/bin/env python
"""
CVFactory 프로젝트 내의 모든 파일에서 cvfactory.dev을 cvfactory.dev로 변경하는 스크립트
"""

import os
import re
from pathlib import Path

def replace_in_file(file_path, old_domain, new_domain):
    """파일 내의 도메인을 변경하는 함수"""
    # 파일 확장자 확인
    if not file_path.endswith(('.html', '.js', '.py', '.xml', '.json', '.yml', '.yaml', '.txt', '.md', '.css')):
        return False
    
    try:
        # 파일 읽기
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
        
        # 도메인 변경
        if old_domain in content:
            new_content = content.replace(old_domain, new_domain)
            
            # 변경된 내용으로 파일 쓰기
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            
            return True
        
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """메인 함수"""
    root_dir = Path(__file__).parent.parent.parent
    old_domain = "cvfactory.dev"
    new_domain = "cvfactory.dev"
    
    count = 0
    skipped = 0
    
    # 프로젝트 디렉토리 순회
    for root, _, files in os.walk(root_dir):
        for file in files:
            file_path = os.path.join(root, file)
            
            # .git 디렉토리 제외
            if '.git' in file_path:
                continue
            
            # 파일 내 도메인 변경
            result = replace_in_file(file_path, old_domain, new_domain)
            
            if result:
                count += 1
                print(f"Updated: {file_path}")
            else:
                skipped += 1
    
    print(f"\n처리 완료: {count}개 파일을 업데이트했습니다. {skipped}개 파일은 건너뛰었습니다.")

if __name__ == "__main__":
    main() 