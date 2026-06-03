from flask import Flask, request, jsonify, render_template
from models import db, Goal, Deposit
from datetime import datetime
import os

app = Flask(__name__)

# DB設定：環境変数 DATABASE_URL があれば使う（Render PostgreSQL）、なければSQLite
database_url = os.environ.get('DATABASE_URL', 'sqlite:///savings.db')
# RenderのPostgreSQL URLは postgres:// だが SQLAlchemy は postgresql:// が必要
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


# ── ページ ──────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')


# ── API：目標一覧 ────────────────────────
@app.route('/api/goals', methods=['GET'])
def get_goals():
    goals = Goal.query.order_by(Goal.created_at).all()
    return jsonify([g.to_dict() for g in goals])


# ── API：目標追加 ────────────────────────
@app.route('/api/goals', methods=['POST'])
def add_goal():
    data = request.json
    name   = data.get('name', '').strip()
    target = data.get('target')
    if not name or not target or float(target) <= 0:
        return jsonify({'error': '入力が不正です'}), 400
    goal = Goal(name=name, target=float(target))
    db.session.add(goal)
    db.session.commit()
    return jsonify(goal.to_dict()), 201


# ── API：目標編集 ────────────────────────
@app.route('/api/goals/<int:goal_id>', methods=['PUT'])
def update_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    data = request.json
    name   = data.get('name', '').strip()
    target = data.get('target')
    if not name or not target or float(target) <= 0:
        return jsonify({'error': '入力が不正です'}), 400
    goal.name   = name
    goal.target = float(target)
    db.session.commit()
    return jsonify(goal.to_dict())


# ── API：目標削除 ────────────────────────
@app.route('/api/goals/<int:goal_id>', methods=['DELETE'])
def delete_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    db.session.delete(goal)
    db.session.commit()
    return jsonify({'ok': True})


# ── API：入金 ───────────────────────────
@app.route('/api/goals/<int:goal_id>/deposits', methods=['POST'])
def add_deposit(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    data   = request.json
    amount = data.get('amount')
    memo   = data.get('memo', '').strip()
    if not amount or float(amount) <= 0:
        return jsonify({'error': '金額が不正です'}), 400
    deposit = Deposit(goal_id=goal_id, amount=float(amount), memo=memo)
    goal.saved += float(amount)
    db.session.add(deposit)
    db.session.commit()
    return jsonify(goal.to_dict()), 201


# ── API：入金履歴 ───────────────────────
@app.route('/api/goals/<int:goal_id>/deposits', methods=['GET'])
def get_deposits(goal_id):
    Goal.query.get_or_404(goal_id)
    deposits = Deposit.query.filter_by(goal_id=goal_id).order_by(Deposit.created_at.desc()).all()
    return jsonify([d.to_dict() for d in deposits])


port = int(os.environ.get("PORT", 5000))
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True)