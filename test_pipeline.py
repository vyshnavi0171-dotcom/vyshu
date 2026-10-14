"""Validation script to test SatyaNet API & Processing Pipeline."""
import json
from pathlib import Path

# Load and test text processor logic directly
from backend.text_processor import analyze_text_misinformation
from backend.config import settings

def run_tests():
    print("=" * 60)
    print("SatyaNet Pipeline Smoke Test")
    print("=" * 60)

    # 1. Test Text Verification on Hinglish Forward
    test_hinglish = "Modi sarkar sabhi ko 3 mahine ka free recharge de rahi hai! Turant link bit.ly/free-recharge pe click karo aur 10 logo ko bhejo."
    print(f"\n[Test 1] Testing Text Verification (Hinglish Hoax):\nInput: {test_hinglish}")
    result = analyze_text_misinformation(test_hinglish, language_hint="hinglish")
    print(f"Verdict: {result['verdict']}")
    print(f"Credibility Score: {result['credibility_score']}/100")
    print(f"Risk Category: {result['risk_category']}")
    print(f"Detected Language: {result['detected_language']}")
    print(f"Tactics: {result['manipulation_tactics']}")
    print(f"Engine: {result['source_engine']}")
    assert result["verdict"] in ["FALSE", "MISLEADING"], "Failed: Expected hoax to be flagged!"
    print("[PASS] Text Hoax Verification Passed!")

    # 2. Test Text Verification on Authentic News
    test_authentic = "The Reserve Bank of India has maintained repo rate unchanged at 6.5 percent."
    print(f"\n[Test 2] Testing Authentic Text Verification:\nInput: {test_authentic}")
    result_auth = analyze_text_misinformation(test_authentic, language_hint="en")
    print(f"Verdict: {result_auth['verdict']}")
    print(f"Credibility Score: {result_auth['credibility_score']}/100")
    print(f"Risk Category: {result_auth['risk_category']}")
    assert result_auth["credibility_score"] >= 65, "Failed: Expected authentic news to have high credibility!"
    print("[PASS] Authentic Text Verification Passed!")

    print("\n" + "=" * 60)
    print("All Text Pipeline Smoke Tests Passed Successfully!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
