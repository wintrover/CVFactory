import os
import requests
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def purge_cache():
    api_token = os.environ.get("CLOUDFLARE_API_TOKEN")
    zone_id = os.environ.get("CLOUDFLARE_ZONE_ID")

    if not api_token:
        logging.error("CLOUDFLARE_API_TOKEN 환경 변수가 설정되지 않았습니다.")
        return False
    if not zone_id:
        logging.error("CLOUDFLARE_ZONE_ID 환경 변수가 설정되지 않았습니다.")
        return False

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }
    data = {
        "purge_everything": True,
    }
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache"

    try:
        logging.info(f"Cloudflare 캐시 퍼지를 시작합니다. Zone ID: {zone_id}")
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        
        result = response.json()
        if result.get("success"):
            logging.info("Cloudflare 캐시 퍼지에 성공했습니다.")
            return True
        else:
            logging.error(f"Cloudflare 캐시 퍼지에 실패했습니다. 응답: {result}")
            return False
    except requests.exceptions.RequestException as e:
        logging.error(f"Cloudflare API 요청 중 오류 발생: {e}")
        return False
    except Exception as e:
        logging.error(f"알 수 없는 오류 발생: {e}")
        return False

if __name__ == "__main__":
    if purge_cache():
        logging.info("스크립트 실행 완료: 성공")
    else:
        logging.error("스크립트 실행 완료: 실패") 