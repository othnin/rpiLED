import time
import multiprocessing
import psutil
from multiprocessing import Process, Value

def worker(target_load, running):
    """Worker function that generates CPU load."""
    interval = 0.01  # 10ms check interval for fine control
    
    while running.value:
        # Calculate work and rest times
        work_time = (target_load / 100.0) * interval
        rest_time = ((100 - target_load) / 100.0) * interval
        
        # Work phase - intensive computation
        if work_time > 0:
            end_time = time.perf_counter() + work_time
            while time.perf_counter() < end_time:
                # Perform actual computation to keep CPU busy
                _ = sum(i * i for i in range(1000))
        
        # Rest phase
        if rest_time > 0:
            time.sleep(rest_time)

class CPULoader:
    def __init__(self, target_load=50, duration=60):
        """
        Initialize CPU loader.
        
        Args:
            target_load: Target CPU load percentage (0-100)
            duration: How long to maintain the load in seconds (0 for infinite)
        """
        self.target_load = max(0, min(100, target_load))
        self.duration = duration
        self.processes = []
        self.running = None
        
    def start(self):
        """Start loading the CPU."""
        num_cores = psutil.cpu_count()
        print(f"Starting CPU load: {self.target_load}% across {num_cores} cores")
        print(f"Duration: {'Infinite (Ctrl+C to stop)' if self.duration == 0 else f'{self.duration} seconds'}")
        print("Press Ctrl+C to stop at any time")
        print("Warming up...\n")
        
        # Shared value to signal workers to stop
        self.running = Value('i', 1)
        
        # Create one process per CPU core
        for i in range(num_cores):
            p = Process(target=worker, args=(self.target_load, self.running))
            p.start()
            self.processes.append(p)
        
        # Give processes time to warm up
        time.sleep(2)
        
        # Monitor and display CPU usage
        start_time = time.time()
        try:
            while True:
                if self.duration > 0 and time.time() - start_time >= self.duration:
                    break
                
                cpu_percent = psutil.cpu_percent(interval=1)
                elapsed = int(time.time() - start_time)
                print(f"[{elapsed}s] Current CPU usage: {cpu_percent:.1f}% (target: {self.target_load}%)")
                
        except KeyboardInterrupt:
            print("\n\nStopping...")
        finally:
            self.stop()
    
    def stop(self):
        """Stop loading the CPU."""
        if self.running:
            self.running.value = 0
        
        # Wait for all processes to finish
        for p in self.processes:
            p.join(timeout=2)
            if p.is_alive():
                p.terminate()
        
        time.sleep(1)
        print(f"CPU load test completed. Final CPU usage: {psutil.cpu_percent(interval=1):.1f}%")

def main():
    print("=== CPU Load Generator ===\n")
    
    # Get user input
    try:
        target = int(input("Enter target CPU load percentage (0-100): "))
        duration = int(input("Enter duration in seconds (0 for infinite): "))
        
        if target < 0 or target > 100:
            print("Error: Target load must be between 0 and 100")
            return
            
        loader = CPULoader(target_load=target, duration=duration)
        loader.start()
        
    except ValueError:
        print("Error: Please enter valid numbers")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()