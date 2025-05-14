import os
import sys
import json
import zipfile
import platform
from pathlib import Path

model_path = ""

def init_model_path():
    global model_path
    models = os.getenv("OLLAMA_MODELS")
    if models:
        model_path = models
    else:
        if platform.system() in ("Windows", "Darwin"):
            home = Path.home()
            model_path = home / ".ollama" / "models"
        else:  # Linux
            model_path = Path("/usr/share/ollama/.ollama/models")
    print(f"模型路径: {model_path}")

def add_to_zip(zip_writer, file_path, base_folder):
    relative_path = os.path.relpath(file_path, base_folder)
    print(f"添加到 ZIP 中: {relative_path}")
    
    if os.path.isdir(file_path):
        # 在Python中不需要显式创建目录，添加文件时会自动创建父目录
        return
    else:
        zip_writer.write(file_path, arcname=relative_path)

def blobs_path(model_data_path, base_path):
    try:
        with open(model_data_path, 'r') as f:
            model_data = json.load(f)
    except Exception as e:
        print(f"model data 文件读取错误! {e}")
        return []
    
    blobs = []
    
    def process_layers(layers):
        for layer in layers:
            if isinstance(layer, dict):
                digest = layer.get("digest", "").replace(":", "-")
                if digest:
                    blob_path = Path(base_path) / "blobs" / digest
                    if blob_path.exists():
                        blobs.append(str(blob_path))
    
    # 处理layers和config
    layers = model_data.get("layers", [])
    config = model_data.get("config")
    if config:
        if isinstance(config, dict):
            layers.append(config)
        else:
            try:
                layers.append(json.loads(config))
            except:
                pass
    
    process_layers(layers)
    return blobs

def build(name, output, folder_paths):
    print("开始打包，耐心等待…………")
    zip_path = Path(output) / f"{name}.zip"
    
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for path in folder_paths:
                path = Path(path)
                if path.is_dir():
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            add_to_zip(zf, os.path.join(root, file), model_path)
                else:
                    add_to_zip(zf, str(path), model_path)
        print(f"zip文件创建成功: {zip_path}")
    except Exception as e:
        print(f"创建zip文件失败: {e}")

if __name__ == "__main__":
    init_model_path()
    
    if len(sys.argv) < 2:
        print("参数: ollamab 名称:型号（必填） 指定输出路径，默认输出当前路径（可选）")
        print("示例: ollamab deepseek-r1:1.5b ")
        print("示例: ollamab deepseek-r1:1.5b D:/models")
        print("示例: ollamab lrs33/bce-embedding-base_v1:latest")
        sys.exit(1)
    
    args = sys.argv[1].split(":", 1)
    if len(args) < 2:
        print("参数格式错误!")
        sys.exit(1)
    
    name_part, version = args
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.cwd()
    
    # 处理自定义模型路径
    if "/" in name_part:
        parts = name_part.split("/")
        library_path = Path(model_path) / "manifests" / "registry.ollama.ai" / parts[0] / parts[1] / version
        zip_name = f"{name_part.replace('/', '-')}-{version}"
    else:
        library_path = Path(model_path) / "manifests" / "registry.ollama.ai" / "library" / name_part / version
        zip_name = f"{name_part}-{version}"
    
    # 收集文件路径
    blobs = blobs_path(str(library_path), model_path)
    all_paths = blobs + [str(library_path)]
    
    # 创建输出目录
    output.mkdir(parents=True, exist_ok=True)
    
    build(zip_name, str(output), all_paths)
