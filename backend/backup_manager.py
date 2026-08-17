import os
import json
import subprocess
from datetime import datetime

class BackupManager:
    def __init__(self, repo_name='v75eur/football-manager-backups'):
        self.repo_name = repo_name
        self.backup_dir = '/tmp/backup_temp'
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def backup_player(self, pseudo, data):
        try:
            player_dir = f"{self.backup_dir}/joueurs/{pseudo}"
            os.makedirs(player_dir, exist_ok=True)
            
            filepath = f"{player_dir}/{pseudo}.FMTK"
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            log = {
                'pseudo': pseudo,
                'date': datetime.now().isoformat(),
                'action': 'backup',
                'status': 'success'
            }
            
            log_file = f"{self.backup_dir}/logs/backups.log"
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            with open(log_file, 'a') as f:
                f.write(json.dumps(log) + '\n')
            
            self._git_commit_and_push(pseudo)
            return True
        except Exception as e:
            print(f"Erreur backup: {e}")
            return False
    
    def _git_commit_and_push(self, pseudo):
        try:
            os.chdir(self.backup_dir)
            
            if not os.path.exists('.git'):
                subprocess.run(['git', 'init'], check=True)
                subprocess.run(['git', 'remote', 'add', 'origin', f'git@github.com:{self.repo_name}.git'], check=True)
            
            subprocess.run(['git', 'add', '.'], check=True)
            
            commit_msg = f"Backup auto - {pseudo} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
            subprocess.run(['git', 'push', 'origin', 'main'], check=True)
            
            return True
        except Exception as e:
            print(f"Erreur git: {e}")
            return False
    
    def restore_player(self, pseudo):
        filepath = f"{self.backup_dir}/joueurs/{pseudo}/{pseudo}.FMTK"
        if not os.path.exists(filepath):
            return None
        with open(filepath, 'r') as f:
            return json.load(f)
