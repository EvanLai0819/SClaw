#!/usr/bin/env python3
"""
FTE Estimator - Calculate FTE based on 3 yes/no questions

Each "Yes" answer = 1 point
Total score determines FTE value
"""

import argparse
import sys


def ask_question(question: str) -> bool:
    """Ask a yes/no question and return True if yes."""
    while True:
        answer = input(f"{question} (yes/no): ").strip().lower()
        if answer in ["yes", "y", "是"]:
            return True
        elif answer in ["no", "n", "否"]:
            return False
        else:
            print("Please enter 'yes' or 'no'")


def calculate_fte(score: int) -> str:
    """Calculate FTE value based on score."""
    if score == 0:
        return "0.5 FTE"
    elif score == 1:
        return "1 FTE"
    elif score == 2:
        return "2 FTE"
    elif score == 3:
        return "3+ FTE"
    else:
        return "Unknown"


def main():
    print("=" * 50)
    print("📊 FTE Estimator")
    print("=" * 50)
    print()
    
    score = 0
    
    # Question 1
    print("Question 1/3:")
    if ask_question("Do you need to onboard a new feed?"):
        score += 1
        print("✓ +1 point")
    else:
        print("○ 0 points")
    print()
    
    # Question 2
    print("Question 2/3:")
    if ask_question("Do you need to modify the data model?"):
        score += 1
        print("✓ +1 point")
    else:
        print("○ 0 points")
    print()
    
    # Question 3
    print("Question 3/3:")
    if ask_question("Do you need to perform end-to-end testing?"):
        score += 1
        print("✓ +1 point")
    else:
        print("○ 0 points")
    print()
    
    # Calculate and display result
    fte = calculate_fte(score)
    print("=" * 50)
    print(f"Total Score: {score}/3")
    print(f"Estimated FTE: {fte}")
    print("=" * 50)
    
    return score


if __name__ == "__main__":
    sys.exit(main())
