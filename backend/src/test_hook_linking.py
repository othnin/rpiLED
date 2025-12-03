#!/usr/bin/env python3
"""
Comprehensive test of hook-pattern linking system
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
    print("=" * 70)
    print("COMPREHENSIVE HOOK-PATTERN LINKING TEST")
    print("=" * 70)
    print()
    
    # Test 1: List all patterns
    print("TEST 1: List all patterns")
    print("-" * 70)
    resp = send_command("list_patterns")
    if resp.get("ok"):
        patterns = resp.get("result", [])
        print(f"✓ Found {len(patterns)} patterns:")
        for p in patterns:
            print(f"  - {p}")
    else:
        print(f"✗ Error: {resp.get('error')}")
    print()
    
    # Test 2: List all hooks
    print("TEST 2: List all hooks")
    print("-" * 70)
    resp = send_command("list_hooks")
    if resp.get("ok"):
        hooks = resp.get("result", [])
        print(f"✓ Found {len(hooks)} hooks:")
        for h in hooks:
            print(f"  - {h}")
    else:
        print(f"✗ Error: {resp.get('error')}")
    print()
    
    # Test 3: Check initial hook-pattern links (should be empty)
    print("TEST 3: Check initial hook-pattern links")
    print("-" * 70)
    resp = send_command("list_hook_pattern_links")
    if resp.get("ok"):
        links = resp.get("result", {})
        linked_count = sum(1 for v in links.values() if v is not None)
        print(f"✓ {linked_count} hooks currently linked")
        for hook, pattern in sorted(links.items()):
            status = f"→ {pattern}" if pattern else "(not linked)"
            print(f"  - {hook}: {status}")
    else:
        print(f"✗ Error: {resp.get('error')}")
    print()
    
    # Test 4: Link a hook to a pattern
    print("TEST 4: Link cpu_over_20 hook to Knight Rider Pattern")
    print("-" * 70)
    resp = send_command("link_hook_to_pattern", {
        "hook_event_name": "cpu_over_20",
        "pattern_name": "Knight Rider Pattern"
    })
    if resp.get("ok"):
        print(f"✓ {resp.get('result')}")
    else:
        print(f"✗ Error: {resp.get('error')}")
    print()
    
    # Test 5: Link another hook
    print("TEST 5: Link cpu_over_50 hook to Loading Bar Pattern")
    print("-" * 70)
    resp = send_command("link_hook_to_pattern", {
        "hook_event_name": "cpu_over_50",
        "pattern_name": "Loading Bar Pattern"
    })
    if resp.get("ok"):
        print(f"✓ {resp.get('result')}")
    else:
        print(f"✗ Error: {resp.get('error')}")
    print()
    
    # Test 6: Verify links were created
    print("TEST 6: Verify links were created")
    print("-" * 70)
    resp = send_command("list_hook_pattern_links")
    if resp.get("ok"):
        links = resp.get("result", {})
        linked_count = sum(1 for v in links.values() if v is not None)
        print(f"✓ {linked_count} hooks now linked:")
        for hook, pattern in sorted(links.items()):
            status = f"→ {pattern}" if pattern else "(not linked)"
            print(f"  - {hook}: {status}")
    else:
        print(f"✗ Error: {resp.get('error')}")
    print()
    
    # Test 7: Unlink a hook
    print("TEST 7: Unlink cpu_over_20 hook")
    print("-" * 70)
    resp = send_command("unlink_hook", {
        "hook_event_name": "cpu_over_20"
    })
    if resp.get("ok"):
        print(f"✓ {resp.get('result')}")
    else:
        print(f"✗ Error: {resp.get('error')}")
    print()
    
    # Test 8: Verify unlink
    print("TEST 8: Verify unlink")
    print("-" * 70)
    resp = send_command("list_hook_pattern_links")
    if resp.get("ok"):
        links = resp.get("result", {})
        linked_count = sum(1 for v in links.values() if v is not None)
        print(f"✓ {linked_count} hooks now linked:")
        for hook, pattern in sorted(links.items()):
            status = f"→ {pattern}" if pattern else "(not linked)"
            print(f"  - {hook}: {status}")
    else:
        print(f"✗ Error: {resp.get('error')}")
    print()
    
    # Test 9: Test error conditions
    print("TEST 9: Test error conditions")
    print("-" * 70)
    
    # Try to link non-existent hook
    print("Attempt 1: Link non-existent hook")
    resp = send_command("link_hook_to_pattern", {
        "hook_event_name": "fake_hook",
        "pattern_name": "Knight Rider Pattern"
    })
    if resp.get("ok"):
        print(f"✗ Should have failed but succeeded")
    else:
        print(f"✓ Correctly rejected: {resp.get('error')}")
    
    # Try to link to non-existent pattern
    print("\nAttempt 2: Link to non-existent pattern")
    resp = send_command("link_hook_to_pattern", {
        "hook_event_name": "cpu_over_75",
        "pattern_name": "Fake Pattern"
    })
    if resp.get("ok"):
        print(f"✗ Should have failed but succeeded")
    else:
        print(f"✓ Correctly rejected: {resp.get('error')}")
    print()
    
    print("=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
