from PIL import ImageGrab
import numpy as np
import re
import os
import json
import mss

def is_option_start(text):
    return text.strip().startswith(('A.', 'B.', 'C.', 'D.'))

def get_option_key(text):
    return text.strip()[:2] if is_option_start(text) else None

def is_question_number(text):
    return bool(re.match(r'^(\d+/\d+|\d+\.\d+)$', text.strip()))

# 匹配第一个中文字符及其后面的内容
def clean_question_start(text):
    match = re.search(r'[\u4e00-\u9fff].*', text)
    return match.group(0) if match else text

def extract_question_structure(ocr, config, isQuiz=False):

    x, y = config.loc
    width, height = config.size

    # region = (x, y, x + width, y + height)
    # img = ImageGrab.grab(bbox=region)
    # img.save("img/screenshot.png")
    with mss.mss() as sct:
        monitor = {
            "left": x,
            "top": y,
            "width": width,
            "height": height
        }
        img = sct.grab(monitor)
    mss.tools.to_png(img.rgb, img.size, output="img/screenshot.png")

    current_dir = os.getcwd()
    img_path = os.path.join(current_dir, 'img/screenshot.png')

    result = ocr.predict(input=img_path)
    for res in result:
        res.save_to_json("output")

    current_dir = os.getcwd()
    json_path = os.path.join(current_dir, "output/screenshot_res.json")
    with open(json_path, "r", encoding="utf-8") as f:
        result = json.load(f)

    text_blocks = []
    for text in result["rec_texts"]:
        text_blocks.append(text)

    question_lines = []
    options = {'A': [], 'B': [], 'C': [], 'D': []}
    current_option = None
    question_number = 0
    for text in text_blocks:
        if is_question_number(text):
            question_number = int(text[0])
        elif is_option_start(text):
            current_option = get_option_key(text)
            options[current_option[0]].append(text[2:].strip())
        elif current_option:
            options[current_option[0]].append(text)
        else:
            question_lines.append(text)
    if isQuiz:
        question = ''.join(question_lines[1:]).strip()
    else:
        options['D'].remove('上一题') if '上一题' in options['D'] else None
        options['D'].remove('下一题') if '下一题' in options['D'] else None
        options['D'].remove('返回') if '返回' in options['D'] else None
        question = ''.join(question_lines).strip()
    # question = clean_question_start(question)
    options_merged = {k: ''.join(v).strip() for k, v in options.items()}

    q = {
        "question": question,
        "options": options_merged,
        "answer": "",
    }
    return q, question_number



