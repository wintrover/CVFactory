#!/usr/bin/env bash
# 오류 발생 시 스크립트 종료
set -o errexit

echo "===== 프로덕션 배포 스크립트 시작 ====="
echo "현재 디렉토리: $(pwd)"

# 현재 브랜치 확인
CURRENT_BRANCH=$(git branch --show-current)
echo "현재 브랜치: $CURRENT_BRANCH"

# 변경사항이 있는지 확인
if [[ -n $(git status -s) ]]; then
    echo "경고: 커밋되지 않은 변경사항이 있습니다."
    git status
    read -p "계속 진행하시겠습니까? (y/n): " CONTINUE
    if [[ "$CONTINUE" != "y" ]]; then
        echo "작업을 취소합니다."
        exit 1
    fi
    
    # 변경사항 스테이징 및 커밋
    echo "변경사항 커밋 중..."
    git add .
    git commit -m "정적 파일 업데이트 및 배포 준비 $(date +%Y-%m-%d)"
fi

# 정적 파일 수집
echo "정적 파일 수집 중..."
python manage.py collectstatic --noinput

# 정적 파일 변경사항 확인 및 커밋
if [[ -n $(git status -s) ]]; then
    echo "정적 파일 변경사항 커밋 중..."
    git add static_prod/
    git commit -m "정적 파일 업데이트 $(date +%Y-%m-%d)"
fi

# production 브랜치로 전환 또는 생성
echo "production 브랜치로 전환 중..."
if git show-ref --quiet refs/heads/production; then
    # production 브랜치가 존재하는 경우
    git checkout production
    git merge $CURRENT_BRANCH --no-edit
else
    # production 브랜치가 존재하지 않는 경우
    git checkout -b production
fi

# 원격 저장소에 푸시
echo "production 브랜치를 원격 저장소에 푸시 중..."
git push origin production

# 원래 브랜치로 복귀
echo "원래 브랜치($CURRENT_BRANCH)로 복귀 중..."
git checkout $CURRENT_BRANCH

echo "===== 프로덕션 배포 완료 =====" 