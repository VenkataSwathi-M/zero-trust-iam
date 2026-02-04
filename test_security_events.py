from iam_core.events.security_event_listener import SecurityEventListener

listener = SecurityEventListener()

result = listener.handle_event(
    event_type="anomaly_detected",
    metadata={
        "source_ip": "192.168.1.10",
        "trust_decay": 0.3
    }
)

print("Security Event Result:")
print(result)