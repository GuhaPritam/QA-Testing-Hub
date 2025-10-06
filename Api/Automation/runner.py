import pytest
import sys

if __name__ == "__main__":
    print("Select which tests to run:")
    print("1. Login tests only")
    print("2. Category tests only")
    print("3. All tests")

    choice = input("Enter your choice (1/2/3): ").strip()

    if choice == "1":
        exit_code = pytest.main(["-v", "./Api/Automation/tests/test_login.py"])
    elif choice == "2":
        exit_code = pytest.main(["-v", "./Api/Automation/tests/test_category.py"])
    elif choice == "3":
        exit_code = pytest.main(["-v", "./Api/Automation/tests/"])
    else:
        print("Invalid choice")
        sys.exit(1)

    sys.exit(exit_code)
