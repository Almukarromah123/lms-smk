import pymysql

try:
    # Connect to MySQL server (without specifying database)
    connection = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='112233',
    )

    cursor = connection.cursor()

    # Create database if not exists
    cursor.execute("CREATE DATABASE IF NOT EXISTS lms_smk CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    print("SUCCESS: Database 'lms_smk' created successfully!")

    cursor.close()
    connection.close()

except Exception as e:
    print(f"ERROR: {e}")
