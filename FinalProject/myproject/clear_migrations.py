import os

def clear_migrations():
    # Define the directory that contains your apps
    project_root = os.path.dirname(os.path.abspath(__file__))
    print(project_root)
    apps_root = os.path.join(project_root, 'myapp')  # Adjust if your apps are not in the root directory

    # List of all directories you consider as apps with migrations

    migration_folder = os.path.join(apps_root, 'migrations')
    if os.path.exists(migration_folder):
        # List all files in the migration folder except __init__.py
        files = [f for f in os.listdir(migration_folder) if f != '__init__.py' and f.endswith('.py')]

        # Remove each file
        for file in files:
            file_path = os.path.join(migration_folder, file)
            os.remove(file_path)
            print(f'Removed {file_path}')

if __name__ == "__main__":
    clear_migrations()
