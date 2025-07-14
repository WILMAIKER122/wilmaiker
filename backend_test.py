#!/usr/bin/env python3
"""
Hotel Reservation System Backend API Tests
Tests all API endpoints for the FastAPI backend
"""

import requests
import sys
import json
from datetime import datetime, timedelta
import uuid

class HotelAPITester:
    def __init__(self, base_url="https://36d48911-e16e-4130-8c31-828b9c7b5029.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.worker_data = None
        self.client_id = None
        self.room_id = None
        self.reservation_id = None
        self.tests_run = 0
        self.tests_passed = 0

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")

    def make_request(self, method, endpoint, data=None, auth_required=False):
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if auth_required and self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None

    def test_health_check(self):
        """Test health check endpoint"""
        response = self.make_request('GET', 'api/health')
        if response and response.status_code == 200:
            data = response.json()
            success = 'status' in data and data['status'] == 'healthy'
            self.log_test("Health Check", success, f"Status: {data.get('status', 'unknown')}")
            return success
        else:
            self.log_test("Health Check", False, f"Status code: {response.status_code if response else 'No response'}")
            return False

    def test_worker_registration(self):
        """Test worker registration"""
        timestamp = datetime.now().strftime("%H%M%S")
        worker_data = {
            "email": f"test_worker_{timestamp}@hotel.com",
            "password": "TestPassword123!",
            "name": f"Test Worker {timestamp}",
            "phone": f"+1234567{timestamp[-3:]}",
            "hotel_name": f"Test Hotel {timestamp}"
        }
        
        response = self.make_request('POST', 'api/workers/register', worker_data)
        if response and response.status_code == 200:
            data = response.json()
            success = 'worker_id' in data and 'message' in data
            if success:
                self.worker_data = worker_data
            self.log_test("Worker Registration", success, f"Worker ID: {data.get('worker_id', 'N/A')}")
            return success
        else:
            error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
            self.log_test("Worker Registration", False, f"Error: {error_msg}")
            return False

    def test_worker_login(self):
        """Test worker login"""
        if not self.worker_data:
            self.log_test("Worker Login", False, "No worker data available")
            return False
            
        login_data = {
            "email": self.worker_data["email"],
            "password": self.worker_data["password"]
        }
        
        response = self.make_request('POST', 'api/workers/login', login_data)
        if response and response.status_code == 200:
            data = response.json()
            success = 'token' in data and 'worker' in data
            if success:
                self.token = data['token']
            self.log_test("Worker Login", success, f"Token received: {'Yes' if self.token else 'No'}")
            return success
        else:
            error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
            self.log_test("Worker Login", False, f"Error: {error_msg}")
            return False

    def test_worker_profile(self):
        """Test get worker profile"""
        response = self.make_request('GET', 'api/workers/profile', auth_required=True)
        if response and response.status_code == 200:
            data = response.json()
            success = 'worker_id' in data and 'name' in data and 'hotel_name' in data
            self.log_test("Worker Profile", success, f"Hotel: {data.get('hotel_name', 'N/A')}")
            return success
        else:
            error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
            self.log_test("Worker Profile", False, f"Error: {error_msg}")
            return False

    def test_get_rooms(self):
        """Test get rooms (should have 3 default rooms)"""
        response = self.make_request('GET', 'api/rooms', auth_required=True)
        if response and response.status_code == 200:
            data = response.json()
            success = isinstance(data, list) and len(data) == 3
            if success and data:
                self.room_id = data[0]['room_id']  # Store first room ID for reservation test
            self.log_test("Get Rooms", success, f"Found {len(data)} rooms")
            return success
        else:
            error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
            self.log_test("Get Rooms", False, f"Error: {error_msg}")
            return False

    def test_get_available_rooms(self):
        """Test get available rooms"""
        response = self.make_request('GET', 'api/rooms/available', auth_required=True)
        if response and response.status_code == 200:
            data = response.json()
            success = isinstance(data, list) and len(data) >= 0
            self.log_test("Get Available Rooms", success, f"Found {len(data)} available rooms")
            return success
        else:
            error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
            self.log_test("Get Available Rooms", False, f"Error: {error_msg}")
            return False

    def test_create_client(self):
        """Test create client"""
        timestamp = datetime.now().strftime("%H%M%S")
        client_data = {
            "name": f"Test Client {timestamp}",
            "email": f"client_{timestamp}@test.com",
            "phone": f"+9876543{timestamp[-3:]}",
            "identification": f"ID{timestamp}"
        }
        
        response = self.make_request('POST', 'api/clients', client_data, auth_required=True)
        if response and response.status_code == 200:
            data = response.json()
            success = 'client_id' in data and 'message' in data
            if success:
                self.client_id = data['client_id']
            self.log_test("Create Client", success, f"Client ID: {data.get('client_id', 'N/A')}")
            return success
        else:
            error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
            self.log_test("Create Client", False, f"Error: {error_msg}")
            return False

    def test_get_clients(self):
        """Test get clients"""
        response = self.make_request('GET', 'api/clients', auth_required=True)
        if response and response.status_code == 200:
            data = response.json()
            success = isinstance(data, list) and len(data) >= 1
            self.log_test("Get Clients", success, f"Found {len(data)} clients")
            return success
        else:
            error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
            self.log_test("Get Clients", False, f"Error: {error_msg}")
            return False

    def test_create_reservation(self):
        """Test create reservation"""
        if not self.client_id or not self.room_id:
            self.log_test("Create Reservation", False, "Missing client_id or room_id")
            return False
            
        # Set dates for tomorrow and day after
        check_in = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        check_out = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
        
        reservation_data = {
            "client_id": self.client_id,
            "room_id": self.room_id,
            "check_in_date": check_in,
            "check_out_date": check_out,
            "guests": 2
        }
        
        response = self.make_request('POST', 'api/reservations', reservation_data, auth_required=True)
        if response and response.status_code == 200:
            data = response.json()
            success = 'reservation_id' in data and 'total_price' in data
            if success:
                self.reservation_id = data['reservation_id']
            self.log_test("Create Reservation", success, f"Total: ${data.get('total_price', 'N/A')}")
            return success
        else:
            error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
            self.log_test("Create Reservation", False, f"Error: {error_msg}")
            return False

    def test_get_reservations(self):
        """Test get reservations"""
        response = self.make_request('GET', 'api/reservations', auth_required=True)
        if response and response.status_code == 200:
            data = response.json()
            success = isinstance(data, list) and len(data) >= 1
            self.log_test("Get Reservations", success, f"Found {len(data)} reservations")
            return success
        else:
            error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
            self.log_test("Get Reservations", False, f"Error: {error_msg}")
            return False

    def test_dashboard_stats(self):
        """Test dashboard statistics"""
        response = self.make_request('GET', 'api/dashboard/stats', auth_required=True)
        if response and response.status_code == 200:
            data = response.json()
            required_fields = ['total_clients', 'total_rooms', 'available_rooms', 'occupied_rooms', 'active_reservations']
            success = all(field in data for field in required_fields)
            self.log_test("Dashboard Stats", success, f"Stats: {data}")
            return success
        else:
            error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
            self.log_test("Dashboard Stats", False, f"Error: {error_msg}")
            return False

    def test_cancel_reservation(self):
        """Test cancel reservation"""
        if not self.reservation_id:
            self.log_test("Cancel Reservation", False, "No reservation_id available")
            return False
            
        response = self.make_request('DELETE', f'api/reservations/{self.reservation_id}', auth_required=True)
        if response and response.status_code == 200:
            data = response.json()
            success = 'message' in data
            self.log_test("Cancel Reservation", success, f"Message: {data.get('message', 'N/A')}")
            return success
        else:
            error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
            self.log_test("Cancel Reservation", False, f"Error: {error_msg}")
            return False

    def run_all_tests(self):
        """Run all API tests in sequence"""
        print("🚀 Starting Hotel Reservation System API Tests")
        print(f"🔗 Backend URL: {self.base_url}")
        print("=" * 60)
        
        # Test sequence
        tests = [
            self.test_health_check,
            self.test_worker_registration,
            self.test_worker_login,
            self.test_worker_profile,
            self.test_get_rooms,
            self.test_get_available_rooms,
            self.test_create_client,
            self.test_get_clients,
            self.test_create_reservation,
            self.test_get_reservations,
            self.test_dashboard_stats,
            self.test_cancel_reservation
        ]
        
        for test in tests:
            test()
            print()  # Add spacing between tests
        
        # Final results
        print("=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! Backend API is working correctly.")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed. Check the errors above.")
            return False

def main():
    """Main function to run tests"""
    tester = HotelAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())