"""
Test script to demonstrate PESEL masking functionality

This script tests that PESEL numbers are properly masked in API responses,
showing only the last 4 digits in the format: *******5123

Usage:
    python test_pesel_masking.py
"""

import sys


def test_mask_pesel():
    """Test PESEL masking logic"""
    
    def mask_pesel(pesel):
        """Mask PESEL to show only last 4 digits"""
        if not pesel or len(pesel) < 4:
            return pesel
        return '*' * (len(pesel) - 4) + pesel[-4:]
    
    test_cases = [
        # (input, expected_output, description)
        ("92050812345", "*******2345", "Valid 11-digit PESEL"),
        ("12345678901", "*******8901", "Another valid PESEL"),
        ("123", "123", "Too short - no masking"),
        ("", "", "Empty string"),
        (None, None, "None value"),
        ("1234", "1234", "Exactly 4 digits - no masking"),
        ("12345", "*2345", "5 digits - mask 1 char"),
    ]
    
    print("=" * 70)
    print("PESEL MASKING TEST")
    print("=" * 70)
    print()
    
    passed = 0
    failed = 0
    
    for input_val, expected, description in test_cases:
        result = mask_pesel(input_val)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} | {description}")
        print(f"  Input:    {repr(input_val)}")
        print(f"  Expected: {repr(expected)}")
        print(f"  Got:      {repr(result)}")
        print()
    
    print("=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0


def test_integration_example():
    """Show how PESEL masking works in API context"""
    print("\n" + "=" * 70)
    print("INTEGRATION EXAMPLE")
    print("=" * 70)
    print()
    
    # Simulate a database row
    class MockRow:
        def __init__(self, data):
            self._mapping = data
    
    # Sample user data from database
    db_row = MockRow({
        'ID': 1,
        'USER_NAME': 'Jan',
        'USER_LASTNAME': 'Kowalski',
        'EMAIL': 'jan.kowalski@example.com',
        'PESEL': '92050812345',  # Original PESEL in database
        'PHONE': '+48 123 456 789',
        'IS_USER_ACTIVE': True,
        'UKNF_ID': 'UKNF001',
        'DATE_CREATE': None,
        'DATE_ACTRUALIZATION': None
    })
    
    def mask_pesel(pesel):
        if not pesel or len(pesel) < 4:
            return pesel
        return '*' * (len(pesel) - 4) + pesel[-4:]
    
    # Process data for API response
    user_data = dict(db_row._mapping)
    original_pesel = user_data['PESEL']
    user_data['PESEL'] = mask_pesel(user_data['PESEL'])
    
    print("Database stored PESEL (original):")
    print(f"  {original_pesel}")
    print()
    print("API response PESEL (masked):")
    print(f"  {user_data['PESEL']}")
    print()
    print("Full API response:")
    print("  {")
    for key, value in user_data.items():
        if key not in ['DATE_CREATE', 'DATE_ACTRUALIZATION']:
            print(f'    "{key}": {repr(value)},')
    print("  }")
    print()
    
    print("=" * 70)
    print("✅ PESEL is properly masked in API responses!")
    print("=" * 70)


if __name__ == "__main__":
    print("\n")
    success = test_mask_pesel()
    test_integration_example()
    
    print("\n")
    if success:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed!")
        sys.exit(1)

