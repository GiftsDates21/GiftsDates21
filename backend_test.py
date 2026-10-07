#!/usr/bin/env python3
"""
Backend API Test Suite for GiftsDates Translation Endpoint
Tests POST /api/i18n/translate endpoint with various scenarios
"""

import requests
import time
import json
from typing import List, Dict, Any

# Backend URL from frontend/.env
BASE_URL = "https://gifts-dates.preview.emergentagent.com/api"

class TestResults:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
    
    def add_pass(self, test_name: str, details: str = ""):
        self.passed.append(f"✅ {test_name}" + (f": {details}" if details else ""))
    
    def add_fail(self, test_name: str, details: str):
        self.failed.append(f"❌ {test_name}: {details}")
    
    def add_warning(self, test_name: str, details: str):
        self.warnings.append(f"⚠️  {test_name}: {details}")
    
    def print_summary(self):
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        if self.failed:
            print("\n🔴 FAILED TESTS:")
            for fail in self.failed:
                print(f"  {fail}")
        
        if self.warnings:
            print("\n🟡 WARNINGS:")
            for warn in self.warnings:
                print(f"  {warn}")
        
        if self.passed:
            print("\n🟢 PASSED TESTS:")
            for p in self.passed:
                print(f"  {p}")
        
        print("\n" + "="*80)
        print(f"Total: {len(self.passed)} passed, {len(self.failed)} failed, {len(self.warnings)} warnings")
        print("="*80 + "\n")

results = TestResults()

