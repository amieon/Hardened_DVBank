from flask import Blueprint, request, jsonify
from models import db, User, Transaction
from datetime import datetime
from decimal import Decimal
from auth import token_required

transaction_bp = Blueprint('transaction', __name__)

@transaction_bp.route('/api/transfer', methods=['POST'])
@token_required
def transfer(current_user):
    data = request.get_json()
    to_user_id = data.get('to_user_id')

    # 1. 金额合法性校验：必须是正数、最多两位小数
    try:
        amount = Decimal(str(data.get('amount', 0))).quantize(Decimal('0.01'))
    except Exception:
        return jsonify({'error': 'Invalid amount'}), 400
    if amount <= 0:
        return jsonify({'error': 'Amount must be positive'}), 400

    # 2. 收款方校验：必须存在，且不能转给自己
    receiver = User.query.get(to_user_id)
    if not receiver:
        return jsonify({'error': 'Receiver not found'}), 404
    if receiver.id == current_user.id:
        return jsonify({'error': 'Cannot transfer to self'}), 400

    # 3. 余额校验
    if current_user.balance < amount:
        return jsonify({'error': 'Insufficient balance'}), 400

    # 4. 扣款、入账、写记录置于同一事务，失败回滚
    try:
        current_user.balance -= amount
        receiver.balance += amount
        transaction = Transaction(
            sender_id=current_user.id,
            receiver_id=receiver.id,
            amount=amount,
            description=data.get('description', ''),
            status='completed',
            completed_at=datetime.utcnow()
        )
        db.session.add(transaction)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Transfer failed'}), 500

    return jsonify({'message': 'Transfer successful', 'transaction': transaction.to_dict()})

@transaction_bp.route('/api/transactions', methods=['GET'])
@token_required
def get_transactions(current_user):
    user_id = current_user.id

    from sqlalchemy import text
    query = text('SELECT * FROM "transaction" WHERE sender_id = :uid OR receiver_id = :uid ORDER BY created_at DESC')
    result = db.session.execute(query, {"uid": user_id})
    transactions = result.fetchall()
    
    return jsonify([{
        'id': t[0],
        'sender_id': t[1],
        'receiver_id': t[2], 
        'amount': float(t[3]),
        'description': t[4],
        'status': t[5],
        'created_at': t[6],
        'completed_at': t[7]
    } for t in transactions])

@transaction_bp.route('/api/transactions/<int:transaction_id>', methods=['GET'])
@token_required
def get_transaction(current_user, transaction_id):
    transaction = Transaction.query.get(transaction_id)
    
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404
        
    if transaction.sender_id != current_user.id and transaction.receiver_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    return jsonify({
        'id': transaction.id,
        'sender_id': transaction.sender_id,
        'receiver_id': transaction.receiver_id,
        'amount': float(transaction.amount),
        'description': transaction.description,
        'status': transaction.status,
        'created_at': transaction.created_at.isoformat(),
        'completed_at': transaction.completed_at.isoformat() if transaction.completed_at else None
    })

@transaction_bp.route('/api/transactions/search', methods=['GET'])
@token_required
def search_transactions(current_user):
    search_term = request.args.get('description', '')
    
    # VULNERABLE CODE: Direct string concatenation in SQL query
    # This is deliberately vulnerable to SQL injection for educational purposes
    query = f"SELECT * FROM \"transaction\" WHERE (sender_id = {current_user.id} OR receiver_id = {current_user.id}) AND description LIKE '%{search_term}%'"
    
    result = db.session.execute(query)
    transactions = result.fetchall()
    
    transaction_list = []
    for t in transactions:
        transaction_list.append({
            'id': t[0],
            'sender_id': t[1],
            'receiver_id': t[2], 
            'amount': float(t[3]),
            'description': t[4],
            'status': t[5],
            'created_at': t[6],
            'completed_at': t[7]
        })
    
    return jsonify(transaction_list) 