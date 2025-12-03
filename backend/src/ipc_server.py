"""
IPC server using a Unix domain socket to control PatternManager from other processes.
Simple JSON request/response protocol.

Requests: JSON object with `action` and optional `params`.
Responses: JSON object with `ok` (bool), `result` or `error`.

Example request:
  {"action": "start_pattern", "params": {"name": "Loading Bar Pattern"}}

Example response:
  {"ok": true, "result": "started"}

Supported actions:
  - list_patterns
  - list_hooks
  - list_hook_pattern_links (returns available hooks and current pattern links)
  - start_pattern {name}
  - stop_pattern
  - stop_all
  - status
  - register_startup {name}
  - unregister_startup {name}
  - list_startup
  - link_hook_to_pattern {hook_event_name, pattern_name}
  - unlink_hook {hook_event_name}
  - trigger_test_hook (triggers the test hook for testing)
  - add_persistent_link {hook_event_name, pattern_name}
  - remove_persistent_link {hook_event_name}
  - list_persistent_links
  - add_pattern_to_startup {pattern_name}
  - remove_pattern_from_startup {pattern_name}
  - list_startup_patterns
  - shutdown (stops manager patterns and stops the server)

This server is intentionally small and dependency-free.
"""

import os
import socket
import threading
import json
import traceback
from typing import Any


