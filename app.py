from flask import (
    Flask,
    render_template,
    request,
    send_file,
    redirect,
    url_for,
    session,
    jsonify
)

from db import get_connection
import psycopg2.extras
import csv
import os
import bcrypt
from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Table,
    TableStyle
)

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from windows.metrics import metrics
from windows.health import health

# ==========================================
# MINI SIEM WEB APPLICATION
# ==========================================

import secrets

app = Flask(__name__)

app.secret_key = secrets.token_hex(32)
# ------------------------------------------
# Database Connection
# ------------------------------------------

def get_db_connection():
    conn = get_connection()

    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.close()
    except Exception:
        pass

    return conn
# ==========================================
# Role Checker
# ==========================================

def require_role(*roles):

    if "user" not in session:

        return redirect("/login")

    if session.get("role") not in roles:

        return render_template("access_denied.html"), 403

    return None

# ==========================================
# Login
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"].strip()

        conn = get_db_connection()

        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute(
            "SELECT * FROM users WHERE username = %s",
            (username,)
        )

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:

            if bcrypt.checkpw(
                password.encode("utf-8"),
                user["password"].encode("utf-8")
            ):

                session["user"] = user["username"]
                session["role"] = user["role"]

                return redirect("/")

        return render_template(
            "login.html",
            error="Invalid username or password"
        )

    return render_template("login.html")


# ==========================================
# Logout
# ==========================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

# ==========================================
# Dashboard
# ==========================================

