import os
import glob
import logging
import sys
from django.core.management.commands.runserver import Command as RunserverCommand

logger = logging.getLogger('cvfactory')

class Command(RunserverCommand):
    """
    로그 파일을 초기화한 후 Django 서버를 실행하는 커스텀 명령어
    사용법: python manage.py runserver_clear
    """
    
    def handle(self, *args, **options):
        """
        서버 시작 전에 로그 파일을 초기화하고 runserver 원본 기능 실행
        """
        # 로그 초기화 진행
        self.clear_log_files()
        
        # 원본 runserver 명령 실행
        super().handle(*args, **options)
    
    def clear_log_files(self):
        """서버 시작 시 로그 파일들을 초기화합니다."""
        try:
            # 로그 디렉토리가 없으면 생성
            os.makedirs('logs', exist_ok=True)
            
            # 서버 시작 전 로그 디버깅을 위해 표준 출력에도 메시지 출력
            print("[로그 정리] 로그 파일 정리 시작")
            
            # 1. 코어 로그 파일 목록 (유지하고 초기화할 파일들)
            core_log_files = [
                os.path.join('logs', 'app.log'),
                os.path.join('logs', 'api.log'),
                os.path.join('logs', 'error.log'),
                os.path.join('logs', 'startup.log')
            ]
            
            # 2. 초기화 전 현재 로그 파일 목록 확인
            current_logs = glob.glob(os.path.join('logs', '*.log'))
            print(f"[로그 정리] 현재 로그 파일 {len(current_logs)}개 발견: {', '.join([os.path.basename(f) for f in current_logs])}")
            
            # 3. 코어 로그 파일 초기화 (내용만 비움)
            for log_file in core_log_files:
                try:
                    with open(log_file, 'w', encoding='utf-8') as f:
                        # 파일 내용을 비우고 닫기
                        pass
                    print(f"[로그 정리] 코어 로그 파일 초기화: {os.path.basename(log_file)}")
                except Exception as e:
                    print(f"[로그 정리] 오류: 로그 파일 초기화 실패: {os.path.basename(log_file)} - {e}")
            
            # 4. 불필요한 로그 파일 삭제 (코어 파일 목록에 없는 모든 .log 파일)
            core_filenames = [os.path.basename(f) for f in core_log_files]
            removed_count = 0
            
            for log_file in current_logs:
                base_name = os.path.basename(log_file)
                if base_name not in core_filenames:
                    try:
                        os.remove(log_file)
                        removed_count += 1
                        print(f"[로그 정리] 불필요한 로그 파일 삭제: {base_name}")
                    except Exception as e:
                        print(f"[로그 정리] 오류: 로그 파일 삭제 실패: {base_name} - {e}")
            
            # 5. 삭제 후 로그 파일 목록 확인
            remaining_logs = glob.glob(os.path.join('logs', '*.log'))
            print(f"[로그 정리] 정리 후 로그 파일 {len(remaining_logs)}개 남음: {', '.join([os.path.basename(f) for f in remaining_logs])}")
            
            # 6. 크롤링 로그 디렉토리 정리
            crawling_log_dir = os.path.join('logs', 'crawling')
            if os.path.exists(crawling_log_dir):
                crawling_logs = glob.glob(os.path.join(crawling_log_dir, '*.txt'))
                for log_file in crawling_logs:
                    try:
                        os.remove(log_file)
                        print(f"[로그 정리] 크롤링 로그 파일 삭제: {os.path.basename(log_file)}")
                    except Exception as e:
                        print(f"[로그 정리] 오류: 크롤링 로그 파일 삭제 실패: {os.path.basename(log_file)} - {e}")
                print(f"[로그 정리] {len(crawling_logs)}개의 크롤링 로그 파일을 삭제했습니다.")
            else:
                os.makedirs(crawling_log_dir, exist_ok=True)
                print("[로그 정리] 크롤링 로그 디렉토리를 생성했습니다.")
            
            print(f"[로그 정리] 로그 파일 정리 완료: {len(core_log_files)}개 코어 로그 파일 초기화, {removed_count}개 불필요 파일 삭제")
            
            # 7. 파일이 제대로 제거되지 않은 경우 강제로 한 번 더 시도
            if len(remaining_logs) > len(core_log_files):
                print("[로그 정리] 일부 로그 파일이 제대로 제거되지 않았습니다. 강제 삭제를 시도합니다.")
                for log_file in remaining_logs:
                    base_name = os.path.basename(log_file)
                    if base_name not in core_filenames:
                        try:
                            # 파일 핸들이 닫혀있는지 확인하기 위해 내용을 비우는 방식으로 접근
                            with open(log_file, 'w') as f:
                                pass
                            # 파일 삭제 재시도
                            os.remove(log_file)
                            print(f"[로그 정리] 재시도: 불필요한 로그 파일 삭제 성공: {base_name}")
                        except Exception as e:
                            print(f"[로그 정리] 재시도: 로그 파일 삭제 실패: {base_name} - {e}")
                
                # 최종 확인
                final_logs = glob.glob(os.path.join('logs', '*.log'))
                print(f"[로그 정리] 최종 로그 파일 {len(final_logs)}개: {', '.join([os.path.basename(f) for f in final_logs])}")
            
        except Exception as e:
            print(f"[로그 정리] 심각한 오류: 로그 파일 초기화 중 오류 발생: {e}")
            
        # 모든 출력을 즉시 표시하기 위해 버퍼 비우기
        sys.stdout.flush() 