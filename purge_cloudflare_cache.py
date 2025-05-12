import os
import requests
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def purge_cache():
    api_token = os.environ.get("CLOUDFLARE_API_TOKEN")
    zone_id = os.environ.get("CLOUDFLARE_ZONE_ID")
    logging.info(f"환경 변수 확인: Zone ID='{zone_id}', API Token='{'*' * (len(api_token) - 4) + api_token[-4:] if api_token else None}'") # 토큰 일부만 로깅

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
    logging.info(f"Cloudflare API 요청 시작: URL='{url}', Headers='{headers}', Data='{data}'") # 헤더는 토큰 제외하고 로깅 고려 필요 (여기선 일단 포함)

    try:
        logging.info(f"Cloudflare 캐시 퍼지를 시도합니다. Zone ID: {zone_id}")
        response = requests.post(url, headers=headers, json=data, timeout=30) # 타임아웃 추가
        logging.info(f"Cloudflare API 응답 수신: Status Code={response.status_code}")

        # 응답 상태 코드가 성공(2xx)이 아닌 경우 상세 로깅
        if not response.ok:
            logging.error(f"Cloudflare API 요청 실패: Status Code={response.status_code}, Response Body={response.text}")
            response.raise_for_status() # 여기서 예외 발생시킴

        result = response.json()
        logging.info(f"Cloudflare API 응답 내용: {result}") # 성공 시 응답 내용 로깅

        if result.get("success"):
            logging.info("Cloudflare 캐시 퍼지에 성공했습니다.")
            return True
        else:
            # API 자체는 성공(200 OK)했지만, 결과가 실패인 경우
            logging.error(f"Cloudflare 캐시 퍼지 작업 실패 (API 응답 success=False): {result}")
            return False
    except requests.exceptions.Timeout:
        logging.error("Cloudflare API 요청 시간 초과")
        return False
    except requests.exceptions.HTTPError as e:
        # raise_for_status()에 의해 발생하는 예외 (이미 위에서 로깅함)
        logging.error(f"Cloudflare API HTTP 오류 발생: {e}") # 이미 위에서 로깅했지만 중복 로깅
        return False
    except requests.exceptions.RequestException as e:
        logging.error(f"Cloudflare API 요청 중 네트워크/연결 오류 발생: {e}")
        return False
    except Exception as e:
        # JSON 파싱 오류 등 예상치 못한 오류
        logging.error(f"캐시 퍼지 중 알 수 없는 오류 발생: {e}", exc_info=True) # 스택 트레이스 포함
        return False

if __name__ == "__main__":
    logging.info("Cloudflare 캐시 퍼지 스크립트 시작")
    success = purge_cache()
    if success:
        logging.info("스크립트 실행 완료: 성공")
        # 성공 시 종료 코드를 0으로 명시 (CI/CD 환경에서 중요할 수 있음)
        exit(0)
    else:
        logging.error("스크립트 실행 완료: 실패")
        # 실패 시 종료 코드를 1로 명시
        exit(1) 