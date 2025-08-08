# ComfyUI-Srt2Voice

基于 [IndexTTS](https://huggingface.co/IndexTeam/IndexTTS-1.5) 的 ComfyUI 插件，用于将 `.srt` 字幕文件转换为语音。支持参考音频复刻语音风格，并自动调整语速以匹配字幕时长。适用于视频配音、语音生成等中英文场景。

## ✨ 功能特色

- 🎙️ 支持输入 `.srt` 字幕内容，生成语音输出  
- 🧬 支持上传参考音频，克隆说话人音色  
- ⏱️ 自动语速调整以匹配字幕时间  
- 🌐 支持中英文
- 🔧 无需编程，直接在 ComfyUI 节点中操作

---

## 🛠️ 安装步骤

### 1. 如果还没有安装comfyui，先下载安装

comfyui下载地址：

[https://github.com/comfyanonymous/ComfyUI/releases/latest/download/ComfyUI_windows_portable_nvidia.7z](https://github.com/comfyanonymous/ComfyUI/releases/latest/download/ComfyUI_windows_portable_nvidia.7z)

### 2. 克隆插件代码

进入 ComfyUI 的 custom_nodes 目录，执行以下命令克隆插件代码：

`cd ComfyUI/custom_nodes`

`git clone https://github.com/bluewing82/ComfyUI-Srt2Voice`

### 3. 安装 pynini

查看 Python 版本：

`..\..\python_embeded\python.exe --version`

从项目的 `pynini安装文件` 文件夹选择对应的 pynini 安装包进行安装：

python 3.10 : `..\..\python_embeded\python.exe -m pip install ".\ComfyUI-Srt2Voice\pynini_files\pynini-2.1.6.post1-cp310-cp310-win_amd64.whl"`

python 3.11 : `..\..\python_embeded\python.exe -m pip install ".\ComfyUI-Srt2Voice\pynini_files\pynini-2.1.6.post1-cp311-cp311-win_amd64.whl"`

python 3.12 : `..\..\python_embeded\python.exe -m pip install ".\ComfyUI-Srt2Voice\pynini_files\pynini-2.1.6.post1-cp312-cp312-win_amd64.whl"`

python 3.13 : `..\..\python_embeded\python.exe -m pip install ".\ComfyUI-Srt2Voice\pynini_files\pynini-2.1.6.post1-cp313-cp313-win_amd64.whl"`

安装 WeTextProcessing：

`..\..\python_embeded\python.exe -m pip install WeTextProcessing --no-deps`

### 4. 安装环境依赖

安装插件所需的依赖：

`..\..\python_embeded\python.exe -m pip install -r .\ComfyUI-Srt2Voice\requirements.txt`

### 5. 下载 IndexTTS 模型

从 Hugging Face 下载 IndexTTS 模型文件，链接：

[https://huggingface.co/IndexTeam/IndexTTS-1.5/tree/main](https://huggingface.co/IndexTeam/IndexTTS-1.5/tree/main)

将模型文件全部放到这个目录下面（如果该目录不存在，请手动创建）：

`ComfyUI/models/IndexTTS-1.5/`

---

## 🚀 使用方法

启动 ComfyUI，添加节点 **SRT to Voice**。

配置参数说明：

- `srt_text`：输入 `.srt` 文件中的字幕内容（纯文本）  
- `reference_audio`：上传参考音频，用于克隆说话人的音色

运行工作流，即可生成对应的语音输出。

---

## 🙏 鸣谢

本项目基于以下开源项目构建：

- **IndexTTS**：高质量文本转语音模型  
- **ComfyUI**：强大的可视化工作流平台  

特别感谢 IndexTTS 项目的开源贡献！

---

## 📄 许可证

本插件遵循 MIT 许可证，详情请见 LICENSE 文件。

⚠️ 本项目使用了 IndexTTS，该项目同样使用 MIT 许可证。请确保在使用本插件过程中遵守其许可证要求。

---

如需进一步帮助或反馈建议，欢迎提交 Issue！
