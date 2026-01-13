"""
Script to send Python coding challenges to the system via API.
This reads the challenges from add_python_challenges.py and sends them via POST request.

Usage:
1. Make sure you're logged in as admin in your browser
2. Get your session cookie from browser developer tools
3. Run: python3 send_challenges_via_api.py

Or use the interactive version that logs in automatically:
python3 send_challenges_via_api.py --auto-login
"""
import requests
import json
import sys
from add_python_challenges import generate_more_challenges

# Configuration
BASE_URL = "http://localhost:8000"  # Change to your domain (e.g., "https://talentschat-1.onrender.com")
ADMIN_EMAIL = "admin@talentschat.com"
ADMIN_PASSWORD = "admin123"


def send_challenges_via_api(session=None, base_url=BASE_URL):
    """Send challenges via API using a session"""
    if not session:
        session = requests.Session()
    
    # Generate challenges from the existing script
    print("📦 Generating challenges from add_python_challenges.py...")
    all_challenges = generate_more_challenges()
    print(f"✅ Generated {len(all_challenges)} challenges")
    
    # Prepare the request data
    request_data = {
        "challenges": all_challenges
    }
    
    # Send to API
    api_url = f"{base_url}/api/admin/coding-challenges/bulk-add"
    print(f"\n🚀 Sending challenges to: {api_url}")
    
    try:
        response = session.post(
            api_url,
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=60  # 60 second timeout for large requests
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Success!")
            print(f"   Added: {result.get('added', 0)} challenges")
            print(f"   Skipped: {result.get('skipped', 0)} challenges (duplicates)")
            print(f"   Total in database: {result.get('total_in_db', 0)} challenges")
            
            if result.get('errors'):
                print(f"\n⚠️  Some errors occurred:")
                for error in result['errors'][:5]:  # Show first 5 errors
                    print(f"   - {error}")
                if len(result.get('errors', [])) > 5:
                    print(f"   ... and {len(result['errors']) - 5} more errors")
            
            return True
        else:
            print(f"\n❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Message: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request failed: {e}")
        return False


def auto_login_and_send(base_url=BASE_URL, email=ADMIN_EMAIL, password=ADMIN_PASSWORD):
    """Automatically log in and send challenges"""
    session = requests.Session()
    
    print(f"🔐 Logging in as {email}...")
    login_url = f"{base_url}/auth/login"
    
    try:
        # Get the login page first to get CSRF token (if needed)
        login_page = session.get(login_url)
        
        # Login
        login_data = {
            "email": email,
            "password": password,
            "remember_me": False
        }
        
        login_response = session.post(login_url, data=login_data, allow_redirects=False)
        
        if login_response.status_code in [302, 200]:
            print("✅ Login successful!")
            return send_challenges_via_api(session, base_url)
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Login request failed: {e}")
        return False


def manual_session_send(base_url=BASE_URL):
    """Instructions for manual session cookie method"""
    print("=" * 60)
    print("Manual Session Cookie Method")
    print("=" * 60)
    print("\n1. Open your browser and log in as admin")
    print("2. Open Developer Tools (F12)")
    print("3. Go to Application/Storage > Cookies")
    print("4. Copy the 'session' cookie value")
    print("5. Run this script with the cookie:")
    print("\n   python3 -c \"")
    print("   import requests")
    print("   from send_challenges_via_api import send_challenges_via_api")
    print("   session = requests.Session()")
    print("   session.cookies.set('session', 'YOUR_SESSION_COOKIE_HERE')")
    print("   send_challenges_via_api(session, 'YOUR_BASE_URL')")
    print("   \"")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Send Python challenges via API')
    parser.add_argument('--base-url', default=BASE_URL, help='Base URL of the application')
    parser.add_argument('--email', default=ADMIN_EMAIL, help='Admin email')
    parser.add_argument('--password', default=ADMIN_PASSWORD, help='Admin password')
    parser.add_argument('--auto-login', action='store_true', help='Automatically log in and send')
    parser.add_argument('--manual', action='store_true', help='Show manual instructions')
    
    args = parser.parse_args()
    
    if args.manual:
        manual_session_send(args.base_url)
        sys.exit(0)
    
    if args.auto_login:
        success = auto_login_and_send(args.base_url, args.email, args.password)
        sys.exit(0 if success else 1)
    else:
        print("=" * 60)
        print("Python Challenges API Sender")
        print("=" * 60)
        print("\nOptions:")
        print("1. Auto-login: python3 send_challenges_via_api.py --auto-login")
        print("2. Manual (with session cookie): python3 send_challenges_via_api.py --manual")
        print("\nFor production (Render.com), use:")
        print(f"   python3 send_challenges_via_api.py --auto-login --base-url https://your-domain.onrender.com")
        print("\n" + "=" * 60)

