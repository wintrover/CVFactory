import os
import re
import json
import fnmatch
from pathlib import Path
from django.contrib.staticfiles.storage import ManifestStaticFilesStorage
from django.conf import settings

class CleanManifestStaticFilesStorage(ManifestStaticFilesStorage):
    """
    기존 ManifestStaticFilesStorage에 이전 버전의 파일을 자동으로 삭제하는 기능을 추가한 스토리지 클래스
    파비콘 파일은 처리하지 않도록 수정
    """
    
    def should_ignore_file(self, path):
        """
        settings.STATICFILES_IGNORE_PATTERNS에 정의된 패턴에 맞는 파일은 처리하지 않음
        """
        ignore_patterns = getattr(settings, 'STATICFILES_IGNORE_PATTERNS', [])
        for pattern in ignore_patterns:
            if fnmatch.fnmatch(path, pattern):
                return True
        return False
    
    def post_process(self, paths, dry_run=False, **options):
        # 파비콘 파일들 필터링
        filtered_paths = {}
        for path, storage_path in paths.items():
            if not self.should_ignore_file(path):
                filtered_paths[path] = storage_path
        
        # 원래 post_process 메서드 실행 (해시된 파일 생성) - 파비콘 제외
        for name, hashed_name, processed in super().post_process(filtered_paths, dry_run, **options):
            yield name, hashed_name, processed
        
        # dry_run 모드에서는 실제 파일 삭제 작업을 수행하지 않음
        if dry_run:
            return
            
        # staticfiles.json 파일 경로
        manifest_path = os.path.join(settings.STATIC_ROOT, 'staticfiles.json')
        
        # staticfiles.json 파일이 존재하는지 확인
        if not os.path.exists(manifest_path):
            return
            
        # staticfiles.json 파일 읽기
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        # 현재 사용 중인 파일 목록
        current_files = set()
        for original, hashed in manifest['paths'].items():
            # 원본 파일과 해시된 파일 모두 보존 목록에 추가
            current_files.add(original)
            current_files.add(hashed)
        
        # 정규식 패턴: 파일명.해시값.확장자 형태를 찾기 위한 패턴
        hash_pattern = re.compile(r'^(.+)\.([a-f0-9]{12,})(\..+)$')
        
        # 정적 파일 디렉토리 검사
        static_dir = Path(settings.STATIC_ROOT)
        for file in static_dir.glob('**/*.*'):
            # staticfiles.json은 건너뜀
            if file.name == 'staticfiles.json':
                continue
                
            # 파일의 상대 경로
            relative_path = str(file.relative_to(static_dir))
            
            # 파비콘 파일은 건너뜀
            if self.should_ignore_file(relative_path):
                continue
                
            # 현재 사용 중인 파일은 건너뜀
            if relative_path in current_files:
                continue
                
            # 해시 패턴에 맞는 파일인지 확인
            match = hash_pattern.match(file.name)
            if match:
                # 파일명.확장자 형태의 원본 파일명 구성
                original_name = match.group(1) + match.group(3)
                # 같은 디렉토리에서 원본 파일명이 있는지 확인
                dir_path = os.path.dirname(relative_path)
                original_path = os.path.join(dir_path, original_name)
                
                # 같은 원본에 대한 새 해시 버전이 있다면 이전 버전 삭제
                for path_key, path_value in manifest['paths'].items():
                    if path_key == original_path or path_value.startswith(dir_path + '/' + match.group(1) + '.'):
                        try:
                            os.remove(file)
                            print(f"이전 버전 파일 삭제: {file}")
                        except OSError:
                            print(f"파일 삭제 실패: {file}")
                        break 