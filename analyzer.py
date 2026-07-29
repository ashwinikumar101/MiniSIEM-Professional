import sqlite3

# ==========================================
# MINI SIEM ANALYZER
# ==========================================

conn = sqlite3.connect("database/siem.db")
cursor = conn.cursor()

# Find IPs with failed login attempts
cursor.execute("""
SELECT ip, COUNT(*) as failed_attempts
FROM logs
WHERE event='LOGIN_FAILED'
GROUP BY ip
""")

results = cursor.fetchall()

print("=" * 60)
print("           MINI SIEM ANALYZER")
print("=" * 60)

attack_found = False

for ip, attempts in results:

    print(f"Checking IP : {ip}")
    print(f"Failed Attempts : {attempts}")
    print("-" * 60)

    if attempts >= 5:

        attack_found = True

        # Check whether the alert already exists
        cursor.execute("""
        SELECT COUNT(*)
        FROM alerts
        WHERE alert_type=? AND ip=?
        """, ("Brute Force Attack", ip))

        exists = cursor.fetchone()[0]

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
            VALUES (?, ?, ?, ?, ?)
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
conn.close()

print("=" * 60)
print("Analysis Completed Successfully!")
print("=" * 60)