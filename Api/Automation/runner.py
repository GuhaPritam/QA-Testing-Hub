import pytest
import sys

if __name__ == "__main__":
    print("Select which tests to run:")
    print("1. Login tests only")
    print("2. Category tests only")
    print("3. All tests")

    choice = input("Enter your choice (1/2/3): ").strip()

    html_report = "./report.html"  # report file path

    if choice == "1":
        exit_code = pytest.main(["-v", "./Api/Automation/Tests/test_login.py", f"--html={html_report}"])
    elif choice == "2":
        exit_code = pytest.main(["-v", "./Api/Automation/Tests/test_category.py", f"--html={html_report}"])
    elif choice == "3":
        exit_code = pytest.main(["-v", "./Api/Automation/Tests/", f"--html={html_report}"])
    else:
        print("Invalid choice")
        sys.exit(1)

    print(f"\nHTML report generated at: {html_report}")
    sys.exit(exit_code)
