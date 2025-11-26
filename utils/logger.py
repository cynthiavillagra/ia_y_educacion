"""
Admin action logging utility
Logs all admin actions for auditing purposes
"""
import json
from datetime import datetime
import os

LOG_FILE = os.path.join(os.path.dirname(__file__), '..', 'admin_actions.log')

def log_admin_action(action: str, user_id: str, resource_id: str = None, details: dict = None):
    """
    Log an admin action
    
    Args:
        action: Action performed (CREATE, UPDATE, DELETE)
        user_id: ID of the user performing the action
        resource_id: ID of the affected resource (if applicable)
        details: Additional details about the action
    """
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'action': action,
        'user_id': user_id,
        'resource_id': resource_id,
        'details': details or {}
    }
    
    try:
        # Append to log file
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        # Don't fail the request if logging fails
        print(f'Warning: Failed to log admin action: {e}')


def get_user_id_from_token(headers) -> str:
    """
    Extract user ID from authorization token
    For now, returns 'admin' - can be enhanced to decode JWT
    """
    # TODO: Decode JWT to get actual user ID
    auth_header = headers.get('Authorization', '')
    if auth_header:
        # For now, just return 'admin'
        # In production, decode JWT and extract user_id
        return 'admin'
    return 'unknown'
