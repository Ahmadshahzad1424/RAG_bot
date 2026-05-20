import sqlite3
import hashlib
import os

DB_FILE = "users.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL
        )
    ''')
    try:
        c.execute("ALTER TABLE users ADD COLUMN full_name TEXT DEFAULT 'User'")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16).hex()
    
    # Simple SHA-256 hash with salt
    # For a real production app, use bcrypt or argon2
    hasher = hashlib.sha256()
    hasher.update((password + salt).encode('utf-8'))
    password_hash = hasher.hexdigest()
    
    return password_hash, salt

def create_user(username, password, full_name):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Check if user exists
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    if c.fetchone() is not None:
        conn.close()
        return False, "Username already exists"
    
    password_hash, salt = hash_password(password)
    
    try:
        c.execute("INSERT INTO users (username, full_name, password_hash, salt) VALUES (?, ?, ?, ?)", 
                  (username, full_name, password_hash, salt))
        conn.commit()
        success = True
        msg = "User created successfully"
    except Exception as e:
        success = False
        msg = str(e)
    finally:
        conn.close()
        
    return success, msg

def authenticate_user(username, password):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute("SELECT full_name, password_hash, salt FROM users WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()
    
    if result is None:
        return False, None
        
    full_name, stored_hash, salt = result
    password_hash, _ = hash_password(password, salt)
    
    if password_hash == stored_hash:
        return True, full_name
    return False, None
