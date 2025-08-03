from pydantic import BaseModel

class QuesResponse(BaseModel):
    answer: str

def model_reply(client, question):
    completion = client.beta.chat.completions.parse(
        model = "doubao-seed-1-6-flash-250615",
        messages = [
            {"role": "system", "content": "你精通科学百科知识,回答只包含答案A/B/C/D中的一个,不需要解释"},
            {"role": "user", "content": question},
        ],
        response_format=QuesResponse,
        extra_body={
            "thinking": {
                "type": "disabled"
            }
        }
    )
    resp = completion.choices[0].message.parsed
    ans = resp.model_dump()
    print("答案：", ans["answer"])
    return ans