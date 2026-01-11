from paddleocr import PaddleOCR
import time
from loc import loc, beginClick, clickAnswer, continueClick, wrongClick, wrongNextClick, chooceCorrect
from utils import exist
from ocr import extract_question_structure
from model import model_reply
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import random
from dataclasses import dataclass
import win32gui
import mss



@dataclass
class WindowConfig:
    loc: tuple[int, int]
    size: tuple[int, int]
    scale: float


def quiz():
    ocr = PaddleOCR(
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False)

    load_dotenv()
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        base_url = "https://ark.cn-beijing.volces.com/api/v3",
    )

    target_title = "微信"
    hwnds = []

    def callback(hwnd, extra):
        title = win32gui.GetWindowText(hwnd)
        if target_title in title:
            hwnds.append(hwnd)

    win32gui.EnumWindows(callback, None)

    print(f"找到窗口：{hwnds}")
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        offset_x = monitor["left"]
        offset_y = monitor["top"]
        print(f"副屏分辨率: {monitor['width']} x {monitor['height']}")

    contest_hwnd = 787958

    current_dir = os.getcwd()
    save_path = os.path.join(current_dir, "output/questions.json")
    if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
        with open(save_path, "r", encoding="utf-8") as f:
            question_data = json.load(f)
    else:
        question_data = {}

    while True:
        config = loc('img/window.png')
        window_config = WindowConfig(loc=config[0], size=config[1], scale=config[2])
        if exist(window_config.loc) and exist(window_config.size):
            window_config.loc = (window_config.loc[0] + offset_x, window_config.loc[1] + offset_y)
            beginClick(contest_hwnd, window_config)
            while True:
                idx = 0
                while idx < 5:
                    time.sleep(2 + random.uniform(0, 1))
                    ques, _ = extract_question_structure(ocr, window_config, True)

                    repeat_question = False
                    for qid, qdata in question_data.items():
                        if qdata["question"] == ques["question"]:
                            print(f"答案：{qdata["answer"]}\n已存在相同题目，跳过保存：{qid}")
                            repeat_question = True
                            time.sleep(1 + random.uniform(0, 1))
                            isClick = False
                            while isClick == False:
                                isClick = clickAnswer(contest_hwnd, qdata["answer"], window_config)
                            break
                    idx = idx + 1
                    if repeat_question:
                        continue
                    
                    quesline = ques["question"] + ' '.join(map(lambda k: k + '.' + ques["options"].get(k, '') + ' ', ['A', 'B', 'C', 'D']))
                    print(quesline)

                    ans = model_reply(client, quesline)
                    ques["answer"] = ans["answer"]
                    question_key = f"Q{len(question_data) + 1}"
                    question_data[question_key] = ques
                    with open(save_path, "w", encoding="utf-8") as f:
                        json.dump(question_data, f, ensure_ascii=False, indent=2)
                    time.sleep(1 + random.uniform(0, 1))
                    isClick = False
                    while isClick == False:
                        isClick = clickAnswer(contest_hwnd, ans["answer"], window_config)

                time.sleep(1 + random.uniform(0, 1))
                iscontinue = False
                while iscontinue == False:
                    iscontinue = continueClick(contest_hwnd, window_config)

def wrong_quiz():
    ocr = PaddleOCR(
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False)
    
    current_dir = os.getcwd()
    save_path = os.path.join(current_dir, "output/questions.json")
    if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
        with open(save_path, "r", encoding="utf-8") as f:
            question_data = json.load(f)
    else:
        question_data = {}

    while True:
        config = loc('img/window.png')
        window_config = WindowConfig(loc=config[0], size=config[1], scale=config[2])
        if exist(window_config.loc) and exist(window_config.size):
            wrongClick(window_config)
            while True:
                time.sleep(3 + random.uniform(-0.5, 1))
                ques, idx = extract_question_structure(ocr, window_config, False)

                qid = "Q"
                isRepat = False
                question = ques.copy()
                question["answer"] = "A"
                for id, qdata in question_data.items():
                    if qdata["question"] == ques["question"]:
                        print(f"已存在相同题目：{id}，原答案：{qdata["answer"]}")
                        isRepat = True
                        qid = id
                        question["answer"] = qdata['answer']
                        break
                
                clickAnswer(question["answer"], window_config)
                time.sleep(1 + random.uniform(0, 1))
                ques, idx = extract_question_structure(ocr, window_config, False)
                ans = chooceCorrect(window_config)
                question['answer'] = ans

                if isRepat:
                    question_data[qid] = question.copy()
                    print(f"更新题目：{qid}，答案：{question['answer']}")
                else:
                    question_key = f"Q{len(question_data) + 1}"
                    question_data[question_key] = question.copy()
                    print(f"新增题目：{question_key}，答案：{question['answer']}")

                with open(save_path, "w", encoding="utf-8") as f:
                    json.dump(question_data, f, ensure_ascii=False, indent=2)

                time.sleep(1 + random.uniform(0, 1))
                isClick = False
                while isClick == False:
                    isClick = wrongNextClick(window_config)



if __name__ == "__main__":
    quiz()