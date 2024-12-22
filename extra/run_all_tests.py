import subprocess
import datetime
import sys

def run_all_tests():
    """Run all tests and capture output."""
    try:
        result = subprocess.run(
            [
                'python', '-m', 'pytest',
                'tests/',
                '-v',
                '--capture=no',
                '--tb=short',
                '--strict-markers',
                '--asyncio-mode=auto',
                '-p', 'no:warnings',
                '--durations=10'
            ],
            capture_output=True,
            text=True
        )
        return result.stdout + result.stderr
    except Exception as e:
        return str(e)

def main():
    print("Starting full test suite execution...")
    print(f"Time: {datetime.datetime.now()}\n")
    
    # Run tests and capture output
    output = run_all_tests()
    
    # Write to test_output.txt
    with open('test_output.txt', 'w') as f:
        f.write(output)
    
    print("\nTest execution completed!")
    print("Results written to test_output.txt")
    
    # Print summary
    failed = output.count('FAILED')
    error = output.count('ERROR')
    passed = output.count('PASSED')
    total = failed + error + passed
    
    print("\nQuick Summary:")
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Errors: {error}")
    if total > 0:
        print(f"Success Rate: {(passed/total)*100:.2f}%")

if __name__ == "__main__":
    main() 