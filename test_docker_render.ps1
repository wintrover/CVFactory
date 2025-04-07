#!/usr/bin/env pwsh
# Docker를 사용한 Render 환경 시뮬레이션을 위한 PowerShell 스크립트

Write-Host "==> Docker 이미지 빌드 시작" -ForegroundColor Blue
docker build -t cvfactory-render-test -f Dockerfile.local .

Write-Host "`n==> Docker 컨테이너 실행" -ForegroundColor Green
Write-Host "웹 브라우저에서 https://localhost:8000 으로 접속하세요 (HTTP는 비활성화되어 있습니다)" -ForegroundColor Yellow
Write-Host "자체 서명 인증서 경고가 표시되면 '고급' → '안전하지 않음으로 계속' 을 선택하세요" -ForegroundColor Magenta
Write-Host "컨테이너를 중지하려면 Ctrl+C를 누른 후 'docker stop cvfactory-render-test' 명령을 실행하세요`n" -ForegroundColor Yellow

docker run --name cvfactory-render-test -p 8000:8000 --rm cvfactory-render-test 