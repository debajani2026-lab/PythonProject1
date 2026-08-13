from db_connection import get_connection


def check_login(username, password):
    connection = get_connection()
    if connection is None:
        return None

    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM admin WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password))
    result = cursor.fetchone()

    cursor.close()
    connection.close()
    return result


if __name__ == "__main__":
    admin = check_login("admin", "admin123")
    if admin:
        print(f"Login successful! Welcome, {admin['full_name']}")
    else:
        print("Login failed. Wrong username or password.")