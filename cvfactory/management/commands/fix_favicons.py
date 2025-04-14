from django.core.management.base import BaseCommand
import os
import sys
from pathlib import Path
from django.conf import settings

class Command(BaseCommand):
    help = '파비콘 이미지의 투명도를 보존하며 static_prod 디렉토리에 복사합니다'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('파비콘 이미지 복원 작업 시작...'))
        
        # BASE_DIR를 Django 설정에서 가져옴
        base_dir = settings.BASE_DIR
        
        # 프로젝트 루트 디렉토리에 있는 스크립트 실행
        script_path = os.path.join(base_dir, 'fix_favicon.py')
        
        if not os.path.exists(script_path):
            self.stdout.write(self.style.ERROR(f'오류: 스크립트를 찾을 수 없습니다: {script_path}'))
            return
        
        # 스크립트 실행
        try:
            # 현재 작업 디렉토리를 프로젝트 루트로 설정
            os.chdir(base_dir)
            
            # 스크립트 실행
            result = os.system(f'python {script_path}')
            
            if result == 0:
                self.stdout.write(self.style.SUCCESS('파비콘 이미지 복원 작업이 완료되었습니다!'))
            else:
                self.stdout.write(self.style.ERROR('파비콘 이미지 복원 작업이 실패했습니다.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'오류 발생: {e}')) 