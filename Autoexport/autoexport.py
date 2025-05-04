import requests
import os
import datetime


# 현재 py 파일의 폴더 경로 구하기
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, 'export_config.txt')

# config 읽기
config = {}
with open(config_path, 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip() and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            config[key.strip()] = value.strip()

BASE_URL = config.get('BASE_URL')
REFRESH_TOKEN = config.get('REFRESH_TOKEN')
PROJECT_ID = config.get('PROJECT_ID')

# === 필수 값 체크 ===
if not BASE_URL or not REFRESH_TOKEN or not PROJECT_ID:
    print("❌ BASE_URL, REFRESH_TOKEN, PROJECT_ID는 필수입니다!")
    exit()

# === Access Token 발급 ===
resp = requests.post(
    f"{BASE_URL}/api/token/refresh",
    headers={"Content-Type": "application/json"},
    json={"refresh": REFRESH_TOKEN}
)
if resp.status_code != 200:
    print("❌ Access Token 발급 실패:", resp.text)
    exit()
access_token = resp.json()["access"]
print("✅ Access Token 발급 성공")

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# === 프로젝트 전체 export 요청 ===
export_url = f"{BASE_URL}/api/projects/{PROJECT_ID}/export"
print("📡 전체 export 데이터 다운로드 중...")

resp = requests.get(export_url, headers=headers)
if resp.status_code == 200:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 저장 폴더 경로
    export_folder = os.path.join(script_dir, "exported_tasks")

    # 폴더 없으면 생성
    os.makedirs(export_folder, exist_ok=True)

    # 오늘 날짜 구하기 (YYYY-MM-DD 형식)
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    # 저장 파일 경로 만들기
    output_path = os.path.join(export_folder, f"오다혜_{today}.json")

    with open(output_path, "w", encoding='utf-8') as f:
        f.write(resp.text)
   
    print("✅ 프로젝트 전체 export 완료! → project_export.json 저장됨")
    print(f"✅ 저장 완료: {output_path}")
else:
    print(f"❌ Export 요청 실패: {resp.status_code} {resp.text}")
