from cvfactory.management.commands.collectstatic_and_push import Command as CollectStaticAndPushCommand

class Command(CollectStaticAndPushCommand):
    """
    기존 collectstatic 명령어를 오버라이드하여 
    자동으로 정적 파일 수집 및 production 브랜치 푸시 기능까지 제공합니다.
    """
    pass 