@app.route("/")
def dashboard():

    # --------------------------------------
    # Role-Based Access Control (RBAC)
    # --------------------------------------

    response = require_role("Admin", "Analyst", "Viewer")

    if response:
        return response

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # --------------------------------------
    # Total Logs
    # --------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM logs
    """)
    total_logs = cursor.fetchone()["count"]

    # --------------------------------------
    # Windows Logs
    # --------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM logs
        WHERE source = 'Windows'
    """)
    windows_logs = cursor.fetchone()["count"]

    # --------------------------------------
    # Linux Logs
    # --------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM logs
        WHERE source = 'Linux'
    """)
    linux_logs = cursor.fetchone()["count"]

    # --------------------------------------
    # Total Alerts
    # --------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM alerts
    """)
    total_alerts = cursor.fetchone()["count"]

    # --------------------------------------
    # High Severity Alerts
    # --------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM alerts
        WHERE severity = 'HIGH'
    """)
    high_alerts = cursor.fetchone()["count"]

    # --------------------------------------
    # Latest Alert
    # --------------------------------------

    cursor.execute("""
        SELECT *
        FROM alerts
        ORDER BY id DESC
        LIMIT 1
    """)
    latest_alert = cursor.fetchone()

    # --------------------------------------
    # Latest 10 Logs
    # --------------------------------------

    cursor.execute("""
        SELECT *
        FROM logs
        ORDER BY id DESC
        LIMIT 10
    """)
    logs = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "dashboard.html",
        total_logs=total_logs,
        windows_logs=windows_logs,
        linux_logs=linux_logs,
        total_alerts=total_alerts,
        high_alerts=high_alerts,
        latest_alert=latest_alert,
        logs=logs
    )

# ==========================================
# Logs Page with Search & Date Filter
# ==========================================

@app.route("/logs")
def logs():

    # --------------------------------------
    # Role-Based Access Control (RBAC)
    # --------------------------------------

    response = require_role("Admin", "Analyst")

    if response:
        return response

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # --------------------------------------
    # Get Search Values
    # --------------------------------------

    search = request.args.get("search", "").strip()
    source = request.args.get("source", "").strip()
    from_date = request.args.get("from_date", "").strip()
    to_date = request.args.get("to_date", "").strip()

    # --------------------------------------
    # Base SQL Query
    # --------------------------------------

    query = "SELECT * FROM logs WHERE 1=1"

    params = []

    # --------------------------------------
    # Search Filter
    # --------------------------------------

    if search:

        query += """
            AND (
                username ILIKE %s
                OR event ILIKE %s
                OR ip ILIKE %s
            )
        """

        params.extend([
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        ])

    # --------------------------------------
    # Source Filter
    # --------------------------------------

    if source:

        query += " AND source = %s"

        params.append(source)

    # --------------------------------------
    # From Date Filter
    # --------------------------------------

    if from_date:

        query += " AND DATE(timestamp) >= %s"

        params.append(from_date)

    # --------------------------------------
    # To Date Filter
    # --------------------------------------

    if to_date:

        query += " AND DATE(timestamp) <= %s"

        params.append(to_date)

    # --------------------------------------
    # Sort Logs
    # --------------------------------------

    query += " ORDER BY id DESC"

    cursor.execute(query, tuple(params))

    logs = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(

        "logs.html",

        logs=logs,

        search=search,

        source=source,

        from_date=from_date,

        to_date=to_date

    )

# ==========================================
# Alerts Page
# ==========================================

@app.route("/alerts")
def alerts():

    # --------------------------------------
    # Role-Based Access Control (RBAC)
    # --------------------------------------

    response = require_role("Admin", "Analyst")

    if response:
        return response

    conn = get_db_connection()

    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute("""
        SELECT *
        FROM alerts
        ORDER BY id DESC
    """)

    alerts = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "alerts.html",
        alerts=alerts
    )

# ==========================================
# Analytics Page
# ==========================================

@app.route("/analytics")
def analytics():

    # --------------------------------------
    # Role-Based Access Control (RBAC)
    # --------------------------------------

    response = require_role("Admin", "Analyst")

    if response:
        return response

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # --------------------------------------
    # Login Statistics
    # --------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM logs
        WHERE event='LOGIN_SUCCESS'
    """)
    login_success = cursor.fetchone()["count"]

    cursor.execute("""
        SELECT COUNT(*)
        FROM logs
        WHERE event='LOGIN_FAILED'
    """)
    login_failed = cursor.fetchone()["count"]

    # --------------------------------------
    # Windows & Linux Events
    # --------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM logs
        WHERE source='Windows'
    """)
    windows_events = cursor.fetchone()["count"]

    cursor.execute("""
        SELECT COUNT(*)
        FROM logs
        WHERE source='Linux'
    """)
    linux_events = cursor.fetchone()["count"]

    # --------------------------------------
    # Top 5 Attacker IPs
    # --------------------------------------

    cursor.execute("""
        SELECT ip,
               COUNT(*) AS attempts
        FROM logs
        WHERE event='LOGIN_FAILED'
        GROUP BY ip
        ORDER BY attempts DESC
        LIMIT 5
    """)

    top_ips = cursor.fetchall()

    # --------------------------------------
    # Alert Severity
    # --------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM alerts
        WHERE severity='HIGH'
    """)
    high_alerts = cursor.fetchone()["count"]

    cursor.execute("""
        SELECT COUNT(*)
        FROM alerts
        WHERE severity='MEDIUM'
    """)
    medium_alerts = cursor.fetchone()["count"]

    cursor.execute("""
        SELECT COUNT(*)
        FROM alerts
        WHERE severity='LOW'
    """)
    low_alerts = cursor.fetchone()["count"]

    # --------------------------------------
    # Top 5 Targeted Users
    # --------------------------------------

    cursor.execute("""
        SELECT username,
               COUNT(*) AS attempts
        FROM logs
        GROUP BY username
        ORDER BY attempts DESC
        LIMIT 5
    """)

    top_users = cursor.fetchall()

    # --------------------------------------
    # Login Activity Timeline
    # --------------------------------------

    cursor.execute("""
        SELECT EXTRACT(HOUR FROM timestamp) AS hour,
               COUNT(*) AS total
        FROM logs
        GROUP BY hour
        ORDER BY hour
    """)

    timeline = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(

        "analytics.html",

        login_success=login_success,
        login_failed=login_failed,

        windows_events=windows_events,
        linux_events=linux_events,

        top_ips=top_ips,

        high_alerts=high_alerts,
        medium_alerts=medium_alerts,
        low_alerts=low_alerts,

        top_users=top_users,

        timeline=timeline

    )

# ==========================================
# About Page
# ==========================================

@app.route("/about")
def about():

    # --------------------------------------
    # Role-Based Access Control (RBAC)
    # --------------------------------------

    response = require_role("Admin", "Analyst", "Viewer")

    if response:
        return response

    return render_template("about.html")

