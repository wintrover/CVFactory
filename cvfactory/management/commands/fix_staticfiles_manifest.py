#!/usr/bin/env python
"""
staticfiles.json 매니페스트 파일에서 파비콘 파일을 원본 파일명으로 매핑하는 명령어
collectstatic 실행 후 이 명령어를 실행하면 파비콘 파일이 해시 없이 원본 파일명으로 제공됩니다.
"""
import os
import json
import fnmatch
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'staticfiles.json 매니페스트 파일에서 파비콘 및 OG 이미지 파일을 원본 파일명으로 매핑'

    def handle(self, *args, **options):
        # staticfiles.json 파일 경로
        manifest_path = os.path.join(settings.STATIC_ROOT, 'staticfiles.json')
        
        if not os.path.exists(manifest_path):
            self.stdout.write(self.style.ERROR('staticfiles.json 파일이 존재하지 않습니다.'))
            return
        
        # 무시할 파일 패턴 (파비콘 파일과 OG 이미지 파일들)
        ignore_patterns = getattr(settings, 'STATICFILES_IGNORE_PATTERNS', [
            'favicon*.png',
            'favicon.ico',
            'android-chrome*.png',
            'apple-touch-icon*.png',
            'og-image*.png',
            'og-image*.webp',
            'twitter-card*.png',
            'twitter-card*.webp'
        ])
        
        # staticfiles.json 파일 읽기
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        # 파비콘 파일을 원본 파일명으로 매핑
        paths = manifest.get('paths', {})
        modified = False
        
        for original_path, hashed_path in list(paths.items()):
            # 파일명만 추출
            filename = os.path.basename(original_path)
            
            # 파비콘 또는 OG 이미지 파일인지 확인
            is_ignored = any(fnmatch.fnmatch(filename, pattern) for pattern in ignore_patterns)
            
            if is_ignored:
                # 파일은 원본 파일명으로 매핑
                self.stdout.write(f'파일 매핑 수정: {original_path} -> {original_path}')
                paths[original_path] = original_path
                modified = True
        
        if modified:
            # 수정된 manifest 파일 저장
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)
            self.stdout.write(self.style.SUCCESS('staticfiles.json 파일이 성공적으로 수정되었습니다.'))
        else:
            self.stdout.write(self.style.WARNING('수정할 파일이 없습니다.')) 