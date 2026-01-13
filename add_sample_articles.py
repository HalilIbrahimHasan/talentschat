#!/usr/bin/env python3
"""
Script to add sample articles with code snippets to the TalentifyLab workspace
"""

import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.workspace import Workspace
from app.models.user import User
from app.models.article import Article
from datetime import datetime

def add_sample_articles():
    app = create_app()
    
    with app.app_context():
        # Find the TalentifyLab workspace
        workspace = Workspace.query.filter_by(slug='talentifylab').first()
        if not workspace:
            print("❌ Workspace 'talentifylab' not found!")
            return
        
        # Get the first admin user or any user in the workspace
        user = User.query.filter_by(is_admin=True).first()
        if not user:
            # Try to get any user
            user = User.query.first()
        if not user:
            print("❌ No users found in the database!")
            return
        
        print(f"✅ Using workspace: {workspace.name}")
        print(f"✅ Using author: {user.name if hasattr(user, 'name') else user.email}")
        
        articles_data = [
            {
                'title': 'Getting Started with Python',
                'excerpt': 'Learn the basics of Python programming with practical examples and code snippets.',
                'content': '''# Getting Started with Python

Python is a powerful and versatile programming language that's perfect for beginners and experts alike.

## Why Python?

Python is known for its:
- **Simple syntax** that's easy to read and write
- **Versatile** - used in web development, data science, AI, and more
- **Large community** with extensive libraries and support

## Your First Python Program

Here's a simple "Hello, World!" program:

```python
# This is a comment in Python
print("Hello, World!")
print("Welcome to Python programming!")
```

## Variables and Data Types

Python is dynamically typed, meaning you don't need to declare variable types:

```python
# Numbers
age = 25
price = 19.99

# Strings
name = "Alice"
greeting = f"Hello, {name}!"

# Lists
fruits = ["apple", "banana", "orange"]
numbers = [1, 2, 3, 4, 5]

# Dictionaries
person = {
    "name": "Bob",
    "age": 30,
    "city": "New York"
}
```

## Control Flow

### If Statements

```python
temperature = 75

if temperature > 80:
    print("It's hot outside!")
elif temperature > 60:
    print("Nice weather!")
else:
    print("It's a bit cool.")
```

### Loops

```python
# For loop
for i in range(5):
    print(f"Number: {i}")

# While loop
count = 0
while count < 5:
    print(f"Count: {count}")
    count += 1
```

## Functions

Functions help you organize and reuse code:

```python
def greet(name, age):
    """Greet a person with their name and age"""
    return f"Hello, {name}! You are {age} years old."

message = greet("Alice", 25)
print(message)
```

## Working with Lists

Python lists are very powerful:

```python
# List comprehension
squares = [x**2 for x in range(10)]
print(squares)  # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# Filter and map
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
even_squares = [x**2 for x in numbers if x % 2 == 0]
print(even_squares)  # [4, 16, 36, 64, 100]
```

Happy coding! 🐍
''',
                'is_published': True
            },
            {
                'title': 'JavaScript Fundamentals: Functions and Closures',
                'excerpt': 'Deep dive into JavaScript functions, arrow functions, and the powerful closure concept.',
                'content': '''# JavaScript Fundamentals: Functions and Closures

Functions are one of the most important concepts in JavaScript. Let's explore different ways to define and use them.

## Function Declarations

The traditional way to define functions:

```javascript
function greet(name) {
    return `Hello, ${name}!`;
}

console.log(greet("Alice")); // Hello, Alice!
```

## Function Expressions

Functions can also be assigned to variables:

```javascript
const add = function(a, b) {
    return a + b;
};

console.log(add(5, 3)); // 8
```

## Arrow Functions (ES6+)

Arrow functions provide a more concise syntax:

```javascript
// Simple arrow function
const multiply = (a, b) => a * b;

// With body and return
const divide = (a, b) => {
    if (b === 0) {
        throw new Error("Cannot divide by zero!");
    }
    return a / b;
};

// Single parameter (no parentheses needed)
const square = x => x * x;
```

## Higher-Order Functions

Functions that operate on other functions:

```javascript
const numbers = [1, 2, 3, 4, 5];

// Map: transform each element
const doubled = numbers.map(n => n * 2);
console.log(doubled); // [2, 4, 6, 8, 10]

// Filter: select elements that meet a condition
const evens = numbers.filter(n => n % 2 === 0);
console.log(evens); // [2, 4]

// Reduce: combine elements into a single value
const sum = numbers.reduce((acc, n) => acc + n, 0);
console.log(sum); // 15
```

## Closures

Closures allow functions to "remember" variables from their outer scope:

```javascript
function createCounter() {
    let count = 0;
    
    return function() {
        count++;
        return count;
    };
}

const counter1 = createCounter();
const counter2 = createCounter();

console.log(counter1()); // 1
console.log(counter1()); // 2
console.log(counter2()); // 1 (independent counter)
```

## Practical Example: API Call Wrapper

Here's a practical example using closures to create an API wrapper:

```javascript
function createAPI(baseURL) {
    return {
        get: async (endpoint) => {
            const response = await fetch(`${baseURL}${endpoint}`);
            return response.json();
        },
        post: async (endpoint, data) => {
            const response = await fetch(`${baseURL}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            return response.json();
        }
    };
}

const api = createAPI('https://api.example.com');
const users = await api.get('/users');
```

Master these concepts and you'll be well on your way to JavaScript mastery! 🚀
''',
                'is_published': True
            },
            {
                'title': 'SQL Queries for Data Analysis',
                'excerpt': 'Essential SQL queries and patterns for analyzing data effectively.',
                'content': '''# SQL Queries for Data Analysis

SQL (Structured Query Language) is essential for working with databases. Here are some powerful queries for data analysis.

## Basic SELECT Queries

```sql
-- Select all columns
SELECT * FROM users;

-- Select specific columns
SELECT id, name, email FROM users;

-- Select with conditions
SELECT * FROM users WHERE age > 18;

-- Select with multiple conditions
SELECT * FROM users 
WHERE age > 18 AND status = 'active';
```

## Aggregations

```sql
-- Count records
SELECT COUNT(*) FROM users;

-- Count with conditions
SELECT COUNT(*) FROM users WHERE status = 'active';

-- Average, Sum, Min, Max
SELECT 
    AVG(price) as avg_price,
    SUM(price) as total_sales,
    MIN(price) as min_price,
    MAX(price) as max_price
FROM orders;

-- Group by
SELECT 
    category,
    COUNT(*) as product_count,
    AVG(price) as avg_price
FROM products
GROUP BY category;
```

## JOINs

```sql
-- Inner Join
SELECT 
    u.name,
    o.order_date,
    o.total_amount
FROM users u
INNER JOIN orders o ON u.id = o.user_id;

-- Left Join (all users, even without orders)
SELECT 
    u.name,
    COALESCE(SUM(o.total_amount), 0) as total_spent
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;
```

## Window Functions

```sql
-- Rank products by price within each category
SELECT 
    name,
    category,
    price,
    RANK() OVER (PARTITION BY category ORDER BY price DESC) as rank
FROM products;

-- Calculate running totals
SELECT 
    order_date,
    total_amount,
    SUM(total_amount) OVER (ORDER BY order_date) as running_total
FROM orders
ORDER BY order_date;
```

## Common Table Expressions (CTEs)

```sql
-- Calculate monthly sales totals
WITH monthly_sales AS (
    SELECT 
        DATE_TRUNC('month', order_date) as month,
        SUM(total_amount) as monthly_total
    FROM orders
    GROUP BY DATE_TRUNC('month', order_date)
)
SELECT 
    month,
    monthly_total,
    LAG(monthly_total) OVER (ORDER BY month) as previous_month,
    monthly_total - LAG(monthly_total) OVER (ORDER BY month) as difference
FROM monthly_sales;
```

## Subqueries

```sql
-- Find users who have placed orders
SELECT * FROM users
WHERE id IN (
    SELECT DISTINCT user_id FROM orders
);

-- Find products more expensive than average
SELECT * FROM products
WHERE price > (
    SELECT AVG(price) FROM products
);
```

SQL is a powerful tool for data analysis. Practice these patterns to become proficient! 📊
''',
                'is_published': True
            },
            {
                'title': 'React Hooks: useState and useEffect Explained',
                'excerpt': 'Master React Hooks with practical examples of useState and useEffect.',
                'content': '''# React Hooks: useState and useEffect Explained

React Hooks revolutionized how we write React components. Let's explore the two most important hooks.

## useState Hook

The `useState` hook allows functional components to have state:

```javascript
import React, { useState } from 'react';

function Counter() {
    const [count, setCount] = useState(0);
    
    return (
        <div>
            <p>Count: {count}</p>
            <button onClick={() => setCount(count + 1)}>
                Increment
            </button>
            <button onClick={() => setCount(count - 1)}>
                Decrement
            </button>
        </div>
    );
}
```

## Multiple State Variables

```javascript
function UserForm() {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [age, setAge] = useState(0);
    
    const handleSubmit = (e) => {
        e.preventDefault();
        console.log({ name, email, age });
    };
    
    return (
        <form onSubmit={handleSubmit}>
            <input 
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Name"
            />
            <input 
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Email"
            />
            <input 
                type="number"
                value={age}
                onChange={(e) => setAge(parseInt(e.target.value))}
                placeholder="Age"
            />
            <button type="submit">Submit</button>
        </form>
    );
}
```

## useEffect Hook

`useEffect` handles side effects in functional components:

```javascript
import React, { useState, useEffect } from 'react';

function UserProfile({ userId }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        // Fetch user data when component mounts or userId changes
        async function fetchUser() {
            setLoading(true);
            const response = await fetch(`/api/users/${userId}`);
            const data = await response.json();
            setUser(data);
            setLoading(false);
        }
        
        fetchUser();
    }, [userId]); // Dependency array
    
    if (loading) return <div>Loading...</div>;
    if (!user) return <div>User not found</div>;
    
    return <div>{user.name}</div>;
}
```

## Cleanup in useEffect

```javascript
function Timer() {
    const [seconds, setSeconds] = useState(0);
    
    useEffect(() => {
        const interval = setInterval(() => {
            setSeconds(prev => prev + 1);
        }, 1000);
        
        // Cleanup function
        return () => clearInterval(interval);
    }, []); // Empty dependency array = run once on mount
    
    return <div>Timer: {seconds} seconds</div>;
}
```

## Combining Hooks

```javascript
function TodoList() {
    const [todos, setTodos] = useState([]);
    const [filter, setFilter] = useState('all');
    
    // Load todos from localStorage on mount
    useEffect(() => {
        const saved = localStorage.getItem('todos');
        if (saved) {
            setTodos(JSON.parse(saved));
        }
    }, []);
    
    // Save todos to localStorage whenever they change
    useEffect(() => {
        localStorage.setItem('todos', JSON.stringify(todos));
    }, [todos]);
    
    const addTodo = (text) => {
        setTodos([...todos, { id: Date.now(), text, completed: false }]);
    };
    
    const filteredTodos = todos.filter(todo => {
        if (filter === 'completed') return todo.completed;
        if (filter === 'active') return !todo.completed;
        return true;
    });
    
    return (
        <div>
            {/* Todo list UI */}
        </div>
    );
}
```

Hooks make React code more readable and reusable. Practice these patterns to master React! ⚛️
''',
                'is_published': True
            },
            {
                'title': 'Git Workflow: Branching and Merging',
                'excerpt': 'Learn essential Git commands for branching, merging, and collaborative development.',
                'content': '''# Git Workflow: Branching and Merging

Git is a powerful version control system. Understanding branching and merging is crucial for collaborative development.

## Creating and Switching Branches

```bash
# Create a new branch
git branch feature/new-feature

# Switch to the branch
git checkout feature/new-feature

# Create and switch in one command
git checkout -b feature/new-feature

# List all branches
git branch

# List remote branches
git branch -r
```

## Working with Branches

```bash
# See which branch you're on
git status

# Rename current branch
git branch -m new-branch-name

# Delete a branch (after merging)
git branch -d feature/old-feature

# Force delete a branch
git branch -D feature/old-feature
```

## Merging Branches

```bash
# Merge a branch into current branch
git checkout main
git merge feature/new-feature

# Merge with a commit message
git merge feature/new-feature -m "Merge feature branch"

# Abort a merge if there are conflicts
git merge --abort
```

## Resolving Merge Conflicts

When conflicts occur, Git marks them in the files:

```bash
# Check which files have conflicts
git status

# Open conflicted files and resolve manually
# Look for markers like:
# <<<<<<< HEAD
# code from current branch
# =======
# code from incoming branch
# >>>>>>> feature/new-feature

# After resolving, stage the files
git add conflicted-file.js

# Complete the merge
git commit
```

## Pull Requests Workflow

```bash
# 1. Create a feature branch
git checkout -b feature/add-login

# 2. Make changes and commit
git add .
git commit -m "Add user login functionality"

# 3. Push branch to remote
git push origin feature/add-login

# 4. Create pull request on GitHub/GitLab
# 5. After review and merge, clean up locally
git checkout main
git pull origin main
git branch -d feature/add-login
```

## Stashing Changes

```bash
# Save current changes without committing
git stash

# List stashes
git stash list

# Apply most recent stash
git stash apply

# Apply and remove from stash
git stash pop

# Create a stash with a message
git stash save "WIP: working on feature"
```

## Rebase (Alternative to Merge)

```bash
# Rebase current branch onto main
git checkout feature/new-feature
git rebase main

# Interactive rebase (last 3 commits)
git rebase -i HEAD~3

# Abort rebase if needed
git rebase --abort
```

## Useful Git Aliases

Add these to your `~/.gitconfig`:

```bash
[alias]
    co = checkout
    br = branch
    ci = commit
    st = status
    unstage = reset HEAD --
    last = log -1 HEAD
    visual = !gitk
```

Master these Git workflows and you'll collaborate more effectively! 🔀
''',
                'is_published': True
            }
        ]
        
        # Create articles
        created_count = 0
        for article_data in articles_data:
            # Create a temporary article to generate the slug
            temp_article = Article(
                workspace_id=workspace.id,
                title=article_data['title']
            )
            base_slug = temp_article.slug
            
            # Check if article with this slug already exists
            existing = Article.query.filter_by(
                workspace_id=workspace.id,
                slug=base_slug
            ).first()
            
            if existing:
                print(f"⏭️  Article '{article_data['title']}' already exists, skipping...")
                continue
            
            # Create article
            article = Article(
                workspace_id=workspace.id,
                author_id=user.id,
                title=article_data['title'],
                content=article_data['content'],
                excerpt=article_data['excerpt'],
                is_published=article_data['is_published']
            )
            
            # Generate HTML content
            article.set_content_html()
            
            if article.is_published:
                article.publish()
            
            db.session.add(article)
            created_count += 1
            print(f"✅ Created article: '{article_data['title']}'")
        
        db.session.commit()
        print(f"\n🎉 Successfully created {created_count} articles!")

if __name__ == '__main__':
    add_sample_articles()

