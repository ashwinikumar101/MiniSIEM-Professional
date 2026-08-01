from db import get_connection
import psycopg2.extras

# ==========================================
# MINI SIEM ANALYZER
# ==========================================

conn = get_connection()

cursor = conn.cursor(
    cursor_factory=psycopg2.extras.RealDictCursor
)

# ==========================================
# Find IPs with failed login attempts
# ==========================================

cursor.execute("""
SELECT ip, COUNT(*) AS failed_attempts
FROM logs
WHERE event='LOGIN_FAILED'
GROUP BY ip
""")

results = cursor.fetchall()

print("=" * 60)
print("           MINI SIEM ANALYZER")
print("=" * 60)

attack_found = False

for row in results:

    ip = row["ip"]
    attempts = row["failed_attempts"]

    print(f"Checking IP : {ip}")
    print(f"Failed Attempts : {attempts}")
    print("-" * 60)

    if attempts >= 5:

        attack_found = True

        # ==========================================
        # Check whether the alert already exists
        # ==========================================

        cursor.execute("""
        SELECT COUNT(*)
        FROM alerts
        WHERE alert_type=%s AND ip=%s
        """, (
            "Brute Force Attack",
            ip
        ))

        exists = cursor.fetchone()["count"]

        if exists == 0:

            cursor.execute("""
            INSERT INTO alerts
            (
                alert_type,
                ip,
                failed_attempts,
                severity,
                recommendation
            )
            VALUES (%s, %s, %s, %s, %s)
            """, (
                "Brute Force Attack",
                ip,
                attempts,
                "HIGH",
                "Block the IP and investigate immediately."
            ))

            print("🚨 NEW BRUTE FORCE ATTACK DETECTED")
            print(f"Attacker IP : {ip}")
            print(f"Attempts    : {attempts}")
            print("Severity    : HIGH")
            print()

        else:

            print("Alert already exists.")
            print()

if not attack_found:

    print("No suspicious activity detected.")

conn.commit()

cursor.close()
conn.close()

print("=" * 60)
print("Analysis Completed Successfully!")
print("=" * 60)