# ==========================================
# Dashboard API
# ==========================================

@app.route("/api/dashboard")
def dashboard_api():

    # --------------------------------------
    # Role-Based Access Control (RBAC)
    # --------------------------------------

    response = require_role("Admin", "Analyst", "Viewer")

    if response:
        return response

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # --------------------------------------
    # Total Logs
    # --------------------------------------

    cursor.execute("SELECT COUNT(*) FROM logs")
    total_logs = cursor.fetchone()["count"]

    # --------------------------------------
    # Windows Logs
    # --------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM logs
        WHERE source='Windows'
    """)
    windows_logs = cursor.fetchone()["count"]

    # --------------------------------------
    # Linux Logs
    # --------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM logs
        WHERE source='Linux'
    """)
    linux_logs = cursor.fetchone()["count"]

    # --------------------------------------
    # Total Alerts
    # --------------------------------------

    cursor.execute("SELECT COUNT(*) FROM alerts")
    total_alerts = cursor.fetchone()["count"]

    # --------------------------------------
    # Latest Alert
    # --------------------------------------

    cursor.execute("""
        SELECT *
        FROM alerts
        ORDER BY id DESC
        LIMIT 1
    """)
    latest_alert = cursor.fetchone()

    # --------------------------------------
    # Latest Logs
    # --------------------------------------

    cursor.execute("""
        SELECT *
        FROM logs
        ORDER BY id DESC
        LIMIT 10
    """)
    logs = cursor.fetchall()

    cursor.close()
    conn.close()

    return {

        "total_logs": total_logs,

        "windows_logs": windows_logs,

        "linux_logs": linux_logs,

        "total_alerts": total_alerts,

        "latest_alert": latest_alert if latest_alert else None,

        "logs": logs

    }

# ==========================================
# Alerts API (Live AJAX)
# ==========================================

@app.route("/api/alerts")
def alerts_api():

    # --------------------------------------
    # Role-Based Access Control (RBAC)
    # --------------------------------------

    response = require_role("Admin", "Analyst")

    if response:
        return response

    conn = get_db_connection()

    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute("""
        SELECT *
        FROM alerts
        ORDER BY id DESC
    """)

    alerts = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        "alerts": alerts
    }

# ==========================================
# Logs API (Live AJAX)
# ==========================================

@app.route("/api/logs")
def logs_api():

    # --------------------------------------
    # Role-Based Access Control (RBAC)
    # --------------------------------------

    response = require_role("Admin", "Analyst")

    if response:
        return response

    conn = get_db_connection()

    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # --------------------------------------
    # Get Filters
    # --------------------------------------

    search = request.args.get("search", "").strip()
    source = request.args.get("source", "").strip()
    from_date = request.args.get("from_date", "").strip()
    to_date = request.args.get("to_date", "").strip()

    query = "SELECT * FROM logs WHERE 1=1"

    params = []

    # --------------------------------------
    # Search Filter
    # --------------------------------------

    if search:

        query += """
            AND (
                ip ILIKE %s
                OR username ILIKE %s
                OR event ILIKE %s
            )
        """

        keyword = f"%{search}%"

        params.extend([keyword, keyword, keyword])

    # --------------------------------------
    # Source Filter
    # --------------------------------------

    if source:

        query += " AND source = %s"

        params.append(source)

    # --------------------------------------
    # Date Filters
    # --------------------------------------

    if from_date:

        query += " AND DATE(timestamp) >= %s"

        params.append(from_date)

    if to_date:

        query += " AND DATE(timestamp) <= %s"

        params.append(to_date)

    query += " ORDER BY id DESC LIMIT 100"

    cursor.execute(query, tuple(params))

    logs = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({

        "logs": logs

    })

# ==========================================
# Analytics API (Live AJAX)
# ==========================================

