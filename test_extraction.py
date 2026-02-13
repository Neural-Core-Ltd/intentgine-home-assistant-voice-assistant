#!/usr/bin/env python3
"""
Test script for classification extraction feature.

This script tests the Home Assistant integration's ability to handle
multi-intent commands using Intentgine's classification extraction.

Usage:
    python test_extraction.py

Requirements:
    - Home Assistant running with Intentgine integration installed
    - API key configured
    - At least 2 areas with exposed entities (e.g., kitchen, bedroom)
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any

# Configuration
HA_URL = "http://localhost:8123"
HA_TOKEN = "YOUR_LONG_LIVED_ACCESS_TOKEN"  # Get from HA profile

# Test commands
TEST_COMMANDS = [
    # Single-intent (should NOT extract)
    {
        "command": "Turn on kitchen lights",
        "expected_extraction": False,
        "expected_actions": 1
    },
    # Two intents, different areas (should extract)
    {
        "command": "Turn on kitchen lights and turn off bedroom lights",
        "expected_extraction": True,
        "expected_actions": 2
    },
    # Three intents, different areas (should extract)
    {
        "command": "Turn on kitchen lights, close bedroom blinds, and set living room to 72",
        "expected_extraction": True,
        "expected_actions": 3
    },
    # Two intents, same area (should extract)
    {
        "command": "Turn on kitchen lights and set kitchen to 50%",
        "expected_extraction": True,
        "expected_actions": 2
    },
    # Ambiguous - might or might not extract
    {
        "command": "Turn on all the lights",
        "expected_extraction": False,
        "expected_actions": 1
    }
]


async def call_intentgine_service(command: str) -> Dict[str, Any]:
    """Call the intentgine.execute_command service."""
    url = f"{HA_URL}/api/services/intentgine/execute_command"
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "command": command
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise Exception(f"Service call failed: {resp.status} - {text}")
            return await resp.json()


async def test_command(test_case: Dict[str, Any]) -> Dict[str, Any]:
    """Test a single command."""
    command = test_case["command"]
    expected_extraction = test_case["expected_extraction"]
    expected_actions = test_case["expected_actions"]
    
    print(f"\n{'='*70}")
    print(f"Testing: {command}")
    print(f"Expected extraction: {expected_extraction}")
    print(f"Expected actions: {expected_actions}")
    print(f"{'='*70}")
    
    try:
        result = await call_intentgine_service(command)
        
        # Check if extraction occurred
        extracted = result.get("extracted", False)
        
        # Count actions
        if extracted:
            actions = len(result.get("results", []))
        else:
            actions = 1
        
        # Determine success
        success = result.get("success", False)
        
        # Print results
        print(f"\n✓ Command executed")
        print(f"  Extraction: {extracted}")
        print(f"  Actions: {actions}")
        print(f"  Success: {success}")
        
        if extracted:
            print(f"\n  Extracted commands:")
            for i, sub_result in enumerate(result.get("results", []), 1):
                print(f"    {i}. {sub_result.get('query')}")
                print(f"       Area: {sub_result.get('area')}")
                print(f"       Tool: {sub_result.get('tool')}")
                print(f"       Success: {sub_result.get('success')}")
        else:
            print(f"\n  Single command:")
            print(f"    Area: {result.get('area')}")
            print(f"    Tool: {result.get('tool')}")
        
        # Check expectations
        extraction_match = extracted == expected_extraction
        actions_match = actions == expected_actions
        
        if not extraction_match:
            print(f"\n⚠️  Extraction mismatch: expected {expected_extraction}, got {extracted}")
        
        if not actions_match:
            print(f"⚠️  Actions mismatch: expected {expected_actions}, got {actions}")
        
        if extraction_match and actions_match and success:
            print(f"\n✅ Test PASSED")
            return {"status": "pass", "result": result}
        elif success:
            print(f"\n⚠️  Test PARTIAL (executed but didn't match expectations)")
            return {"status": "partial", "result": result}
        else:
            print(f"\n❌ Test FAILED (execution failed)")
            return {"status": "fail", "result": result}
    
    except Exception as err:
        print(f"\n❌ Test FAILED with error: {err}")
        return {"status": "error", "error": str(err)}


async def main():
    """Run all tests."""
    print("="*70)
    print("Classification Extraction Test Suite")
    print("="*70)
    print(f"\nHome Assistant URL: {HA_URL}")
    print(f"Number of tests: {len(TEST_COMMANDS)}")
    
    results = []
    for test_case in TEST_COMMANDS:
        result = await test_command(test_case)
        results.append(result)
        await asyncio.sleep(1)  # Rate limiting
    
    # Summary
    print(f"\n{'='*70}")
    print("Test Summary")
    print(f"{'='*70}")
    
    passed = sum(1 for r in results if r["status"] == "pass")
    partial = sum(1 for r in results if r["status"] == "partial")
    failed = sum(1 for r in results if r["status"] == "fail")
    errors = sum(1 for r in results if r["status"] == "error")
    
    print(f"\nTotal tests: {len(results)}")
    print(f"✅ Passed: {passed}")
    print(f"⚠️  Partial: {partial}")
    print(f"❌ Failed: {failed}")
    print(f"💥 Errors: {errors}")
    
    if passed == len(results):
        print(f"\n🎉 All tests passed!")
    elif passed + partial == len(results):
        print(f"\n⚠️  All tests executed, but some didn't match expectations")
        print(f"   This might be expected behavior depending on your setup")
    else:
        print(f"\n❌ Some tests failed or errored")
    
    print(f"\n{'='*70}")


if __name__ == "__main__":
    asyncio.run(main())
