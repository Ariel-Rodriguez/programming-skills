
import sys
import os
from pathlib import Path

# Add tests directory to path
sys.path.append(str(Path(__file__).parent))
os.chdir(str(Path(__file__).parent))

from services.test_generation import generate_test_suite
from domain import Skill, Severity
from adapters.filesystem import RealFileSystem

def main():
    fs = RealFileSystem()
    skill_path = Path("../skills/ps-composition-over-coordination")
    
    skill = Skill(
        name="ps-composition-over-coordination",
        path=skill_path,
        description="debug skill",
        content="",
        severity=Severity.SUGGEST
    )
    
    print(f"Loading tests from: {skill.path.resolve()}")
    try:
        suite = generate_test_suite(skill, fs)
        
        for test in suite.tests:
            if test.name == "refactor_orchestrator_class":
                print(f"\n--- Test: {test.name} ---")
                print("Input Prompt Lines:")
                for i, line in enumerate(test.input_prompt.split('\n')):
                    print(f"{i}: {repr(line)}")
                    
                if "class PaymentProcessor" in test.input_prompt:
                     print("\n[SUCCESS] 'class PaymentProcessor' found.")
                else:
                     print("\n[FAIL] 'class PaymentProcessor' NOT found.")
                 
    except Exception as e:
        print(f"Error generating suite: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
