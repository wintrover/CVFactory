#!/usr/bin/env pwsh
# Docker를 사용한 Render 환경 시뮬레이션을 위한 PowerShell 스크립트

Write-Host "==> Docker 이미지 빌드 시작" -ForegroundColor Blue
docker build -t cvfactory-render-test -f Dockerfile.local .

Write-Host "`n==> Docker 컨테이너 실행" -ForegroundColor Green
Write-Host "웹 브라우저에서 http://localhost:8080 으로 접속하세요" -ForegroundColor Yellow
Write-Host "컨테이너를 중지하려면 Ctrl+C를 누른 후 'docker stop cvfactory-render-test' 명령을 실행하세요`n" -ForegroundColor Yellow

docker run --name cvfactory-render-test -p 8080:8000 --rm cvfactory-render-test 