@app.route("/api/analytics")
def analytics_api():

    # --------------------------------------
    # Role-Based Access Control (RBAC)
    # --------------------------------------

    response = require_role("Admin", "Analyst")

    if response:
        return response

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # --------------------------------------
    # Dashboard Statistics
    # --------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM logs
    """)
    total_logs = cursor.fetchone()["count"]

    cursor.execute("""
        SELECT COUNT(*)
        FROM alerts
    """)
    total_alerts = cursor.fetchone()["count"]

    # --------------------------------------
    # Login Statistics
    # --------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM logs
        WHERE event='LOGIN_SUCCESS'
    """)
    login_success = cursor.fetchone()["count"]

    cursor.execute("""
        SELECT COUNT(*)
        FROM logs
        WHERE event='LOGIN_FAILED'
    """)
    login_failed = cursor.fetchone()["count"]

    # --------------------------------------
    # Windows & Linux Statistics
    # --------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM logs
        WHERE source='Windows'
    """)
    windows_events = cursor.fetchone()["count"]

    cursor.execute("""
        SELECT COUNT(*)
        FROM logs
        WHERE source='Linux'
    """)
    linux_events = cursor.fetchone()["count"]

    # --------------------------------------
    # Alert Severity
    # --------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM alerts
        WHERE severity='HIGH'
    """)
    high_alerts = cursor.fetchone()["count"]

    cursor.execute("""
        SELECT COUNT(*)
        FROM alerts
        WHERE severity='MEDIUM'
    """)
    medium_alerts = cursor.fetchone()["count"]

    cursor.execute("""
        SELECT COUNT(*)
        FROM alerts
        WHERE severity='LOW'
    """)
    low_alerts = cursor.fetchone()["count"]

    # --------------------------------------
    # Event Statistics
    # --------------------------------------

    cursor.execute("""
        SELECT event,
               COUNT(*) AS count
        FROM logs
        GROUP BY event
        ORDER BY count DESC
    """)

    event_stats = cursor.fetchall()

    # --------------------------------------
    # Top Attacker IPs
    # --------------------------------------

    cursor.execute("""
        SELECT ip,
               COUNT(*) AS attempts
        FROM logs
        WHERE event='LOGIN_FAILED'
        GROUP BY ip
        ORDER BY attempts DESC
        LIMIT 5
    """)

    top_ips = cursor.fetchall()

    # --------------------------------------
    # Top Users
    # --------------------------------------

    cursor.execute("""
        SELECT username,
               COUNT(*) AS attempts
        FROM logs
        GROUP BY username
        ORDER BY attempts DESC
        LIMIT 5
    """)

    top_users = cursor.fetchall()

    # --------------------------------------
    # Login Timeline
    # --------------------------------------

    cursor.execute("""
        SELECT EXTRACT(HOUR FROM timestamp) AS hour,
               COUNT(*) AS total
        FROM logs
        GROUP BY hour
        ORDER BY hour
    """)

    timeline = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({

        "total_logs": total_logs,

        "total_alerts": total_alerts,

        "login_success": login_success,

        "login_failed": login_failed,

        "windows_events": windows_events,

        "linux_events": linux_events,

        "high_alerts": high_alerts,

        "medium_alerts": medium_alerts,

        "low_alerts": low_alerts,

        "event_stats": event_stats,

        "top_ips": top_ips,

        "top_users": top_users,

        "timeline": timeline

    })

# ==========================================
# Collector Status API
# ==========================================

@app.route("/api/collector/status")
def collector_status():

    # --------------------------------------
    # Role-Based Access Control (RBAC)
    # --------------------------------------

    response = require_role("Admin", "Analyst", "Viewer")

    if response:
        return response

    health_data = health.status()
    metric_data = metrics.status()

    return {

        "collector": health_data["collector"],
        "database": health_data["database"],
        "state_file": health_data["state_file"],
        "last_scan": health_data["last_scan"],
        "overall": health_data["overall"],

        "uptime": metric_data["uptime"],
        "events_processed": metric_data["events_processed"],
        "duplicates_skipped": metric_data["duplicates_skipped"],
        "errors": metric_data["errors"],
        "last_record_id": metric_data["last_record_id"],
        "events_per_second": metric_data["events_per_second"]

    }

# ==========================================
# Export Logs to CSV
# ==========================================

