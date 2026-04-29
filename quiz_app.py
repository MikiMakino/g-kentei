import json
import random
from pathlib import Path

import streamlit as st

# ── 問題データ読み込み ──────────────────────────────────────────
@st.cache_data
def load_questions():
    path = Path(__file__).parent / "docs" / "quiz" / "questions.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ── Session State 初期化（pybotと同じパターン）──────────────────
def init_state():
    defaults = {
        "started": False,
        "pool": [],
        "cur": 0,
        "score": 0,
        "answered": False,
        "selected": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ── アプリ本体 ──────────────────────────────────────────────────
st.title("🎓 G検定 クイズアプリ")
init_state()

questions = load_questions()

if not questions:
    st.error("問題データがありません。generate_questions.py を実行してください。")
    st.stop()


# ① スタート画面
if not st.session_state["started"]:
    cats = ["すべて"] + sorted({q["category"] for q in questions})
    cat = st.selectbox("カテゴリを選んでください", cats)

    src = questions if cat == "すべて" else [q for q in questions if q["category"] == cat]
    st.write(f"**{len(src)} 問** あります")

    if st.button("クイズを始める", type="primary"):
        pool = src.copy()
        random.shuffle(pool)
        st.session_state["pool"]     = pool
        st.session_state["cur"]      = 0
        st.session_state["score"]    = 0
        st.session_state["answered"] = False
        st.session_state["selected"] = None
        st.session_state["started"]  = True
        st.rerun()


# ② クイズ中 / 結果
else:
    pool = st.session_state["pool"]
    cur  = st.session_state["cur"]

    # ── 結果画面 ──────────────────────────────────────────────
    if cur >= len(pool):
        score = st.session_state["score"]
        total = len(pool)
        pct   = round(score / total * 100)

        st.markdown(f"## 結果：{pct}%")
        st.markdown(f"**{score} / {total} 問 正解**")

        if pct >= 80:
            st.success("合格ライン到達！この調子で！")
        elif pct >= 60:
            st.warning("もう少し！苦手な章を復習しよう")
        else:
            st.error("ノートを読み返してから再チャレンジ！")

        if st.button("もう一度挑戦する"):
            st.session_state["started"] = False
            st.rerun()

    # ── 問題画面 ──────────────────────────────────────────────
    else:
        q      = pool[cur]
        labels = ["A", "B", "C", "D"]

        st.progress(cur / len(pool))
        st.caption(f"{cur + 1} / {len(pool)} 問　｜　カテゴリ：{q['category']}")
        st.markdown(f"### {q['question']}")

        # 未回答：選択肢ボタンを表示（pybotのtext_input→ボタンに対応）
        if not st.session_state["answered"]:
            for i, opt in enumerate(q["options"]):
                if st.button(f"{labels[i]}．{opt}", key=f"opt_{i}"):
                    st.session_state["selected"]  = i
                    st.session_state["answered"]  = True
                    if i == q["answer"]:
                        st.session_state["score"] += 1
                    st.rerun()

        # 回答済：正誤表示＋解説（pybotのresponse表示に対応）
        else:
            selected = st.session_state["selected"]
            for i, opt in enumerate(q["options"]):
                if i == q["answer"]:
                    st.success(f"✓ {labels[i]}．{opt}")
                elif i == selected:
                    st.error(f"✗ {labels[i]}．{opt}")
                else:
                    st.write(f"　 {labels[i]}．{opt}")

            if selected == q["answer"]:
                st.info(f"○ 正解！\n\n{q['explanation']}")
            else:
                st.warning(f"× 不正解\n\n{q['explanation']}")

            label = "次の問題 →" if cur + 1 < len(pool) else "結果を見る"
            if st.button(label, type="primary"):
                st.session_state["cur"]      += 1
                st.session_state["answered"]  = False
                st.session_state["selected"]  = None
                st.rerun()
