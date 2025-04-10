import os
import subprocess
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import datetime

class Command(BaseCommand):
    help = 'Collect static files and push to production branch'

    def add_arguments(self, parser):
        # collectstatic 명령에 전달할 옵션들
        parser.add_argument(
            '--noinput', '--no-input',
            action='store_true',
            dest='interactive',
            help='Do NOT prompt the user for input of any kind.',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            dest='clear',
            help='Clear the existing files before trying to copy or link the original file.',
        )
        # Git 관련 옵션
        parser.add_argument(
            '--no-push',
            action='store_true',
            dest='no_push',
            help='Do not push to production branch, only collect static files.',
        )
        parser.add_argument(
            '--commit-msg',
            dest='commit_msg',
            default=f'정적 파일 업데이트 {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}',
            help='Custom commit message for the static files update.',
        )

    def handle(self, *args, **options):
        # 1. collectstatic 실행
        self.stdout.write(self.style.WARNING('정적 파일 수집 중...'))
        
        # collectstatic 명령에 전달할 옵션
        collectstatic_options = {
            'interactive': not options['interactive'],
            'clear': options['clear'],
        }
        
        call_command('collectstatic', **collectstatic_options)
        
        # Git 푸시 작업을 건너뛰는 경우
        if options['no_push']:
            self.stdout.write(self.style.SUCCESS('정적 파일 수집 완료. Git 푸시는 건너뜁니다.'))
            return
        
        try:
            # 2. 현재 브랜치 확인
            current_branch = subprocess.check_output(
                ['git', 'branch', '--show-current'], 
                stderr=subprocess.STDOUT
            ).decode('utf-8').strip()
            
            self.stdout.write(self.style.WARNING(f'현재 브랜치: {current_branch}'))
            
            # 3. 변경사항 확인
            status_output = subprocess.check_output(
                ['git', 'status', '-s'],
                stderr=subprocess.STDOUT
            ).decode('utf-8').strip()
            
            if status_output:
                # 4. static_prod 변경사항만 커밋
                self.stdout.write(self.style.WARNING('정적 파일 변경사항 커밋 중...'))
                subprocess.run(['git', 'add', 'static_prod/'], check=True)
                subprocess.run(['git', 'commit', '-m', options['commit_msg']], check=True)
            else:
                self.stdout.write(self.style.WARNING('변경된 정적 파일 없음, 커밋 건너뜀'))
                return
            
            # 5. production 브랜치로 전환 또는 생성
            self.stdout.write(self.style.WARNING('production 브랜치로 전환 중...'))
            
            # production 브랜치 존재 여부 확인
            try:
                subprocess.run(
                    ['git', 'show-ref', '--quiet', 'refs/heads/production'],
                    check=True
                )
                # production 브랜치가 존재하는 경우
                subprocess.run(['git', 'checkout', 'production'], check=True)
                subprocess.run(['git', 'merge', current_branch, '--no-edit'], check=True)
            except subprocess.CalledProcessError:
                # production 브랜치가 존재하지 않는 경우
                subprocess.run(['git', 'checkout', '-b', 'production'], check=True)
            
            # 6. 원격 저장소에 푸시
            self.stdout.write(self.style.WARNING('production 브랜치를 원격 저장소에 푸시 중...'))
            subprocess.run(['git', 'push', 'origin', 'production'], check=True)
            
            # 7. 원래 브랜치로 복귀
            self.stdout.write(self.style.WARNING(f'원래 브랜치({current_branch})로 복귀 중...'))
            subprocess.run(['git', 'checkout', current_branch], check=True)
            
            self.stdout.write(self.style.SUCCESS('정적 파일 수집 및 production 브랜치 푸시 완료!'))
            
        except subprocess.CalledProcessError as e:
            self.stdout.write(self.style.ERROR(f'Git 작업 중 오류 발생: {e}'))
            # 원래 브랜치로 복귀 시도
            try:
                subprocess.run(['git', 'checkout', current_branch], check=False)
            except:
                pass
            raise 