@app.route("/export/csv")
def export_csv():

    # --------------------------------------
    # Role-Based Access Control (RBAC)
    # --------------------------------------

    response = require_role("Admin", "Analyst")

    if response:
        return response

    conn = get_db_connection()

    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # --------------------------------------
    # Fetch All Logs
    # --------------------------------------

    cursor.execute("""
        SELECT
            id,
            timestamp,
            event,
            username,
            ip,
            source,
            hostname,
            severity
        FROM logs
        ORDER BY id DESC
    """)

    logs = cursor.fetchall()

    cursor.close()
    conn.close()

    # --------------------------------------
    # Create Export Folder
    # --------------------------------------

    os.makedirs("exports", exist_ok=True)

    file_path = os.path.join("exports", "logs.csv")

    # --------------------------------------
    # Write CSV File
    # --------------------------------------

    with open(file_path, "w", newline="", encoding="utf-8") as csv_file:

        writer = csv.writer(csv_file)

        # CSV Header
        writer.writerow([
            "ID",
            "Timestamp",
            "Event",
            "Username",
            "IP Address",
            "Source",
            "Hostname",
            "Severity"
        ])

        # CSV Data
        for log in logs:

            writer.writerow([
                log["id"],
                log["timestamp"],
                log["event"],
                log["username"],
                log["ip"],
                log["source"],
                log["hostname"],
                log["severity"]
            ])

    # --------------------------------------
    # Download CSV
    # --------------------------------------

    return send_file(
        file_path,
        as_attachment=True,
        download_name="MiniSIEM_Logs.csv",
        mimetype="text/csv"
    )

# ==========================================
# Export Professional PDF Report
# ==========================================

