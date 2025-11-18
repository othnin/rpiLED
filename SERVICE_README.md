Service / IPC integration for WOPR

This repository includes a simple IPC server and a run script to run the manager as a long-running service.

Files added:
- `src/ipc_server.py` - Unix domain socket IPC server (JSON protocol)
- `src/run_service.py` - Bootable runner: initializes Neo, PatternManager, loads patterns/hooks, starts startup patterns and the IPC server.
- `systemd/wopr.service` - Example systemd unit file to run `run_service.py` at boot.

Installing as a systemd service (on Raspberry Pi / Debian-like systems)

1. Copy the service file to systemd and reload units (requires sudo):

   sudo cp systemd/wopr.service /etc/systemd/system/wopr.service
   sudo systemctl daemon-reload

2. Enable and start the service:

   sudo systemctl enable wopr.service
   sudo systemctl start wopr.service

3. Check status and logs:

   sudo systemctl status wopr.service
   sudo journalctl -u wopr.service -f

IPC usage (Unix domain socket at /tmp/wopr.sock by default)

Send JSON requests (single JSON object per connection). Example using socat:

# list patterns
printf '{"action":"list_patterns"}' | socat - UNIX-CONNECT:/tmp/wopr.sock

# start a pattern
printf '{"action":"start_pattern","params":{"name":"Loading Bar Pattern"}}' | socat - UNIX-CONNECT:/tmp/wopr.sock

# stop current pattern
printf '{"action":"stop_pattern"}' | socat - UNIX-CONNECT:/tmp/wopr.sock

The server replies with a single JSON response.

Notes & security
- The socket file is created at /tmp/wopr.sock by default with 0666 permissions; adjust if you need stricter access control.
- The systemd unit uses `User=pi` and a hard-coded WorkingDirectory - update paths/user to match your system.
- You can change the socket path by editing `src/run_service.py` or starting your own runner.

Next steps
- Add auth or restrict socket permissions if exposing to multi-user systems.
- Optionally provide a small client script to make IPC calls more convenient.
- Integrate with a GUI by creating a small adapter that issues IPC commands and receives responses.