class IPCServer(threading.Thread):
    def __init__(self, manager, socket_path: str = "/tmp/wopr.sock"):
        super().__init__(daemon=True)
        self.manager = manager
        self.socket_path = socket_path
        self._stop_event = threading.Event()
        self._sock = None

    def run(self):
        # Remove stale socket
        try:
            if os.path.exists(self.socket_path):
                os.remove(self.socket_path)
        except Exception:
            pass

        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        # Set permissions after binding; some systems require umask handling
        try:
            self._sock.bind(self.socket_path)
        except Exception as e:
            print(f"IPC: failed to bind socket {self.socket_path}: {e}")
            return

        # Allow other users in same group to access the socket if desired
        try:
            os.chmod(self.socket_path, 0o666)
        except Exception:
            pass

        self._sock.listen(1)
        print(f"IPC: listening on {self.socket_path}")

        while not self._stop_event.is_set():
            try:
                self._sock.settimeout(1.0)
                conn, _ = self._sock.accept()
            except socket.timeout:
                continue
            except Exception as e:
                if not self._stop_event.is_set():
                    print(f"IPC: accept error: {e}")
                break

            with conn:
                try:
                    data = b""
                    # read until EOF
                    while True:
                        chunk = conn.recv(4096)
                        if not chunk:
                            break
                        data += chunk
                    if not data:
                        continue

                    try:
                        req = json.loads(data.decode("utf-8"))
                    except Exception:
                        self._send(conn, ok=False, error="invalid json")
                        continue

                    action = req.get("action")
                    params = req.get("params", {}) or {}
                    resp = self._handle_action(action, params)
                    self._send(conn, **resp)

                    # If action asked to shutdown, break loop
                    if action == "shutdown":
                        self.stop()
                        break

                except Exception:
                    traceback.print_exc()
                    try:
                        self._send(conn, ok=False, error="internal error")
                    except Exception:
                        pass

        self._cleanup()

    def _send(self, conn: socket.socket, ok: bool, result: Any = None, error: str = None):
        payload = {"ok": ok}
        if ok:
            payload["result"] = result
        else:
            payload["error"] = error
        try:
            conn.sendall(json.dumps(payload).encode("utf-8"))
        except Exception:
            pass
        

    def _handle_action(self, action: str, params: dict) -> dict:
        try:
            if action == "list_patterns":
                self.manager.load_patterns()  # Reload patterns to pick up new files
                return {"ok": True, "result": list(self.manager.patterns.keys())}

            if action == "list_hooks":
                self.manager.load_hooks()  # Reload hooks to pick up new files
                return {"ok": True, "result": [h.event_name for h in self.manager.hooks]}

            if action == "start_pattern":
                name = params.get("name")
                if not name:
                    return {"ok": False, "error": "missing name"}
                self.manager.start_pattern(name)
                return {"ok": True, "result": "started"}

            if action == "stop_pattern":
                self.manager.stop_pattern()
                return {"ok": True, "result": "stopped"}

            if action == "stop_all":
                self.manager.stop_all_patterns()
                return {"ok": True, "result": "stopped_all"}

            if action == "status":
                cur = self.manager.current_pattern.name if self.manager.current_pattern else None
                return {"ok": True, "result": {"current_pattern": cur}}

            if action == "save_pattern":
                name = params.get("name")
                if not name:
                    return {"ok": False, "error": "missing name"}
                self.manager.save_pattern(name)
                return {"ok": True, "result": "saved"}


            if action == "register_startup":
                name = params.get("name")
                if not name:
                    return {"ok": False, "error": "missing name"}
                linked_hook = params.get("linked_hook")
                self.manager.register_startup_pattern(name, linked_hook=linked_hook)
                return {"ok": True, "result": "registered"}



            if action == "unregister_startup":
                name = params.get("name")
                if not name:
                    return {"ok": False, "error": "missing name"}
                try:
                    self.manager.startup_patterns.remove(name)
                except ValueError:
                    pass
                # remove any links pointing to the pattern
                for k in list(self.manager.startup_links.keys()):
                    if self.manager.startup_links.get(k) == name:
                        del self.manager.startup_links[k]
                return {"ok": True, "result": "unregistered"}

            if action == "list_startup":
                return {"ok": True, "result": {"startup_patterns": list(self.manager.startup_patterns), "startup_links": dict(self.manager.startup_links)}}

            if action == "list_hook_pattern_links":
                # Return all hooks and their current pattern links (if any)
                hook_patterns = {}
                for hook in self.manager.hooks:
                    linked_pattern = self.manager.startup_links.get(hook.event_name)
                    hook_patterns[hook.event_name] = linked_pattern
                return {"ok": True, "result": hook_patterns}

            if action == "link_hook_to_pattern":
                hook_event_name = params.get("hook_event_name")
                pattern_name = params.get("pattern_name")
                if not hook_event_name or not pattern_name:
                    return {"ok": False, "error": "missing hook_event_name or pattern_name"}
                
                # Verify hook exists
                hook_exists = any(h.event_name == hook_event_name for h in self.manager.hooks)
                if not hook_exists:
                    return {"ok": False, "error": f"hook '{hook_event_name}' not found"}
                
                # Verify pattern exists
                if pattern_name not in self.manager.patterns:
                    return {"ok": False, "error": f"pattern '{pattern_name}' not found"}
                
                self.manager.startup_links[hook_event_name] = pattern_name
                return {"ok": True, "result": f"linked {hook_event_name} to {pattern_name}"}

            if action == "unlink_hook":
                hook_event_name = params.get("hook_event_name")
                if not hook_event_name:
                    return {"ok": False, "error": "missing hook_event_name"}
                
                if hook_event_name in self.manager.startup_links:
                    del self.manager.startup_links[hook_event_name]
                    return {"ok": True, "result": f"unlinked {hook_event_name}"}
                else:
                    return {"ok": False, "error": f"hook '{hook_event_name}' not linked"}

            if action == "trigger_test_hook":
                # Find and trigger the test hook
                for hook in self.manager.hooks:
                    if hook.event_name == "test_trigger":
                        if hasattr(hook, 'trigger'):
                            hook.trigger()
                            return {"ok": True, "result": "test hook triggered"}
                        else:
                            return {"ok": False, "error": "test hook does not support triggering"}
                return {"ok": False, "error": "test hook not found"}

            if action == "add_persistent_link":
                hook_event_name = params.get("hook_event_name")
                pattern_name = params.get("pattern_name")
                if not hook_event_name or not pattern_name:
                    return {"ok": False, "error": "missing hook_event_name or pattern_name"}
                
                # Verify hook exists
                hook_exists = any(h.event_name == hook_event_name for h in self.manager.hooks)
                if not hook_exists:
                    return {"ok": False, "error": f"hook '{hook_event_name}' not found"}
                
                # Verify pattern exists
                if pattern_name not in self.manager.patterns:
                    return {"ok": False, "error": f"pattern '{pattern_name}' not found"}
                
                # Also add to runtime links
                self.manager.startup_links[hook_event_name] = pattern_name
                # Save to persistent storage
                self.manager.save_persistent_link(hook_event_name, pattern_name)
                return {"ok": True, "result": f"added persistent link {hook_event_name} → {pattern_name}"}

            if action == "remove_persistent_link":
                hook_event_name = params.get("hook_event_name")
                if not hook_event_name:
                    return {"ok": False, "error": "missing hook_event_name"}
                
                # Remove from runtime
                if hook_event_name in self.manager.startup_links:
                    del self.manager.startup_links[hook_event_name]
                
                # Remove from persistent storage
                self.manager.remove_persistent_link(hook_event_name)
                return {"ok": True, "result": f"removed persistent link {hook_event_name}"}

            if action == "list_persistent_links":
                links = self.manager.load_persistent_links()
                return {"ok": True, "result": links}

            if action == "add_pattern_to_startup":
                pattern_name = params.get("pattern_name")
                if not pattern_name:
                    return {"ok": False, "error": "missing pattern_name"}
                
                # Verify pattern exists
                if pattern_name not in self.manager.patterns:
                    return {"ok": False, "error": f"pattern '{pattern_name}' not found"}
                
                # Save standalone pattern to persistent storage
                self.manager.save_pattern_to_startup(pattern_name)
                return {"ok": True, "result": f"added pattern '{pattern_name}' to startup"}

            if action == "remove_pattern_from_startup":
                pattern_name = params.get("pattern_name")
                if not pattern_name:
                    return {"ok": False, "error": "missing pattern_name"}
                
                # Remove standalone pattern from persistent storage
                self.manager.remove_pattern_from_startup(pattern_name)
                return {"ok": True, "result": f"removed pattern '{pattern_name}' from startup"}

            if action == "list_startup_patterns":
                patterns = self.manager.load_startup_patterns_list()
                return {"ok": True, "result": patterns}
            
            if action == "shutdown":
                # Stop patterns and return
                self.manager.stop_all_patterns()
                return {"ok": True, "result": "shutting_down"}
            

            return {"ok": False, "error": f"unknown action {action}"}

        except Exception as e:
            return {"ok": False, "error": str(e)}

    def stop(self):
        self._stop_event.set()
        try:
            if self._sock:
                try:
                    self._sock.close()
                except Exception:
                    pass
        except Exception:
            pass

    def _cleanup(self):
        try:
            if os.path.exists(self.socket_path):
                os.remove(self.socket_path)
        except Exception:
            pass


if __name__ == "__main__":
    print("This module provides IPCServer for use by run_service.py")
