with open('app.py', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'def apply_action_required_health_badge_rules' in line:
            print(f"FOUND AT: {i+1}")
