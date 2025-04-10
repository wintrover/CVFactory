import subprocess
from django.core.management.base import BaseCommand
import datetime

class Command(BaseCommand):
    help = 'Push current branch to develop branch'

    def add_arguments(self, parser):
        parser.add_argument(
            '--commit-msg',
            dest='commit_msg',
            default=f'개발 코드 업데이트 {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}',
            help='Custom commit message for pushing to develop branch.',
        )

    def handle(self, *args, **options):
        try:
            # 1. 현재 브랜치 확인
            current_branch = subprocess.check_output(
                ['git', 'branch', '--show-current'], 
                stderr=subprocess.STDOUT
            ).decode('utf-8').strip()
            
            self.stdout.write(self.style.WARNING(f'현재 브랜치: {current_branch}'))
            
            # 2. 변경사항 확인
            status_output = subprocess.check_output(
                ['git', 'status', '-s'],
                stderr=subprocess.STDOUT
            ).decode('utf-8').strip()
            
            if status_output:
                # 3. 변경사항 커밋
                self.stdout.write(self.style.WARNING('변경사항 커밋 중...'))
                subprocess.run(['git', 'add', '.'], check=True)
                subprocess.run(['git', 'commit', '-m', options['commit_msg']], check=True)
            else:
                self.stdout.write(self.style.WARNING('커밋할 변경사항 없음'))
            
            # 4. develop 브랜치로 전환 또는 생성
            self.stdout.write(self.style.WARNING('develop 브랜치로 전환 중...'))
            
            # develop 브랜치 존재 여부 확인
            try:
                subprocess.run(
                    ['git', 'show-ref', '--quiet', 'refs/heads/develop'],
                    check=True
                )
                # develop 브랜치가 존재하는 경우
                subprocess.run(['git', 'checkout', 'develop'], check=True)
                subprocess.run(['git', 'merge', current_branch, '--no-edit'], check=True)
            except subprocess.CalledProcessError:
                # develop 브랜치가 존재하지 않는 경우
                subprocess.run(['git', 'checkout', '-b', 'develop'], check=True)
            
            # 5. 원격 저장소에 푸시
            self.stdout.write(self.style.WARNING('develop 브랜치를 원격 저장소에 푸시 중...'))
            subprocess.run(['git', 'push', 'origin', 'develop'], check=True)
            
            # 6. 원래 브랜치로 복귀
            self.stdout.write(self.style.WARNING(f'원래 브랜치({current_branch})로 복귀 중...'))
            subprocess.run(['git', 'checkout', current_branch], check=True)
            
            self.stdout.write(self.style.SUCCESS('develop 브랜치 푸시 완료!'))
            
        except subprocess.CalledProcessError as e:
            self.stdout.write(self.style.ERROR(f'Git 작업 중 오류 발생: {e}'))
            # 원래 브랜치로 복귀 시도
            try:
                subprocess.run(['git', 'checkout', current_branch], check=False)
            except:
                pass
            raise 