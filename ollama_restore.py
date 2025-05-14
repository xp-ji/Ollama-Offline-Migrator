# save as ollama_restore.py
import os
import sys
import zipfile
import platform
from pathlib import Path

def init_model_path():
    models = os.getenv("OLLAMA_MODELS")
    if models:
        return Path(models)
    
    if platform.system() in ("Windows", "Darwin"):
        home = Path.home()
        return home / ".ollama" / "models"
    else:  # Linux
        return Path("/usr/share/ollama/.ollama/models")

def restore_model(zip_path):
    target_dir = init_model_path()
    print(f"准备解压到: {target_dir}")
    
    if not target_dir.exists():
        target_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # 先验证路径安全性
            for file in zip_ref.namelist():
                if file.startswith(('..', '/', '\\')) or ':' in file:
                    raise ValueError("检测到不安全路径!")
            
            # 执行解压
            zip_ref.extractall(target_dir)
            
        print("解压完成！请验证模型文件:")
        print(f"ls {target_dir / 'manifests'}")  # 示例验证命令
        print(f"ls {target_dir / 'blobs'}")
        
    except Exception as e:
        print(f"解压失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python ollama_restore.py <备份文件路径>")
        print("示例: python ollama_restore.py deepseek-r1-1.5b.zip")
        sys.exit(1)
    
    restore_model(sys.argv[1])
