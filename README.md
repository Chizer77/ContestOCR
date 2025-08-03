# ContestOCR

基于OCR的某知识竞赛自动化答题小脚本，通过图像识别和大模型API自动完成答题任务。项目使用 PaddleOCR 进行文字识别，并结合 OpenAI 的模型进行答案推理。


## 项目结构
```
ContestOCR/
├── setup.py              # 答题和错题处理逻辑
├── loc.py                # 窗口定位与点击操作
├── model.py              # 调用 OpenAI 模型进行答案推理
├── ocr.py                # OCR 文字识别与题目结构提取
├── utils.py
├── requirements.txt
├── README.md
└── img/                  # 存放模板图片（如按钮、选项等）
    ├── window.png
    ├── continue.png
    ├── wrong_next.png
    ├── A.png
    ├── B.png
    ├── C.png
    ├── D.png
    └── corr_*.png
```

## 功能说明
1. **自动答题**：
   - 通过 OCR 识别屏幕上的题目和选项。
   - 调用 OpenAI 模型推理答案。
   - 自动点击正确答案。

2. **错题处理**：
   - 识别错题并记录。
   - 更新或新增错题答案。

3. **题目记录**：
   - 将识别的题目和答案保存为 JSON 文件。



## 环境依赖
请确保安装以下依赖：
- Python 3.8 或更高版本
- 依赖库（详见 `requirements.txt`）

```bash
pip install -r requirements.txt
```

## 使用方法
1. **配置环境**：
   - 在项目根目录下创建 `.env` 文件，添加 OpenAI API Key：
     ```
     OPENAI_API_KEY=your_openai_api_key
     ```

2. **运行项目**：
   - 启动答题功能：
     ```bash
     python setup.py
     ```
   - 启动错题处理功能：
     修改 `setup.py` 的 `if __name__ == "__main__":` 部分为 `wrong_quiz()`，然后运行。

3. **模板图片**：
   - 确保 `img/` 文件夹中包含所有必要的模板图片（如按钮、选项等）。
