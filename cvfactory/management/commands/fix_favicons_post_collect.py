from django.core.management.base import BaseCommand
import os
import shutil
from pathlib import Path
import glob
import sys
from django.conf import settings

class Command(BaseCommand):
    help = 'collectstatic 실행 후 투명도가 보존된 파비콘 파일을 static_prod 디렉토리로 직접 복사합니다'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('collectstatic 이후 파비콘 파일 수정 작업 시작...'))
        
        # 기본 디렉토리 설정
        base_dir = settings.BASE_DIR
        static_dir = os.path.join(base_dir, 'static')
        static_prod_dir = settings.STATIC_ROOT
        
        if not os.path.exists(static_dir) or not os.path.exists(static_prod_dir):
            self.stdout.write(self.style.ERROR(f'오류: 필요한 디렉토리를 찾을 수 없습니다.'))
            return
        
        # 기존 해시된 파일들 삭제
        favicon_patterns = [
            'favicon*.png', 
            'favicon.ico', 
            'android-chrome*.png', 
            'apple-touch-icon*.png'
        ]
        
        # 각 패턴에 맞는 파일 삭제
        for pattern in favicon_patterns:
            search_pattern = os.path.join(static_prod_dir, pattern)
            matching_files = glob.glob(search_pattern)
            
            for file_path in matching_files:
                try:
                    os.remove(file_path)
                    self.stdout.write(f'삭제됨: {os.path.basename(file_path)}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'삭제 실패: {os.path.basename(file_path)} - {e}'))
        
        # 파비콘 파일 목록
        favicon_files = [
            'favicon-16x16.png',
            'favicon-32x32.png',
            'favicon.ico',
            'apple-touch-icon.png',
            'android-chrome-192x192.png',
            'android-chrome-512x512.png'
        ]
        
        # 파일 직접 복사
        for filename in favicon_files:
            src_path = os.path.join(static_dir, filename)
            dst_path = os.path.join(static_prod_dir, filename)
            
            if os.path.exists(src_path):
                try:
                    shutil.copy2(src_path, dst_path)
                    self.stdout.write(f'복사 완료: {filename}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'복사 실패: {filename} - {e}'))
            else:
                self.stdout.write(self.style.WARNING(f'원본 파일 없음: {filename}'))
        
        self.stdout.write(self.style.SUCCESS('처리 완료: 투명도가 보존된 파비콘 파일이 static_prod 디렉토리에 복사되었습니다.')) 