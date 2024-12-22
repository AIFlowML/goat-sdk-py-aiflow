import subprocess
import datetime
import logging
import sys
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('core_test_debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def run_core_test(test_path: str) -> dict:
    """Run a single core test with detailed logging."""
    logging.info(f"Running test: {test_path}")
    try:
        result = subprocess.run(
            [
                'python', '-m', 'pytest',
                test_path,
                '-v',
                '--capture=no',
                '--tb=long',
                '--showlocals',
                '--durations=0'
            ],
            capture_output=True,
            text=True
        )
        success = result.returncode == 0
        logging.info(f"Test {'passed' if success else 'failed'}: {test_path}")
        if not success:
            logging.error(f"Test output:\n{result.stdout}\n{result.stderr}")
        return {
            'path': test_path,
            'success': success,
            'output': result.stdout,
            'error': result.stderr
        }
    except Exception as e:
        logging.error(f"Error running test {test_path}: {str(e)}")
        return {
            'path': test_path,
            'success': False,
            'output': '',
            'error': str(e)
        }

def write_report(results: list):
    """Write detailed test results to a markdown file."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"core_test_report_{timestamp}.md"
    
    with open(report_path, 'w') as f:
        f.write("# Core Tests Execution Report\n\n")
        f.write(f"Generated: {datetime.datetime.now()}\n\n")
        
        # Summary
        total = len(results)
        passed = sum(1 for r in results if r['success'])
        failed = total - passed
        
        f.write("## Summary\n\n")
        f.write(f"- Total Tests: {total}\n")
        f.write(f"- Passed: {passed}\n")
        f.write(f"- Failed: {failed}\n")
        f.write(f"- Success Rate: {(passed/total)*100:.2f}%\n\n")
        
        # Detailed Results
        f.write("## Detailed Results\n\n")
        for result in results:
            f.write(f"### {result['path']}\n")
            f.write(f"Status: {'✅ PASSED' if result['success'] else '❌ FAILED'}\n\n")
            if not result['success']:
                f.write("Error Output:\n")
                f.write("```\n")
                f.write(result['error'])
                f.write("\n```\n\n")
                f.write("Full Output:\n")
                f.write("```\n")
                f.write(result['output'])
                f.write("\n```\n\n")

def main():
    logging.info("Starting core tests execution")
    
    # Define core test paths
    core_tests = [
        "tests/core/utils/test_snake_case.py",
        "tests/core/utils/test_add_parameters_to_description.py",
        "tests/core/utils/test_get_tools.py",
        "tests/core/utils/test_create_tool_parameters.py",
        "tests/core/types/test_chain.py",
        "tests/core/classes/test_plugin_base.py",
        "tests/core/classes/test_tool_base.py",
        "tests/core/classes/test_wallet_client_base.py",
        "tests/core/decorators/test_tool.py"
    ]
    
    results = []
    for test_path in core_tests:
        if not Path(test_path).exists():
            logging.warning(f"Test path does not exist: {test_path}")
            continue
        result = run_core_test(test_path)
        results.append(result)
    
    write_report(results)
    logging.info("Core tests execution completed")

if __name__ == "__main__":
    main() 