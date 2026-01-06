import requests
import base64

BASE_URL = "http://localhost:5000"

def get_auth_header(username, password):
    auth = f"{username}:{password}"
    encoded = base64.b64encode(auth.encode()).decode()
    return {"Authorization": f"Basic {encoded}"}

print("🧪 Testing Indian Library API...")
print()

# Test 1: Home page
print("1. Testing home page...")
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"   ✅ Status: {response.status_code}")
    print(f"   📄 Response: {response.json()['message']}")
except:
    print("   ❌ Failed to connect")

# Test 2: Health check
print("\n2. Testing health check...")
try:
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"   ✅ Status: {response.status_code}")
    data = response.json()
    print(f"   📊 Books in database: {data['books_count']}")
except:
    print("   ❌ Failed")

# Test 3: Get books with sai credentials
print("\n3. Getting books (as sai)...")
try:
    headers = get_auth_header("sai", "sai@123")
    response = requests.get(f"{BASE_URL}/api/books", headers=headers)
    print(f"   ✅ Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   📚 Found {data['count']} books")
        print(f"   👤 Logged in as: {data['user']}")
        
        # Show first 2 books
        print("\n   📖 Sample books:")
        for i, book in enumerate(data['books'][:2]):
            print(f"     {i+1}. {book['title']} by {book['author']}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Get stats
print("\n4. Getting statistics (as teja)...")
try:
    headers = get_auth_header("teja", "teja@123")
    response = requests.get(f"{BASE_URL}/api/stats", headers=headers)
    print(f"   ✅ Status: {response.status_code}")
    if response.status_code == 200:
        stats = response.json()['stats']
        print(f"   📊 Total books: {stats['total_books']}")
        print(f"   📊 Books by sai: {stats['books_by_sai']}")
        print(f"   📊 Books by teja: {stats['books_by_teja']}")
except:
    print("   ❌ Failed")

print("\n" + "="*50)
print("🎉 Test completed!")
print("\n📌 Credentials to use:")
print("   Username: sai, Password: sai@123")
print("   Username: teja, Password: teja@123")