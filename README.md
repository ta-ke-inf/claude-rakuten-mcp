# 楽天商品検索 MCP サーバー

Claude Code と連携して楽天市場の商品検索機能を提供するカスタム MCP サーバーです。

## 🚀 機能

- 楽天市場での商品検索
- 価格・ジャンル・レビューでの絞り込み
- Claude Code からの直接利用

## 📋 前提条件

- Python 3.8+
- uv パッケージマネージャー
- Claude Code CLI
- 楽天デベロッパーアカウント

## 🛠 セットアップ

### 1. Claude Code のインストール

```bash
npm install -g @anthropic-ai/claude-code
```

インストール確認：
```bash
claude --version
```

### 2. プロジェクトのセットアップ

```bash
# MCP サーバー用ディレクトリの作成
mkdir -p ~/.claude-mcp-servers/
cd ~/.claude-mcp-servers/

# リポジトリのクローン
git clone git@github.com:ta-ke-inf/rakuten-item-mcp.git
cd rakuten-item-mcp
```

### 3. Python 環境の構築

```bash
# uv のインストール（未インストールの場合）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 仮想環境の作成とアクティベート
uv venv
source .venv/bin/activate

# 依存パッケージのインストール
uv pip install -r requirements.txt

# サーバーを実行可能にする
chmod +x server.py
```

### 4. 環境変数の設定

```bash
# 環境変数ファイルの作成
cp .env.sample .env
```

`.env` ファイルを編集し、楽天アプリケーション ID を設定：
```env
RAKUTEN_APPLICATION_ID=your_rakuten_app_id_here
```

> 💡 楽天アプリケーション ID の取得方法：
> 1. [楽天デベロッパーサイト](https://webservice.rakuten.co.jp/) にアクセス
> 2. アカウント作成・ログイン
> 3. 「アプリ ID 発行」でアプリケーション ID を取得

### 5. Claude Code への登録

```bash
# MCP サーバーをユーザースコープで登録
claude mcp add --scope user rakuten-item-mcp \
  ~/.claude-mcp-servers/rakuten-item-mcp/.venv/bin/python \
  ~/.claude-mcp-servers/rakuten-item-mcp/server.py

# 権限バイパス付きの初期設定（必要に応じて）
claude --dangerously-skip-permissions
```

## 📖 使用方法

Claude Code を起動後、以下のようなコマンドで楽天商品検索が利用できます：

```
楽天でノートパソコンを検索して
```

```
5万円以下のディスプレイを探して
```

## 🔧 管理コマンド

```bash
# 登録状況の確認
claude mcp list

# MCP サーバーの削除
claude mcp remove rakuten-item-mcp
```

## 📂 プロジェクト構造

```
rakuten-item-mcp/
├── README.md           # このファイル
├── server.py          # MCP サーバーのメイン実装
├── requirements.txt   # Python 依存関係
├── .env.sample       # 環境変数のサンプル
└── .env              # 実際の環境変数（要作成）
```

## 🐛 トラブルシューティング

### よくある問題

1. **楽天 API エラー**: `.env` ファイルのアプリケーション ID を確認
2. **Python 環境エラー**: 仮想環境がアクティベートされているか確認
3. **Claude Code 認識エラー**: MCP サーバーが正しく登録されているか `claude mcp list` で確認

