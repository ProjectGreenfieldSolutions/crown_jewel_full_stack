import os
import requests

# Replace with your Asana Personal Access Token
ASANA_ACCESS_TOKEN = "ACCESS_TOKEN"

# Replace with your Asana project ID
ASANA_PROJECT_ID = 'PROJECT_ID'

# Set the project directory to the root of your project, adjusting from .local to the actual root
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# List of file extensions to include in the search
included_extensions = ['.py', '.sql', '.yml', '.yaml', '.env', '.md']
dockerfile_names = ['Dockerfile', '.dockerignore']  # Docker-specific files

# Folders to skip (like virtual environments, build directories, etc.)
skip_dirs = {'venv', '.venv', '__pycache__', 'node_modules'}


# Functions

def find_todos(directory):
  todos = []
  for root, dirs, files in os.walk(directory):
    dirs[:] = [d for d in dirs if d not in skip_dirs]
    for file in files:
      if file in dockerfile_names or any(file.endswith(ext) for ext in included_extensions):
        file_path = os.path.join(root, file)
        try:
          with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_number, line in enumerate(f, start=1):
              if '# TODO' in line:
                todos.append({
                  'file_path': file_path,
                  'line_number': line_number,
                  'todo': line.strip()
                })
        except Exception as e:
          print(f"Error reading {file_path}: {e}")
  return todos


def fetch_all_tasks(project_id):
  ASANA_API_URL = f'https://app.asana.com/api/1.0/projects/{project_id}/tasks'
  headers = {'Authorization': f'Bearer {ASANA_ACCESS_TOKEN}'}
  tasks = []
  url = ASANA_API_URL

  while url:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    tasks.extend(data.get('data', []))
    url = data.get('next_page', {}).get('uri')

  return tasks


def get_existing_todo_titles(tasks):
  return {task['name'] for task in tasks}


def compare_todos_with_existing(todos, existing_tasks):
  existing_titles = get_existing_todo_titles(existing_tasks)
  new_todos = [todo for todo in todos if todo['todo'] not in existing_titles]
  return new_todos


def add_todo_to_asana(todo, project_id):
  ASANA_API_URL = 'https://app.asana.com/api/1.0/tasks'
  headers = {'Authorization': f'Bearer {ASANA_ACCESS_TOKEN}', 'Content-Type': 'application/json'}
  payload = {
    'data': {
      'name': todo['todo'],
      'projects': [project_id],
      'notes': f'TODO found in {todo["file_path"]} at line {todo["line_number"]}'
    }
  }
  response = requests.post(ASANA_API_URL, json=payload, headers=headers)
  response.raise_for_status()
  return response.json()


def main():
  todos = find_todos(project_dir)
  existing_tasks = fetch_all_tasks(ASANA_PROJECT_ID)
  new_todos = compare_todos_with_existing(todos, existing_tasks)

  for todo in new_todos:
    result = add_todo_to_asana(todo, ASANA_PROJECT_ID)
    print(f"Added TODO to Asana: {result['data']['name']}")


if __name__ == "__main__":
  main()