import requests
import json
import re
import os

# === config.txt 읽기 ===
config_file = "config.txt"
if not os.path.exists(config_file):
    print("❌ config.txt 파일이 없습니다. 같은 폴더에 config.txt를 만들어주세요.")
    exit()

with open(config_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

config = {}
for line in lines:
    if "=" in line:
        key, value = line.strip().split("=", 1)
        config[key.strip()] = value.strip()

BASE_URL = config.get("BASE_URL")       #config내용 
REFRESH_TOKEN = config.get("TOKEN")
PROJECT_ID = config.get("PROJECT_ID")
INPUT_FOLDER = "./json_inputs"

if not BASE_URL or not REFRESH_TOKEN or not PROJECT_ID:
    print("❌ config.txt에서 BASE_URL, TOKEN 또는 PROJECT_ID 값을 읽지 못했습니다.")
    exit()

# PROJECT_ID를 int로 변환
PROJECT_ID = int(PROJECT_ID)

# === Access Token 발급 ===
#주의할점 Label studio의 개인토큰은 API토큰으로 바로 쓸수없는 리프레시 토큰이었음
#API용 Access Token을 발급받는 과정이 필요
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

# === API에서 프로젝트 task 목록 가져오기 ===
print("📡 Label Studio에서 작업 목록 가져오는 중...")
resp = requests.get(f"{BASE_URL}/api/projects/{PROJECT_ID}/tasks", headers=headers)
if resp.status_code != 200:
    print("❌ API 호출 실패:", resp.text)
    exit()
receiver_tasks = resp.json()

# suffix_map: {suffix: task_id}
suffix_map = {}
for task in receiver_tasks:
    data_video = task.get("data", {}).get("video", "")
    match = re.search(r'/upload/\d+/([^-]+)-(.+\.MP4)', data_video)
    if match:
        uid, suffix = match.groups()
        suffix_map[suffix] = task["id"]

print("📦 suffix_map 생성 완료:")
for suffix, task_id in suffix_map.items():
    print(f"  suffix: {suffix}, task_id: {task_id}")

# === JSON 파일 순회하며 annotation 추가 ===
#import로 처리하면 미리업로드된 영상과 json파일이 분리되는사항을 해결하지 못했음
#두가지가합병되도록 json을 import가 아닌 annotation으로 추가하도록 변경
for filename in os.listdir(INPUT_FOLDER):
    if filename.endswith(".json"):
        input_path = os.path.join(INPUT_FOLDER, filename)
        print(f"\n🔄 {filename} 처리 중...")
        with open(input_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        for task in json_data:
            file_upload = task.get("file_upload", "")
            match = re.search(r'([^-]+)-(.+\.MP4)', file_upload)
            if match:
                _, suffix = match.groups()
                if suffix in suffix_map:
                    target_task_id = suffix_map[suffix]
                    annotations = task.get("annotations", [])
                    for annotation in annotations:
                        annotation_payload = {
                            "result": annotation["result"]
                        }
                        resp = requests.post(
                            f"{BASE_URL}/api/tasks/{target_task_id}/annotations",
                            headers=headers,
                            json=annotation_payload
                        )
                        if resp.status_code == 201:
                            print(f"✅ {suffix} → task {target_task_id} annotation 추가 성공")
                        else:
                            print(f"❌ {suffix} → task {target_task_id} annotation 추가 실패: {resp.text}")
                else:
                    print(f"⚠️ {suffix} → 해당 task 없음, 건너뜀")


input("\n작업이 완료되었습니다. 엔터 키를 누르면 창이 닫힙니다.")
