import sqlite3
import bcrypt

def verify_login(email, password):
    """
    Verify login by checking if the email exists in the database
    and if the provided password matches the hashed one.
    """
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Assuming 'name' column stores the client's email
        cursor.execute("SELECT password FROM clients WHERE name = ?", (email,))
        result = cursor.fetchone()
        if not result:
            cursor.execute("SELECT password FROM drivers WHERE email = ?", (email,))
            result = cursor.fetchone()
            if not result:
                conn.close()
                return False
        conn.close()

        stored_hash = result[0]

        # Compare the entered password with the stored hash
        return bcrypt.checkpw(password.encode('utf-8'), stored_hash)

    except Exception as e:
        print("Error during login verification:", e)
        return False
