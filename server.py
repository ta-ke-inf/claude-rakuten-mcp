#!/usr/bin/env python3
"""
Claude Code統合のためのカスタムMCPサーバー
"""


import json
import sys
import os
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()  

# 適切なMCP通信のためにバッファリングなしの出力を保証
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1)
sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 1)

def send_response(response: Dict[str, Any]):
    """Claude CodeにJSON-RPCレスポンスを送信"""
    print(json.dumps(response), flush=True)

def handle_initialize(request_id: Any) -> Dict[str, Any]:
    """MCP初期化ハンドシェイクを処理"""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "my-custom-server",
                "version": "1.0.0"
            }
        }
    }

def handle_tools_list(request_id: Any) -> Dict[str, Any]:
    """Claude Codeのために利用可能なツールをリストアップ"""
    tools = [
        {
            "name": "hello_world",
            "description": "簡単なデモンストレーションツール",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "挨拶する名前"
                    }
                },
                "required": ["name"]
            }
        },
        {
            "name": "rakuten_search",
            "description": "楽天市場で商品を検索します",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "検索キーワード"
                    },
                    "genre_id": {
                        "type": "string",
                        "description": "ジャンルID(オプション)"
                    },
                    "price_min": {
                        "type": "integer",
                        "description": "最低価格(オプション)"
                    },
                    "price_max": {
                        "type": "integer",
                        "description": "最高価格(オプション)"
                    },
                    "sort": {
                        "type": "string",
                        "description": "ソート順(オプション): +itemPrice(価格昇順), -itemPrice(価格降順), +reviewCount(レビュー数昇順), -reviewCount(レビュー数降順), +reviewAverage(レビュー平均昇順), -reviewAverage(レビュー平均降順)",
                        "default": "+itemPrice"
                    }
                },
                "required": ["keyword"]
            }
        }
    ]

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "tools": tools
        }
    }

def search_rakuten_products(keyword: str, genre_id: Optional[str] = None, 
                           price_min: Optional[int] = None, price_max: Optional[int] = None,
                           sort: str = "+itemPrice") -> Dict[str, Any]:
    """楽天商品検索APIを使用して商品を検索"""
    app_id = os.getenv("RAKUTEN_APPLICATION_ID")
    if app_id == "your_app_id":
        raise ValueError("楽天アプリケーションIDが設定されていません。.envファイルでRAKUTEN_APPLICATION_IDを設定してください。")
    
    url = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20220601"
    params = {
        "applicationId": app_id,
        "keyword": keyword,
        "format": "json",
        "hits": 30,
        "sort": sort
    }
    
    if genre_id:
        params["genreId"] = genre_id
    if price_min:
        params["minPrice"] = price_min
    if price_max:
        params["maxPrice"] = price_max
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise ValueError(f"APIリクエストエラー: {str(e)}")

def format_rakuten_results(api_response: Dict[str, Any]) -> str:
    """楽天APIのレスポンスをフォーマット"""
    if "Items" not in api_response or not api_response["Items"]:
        return "検索結果が見つかりませんでした。"
    
    results = []
    results.append(f"検索結果: {api_response['count']}件見つかりました\n")
    
    for i, item_data in enumerate(api_response["Items"][:10], 1):  # 上位10件を表示
        item = item_data["Item"]
        
        name = item.get("itemName", "N/A")
        price = item.get("itemPrice", 0)
        shop_name = item.get("shopName", "N/A")
        review_count = item.get("reviewCount", 0)
        review_average = item.get("reviewAverage", 0)
        item_url = item.get("itemUrl", "")
        
        results.append(f"{i}. {name}")
        results.append(f"   価格: ¥{price:,}")
        results.append(f"   ショップ: {shop_name}")
        if review_count > 0:
            results.append(f"   レビュー: {review_average:.1f}/5.0 ({review_count}件)")
        results.append(f"   URL: {item_url}")
        results.append("")
    
    return "\n".join(results)

def handle_tool_call(request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
    """Claude Codeからのツール呼び出しを実行"""
    tool_name = params.get("name")
    arguments = params.get("arguments", {})

    try:
        if tool_name == "hello_world":
            name = arguments.get("name", "World")
            result = f"Hello, {name}! Your MCP server is working perfectly."
        elif tool_name == "rakuten_search":
            keyword = arguments.get("keyword")
            if not keyword:
                raise ValueError("検索キーワードが必要です")
            
            genre_id = arguments.get("genre_id")
            price_min = arguments.get("price_min")
            price_max = arguments.get("price_max")
            sort = arguments.get("sort", "+itemPrice")
            
            # 環境変数を読み込み
            try:
                with open(".env", "r") as f:
                    for line in f:
                        if line.strip() and not line.startswith("#"):
                            key, value = line.strip().split("=", 1)
                            os.environ[key] = value
            except FileNotFoundError:
                pass
            
            api_response = search_rakuten_products(keyword, genre_id, price_min, price_max, sort)
            result = format_rakuten_results(api_response)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": result
                    }
                ]
            }
        }
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32603,
                "message": str(e)
            }
        }

def main():
    """JSON-RPC通信を処理するメインサーバーループ"""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break

            request = json.loads(line.strip())
            method = request.get("method")
            request_id = request.get("id")
            params = request.get("params", {})

            if method == "initialize":
                response = handle_initialize(request_id)
            elif method == "tools/list":
                response = handle_tools_list(request_id)
            elif method == "tools/call":
                response = handle_tool_call(request_id, params)
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }

            send_response(response)

        except json.JSONDecodeError:
            continue
        except EOFError:
            break
        except Exception as e:
            if 'request_id' in locals():
                send_response({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                })

if __name__ == "__main__":
    app_id = os.getenv("RAKUTEN_APPLICATION_ID")
    main()
