import json
import os
from datetime import datetime

# 현재 py 파일 위치
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, 'export_config.txt')
exported_tasks_dir = os.path.join(current_dir, 'exported_tasks')
exported_dir = os.path.join(current_dir, 'exported')

# exported 폴더 생성
os.makedirs(exported_dir, exist_ok=True)

# config 읽기
config = {}
with open(config_path, 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip() and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            config[key.strip()] = value.strip()

# TASK 번호 추출
task_numbers = [int(x.strip()) for x in config.get('TASK', '').split(',') if x.strip().isdigit()]

# exported_tasks 폴더의 모든 json 읽기
all_tasks = []
for filename in os.listdir(exported_tasks_dir):
    if filename.endswith('.json'):
        file_path = os.path.join(exported_tasks_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_tasks.extend(data)

# 필터링
filtered_tasks = [task for task in all_tasks if task.get('id') in task_numbers]

# 오늘 날짜 구하기
today_str = datetime.now().strftime('%Y_%m_%d')

# 결과 저장 경로
output_filename = f'오다혜_{today_str}.json'
output_path = os.path.join(exported_dir, output_filename)

# 결과 저장
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(filtered_tasks, f, ensure_ascii=False, indent=4)

print(f"✅ 선택된 task {task_numbers} 추출 완료! → {output_path}")