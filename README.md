claude codeのインストール
```
npm install -g @anthropic-ai/claude-code

```

インストールの確認

```
claude --version
```

権限バイパス付きの初期設定を実行
```
claude --dangerously-skip-permissions
```

今回はプロジェクトスコープではなく、ユーザースコープにより構成します。

ユーザースコープのMCPサーバーの保存場所を作成
```
mkdir -p ~/.claude-mcp-servers/
cd ~/.claude-mcp-servers/

git clone リポジトリ名
cd リポジトリ名

```

Python環境をuvで構築
```
# uvのインストール（まだインストールしていない場合）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 仮想環境の作成とアクティベート
uv venv
source .venv/bin/activate

# 依存パッケージのインストール
uv pip install -r requirements.txt
```

サーバーを実行可能にする
```
chmod +x server.py
```

グローバルユーザースコープで登録し、ユニバーサルアクセスを可能にする

```
claude mcp add --scope user rakuten_item_mcp ~/.claude-mcp-servers/rakuten_item_mcp/.venv/bin/python ~/.claude-mcp-servers/rakuten_item_mcp/server.py
```

登録を解除
```
claude mcp remove rakuten_item_mcp 
```

登録を確認するには以下のコマンドを打ちます。
```
claude mcp list
```

