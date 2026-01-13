"""API routes for admin operations (requires admin authentication)"""
from flask import jsonify, request
from flask_login import login_required, current_user
from app.blueprints.api import bp
from app.models.learning import CodingChallenge
from app.extensions import db
import json


def require_admin_api():
    """Check if current user is admin - for API endpoints"""
    if not current_user.is_authenticated:
        return jsonify({'error': 'Authentication required'}), 401
    if not current_user.is_admin:
        return jsonify({'error': 'Admin privileges required'}), 403
    return None


@bp.route('/admin/coding-challenges/bulk-add', methods=['POST'])
@login_required
def bulk_add_coding_challenges():
    """
    Add multiple coding challenges via API.
    Requires admin authentication.
    
    Request body (JSON):
    {
        "challenges": [
            {
                "title": "Challenge Title",
                "description": "Challenge description",
                "difficulty": "easy|medium|hard",
                "starter_code": "def function_name():\n    pass",
                "test_cases": [
                    {"input": "arg1, arg2", "expected_output": "result"}
                ],
                "points": 10
            },
            ...
        ]
    }
    
    Returns:
    {
        "success": true,
        "added": 5,
        "skipped": 2,
        "total": 7,
        "total_in_db": 15
    }
    """
    # Check admin status
    admin_check = require_admin_api()
    if admin_check:
        return admin_check
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        challenges_data = data.get('challenges', [])
        if not challenges_data:
            return jsonify({'error': 'No challenges provided in "challenges" array'}), 400
        
        if not isinstance(challenges_data, list):
            return jsonify({'error': '"challenges" must be an array'}), 400
        
        added = 0
        skipped = 0
        errors = []
        
        for idx, challenge_data in enumerate(challenges_data):
            try:
                # Validate required fields
                title = challenge_data.get('title', '').strip()
                description = challenge_data.get('description', '').strip()
                difficulty = challenge_data.get('difficulty', 'easy').lower()
                starter_code = challenge_data.get('starter_code', '')
                test_cases = challenge_data.get('test_cases', [])
                points = int(challenge_data.get('points', 10) or 10)
                
                if not title:
                    errors.append(f"Challenge {idx + 1}: Missing 'title'")
                    skipped += 1
                    continue
                
                if not description:
                    errors.append(f"Challenge {idx + 1} ({title}): Missing 'description'")
                    skipped += 1
                    continue
                
                if difficulty not in ['easy', 'medium', 'hard']:
                    difficulty = 'easy'  # Default to easy if invalid
                
                # Check if challenge with same title already exists
                existing = CodingChallenge.query.filter_by(title=title).first()
                if existing:
                    skipped += 1
                    continue
                
                # Create challenge
                challenge = CodingChallenge(
                    title=title,
                    description=description,
                    difficulty=difficulty,
                    starter_code=starter_code if starter_code else None,
                    test_cases_json=json.dumps(test_cases) if test_cases else json.dumps([]),
                    points=points,
                    is_active=True
                )
                db.session.add(challenge)
                added += 1
                
            except Exception as e:
                errors.append(f"Challenge {idx + 1}: {str(e)}")
                skipped += 1
                continue
        
        # Commit all changes
        db.session.commit()
        
        total_in_db = CodingChallenge.query.count()
        
        response = {
            'success': True,
            'added': added,
            'skipped': skipped,
            'total': len(challenges_data),
            'total_in_db': total_in_db
        }
        
        if errors:
            response['errors'] = errors[:10]  # Limit errors in response
            if len(errors) > 10:
                response['error_count'] = len(errors)
        
        return jsonify(response), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

