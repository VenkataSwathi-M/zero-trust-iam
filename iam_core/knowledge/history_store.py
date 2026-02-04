SECURITY_HISTORY = []

def store_event(event):
    SECURITY_HISTORY.append(event)

def get_recent_events(limit=10):
    return SECURITY_HISTORY[-limit:]