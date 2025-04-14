# 오류 발생 시 스크립트 종료
$ErrorActionPreference = "Stop"

Write-Host "===== 프로덕션 배포 스크립트 시작 =====" -ForegroundColor Green
Write-Host "현재 디렉토리: $(Get-Location)"

# 현재 브랜치 확인
$CURRENT_BRANCH = git branch --show-current
Write-Host "현재 브랜치: $CURRENT_BRANCH"

# 변경사항이 있는지 확인
$STATUS = git status -s
if ($STATUS) {
    Write-Host "경고: 커밋되지 않은 변경사항이 있습니다." -ForegroundColor Yellow
    git status
    $CONTINUE = Read-Host "계속 진행하시겠습니까? (y/n)"
    if ($CONTINUE -ne "y") {
        Write-Host "작업을 취소합니다." -ForegroundColor Red
        exit 1
    }
    
    # 변경사항 스테이징 및 커밋
    Write-Host "변경사항 커밋 중..." -ForegroundColor Cyan
    git add .
    git commit -m "정적 파일 업데이트 및 배포 준비 $(Get-Date -Format 'yyyy-MM-dd')"
}

# 정적 파일 수집
Write-Host "정적 파일 수집 중..." -ForegroundColor Cyan
python manage.py collectstatic --noinput

# 정적 파일 변경사항 확인 및 커밋
$STATUS = git status -s
if ($STATUS) {
    Write-Host "정적 파일 변경사항 커밋 중..." -ForegroundColor Cyan
    git add static_prod/
    git commit -m "정적 파일 업데이트 $(Get-Date -Format 'yyyy-MM-dd')"
}

# production 브랜치로 전환 또는 생성
Write-Host "production 브랜치로 전환 중..." -ForegroundColor Cyan
$PRODUCTION_EXISTS = git show-ref --quiet refs/heads/production
if ($LASTEXITCODE -eq 0) {
    # production 브랜치가 존재하는 경우
    git checkout production
    git merge $CURRENT_BRANCH --no-edit
}
else {
    # production 브랜치가 존재하지 않는 경우
    git checkout -b production
}

# 원격 저장소에 푸시
Write-Host "production 브랜치를 원격 저장소에 푸시 중..." -ForegroundColor Cyan
git push origin production

# 원래 브랜치로 복귀
Write-Host "원래 브랜치($CURRENT_BRANCH)로 복귀 중..." -ForegroundColor Cyan
git checkout $CURRENT_BRANCH

Write-Host "===== 프로덕션 배포 완료 =====" -ForegroundColor Green 