def test_translation_endpoint():
    """Test POST /api/i18n/translate endpoint"""
    
    print("\n" + "="*80)
    print("TESTING: POST /api/i18n/translate")
    print("="*80 + "\n")
    
    # Test 1: Swahili translation with placeholders and brand name
    print("Test 1: Swahili (sw) translation with placeholders and brand name...")
    test_texts = [
        "Top up",
        "Withdraw",
        "Withdrawable coins are also spendable. Only withdrawable coins can be withdrawn, not the main balance.",
        "Waiting for {o} to choose a date option.",
        "GiftsDates"
    ]
    
    try:
        response = requests.post(
            f"{BASE_URL}/i18n/translate",
            json={"lang": "sw", "texts": test_texts},
            timeout=90
        )
        
        if response.status_code != 200:
            results.add_fail("Test 1 - Swahili translation", f"Status {response.status_code}: {response.text}")
        else:
            data = response.json()
            translations = data.get("translations", [])
            
            # Check response structure
            if not isinstance(translations, list):
                results.add_fail("Test 1 - Response structure", "translations is not a list")
            elif len(translations) != len(test_texts):
                results.add_fail("Test 1 - Response length", f"Expected {len(test_texts)} translations, got {len(translations)}")
            else:
                # Check each translation
                all_valid = True
                issues = []
                
                for i, (original, translated) in enumerate(zip(test_texts, translations)):
                    print(f"  [{i}] '{original}' -> '{translated}'")
                    
                    # Check if translated (not English)
                    if i < 4:  # First 4 should be translated
                        if translated == original:
                            issues.append(f"Text {i} not translated: '{original}'")
                            all_valid = False
                        elif translated.lower() == original.lower():
                            issues.append(f"Text {i} appears unchanged: '{original}'")
                            all_valid = False
                    
                    # Check placeholder preservation for text with {o}
                    if "{o}" in original and "{o}" not in translated:
                        issues.append(f"Text {i} missing placeholder {{o}}: '{translated}'")
                        all_valid = False
                    
                    # Check brand name unchanged
                    if original == "GiftsDates" and translated != "GiftsDates":
                        issues.append(f"Brand name changed: '{translated}' (should be 'GiftsDates')")
                        all_valid = False
                
                if all_valid:
                    results.add_pass("Test 1 - Swahili translation", "All texts translated correctly, placeholders preserved, brand unchanged")
                else:
                    results.add_fail("Test 1 - Swahili translation", "; ".join(issues))
    
    except requests.exceptions.Timeout:
        results.add_fail("Test 1 - Swahili translation", "Request timeout (>90s)")
    except Exception as e:
        results.add_fail("Test 1 - Swahili translation", f"Exception: {str(e)}")
    
    # Small delay to respect serialization
    time.sleep(1)
    
    # Test 2: Repeat same request (should be cached and fast)
    print("\nTest 2: Repeat Swahili request (cache test)...")
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/i18n/translate",
            json={"lang": "sw", "texts": test_texts},
            timeout=90
        )
        elapsed = time.time() - start_time
        
        if response.status_code != 200:
            results.add_fail("Test 2 - Cached request", f"Status {response.status_code}: {response.text}")
        else:
            data = response.json()
            translations_cached = data.get("translations", [])
            
            # Check if results are identical
            if translations_cached == translations:
                if elapsed < 5:
                    results.add_pass("Test 2 - Cached request", f"Fast response ({elapsed:.2f}s), identical results")
                else:
                    results.add_warning("Test 2 - Cached request", f"Results identical but slow ({elapsed:.2f}s, expected <5s)")
            else:
                results.add_fail("Test 2 - Cached request", "Results differ from first request")
    
    except Exception as e:
        results.add_fail("Test 2 - Cached request", f"Exception: {str(e)}")
    
    time.sleep(1)
    
    # Test 3: English language (should return input unchanged)
    print("\nTest 3: English (en) - should return input unchanged...")
    en_texts = ["Hello", "Welcome", "Sign up"]
    try:
        response = requests.post(
            f"{BASE_URL}/i18n/translate",
            json={"lang": "en", "texts": en_texts},
            timeout=90
        )
        
        if response.status_code != 200:
            results.add_fail("Test 3 - English unchanged", f"Status {response.status_code}: {response.text}")
        else:
            data = response.json()
            translations = data.get("translations", [])
            
            if translations == en_texts:
                results.add_pass("Test 3 - English unchanged", "Input returned unchanged")
            else:
                results.add_fail("Test 3 - English unchanged", f"Expected {en_texts}, got {translations}")
    
    except Exception as e:
        results.add_fail("Test 3 - English unchanged", f"Exception: {str(e)}")
    
    time.sleep(1)
    
    # Test 4: Invalid language code (should return 400)
    print("\nTest 4: Invalid language code '123!!' - should return 400...")
    try:
        response = requests.post(
            f"{BASE_URL}/i18n/translate",
            json={"lang": "123!!", "texts": ["test"]},
            timeout=90
        )
        
        if response.status_code == 400:
            results.add_pass("Test 4 - Invalid language code", f"Correctly returned 400: {response.json().get('detail', '')}")
        else:
            results.add_fail("Test 4 - Invalid language code", f"Expected 400, got {response.status_code}")
    
    except Exception as e:
        results.add_fail("Test 4 - Invalid language code", f"Exception: {str(e)}")
    
    time.sleep(1)
    
    # Test 5: Regional code pt-BR (should work)
    print("\nTest 5: Regional code 'pt-BR' (Portuguese Brazil)...")
    pt_texts = ["Hello", "Welcome"]
    try:
        response = requests.post(
            f"{BASE_URL}/i18n/translate",
            json={"lang": "pt-BR", "texts": pt_texts},
            timeout=90
        )
        
        if response.status_code != 200:
            results.add_fail("Test 5 - Regional code pt-BR", f"Status {response.status_code}: {response.text}")
        else:
            data = response.json()
            translations = data.get("translations", [])
            
            if len(translations) == len(pt_texts):
                # Check if translated (should be Portuguese)
                if translations != pt_texts:
                    results.add_pass("Test 5 - Regional code pt-BR", f"Translations: {translations}")
                else:
                    results.add_warning("Test 5 - Regional code pt-BR", "Texts appear unchanged (might be already Portuguese)")
            else:
                results.add_fail("Test 5 - Regional code pt-BR", f"Expected {len(pt_texts)} translations, got {len(translations)}")
    
    except Exception as e:
        results.add_fail("Test 5 - Regional code pt-BR", f"Exception: {str(e)}")
    
    time.sleep(1)
    
    # Test 6: Empty texts array
    print("\nTest 6: Empty texts array []...")
    try:
        response = requests.post(
            f"{BASE_URL}/i18n/translate",
            json={"lang": "fr", "texts": []},
            timeout=90
        )
        
        if response.status_code != 200:
            results.add_fail("Test 6 - Empty texts array", f"Status {response.status_code}: {response.text}")
        else:
            data = response.json()
            translations = data.get("translations", [])
            
            if translations == []:
                results.add_pass("Test 6 - Empty texts array", "Correctly returned empty array")
            else:
                results.add_fail("Test 6 - Empty texts array", f"Expected [], got {translations}")
    
    except Exception as e:
        results.add_fail("Test 6 - Empty texts array", f"Exception: {str(e)}")
    
    time.sleep(1)
    
    # Test 7: Duplicate strings in one request
    print("\nTest 7: Duplicate strings in request...")
    dup_texts = ["Hello", "Goodbye", "Hello"]  # "Hello" appears twice
    try:
        response = requests.post(
            f"{BASE_URL}/i18n/translate",
            json={"lang": "fr", "texts": dup_texts},
            timeout=90
        )
        
        if response.status_code != 200:
            results.add_fail("Test 7 - Duplicate strings", f"Status {response.status_code}: {response.text}")
        else:
            data = response.json()
            translations = data.get("translations", [])
            
            if len(translations) == 3:
                # Check if duplicates have same translation
                if translations[0] == translations[2]:
                    results.add_pass("Test 7 - Duplicate strings", f"Duplicates handled correctly: {translations}")
                else:
                    results.add_fail("Test 7 - Duplicate strings", f"Duplicate 'Hello' has different translations: {translations[0]} vs {translations[2]}")
            else:
                results.add_fail("Test 7 - Duplicate strings", f"Expected 3 translations, got {len(translations)}")
    
    except Exception as e:
        results.add_fail("Test 7 - Duplicate strings", f"Exception: {str(e)}")


