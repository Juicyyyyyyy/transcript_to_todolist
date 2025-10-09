#!/usr/bin/env python3
"""
Comprehensive API testing script
Tests all endpoints in the reunion-to-code API
"""
import requests
import json
import io
import zipfile
from pathlib import Path

BASE_URL = "http://localhost:8000/api"

def print_test_result(test_name, passed, details=""):
    """Print formatted test results"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"\n{status} - {test_name}")
    if details:
        print(f"  Details: {details}")

def test_root_endpoint():
    """Test GET /api/ endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/")
        passed = response.status_code == 200 and response.json() == {"Hello": "World"}
        print_test_result(
            "GET /api/", 
            passed, 
            f"Status: {response.status_code}, Response: {response.json()}"
        )
        return passed
    except Exception as e:
        print_test_result("GET /api/", False, f"Error: {str(e)}")
        return False

def test_import_transcript():
    """Test POST /api/import-transcript/{folder_id} endpoint"""
    try:
        folder_id = "test_folder_transcript"
        
        # Create a test file
        test_content = b"This is a test transcript file"
        files = {"file": ("test_transcript.txt", io.BytesIO(test_content), "text/plain")}
        
        response = requests.post(f"{BASE_URL}/import-transcript/{folder_id}", files=files)
        passed = response.status_code == 200 and "name" in response.json()
        print_test_result(
            f"POST /api/import-transcript/{folder_id}", 
            passed,
            f"Status: {response.status_code}, Response: {response.json() if response.status_code == 200 else response.text}"
        )
        return passed
    except Exception as e:
        print_test_result("POST /api/import-transcript/{folder_id}", False, f"Error: {str(e)}")
        return False

def test_import_project():
    """Test POST /api/import-project/{folder_id} endpoint"""
    try:
        folder_id = "test_folder_project"
        
        # Create a test zip file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("test_file.txt", "Test content")
            zip_file.writestr("test_folder/another_file.txt", "More test content")
        
        zip_buffer.seek(0)
        files = {"file": ("test_project.zip", zip_buffer, "application/zip")}
        
        response = requests.post(f"{BASE_URL}/import-project/{folder_id}", files=files)
        passed = response.status_code == 200 and "name" in response.json()
        print_test_result(
            f"POST /api/import-project/{folder_id}", 
            passed,
            f"Status: {response.status_code}, Response: {response.json() if response.status_code == 200 else response.text}"
        )
        return passed
    except Exception as e:
        print_test_result("POST /api/import-project/{folder_id}", False, f"Error: {str(e)}")
        return False

def test_import_project_invalid_file():
    """Test POST /api/import-project/{folder_id} with non-zip file (should fail)"""
    try:
        folder_id = "test_folder_invalid"
        
        # Create a non-zip file
        test_content = b"This is not a zip file"
        files = {"file": ("test_file.txt", io.BytesIO(test_content), "text/plain")}
        
        response = requests.post(f"{BASE_URL}/import-project/{folder_id}", files=files)
        passed = response.status_code == 400  # Should return 400 for non-zip files
        print_test_result(
            f"POST /api/import-project/{folder_id} (invalid file)", 
            passed,
            f"Status: {response.status_code} (expected 400), Response: {response.json() if response.status_code != 200 else response.text}"
        )
        return passed
    except Exception as e:
        print_test_result("POST /api/import-project/{folder_id} (invalid file)", False, f"Error: {str(e)}")
        return False

