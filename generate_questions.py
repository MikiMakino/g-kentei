import anthropic
import json
import re
from pathlib import Path

client = anthropic.Anthropic()

CATEGORY_NAMES = {
    "ai": "AI概論",
    "ml": "機械学習",
    "dl": "ディープラーニング",
    "math": "数学・統計",
    "ethics": "法律・倫理",
}

SYSTEM_PROMPT = """あなたはG検定（JDLA）の試験問題作成の専門家です。
提供された学習ノートの内容から、試験に出やすい4択問題を作成してください。

出力は以下のJSON配列形式のみとし、他のテキストは含めないでください：
[
  {
    "question": "問題文",
    "options": ["選択肢A", "選択肢B", "選択肢C", "選択肢D"],
    "answer": 0,
    "explanation": "解説文（なぜその答えが正しいか）"
  }
]

ルール：
- answerは正解の選択肢のインデックス（0〜3）
- 問題は明確で試験に出やすい内容にする
- 解説は学習に役立つ具体的な内容にする
- JSON配列のみ出力（前後のテキスト不要）"""


def generate_questions(category: str, content: str, num: int = 5) -> list:
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=2048,
        system=[{
            "type": "text",
            "text": SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{
            "role": "user",
            "content": f"カテゴリ：{category}\n問題数：{num}問\n\n## 学習ノート\n\n{content}",
        }],
    )

    text = response.content[0].text
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError as e:
            print(f"  JSON解析エラー: {e}")
    return []


def main():
    docs_dir = Path(__file__).parent / "docs"
    output_file = Path(__file__).parent / "docs" / "quiz" / "questions.json"
    output_file.parent.mkdir(exist_ok=True)

    all_questions = []
    qid = 1

    for key, name in CATEGORY_NAMES.items():
        cat_dir = docs_dir / key
        if not cat_dir.exists():
            continue

        for md_file in sorted(cat_dir.glob("*.md")):
            content = md_file.read_text(encoding="utf-8").strip()
            if len(content) < 100 or content == "（作成中）":
                continue

            print(f"生成中: {md_file.relative_to(docs_dir)} ...", end=" ", flush=True)
            questions = generate_questions(name, content)

            for q in questions:
                q["id"] = qid
                q["category"] = name
                all_questions.append(q)
                qid += 1

            print(f"{len(questions)}問")

    output_file.write_text(
        json.dumps(all_questions, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n✓ 合計 {len(all_questions)}問生成 → {output_file}")


if __name__ == "__main__":
    main()