@app.route("/export/pdf")
def export_pdf():

    # --------------------------------------
    # Role-Based Access Control (RBAC)
    # --------------------------------------

    response = require_role("Admin")

    if response:
        return response

    conn = get_db_connection()

    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # --------------------------------------
    # System Summary
    # --------------------------------------

    cursor.execute("""
        SELECT COUNT(*) FROM logs
    """)
    total_logs = cursor.fetchone()["count"]

    cursor.execute("""
        SELECT COUNT(*) FROM logs
        WHERE source='Windows'
    """)
    windows_logs = cursor.fetchone()["count"]

    cursor.execute("""
        SELECT COUNT(*) FROM logs
        WHERE source='Linux'
    """)
    linux_logs = cursor.fetchone()["count"]

    cursor.execute("""
        SELECT COUNT(*) FROM alerts
    """)
    total_alerts = cursor.fetchone()["count"]

    cursor.execute("""
        SELECT COUNT(*) FROM alerts
        WHERE severity='HIGH'
    """)
    high_alerts = cursor.fetchone()["count"]

    cursor.execute("""
        SELECT COUNT(*) FROM alerts
        WHERE severity='MEDIUM'
    """)
    medium_alerts = cursor.fetchone()["count"]

    cursor.execute("""
        SELECT COUNT(*) FROM alerts
        WHERE severity='LOW'
    """)
    low_alerts = cursor.fetchone()["count"]

    # --------------------------------------
    # Latest Alert
    # --------------------------------------

    cursor.execute("""
        SELECT *
        FROM alerts
        ORDER BY id DESC
        LIMIT 1
    """)

    latest_alert = cursor.fetchone()

    # --------------------------------------
    # Top 5 Attacker IPs
    # --------------------------------------

    cursor.execute("""
        SELECT ip,
               COUNT(*) AS attempts
        FROM logs
        WHERE event='LOGIN_FAILED'
        GROUP BY ip
        ORDER BY attempts DESC
        LIMIT 5
    """)

    top_ips = cursor.fetchall()

    cursor.close()
    conn.close()

    # --------------------------------------
    # Create Reports Folder
    # --------------------------------------

    os.makedirs("reports", exist_ok=True)

    file_path = os.path.join(
        "reports",
        "MiniSIEM_Security_Report.pdf"
    )

    # --------------------------------------
    # Create PDF
    # --------------------------------------

    doc = SimpleDocTemplate(file_path)

    styles = getSampleStyleSheet()

    story = []

    # ======================================
    # Title
    # ======================================

    story.append(
        Paragraph(
            "<b>MiniSIEM Security Report</b>",
            styles["Title"]
        )
    )

    story.append(
        Paragraph(
            f"Generated: {datetime.now().strftime('%d %B %Y %I:%M %p')}",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph("<br/>", styles["Normal"])
    )

    # ======================================
    # System Summary
    # ======================================

    story.append(
        Paragraph("<b>System Summary</b>", styles["Heading2"])
    )

    summary = [

        ["Total Logs", str(total_logs)],

        ["Windows Events", str(windows_logs)],

        ["Linux Events", str(linux_logs)],

        ["Total Alerts", str(total_alerts)]

    ]

    table = Table(summary)

    table.setStyle(TableStyle([

        ("GRID", (0,0), (-1,-1), 1, colors.black),

        ("BACKGROUND", (0,0), (0,-1), colors.lightgrey),

        ("BOTTOMPADDING", (0,0), (-1,-1), 8)

    ]))

    story.append(table)

    story.append(
        Paragraph("<br/>", styles["Normal"])
    )

    # ======================================
    # Alert Summary
    # ======================================

    story.append(
        Paragraph("<b>Alert Summary</b>", styles["Heading2"])
    )

    alerts = [

        ["High Severity", str(high_alerts)],

        ["Medium Severity", str(medium_alerts)],

        ["Low Severity", str(low_alerts)]

    ]

    alert_table = Table(alerts)

    alert_table.setStyle(TableStyle([

        ("GRID",(0,0),(-1,-1),1,colors.black),

        ("BACKGROUND",(0,0),(0,-1),colors.lightgrey)

    ]))

    story.append(alert_table)

    story.append(
        Paragraph("<br/>", styles["Normal"])
    )

    # ======================================
    # Latest Alert
    # ======================================

    story.append(
        Paragraph("<b>Latest Alert</b>", styles["Heading2"])
    )

    if latest_alert:

        story.append(
            Paragraph(
                f"<b>Attack Type:</b> {latest_alert['alert_type']}",
                styles["Normal"]
            )
        )

        story.append(
            Paragraph(
                f"<b>Attacker IP:</b> {latest_alert['ip']}",
                styles["Normal"]
            )
        )

        story.append(
            Paragraph(
                f"<b>Severity:</b> {latest_alert['severity']}",
                styles["Normal"]
            )
        )

        story.append(
            Paragraph(
                f"<b>Recommendation:</b> {latest_alert['recommendation']}",
                styles["Normal"]
            )
        )

    else:

        story.append(
            Paragraph(
                "No alerts available.",
                styles["Normal"]
            )
        )

    story.append(
        Paragraph("<br/>", styles["Normal"])
    )

    # ======================================
    # Top Attacker IPs
    # ======================================

    story.append(
        Paragraph("<b>Top Attacker IPs</b>", styles["Heading2"])
    )

    ip_data = [["IP Address", "Failed Attempts"]]

    for ip in top_ips:

        ip_data.append([
            ip["ip"],
            str(ip["attempts"])
        ])

    ip_table = Table(ip_data)

    ip_table.setStyle(TableStyle([

        ("GRID",(0,0),(-1,-1),1,colors.black),

        ("BACKGROUND",(0,0),(-1,0),colors.grey),

        ("TEXTCOLOR",(0,0),(-1,0),colors.white),

        ("ALIGN",(0,0),(-1,-1),"CENTER")

    ]))

    story.append(ip_table)

    story.append(
        Paragraph("<br/>", styles["Normal"])
    )

   # ======================================
# Footer
# ======================================

story.append(
    Paragraph(
        "<b>Generated by MiniSIEM Professional v2.0</b>",
        styles["Heading3"]
    )
)

story.append(
    Paragraph(
        "Powered by Python • Flask • PostgreSQL (Neon)",
        styles["Normal"]
    )
)

doc.build(story)

return send_file(
    file_path,
    as_attachment=True,
    download_name="MiniSIEM_Professional_Security_Report.pdf",
    mimetype="application/pdf"
)
# ==========================================
# 404 Error Handler
# ==========================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template("404.html"), 404


# ==========================================
# 500 Error Handler
# ==========================================

@app.errorhandler(500)
def internal_server_error(error):

    return render_template("500.html"), 500


# ==========================================
# Run Application
# ==========================================
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )