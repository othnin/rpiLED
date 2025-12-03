#!/usr/bin/env python3
"""
Simple IPC client to test the backend functionality
"""
import socket
import json


def send_command(action, params=None, socket_path="/tmp/wopr.sock"):
    """Send a command to the IPC server and print the response."""
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(socket_path)
        
        request = {"action": action}
        if params:
            request["params"] = params
        
        sock.sendall(json.dumps(request).encode("utf-8"))
        sock.shutdown(socket.SHUT_WR)
        
        # Read response
        data = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
        
        sock.close()
        
        response = json.loads(data.decode("utf-8"))
        return response
        
    except Exception as e:
        return {"ok": False, "error": str(e)}


if __name__ == "__main__":
    print("Testing IPC commands...")
    print()
    
    # Test list_patterns
    print("1. list_patterns:")
    resp = send_command("list_patterns")
    print(json.dumps(resp, indent=2))
    print()
    
    # Test list_hooks
    print("2. list_hooks:")
    resp = send_command("list_hooks")
    print(json.dumps(resp, indent=2))
    print()
    
    # Test list_startup
    print("3. list_startup:")
    resp = send_command("list_startup")
    print(json.dumps(resp, indent=2))
    print()
    
    # Test list_hook_pattern_links
    print("4. list_hook_pattern_links:")
    resp = send_command("list_hook_pattern_links")
    print(json.dumps(resp, indent=2))
    print()
    
    # Test status
    print("5. status:")
    resp = send_command("status")
    print(json.dumps(resp, indent=2))
    print()
    
    # Test link_hook_to_pattern (if patterns/hooks exist)
    print("6. Attempting to link a hook to a pattern...")
    resp = send_command("link_hook_to_pattern", {
        "hook_event_name": "cpu_over_20",
        "pattern_name": "Knight Rider Pattern"
    })
    print(json.dumps(resp, indent=2))
    print()
    
    # Test list_hook_pattern_links again to see the link
    print("7. list_hook_pattern_links (after link):")
    resp = send_command("list_hook_pattern_links")
    print(json.dumps(resp, indent=2))
