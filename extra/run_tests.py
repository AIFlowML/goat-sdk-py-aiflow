import subprocess
import re
from pathlib import Path
import sys
import datetime

def extract_test_names(test_output):
    """Extract test names from test output."""
    test_lines = []
    for line in test_output.split('\n'):
        if line.startswith('FAILED') or line.startswith('ERROR'):
            test_lines.append(line.split(' ')[1])
    return test_lines

def run_single_test(test_path):
    """Run a single test and return the result."""
    try:
        result = subprocess.run(
            ['python', '-m', 'pytest', test_path, '-v', '--capture=no'],
            capture_output=True,
            text=True
        )
        return {
            'test': test_path,
            'success': result.returncode == 0,
            'output': result.stdout + result.stderr
        }
    except Exception as e:
        return {
            'test': test_path,
            'success': False,
            'output': str(e)
        }

def main():
    # Read test_output.txt to get list of tests
    with open('test_output.txt', 'r') as f:
        test_output = f.read()
    
    test_paths = extract_test_names(test_output)
    
    # Create report file
    report = []
    report.append("# Test Execution Report")
    report.append(f"\nGenerated at: {datetime.datetime.now()}\n")
    
    # Statistics
    total_tests = len(test_paths)
    passed_tests = 0
    failed_tests = 0
    
    report.append("## Individual Test Results\n")
    
    # Run each test individually
    for test_path in test_paths:
        print(f"Running test: {test_path}")
        result = run_single_test(test_path)
        
        if result['success']:
            status = "✅ PASSED"
            passed_tests += 1
        else:
            status = "❌ FAILED"
            failed_tests += 1
        
        report.append(f"### {test_path}")
        report.append(f"Status: {status}")
        report.append("```")
        report.append(result['output'])
        report.append("```\n")
    
    # Add summary
    summary = [
        "## Summary",
        f"- Total Tests: {total_tests}",
        f"- Passed: {passed_tests}",
        f"- Failed: {failed_tests}",
        f"- Success Rate: {(passed_tests/total_tests)*100:.2f}%\n"
    ]
    
    # Write report
    with open('report_errors.md', 'w') as f:
        f.write('\n'.join(report))
    
    print("\nTest execution completed!")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.2f}%")
    print("\nDetailed report written to report_errors.md")

if __name__ == "__main__":
    main() 