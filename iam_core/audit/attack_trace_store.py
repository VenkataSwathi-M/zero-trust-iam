ATTACK_TRACES = {}

def save_trace(session_id, trace):
    ATTACK_TRACES[session_id] = trace

def get_trace(session_id):
    return ATTACK_TRACES.get(session_id)