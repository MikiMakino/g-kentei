# G検定 学習ノート

MkDocs Material で作成した G検定対策ノートと、クイズアプリです。

## セットアップ

このプロジェクトは `uv` を使う想定です。

```powershell
uv sync
```

## MkDocs

ローカルで資料を確認します。

```powershell
uv run mkdocs serve
```

静的サイトを生成します。

```powershell
uv run mkdocs build --strict
```

## クイズアプリ

Streamlit 版のクイズアプリを起動します。

```powershell
uv run streamlit run quiz_app.py
```

## 問題生成

`generate_questions.py` は Anthropic API を使って `docs/quiz/questions.json` を生成します。
実行前に `ANTHROPIC_API_KEY` を設定してください。

```powershell
$env:ANTHROPIC_API_KEY="..."
uv run python generate_questions.py
```

## チートシートPDF生成

`docs/assets/sheets/*.png` を、A4縦・1画像1ページのPDFに変換します。PowerShell 7 (`pwsh`) で実行してください。

```powershell
pwsh -ExecutionPolicy Bypass -File scripts/png_to_pdf.ps1
```

生成先:

- `docs/assets/sheets/pdf/g-kentei-cheatsheets.pdf`
- `docs/assets/sheets/pdf/*.pdf`