def test_auth_endpoints():
    """Test authentication endpoints and language persistence"""
    
    print("\n" + "="*80)
    print("TESTING: Authentication & Language Persistence")
    print("="*80 + "\n")
    
    # Generate unique email
    import random
    email = f"test_i18n_{int(time.time())}_{random.randint(1000,9999)}@example.com"
    password = "SecurePass123!"
    
    # Test: Register user
    print(f"Test: Register user {email}...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "email": email,
                "password": password,
                "name": "Test User",
                "gender": "male",
                "age": 28,
                "interested_in": "female",
                "city": "New York",
                "country": "USA"
            },
            timeout=30
        )
        
        if response.status_code != 200:
            results.add_fail("Auth - User registration", f"Status {response.status_code}: {response.text}")
            return  # Can't continue without registration
        
        data = response.json()
        token = data.get("token")
        
        if not token:
            results.add_fail("Auth - User registration", "No token in response")
            return
        
        results.add_pass("Auth - User registration", f"User created: {email}")
        
        # Test: Update profile with language "qu" (Quechua)
        print("\nTest: PATCH /api/auth/me with language='qu'...")
        response = requests.patch(
            f"{BASE_URL}/auth/me",
            json={"language": "qu"},
            headers={"Authorization": f"Bearer {token}"},
            timeout=30
        )
        
        if response.status_code != 200:
            results.add_fail("Auth - Language update", f"Status {response.status_code}: {response.text}")
        else:
            data = response.json()
            if data.get("language") == "qu":
                results.add_pass("Auth - Language update", "Language set to 'qu'")
            else:
                results.add_fail("Auth - Language update", f"Expected language='qu', got {data.get('language')}")
        
        # Test: Verify language persists
        print("\nTest: GET /api/auth/me to verify language persistence...")
        response = requests.get(
            f"{BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=30
        )
        
        if response.status_code != 200:
            results.add_fail("Auth - Language persistence", f"Status {response.status_code}: {response.text}")
        else:
            data = response.json()
            if data.get("language") == "qu":
                results.add_pass("Auth - Language persistence", "Language 'qu' persisted correctly")
            else:
                results.add_fail("Auth - Language persistence", f"Expected language='qu', got {data.get('language')}")
        
        # Test: Login regression
        print("\nTest: POST /api/auth/login (regression test)...")
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": email, "password": password},
            timeout=30
        )
        
        if response.status_code != 200:
            results.add_fail("Auth - Login regression", f"Status {response.status_code}: {response.text}")
        else:
            data = response.json()
            if data.get("token"):
                results.add_pass("Auth - Login regression", "Login successful")
            else:
                results.add_fail("Auth - Login regression", "No token in login response")
    
    except Exception as e:
        results.add_fail("Auth tests", f"Exception: {str(e)}")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("GIFTSDATES BACKEND API TEST SUITE")
    print("Translation Endpoint & Auth Testing")
    print("="*80)
    print(f"\nBackend URL: {BASE_URL}")
    print(f"Test started at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Run translation tests
    test_translation_endpoint()
    
    # Run auth tests
    test_auth_endpoints()
    
    # Print summary
    results.print_summary()
    
    # Exit with appropriate code
    exit(0 if len(results.failed) == 0 else 1)
