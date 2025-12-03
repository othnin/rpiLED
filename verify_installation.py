#!/usr/bin/env python3
"""
HOOK ALERT SYSTEM - Verification Script
Checks that all components are properly installed and working
"""

import sys
import os
from pathlib import Path

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
CHECKMARK = '✓'
CROSS = '✗'

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_success(text):
    print(f"{GREEN}{CHECKMARK} {text}{RESET}")

def print_error(text):
    print(f"{RED}{CROSS} {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠ {text}{RESET}")

def check_file_exists(path, description):
    """Check if a file exists"""
    if os.path.exists(path):
        print_success(f"{description}: {path}")
        return True
    else:
        print_error(f"{description}: {path} NOT FOUND")
        return False

def check_import(module_name, description):
    """Check if a module can be imported"""
    try:
        __import__(module_name)
        print_success(f"{description}: {module_name}")
        return True
    except ImportError as e:
        print_error(f"{description}: {module_name} - {e}")
        return False

def check_syntax(filepath):
    """Check if Python file has valid syntax"""
    try:
        compile(open(filepath).read(), filepath, 'exec')
        return True
    except SyntaxError as e:
        print_error(f"Syntax error in {filepath}: {e}")
        return False

def main():
    print_header("HOOK ALERT SYSTEM - VERIFICATION")
    
    all_passed = True
    
    # ====================================================================
    # DOCUMENTATION FILES
    # ====================================================================
    print(f"{BLUE}Checking Documentation Files...{RESET}")
    
    docs_to_check = [
        ("/opt/WOPR/docs/HOOK_ALERT_SYSTEM.md", "Architecture documentation"),
        ("/opt/WOPR/docs/HOOK_ALERT_QUICK_REFERENCE.md", "Quick reference"),
        ("/opt/WOPR/docs/HOOK_ALERT_WORKFLOW_EXAMPLE.md", "Workflow example"),
        ("/opt/WOPR/docs/INTEGRATION_GUIDE.md", "Integration guide"),
        ("/opt/WOPR/docs/IMPLEMENTATION_SUMMARY.md", "Implementation summary"),
        ("/opt/WOPR/docs/DOCUMENTATION_INDEX.md", "Documentation index"),
    ]
    
    for filepath, description in docs_to_check:
        if not check_file_exists(filepath, description):
            all_passed = False
    
    # ====================================================================
    # SOURCE CODE FILES
    # ====================================================================
    print(f"\n{BLUE}Checking Source Code Files...{RESET}")
    
    src_files = [
        ("/opt/WOPR/backend/src/hook_alerts.py", "Alert infrastructure"),
        ("/opt/WOPR/backend/src/backend.py", "Core system"),
        ("/opt/WOPR/backend/src/hooks/cpu_monitor.py", "CPU monitor hook"),
        ("/opt/WOPR/backend/src/hooks/disk_monitor.py", "Disk monitor hook"),
        ("/opt/WOPR/backend/src/hooks/cpu_temp.py", "Temperature hook"),
        ("/opt/WOPR/backend/src/hooks/mem_monitor.py", "Memory hook"),
        ("/opt/WOPR/backend/src/hooks/voltage_monitor.py", "Voltage hook"),
        ("/opt/WOPR/backend/src/patterns/knight_rider.py", "Knight Rider pattern"),
        ("/opt/WOPR/backend/src/patterns/loading_bar.py", "Loading Bar pattern"),
        ("/opt/WOPR/backend/src/patterns/my_cool_pattern.py", "My Cool pattern"),
    ]
    
    for filepath, description in src_files:
        if not check_file_exists(filepath, description):
            all_passed = False
        elif not check_syntax(filepath):
            all_passed = False
    
    # ====================================================================
    # TEST FILES
    # ====================================================================
    print(f"\n{BLUE}Checking Test Files...{RESET}")
    
    if not check_file_exists("/opt/WOPR/test_alert_system.py", "Alert system test"):
        all_passed = False
    
    # ====================================================================
    # IMPORTS TEST
    # ====================================================================
    print(f"\n{BLUE}Checking Python Imports...{RESET}")
    
    # Add backend/src to path for imports
    sys.path.insert(0, '/opt/WOPR/backend/src')
    
    imports_to_check = [
        ("hook_alerts", "Alert infrastructure module"),
        ("queue", "Python queue module (std lib)"),
        ("threading", "Threading module (std lib)"),
        ("psutil", "System metrics library"),
    ]
    
    for module_name, description in imports_to_check:
        if not check_import(module_name, description):
            if module_name != "psutil":  # psutil is optional for non-Pi systems
                all_passed = False
            else:
                print_warning(f"psutil not installed (optional, needed on target system)")
    
    # ====================================================================
    # ALERTLEVEL ENUM TEST
    # ====================================================================
    print(f"\n{BLUE}Checking AlertLevel Enum...{RESET}")
    
    try:
        from hook_alerts import AlertLevel, AlertColorScheme
        
        # Check all levels exist
        levels = [AlertLevel.NORMAL, AlertLevel.WARNING, AlertLevel.CRITICAL]
        print_success("AlertLevel enum has all expected levels")
        
        # Check colors map
        for level in levels:
            color = AlertColorScheme.get_color(level)
            if isinstance(color, tuple) and len(color) == 3:
                print_success(f"  {level.name}: {color}")
            else:
                print_error(f"  {level.name}: Invalid color {color}")
                all_passed = False
        
    except Exception as e:
        print_error(f"AlertLevel test failed: {e}")
        all_passed = False
    
    # ====================================================================
    # HOOKMESSAGE TEST
    # ====================================================================
    print(f"\n{BLUE}Checking HookMessage Class...{RESET}")
    
    try:
        from hook_alerts import HookMessage, AlertLevel
        
        msg = HookMessage(
            hook_name="test_hook",
            alert_level=AlertLevel.WARNING,
            color=(255, 165, 0),
            metadata={"test": "value"}
        )
        
        print_success(f"HookMessage created successfully")
        print_success(f"  Hook: {msg.hook_name}")
        print_success(f"  Level: {msg.alert_level.name}")
        print_success(f"  Color: {msg.color}")
        print_success(f"  Metadata: {msg.metadata}")
        
    except Exception as e:
        print_error(f"HookMessage test failed: {e}")
        all_passed = False
    
    # ====================================================================
    # HOOK TEST
    # ====================================================================
    print(f"\n{BLUE}Checking Hooks...{RESET}")
    
    try:
        from hooks.cpu_monitor import CPUMonitorHook
        
        hook = CPUMonitorHook(warn_threshold=20, crit_threshold=75)
        print_success(f"CPUMonitorHook instantiated")
        print_success(f"  Event name: {hook.event_name}")
        
        # Test check method
        result = hook.check()
        print_success(f"  check() returned: {result}")
        
        # If triggered, test get_message
        if result:
            msg = hook.get_message()
            if msg:
                print_success(f"  get_message() returned: {msg}")
            else:
                print_error(f"  get_message() returned None")
                all_passed = False
        
    except Exception as e:
        print_error(f"Hook test failed: {e}")
        all_passed = False
    
    # ====================================================================
    # PATTERN TEST
    # ====================================================================
    print(f"\n{BLUE}Checking Pattern Signatures...{RESET}")
    
    try:
        from patterns.knight_rider import KnightRiderPattern
        import inspect
        
        pattern = KnightRiderPattern()
        print_success(f"KnightRiderPattern instantiated")
        print_success(f"  Name: {pattern.name}")
        print_success(f"  Description: {pattern.description}")
        
        # Check run signature
        sig = inspect.signature(pattern.run)
        params = list(sig.parameters.keys())
        
        expected = ['neo', 'stop_event', 'alert_queue']
        if all(p in params for p in expected):
            print_success(f"  run() has alert_queue parameter ✓")
        else:
            print_error(f"  run() signature incorrect. Has: {params}")
            all_passed = False
        
    except Exception as e:
        print_error(f"Pattern test failed: {e}")
        all_passed = False
    
    # ====================================================================
    # QUEUE TEST
    # ====================================================================
    print(f"\n{BLUE}Checking Queue Mechanism...{RESET}")
    
    try:
        import queue
        from hook_alerts import HookMessage, AlertLevel
        
        # Create queue
        test_queue = queue.Queue()
        print_success("Alert queue created")
        
        # Put message
        msg = HookMessage(
            hook_name="test",
            alert_level=AlertLevel.CRITICAL,
            color=(255, 0, 0),
            metadata={}
        )
        test_queue.put_nowait(msg)
        print_success("Message queued")
        
        # Get message
        received = test_queue.get_nowait()
        print_success("Message received")
        
        if received.hook_name == "test":
            print_success("Message contents verified")
        else:
            print_error("Message contents incorrect")
            all_passed = False
        
    except Exception as e:
        print_error(f"Queue test failed: {e}")
        all_passed = False
    
    # ====================================================================
    # SUMMARY
    # ====================================================================
    print_header("VERIFICATION COMPLETE")
    
    if all_passed:
        print(f"{GREEN}{'='*60}{RESET}")
        print(f"{GREEN}ALL CHECKS PASSED ✓{RESET}")
        print(f"{GREEN}{'='*60}{RESET}")
        print(f"\n{BLUE}System is ready for integration!{RESET}\n")
        print("Next steps:")
        print("  1. Read INTEGRATION_GUIDE.md")
        print("  2. Add manager.check_hooks() to your service loop")
        print("  3. Start the service and test with stress --cpu 4 --timeout 30s")
        print("  4. Watch LED colors change based on system metrics\n")
        return 0
    else:
        print(f"{RED}{'='*60}{RESET}")
        print(f"{RED}SOME CHECKS FAILED ✗{RESET}")
        print(f"{RED}{'='*60}{RESET}")
        print(f"\n{YELLOW}Please fix the errors above and try again.{RESET}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
