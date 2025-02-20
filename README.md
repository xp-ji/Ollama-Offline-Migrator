# Ollama 模型迁移备份工具 ollamab 
转自: https://www.cnblogs.com/bxmm/p/18721265

## 背景

`ollama` 模型和相关配置文件默认都放在 `models` 文件夹下，想要把指定模型迁移到其他电脑比较麻烦，所以就有了该工具。还有就是模型下载本身就慢，一次下载多台使用减少下载次数。最重要的是公司电脑下载快，家里下载慢，在公司下载拷贝回家用 😄

## 如何使用

**下载地址**：

- Window [ollamab.exe](https://864000.lanzouu.com/i1fv42o5l7te)
- Linux [ollamab](https://864000.lanzouu.com/ir8E62o5l8ja)

### 命令

`ollamab` `模型名称+型号`（和 ollama 名称列表一致） `输出路径` (可选)

```shell
ollamab.exe qwen:0.5b D:/
```

**执行结果**

```shell
D:\code\private\model-backup>ollamab.exe qwen:0.5b
模型路径: D:\ai\.ollama\models
开始打包，耐心等待…………
添加到 ZIP 中: blobs\sha256-fad2a06e4cc705c2fa8bec5477ddb00dc0c859ac184c34dcc5586663774161ca
添加到 ZIP 中: blobs\sha256-41c2cf8c272f6fb0080a97cd9d9bd7d4604072b80a0b10e7d65ca26ef5000c0c
添加到 ZIP 中: blobs\sha256-1da0581fd4ce92dcf5a66b1da737cf215d8dcf25aa1b98b44443aaf7173155f5
添加到 ZIP 中: blobs\sha256-f02dd72bb2423204352eabc5637b44d79d17f109fdb510a7c51455892aa2d216
添加到 ZIP 中: manifests\registry.ollama.ai\library\qwen\0.5b
zip文件创建成功: qwen-0.5b.zip
```

### 目标电脑

将打包的 `zip` 拷贝到目标电脑 `models` 下直接解压到当前目录即可

### ollama

`ollama list` 输出所有模型命令

```shell
NAME                ID              SIZE      MODIFIED
gemma2:9b           ff02c3702f32    5.4 GB    5 hours ago
phi:2.7b            e2fd6321a5fe    1.6 GB    5 hours ago
qwen:7b             2091ee8c8d8f    4.5 GB    4 days ago
qwen:0.5b           b5dc5e784f2a    394 MB    4 days ago
llama3.1:8b         46e0c10c039e    4.9 GB    5 days ago
deepseek-r1:1.5b    a42b25d8c10a    1.1 GB    6 days ago
deepseek-r1:7b      0a8c26691023    4.7 GB    8 days ago
```

Ollama 在 Windows 上存储文件在几个不同的位置。您可以通过以下步骤查看它们：

- 按 `<cmd>+R` 键并输入：
  - `explorer %LOCALAPPDATA%\Ollama` ：包含日志和下载的更新
    - *app.log*：最近的 GUI 应用程序日志
    - *server.log*：最近的服务器日志
    - *upgrade.log*：升级日志输出
  - `explorer %LOCALAPPDATA%\Programs\Ollama`：包含二进制文件（安装器将其添加到用户 PATH 中）
  - `explorer %HOMEPATH%\.ollama`：包含模型和配置
  - `explorer %TEMP%`：包含临时执行文件，在一个或多个 `ollama*` 目录中

## 源码

```go
/**
 * @Time : 2025/2/14 
 * @File : main.go
 * @Software: ollamab
 * @Author : Mr.Fang
 * @Description: 备份 ollama 模型
 */
 
package main
 
import (
	"archive/zip"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"os"
	"path/filepath"
	"runtime"
	"strings"
)
 
var modelPath = ""
 
// 初始化获取模型文件路径，优先从系统环境变量获取，其次获取默认路径
func init() {
	models := os.Getenv("OLLAMA_MODELS")
	if len(models) > 0 {
		modelPath = models
	} else {
		// Window
		if runtime.GOOS == "windows" {
			home, err := os.UserHomeDir()
			if err != nil {
				log.Panicln("获取用户主目录失败:", err)
			}
			modelPath = filepath.Join(home, ".ollama", "models")
		} else { // Linux
			modelPath = filepath.Join("/usr/share/ollama/", ".ollama", "models")
		}
	}
	fmt.Println("模型路径:", modelPath)
}
 
// 将文件或文件夹添加到 zip 中
func addToZip(zipWriter *zip.Writer, filePath, baseFolder string) error {
	// 计算文件的相对路径
	relativePath, err := filepath.Rel(baseFolder, filePath)
	if err != nil {
		return err
	}
 
	fmt.Println("添加到 ZIP 中:", relativePath)
 
	// 如果是目录，则创建空目录
	info, err := os.Stat(filePath)
	if err != nil {
		return err
	}
 
	// 如果是目录，创建空目录
	if info.IsDir() {
		_, err := zipWriter.Create(relativePath + "/")
		return err
	}
 
	// 如果是文件，创建文件条目
	fileInZip, err := zipWriter.Create(relativePath)
	if err != nil {
		return err
	}
 
	// 打开文件并复制内容到zip中
	file, err := os.Open(filePath)
	if err != nil {
		return err
	}
	defer file.Close()
 
	// 复制文件内容到zip
	_, err = io.Copy(fileInZip, file)
	return err
}
 
// 模型相关所有文件路径
func blobsPath(modelDataPath, basePath string) []string {
	file, err := os.ReadFile(modelDataPath)
	if err != nil {
		fmt.Println("model data 文件读取错误！", err)
	}
	// 转 map
	var modelData map[string]interface{}
	var blobsPath []string
	err = json.Unmarshal(file, &modelData)
	if err != nil {
		fmt.Println("model data 转换错误！", err)
	}
	// 层数据
	layers := modelData["layers"].([]interface{})
	// 模型详情信息
	layers = append(layers, modelData["config"].(interface{}))
 
	for _, layer := range layers {
		item := layer.(map[string]interface{})
		digest := item["digest"].(string) // sha256
		digest = strings.ReplaceAll(digest, ":", "-")
		join := filepath.Join(basePath, "blobs", digest)
		// 使用 os.Stat 检查文件是否存在
		fileInfo, _ := os.Stat(join)
		if fileInfo != nil {
			blobsPath = append(blobsPath, join)
		}
	}
	return blobsPath
}
 
// build 打包 zip
func build(name string, output string, folderPaths []string) {
	fmt.Println("开始打包，耐心等待…………")
	// 创建目标zip文件
	zipFilePath := filepath.Join(output, name)
	zipFile, err := os.Create(zipFilePath)
	if err != nil {
		fmt.Println("创建zip文件失败:", err)
		return
	}
	defer zipFile.Close()
 
	// 创建zip写入器
	zipWriter := zip.NewWriter(zipFile)
	defer zipWriter.Close()
 
	// 逐个添加文件或目录到zip文件中
	for _, filePath := range folderPaths {
		// 注意：baseFolder 是我们希望在zip文件中根目录
		err := addToZip(zipWriter, filePath, modelPath)
		if err != nil {
			fmt.Println("添加文件到zip失败:", err)
			return
		}
	}
	fmt.Println("zip文件创建成功:", zipFilePath)
}
 
func main() {
	args := os.Args[1:]
 
	if len(args) == 0 {
		fmt.Println("参数: ollamab 名称:型号（必填） 指定输出路径，默认输出当前路径（可选）")
		fmt.Println("示例: ollamab deepseek-r1:1.5b ")
		fmt.Println("示例: ollamab deepseek-r1:1.5b D:/models")
		fmt.Println("示例: ollamab lrs33/bce-embedding-base_v1:latest")
		return
	}
	arg := strings.Split(args[0], ":")
	name := arg[0]
	version := arg[1]
	output := "./"
	if len(args) == 2 {
		output = args[1]
	}
	// 配置文件路径
	library := filepath.Join(modelPath, "manifests", "registry.ollama.ai", "library", name, version)
	// 特殊情况，用户自己分享的模型
	contains := strings.Contains(name, "/")
	if contains {
		libs := strings.Split(name, "/")
		library = filepath.Join(modelPath, "manifests", "registry.ollama.ai", libs[0], libs[1], version)
		// 替换 "/" 否则无法创建 zip
		name = strings.ReplaceAll(name, "/", "-")
	}
	folderPaths := blobsPath(library, modelPath)
	// 模型路径
	folderPaths = append(folderPaths, library)
	// 打包
	build(fmt.Sprintf("%s-%s.zip", name, version), output, folderPaths)
 
}
```

## 更新说明

- 解决用户自己分享的模型备份路径问题
- 模型 `config` 配置文件未拷贝导致 `ollama list` 未显示迁移模型，需要执行 `ollama run 模型`
- Linux 下默认模型路径未处理

哇！又赚了一天人民币
