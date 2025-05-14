# Ollama 模型迁移工具

## 工具介绍
用于在无网络环境部署Ollama框架及预下载模型，包含安装脚本和模型迁移工具。

## 文件说明
```
├── install_ollama.sh # 离线安装脚本 
├── ollama_export.py # 模型导出工具 
├── ollama_restore.py # 模型导入工具 
├── ollama-linux-*.tgz # Ollama主程序包（需自行下载） 
└── *.zip # 预下载模型文件（示例：deepseek-r1-1.5b.zip）
```

## 安装步骤

### 外网准备
```bash
# 1. 下载Ollama安装包（示例AMD64）
curl -L https://ollama.com/download/ollama-linux-amd64.tgz -o ollama-linux-amd64.tgz

# 2. 导出模型（需提前安装Ollama）
ollama run deepseek-r1:1.5b
python3 ollama_export.py deepseek-r1:1.5b ./
```

### 离线部署
拷贝当前目录至到目标服务器，并执行以下命令
```bash
# 1. 安装主程序（需指定安装包路径）
sudo ./install_ollama.sh ./ollama-linux-amd64.tgz

# 2. 导入模型
sudo python3 ollama_restore.py deepseek-r1-1.5b.zip

# 3. 验证模型导入
ollama list
```