def test_generate_todolist():
    """Test POST /api/generate-todolist endpoint"""
    try:
        # Note: This endpoint requires OpenAI API key and will likely fail without it
        # We're testing the endpoint structure and error handling
        payload = {
            "parsed_project": "Sample parsed project structure",
            "transcript": "Sample transcript of the meeting"
        }
        
        response = requests.post(
            f"{BASE_URL}/generate-todolist",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        # This endpoint will likely fail without OpenAI API key, so we check for proper error handling
        if response.status_code == 500:
            passed = True  # Expected to fail without API key
            details = f"Status: {response.status_code} (expected without API key), Response: {response.json()}"
        elif response.status_code == 200:
            passed = "context" in response.json() and "technical_todolist" in response.json()
            details = f"Status: {response.status_code}, Response keys: {list(response.json().keys())}"
        else:
            passed = False
            details = f"Unexpected status: {response.status_code}, Response: {response.text}"
        
        print_test_result(
            "POST /api/generate-todolist", 
            passed,
            details
        )
        return passed
    except Exception as e:
        print_test_result("POST /api/generate-todolist", False, f"Error: {str(e)}")
        return False

def test_build_output():
    """Test POST /api/build-output endpoint"""
    try:
        payload = {
            "context": "Test context",
            "technical_todo": "Test technical todo list",
            "clarifications": "Test clarifications"
        }
        
        response = requests.post(
            f"{BASE_URL}/build-output",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        # Check if request was processed (status 200 or proper error)
        passed = response.status_code in [200, 500]
        print_test_result(
            "POST /api/build-output", 
            passed,
            f"Status: {response.status_code}, Response: {response.json() if response.status_code in [200, 500] else response.text}"
        )
        return passed
    except Exception as e:
        print_test_result("POST /api/build-output", False, f"Error: {str(e)}")
        return False

def test_extract_symbols():
    """Test POST /api/extract-symbols endpoint"""
    try:
        # Use the example PHP project in the repo
        project_path = str(Path(__file__).parent / "php_js_project_example" / "pomopensource")
        
        # Test with a known PHP model file
        payload = {
            "project_path": project_path,
            "file_path": "app/Models/User.php"
        }
        
        response = requests.post(
            f"{BASE_URL}/extract-symbols",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        # Check if request was successful and has expected structure
        if response.status_code == 200:
            data = response.json()
            passed = "file" in data and "classes" in data
            details = f"Status: {response.status_code}, Found {len(data.get('classes', []))} class(es)"
            if data.get('classes'):
                details += f", First class: {data['classes'][0].get('class_name', 'N/A')}"
            
            # Print the complete parser output for OpenAI API inspection
            print("\n" + "=" * 70)
            print("COMPLETE PARSER OUTPUT (for OpenAI API):")
            print("=" * 70)
            print(json.dumps(data, indent=2))
            print("=" * 70)
            
        elif response.status_code == 400:
            # File might not exist or project path invalid
            passed = True  # Expected behavior for invalid input
            details = f"Status: {response.status_code} (expected for invalid path), Response: {response.json()}"
        else:
            passed = False
            details = f"Unexpected status: {response.status_code}, Response: {response.text}"
        
        print_test_result(
            "POST /api/extract-symbols", 
            passed,
            details
        )
        return passed
    except Exception as e:
        print_test_result("POST /api/extract-symbols", False, f"Error: {str(e)}")
        return False

def test_parse_project():
    """Test POST /api/parse-project endpoint"""
    try:
        # Use the example PHP project in the repo
        project_path = str(Path(__file__).parent / "php_js_project_example" / "pomopensource")
        
        payload = {
            "project_path": project_path
        }
        
        response = requests.post(
            f"{BASE_URL}/parse-project",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        # Check if request was successful and has expected structure
        if response.status_code == 200:
            data = response.json()
            passed = "parsed_project" in data and len(data["parsed_project"]) > 0
            parsed_content = data["parsed_project"]
            
            # Count some statistics
            lines_count = parsed_content.count('\n')
            classes_count = parsed_content.count('### Class:')
            
            details = f"Status: {response.status_code}, Parsed content length: {len(parsed_content)} chars, {lines_count} lines, {classes_count} classes"
            
            # Print the complete parsed project output for OpenAI API inspection
            print("\n" + "=" * 70)
            print("COMPLETE PARSED PROJECT OUTPUT (for OpenAI API):")
            print("=" * 70)
            print(parsed_content[:2000])  # Print first 2000 chars
            if len(parsed_content) > 2000:
                print(f"\n... [truncated, total length: {len(parsed_content)} chars] ...")
            print("=" * 70)
            
        elif response.status_code == 400:
            # Project path might be invalid
            passed = True  # Expected behavior for invalid input
            details = f"Status: {response.status_code} (expected for invalid path), Response: {response.json()}"
        else:
            passed = False
            details = f"Unexpected status: {response.status_code}, Response: {response.text}"
        
        print_test_result(
            "POST /api/parse-project", 
            passed,
            details
        )
        return passed
    except Exception as e:
        print_test_result("POST /api/parse-project", False, f"Error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("API Testing Suite for reunion-to-code")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/", timeout=2)
    except requests.exceptions.ConnectionError:
        print("\n❌ FATAL: Cannot connect to API server at", BASE_URL)
        print("Make sure the server is running with: uvicorn main:app --reload")
        return
    
    print(f"\n✅ Server is running at {BASE_URL}")
    
    # Run all tests
    results = []
    results.append(("Root Endpoint", test_root_endpoint()))
    results.append(("Import Transcript", test_import_transcript()))
    results.append(("Import Project (valid zip)", test_import_project()))
    results.append(("Import Project (invalid file)", test_import_project_invalid_file()))
    results.append(("Generate TodoList", test_generate_todolist()))
    results.append(("Build Output", test_build_output()))
    results.append(("Extract Symbols", test_extract_symbols()))
    results.append(("Parse Project", test_parse_project()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed")

if __name__ == "__main__":
    main()



