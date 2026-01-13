# API Endpoint: Bulk Add Coding Challenges

## Endpoint
`POST /api/admin/coding-challenges/bulk-add`

## Authentication
Requires admin user to be logged in (session-based authentication via Flask-Login).

## Request Format

### Headers
```
Content-Type: application/json
Cookie: session=<your_session_cookie>
```

### Body (JSON)
```json
{
  "challenges": [
    {
      "title": "Hello World",
      "description": "Write a function that returns the string 'Hello, World!'",
      "difficulty": "easy",
      "starter_code": "def hello_world():\n    # Your code here\n    pass",
      "test_cases": [
        {"input": "", "expected_output": "Hello, World!"}
      ],
      "points": 5
    },
    {
      "title": "Sum Two Numbers",
      "description": "Write a function that takes two numbers and returns their sum.",
      "difficulty": "easy",
      "starter_code": "def sum_numbers(a, b):\n    # Your code here\n    pass",
      "test_cases": [
        {"input": "2, 3", "expected_output": "5"},
        {"input": "-1, 1", "expected_output": "0"}
      ],
      "points": 5
    }
  ]
}
```

### Field Descriptions
- `challenges` (array, required): Array of challenge objects
- `title` (string, required): Challenge title
- `description` (string, required): Challenge description
- `difficulty` (string, optional): "easy", "medium", or "hard" (defaults to "easy")
- `starter_code` (string, optional): Starter code for the challenge
- `test_cases` (array, optional): Array of test case objects with `input` and `expected_output`
- `points` (integer, optional): Points awarded (defaults to 10)

## Response Format

### Success (200)
```json
{
  "success": true,
  "added": 95,
  "skipped": 5,
  "total": 100,
  "total_in_db": 95
}
```

### Error (400/401/403/500)
```json
{
  "success": false,
  "error": "Error message"
}
```

## Usage Examples

### Using cURL (after logging in and getting session cookie)
```bash
# First, log in via the web interface to get session cookie
# Then use the session cookie in your request:

curl -X POST https://your-domain.com/api/admin/coding-challenges/bulk-add \
  -H "Content-Type: application/json" \
  -H "Cookie: session=your_session_cookie_here" \
  -d @challenges.json
```

### Using Python requests (after logging in)
```python
import requests

# First log in to get session
session = requests.Session()
login_response = session.post('https://your-domain.com/auth/login', data={
    'email': 'admin@talentschat.com',
    'password': 'admin123'
})

# Then add challenges
with open('challenges.json', 'r') as f:
    challenges_data = json.load(f)

response = session.post(
    'https://your-domain.com/api/admin/coding-challenges/bulk-add',
    json=challenges_data
)

print(response.json())
```

### Using JavaScript/Fetch (in browser console, while logged in as admin)
```javascript
fetch('/api/admin/coding-challenges/bulk-add', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  credentials: 'include',  // Include cookies
  body: JSON.stringify({
    challenges: [
      {
        title: "Hello World",
        description: "Write a function that returns 'Hello, World!'",
        difficulty: "easy",
        starter_code: "def hello_world():\n    pass",
        test_cases: [{"input": "", "expected_output": "Hello, World!"}],
        points: 5
      }
      // ... more challenges
    ]
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

## Notes
- Challenges with duplicate titles are skipped (not added)
- All challenges are set as `is_active=True` by default
- Test cases are stored as JSON string in the database
- The endpoint will skip invalid challenges and continue processing others
- Errors for individual challenges are included in the response if any occur

