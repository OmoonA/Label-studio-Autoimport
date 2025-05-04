import requests
import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'export_config.txt')

# config 읽기
config = {}
with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
    for line in f:
        if '=' in line:
            key, value = line.strip().split('=', 1)
            config[key.strip()] = value.strip()

BASE_URL = config.get('BASE_URL')
TOKEN = config.get('TOKEN')
PROJECT_ID = config.get('PROJECT_ID')
TASK_IDS = config.get('TASK_IDS', '').split(',')

print(f"🔑 TOKEN: {TOKEN[:4]}...(앞 4자리만 표시)")
print(f"📝 가져올 Task IDs: {TASK_IDS}")

# API 요청 헤더 (★ PAT 방식)
headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

# output 폴더 만들기
OUTPUT_FOLDER = './exports'
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 각 task export
for task_id in TASK_IDS:
    task_id = task_id.strip()
    url = f"{BASE_URL}/api/projects/{PROJECT_ID}/tasks/{task_id}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        output_path = os.path.join(OUTPUT_FOLDER, f"task_{task_id}.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(response.json(), f, ensure_ascii=False, indent=4)
        print(f"✅ Exported Task {task_id} → {output_path}")
    else:
        print(f"❌ Failed to export Task {task_id}: {response.status_code} {response.text}")

print("🎉 모든 export 완료!")