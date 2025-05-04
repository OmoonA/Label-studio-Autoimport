import requests
import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'export_config.txt')
OUTPUT_FOLDER = './exported_tasks'

# === 1. config.txt 읽기 ===
with open(CONFIG_FILE, 'r') as f:
    lines = [line.strip() for line in f if line.strip()]

# BASE_URL, TOKEN 추출
base_url_line = next((line for line in lines if line.startswith('BASE_URL=')), None)
token_line = next((line for line in lines if line.startswith('TOKEN=')), None)

if not base_url_line or not token_line:
    raise ValueError("⚠️ export_config.txt에 BASE_URL= 와 TOKEN= 라인을 꼭 넣어주세요!")

BASE_URL = base_url_line.split('=', 1)[1]
TOKEN = token_line.split('=', 1)[1]
HEADERS = {'Authorization': f'Token {TOKEN}'}

# task ID 추출 (숫자 라인만)
task_ids = [line for line in lines if line.isdigit()]

# 출력 폴더 준비
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

print(f"📋 BASE_URL: {BASE_URL}")
print(f"🔑 TOKEN: {TOKEN[:4]}... (앞 4자리만 표시)")
print(f"📝 가져올 Task IDs: {task_ids}")

# === 2. 각 task API 호출해서 JSON 저장 ===
for task_id in task_ids:
    url = f'{BASE_URL}/api/tasks/{task_id}'
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        task_data = response.json()
        output_file = os.path.join(OUTPUT_FOLDER, f'task_{task_id}.json')
        with open(output_file, 'w', encoding='utf-8') as f_out:
            json.dump(task_data, f_out, indent=4, ensure_ascii=False)
        print(f"✅ Task {task_id} exported → {output_file}")
    else:
        print(f"❌ Failed to export Task {task_id}: {response.status_code} {response.text}")

print("🎉 모든 export 완료!")
