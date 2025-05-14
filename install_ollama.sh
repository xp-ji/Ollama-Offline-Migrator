#!/bin/bash

# Ollama一键安装脚本
# 使用方法：sudo ./install_ollama.sh [安装包路径]
# 示例：sudo ./install_ollama.sh ./ollama-linux-arm64.tgz

# 参数检查
if [ -z "$1" ]; then
    echo "错误：请指定Ollama安装包路径"
    echo "示例：sudo $0 ./ollama-linux-arm64.tgz"
    exit 1
fi

INSTALL_PKG="$1"

# 验证安装包存在
if [ ! -f "$INSTALL_PKG" ]; then
    echo "错误：安装包 $INSTALL_PKG 不存在"
    exit 1
fi

# 解压安装包到系统目录
echo "正在安装Ollama主程序（使用安装包：$INSTALL_PKG）..."
sudo tar -C /usr -xzf "$INSTALL_PKG"

# 创建专用用户和组
echo "正在创建系统用户和组..."
sudo useradd -r -s /bin/false -U -m -d /usr/share/ollama ollama
sudo usermod -a -G ollama $(whoami)

# 创建systemd服务文件
echo "正在配置系统服务..."
sudo tee /etc/systemd/system/ollama.service > /dev/null <<EOF
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
ExecStart=/usr/bin/ollama serve
User=ollama
Group=ollama
Restart=always
RestartSec=3
Environment="PATH=\$PATH"

[Install]
WantedBy=multi-user.target
EOF

# 启用并启动服务
echo "正在启动后台服务..."
sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl start ollama

echo "安装完成！"
echo "服务状态检查命令：sudo systemctl status ollama"
