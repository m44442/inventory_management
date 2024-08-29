from flask import Flask, request, jsonify
from typing import Dict, List
import re

app = Flask(__name__)

# インメモリデータストア（データベースの代わりに使用）
stocks: Dict[str, int] = {}  # 商品名と在庫数を保持
total_sales: float = 0.0     # 総売上額を保持

def validate_name(name: str) -> bool:
    """
    商品名のバリデーション
    1-8文字のアルファベットのみを許可
    """
    return bool(re.match(r'^[a-zA-Z]{1,8}$', name))

@app.route('/v1/stocks', methods=['POST'])
def update_stock():
    """
    在庫の更新・作成エンドポイント
    POSTリクエストで商品名と数量を受け取り、在庫を更新
    """
    data = request.json
    name = data.get('name')
    amount = data.get('amount', 1)  # amountが指定されていない場合は1とする

    # 入力値のバリデーション
    if not validate_name(name) or not isinstance(amount, int) or amount <= 0:
        return jsonify({"message": "ERROR"}), 400

    # 在庫の更新
    stocks[name] = stocks.get(name, 0) + amount
    return jsonify({"name": name, "amount": amount}), 200

@app.route('/v1/stocks', methods=['GET'])
@app.route('/v1/stocks/<name>', methods=['GET'])
def check_stock(name=None):
    """
    在庫チェックエンドポイント
    GETリクエストで全商品または指定商品の在庫を返す
    """
    if name:
        if not validate_name(name):
            return jsonify({"message": "ERROR"}), 400
        return jsonify({name: stocks.get(name, 0)}), 200
    else:
        # 在庫がある商品のみを返す（商品名でソート）
        return jsonify({k: v for k, v in sorted(stocks.items()) if v > 0}), 200

@app.route('/v1/sales', methods=['POST'])
def sell_item():
    """
    販売エンドポイント
    POSTリクエストで商品名、数量、価格を受け取り、販売処理を行う
    """
    global total_sales
    data = request.json
    name = data.get('name')
    amount = data.get('amount', 1)
    price = data.get('price')

    # 入力値のバリデーション
    if not validate_name(name) or not isinstance(amount, int) or amount <= 0:
        return jsonify({"message": "ERROR"}), 400

    if price is not None and (not isinstance(price, (int, float)) or price <= 0):
        return jsonify({"message": "ERROR"}), 400

    # 在庫チェック
    if stocks.get(name, 0) < amount:
        return jsonify({"message": "ERROR"}), 400

    # 在庫の減少と売上の計算
    stocks[name] -= amount
    if price is not None:
        total_sales += price * amount

    return jsonify({"name": name, "amount": amount}), 200

@app.route('/v1/sales', methods=['GET'])
def check_sales():
    """
    売上チェックエンドポイント
    GETリクエストで総売上額を返す
    """
    return jsonify({"sales": round(total_sales, 2)}), 200

@app.route('/v1/stocks', methods=['DELETE'])
def delete_all():
    """
    全データ削除エンドポイント
    DELETEリクエストで全ての在庫と売上データを削除
    """
    global total_sales
    stocks.clear()
    total_sales = 0.0
    return '', 204

if __name__ == '__main__':
    # アプリケーションの起動
    # 0.0.0.0はすべてのネットワークインターフェースでリッスンすることを意味する
    app.run(host='0.0.0.0', port=8080)

