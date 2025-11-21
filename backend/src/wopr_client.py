#!/usr/bin/env python3
"""
WOPR Client - Easy command-line interface to control the daemon
Usage: ./wopr_client.py <command> [args]
"""

import socket
import json
import sys
import argparse


SOCKET_PATH = "/tmp/wopr.sock"


def send_command(action, params=None):
    """Send command to daemon and return response"""
    try:
        # Create socket
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(SOCKET_PATH)
        
        # Build command
        command = {"action": action}
        if params:
            command["params"] = params
        
        # Send command
        client.sendall(json.dumps(command).encode('utf-8'))
        
        # Close write side (signals EOF to server)
        client.shutdown(socket.SHUT_WR)
        
        # Receive response
        response = b""
        while True:
            chunk = client.recv(4096)
            if not chunk:
                break
            response += chunk
        
        client.close()
        
        return json.loads(response.decode('utf-8'))
    
    except FileNotFoundError:
        return {
            "ok": False,
            "error": f"Daemon not running (socket not found: {SOCKET_PATH})"
        }
    except ConnectionRefusedError:
        return {
            "ok": False,
            "error": "Connection refused. Is the daemon running?"
        }
    except Exception as e:
        return {
            "ok": False,
            "error": f"Error: {str(e)}"
        }


def main():
    parser = argparse.ArgumentParser(
        description="Control NeoPixel patterns via daemon",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list                    # List all available patterns
  %(prog)s start "Rainbow Cycle"   # Start a pattern
  %(prog)s stop                    # Stop current pattern
  %(prog)s status                  # Show daemon status
        """
    )
    
    parser.add_argument(
        'command',
        choices=['list', 'start', 'stop', 'status'],
        help='Command to execute'
    )
    
    parser.add_argument(
        'pattern',
        nargs='?',
        help='Pattern name (for start command)'
    )
    
    args = parser.parse_args()
    
    # Execute command
    if args.command == 'list':
        response = send_command("list_patterns")
        if response.get('ok'):
            patterns = response.get('result', [])
            print(f"Available patterns ({len(patterns)}):")
            for pattern in patterns:
                print(f"  • {pattern}")
        else:
            print(f"Error: {response.get('error')}")
            sys.exit(1)
    
    elif args.command == 'start':
        if not args.pattern:
            print("Error: Pattern name required")
            print("Usage: wopr_client.py start <pattern_name>")
            sys.exit(1)
        
        response = send_command("start_pattern", {"name": args.pattern})
        if response.get('ok'):
            print(f"✓ Started pattern: {args.pattern}")
        else:
            print(f"✗ Error: {response.get('error')}")
            sys.exit(1)
    
    elif args.command == 'stop':
        response = send_command("stop_pattern")
        if response.get('ok'):
            print(f"✓ Pattern stopped")
        else:
            print(f"✗ Error: {response.get('error')}")
            sys.exit(1)
    
    elif args.command == 'status':
        response = send_command("status")
        if response.get('ok'):
            result = response.get('result', {})
            current = result.get('current_pattern')
            print(f"Status:")
            print(f"  Current pattern: {current if current else 'None'}")
        else:
            print(f"Error: {response.get('error')}")
            sys.exit(1)


if __name__ == "__main__":
    main()