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

import sqlite3
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
    conn = sqlite3.connect("database/siem.db")
    conn.row_factory = sqlite3.Row
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

        user = conn.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()

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

    # --------------------------------------
    # Total Logs
    # --------------------------------------

    total_logs = conn.execute("""
        SELECT COUNT(*)
        FROM logs
    """).fetchone()[0]

    # --------------------------------------
    # Windows Logs
    # --------------------------------------

    windows_logs = conn.execute("""
        SELECT COUNT(*)
        FROM logs
        WHERE source = 'Windows'
    """).fetchone()[0]

    # --------------------------------------
    # Linux Logs
    # --------------------------------------

    linux_logs = conn.execute("""
        SELECT COUNT(*)
        FROM logs
        WHERE source = 'Linux'
    """).fetchone()[0]

    # --------------------------------------
    # Total Alerts
    # --------------------------------------

    total_alerts = conn.execute("""
        SELECT COUNT(*)
        FROM alerts
    """).fetchone()[0]

    # --------------------------------------
    # High Severity Alerts
    # --------------------------------------

    high_alerts = conn.execute("""
        SELECT COUNT(*)
        FROM alerts
        WHERE severity = 'HIGH'
    """).fetchone()[0]

    # --------------------------------------
    # Latest Alert
    # --------------------------------------

    latest_alert = conn.execute("""
        SELECT *
        FROM alerts
        ORDER BY id DESC
        LIMIT 1
    """).fetchone()

    # --------------------------------------
    # Latest 10 Logs
    # --------------------------------------

    logs = conn.execute("""
        SELECT *
        FROM logs
        ORDER BY id DESC
        LIMIT 10
    """).fetchall()

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
                username LIKE ?
                OR event LIKE ?
                OR ip LIKE ?
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

        query += " AND source=?"

        params.append(source)

    # --------------------------------------
    # From Date Filter
    # --------------------------------------

    if from_date:

        query += " AND DATE(timestamp) >= ?"

        params.append(from_date)

    # --------------------------------------
    # To Date Filter
    # --------------------------------------

    if to_date:

        query += " AND DATE(timestamp) <= ?"

        params.append(to_date)

    # --------------------------------------
    # Sort Logs
    # --------------------------------------

    query += " ORDER BY id DESC"

    logs = conn.execute(query, params).fetchall()

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

    alerts = conn.execute("""
        SELECT *
        FROM alerts
        ORDER BY id DESC
    """).fetchall()

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

    # --------------------------------------
    # Login Statistics
    # --------------------------------------

    login_success = conn.execute("""
        SELECT COUNT(*)
        FROM logs
        WHERE event='LOGIN_SUCCESS'
    """).fetchone()[0]

    login_failed = conn.execute("""
        SELECT COUNT(*)
        FROM logs
        WHERE event='LOGIN_FAILED'
    """).fetchone()[0]

    # --------------------------------------
    # Windows & Linux Events
    # --------------------------------------

    windows_events = conn.execute("""
        SELECT COUNT(*)
        FROM logs
        WHERE source='Windows'
    """).fetchone()[0]

    linux_events = conn.execute("""
        SELECT COUNT(*)
        FROM logs
        WHERE source='Linux'
    """).fetchone()[0]

    # --------------------------------------
    # Top 5 Attacker IPs
    # --------------------------------------

    top_ips = conn.execute("""
        SELECT ip,
               COUNT(*) AS attempts
        FROM logs
        WHERE event='LOGIN_FAILED'
        GROUP BY ip
        ORDER BY attempts DESC
        LIMIT 5
    """).fetchall()

    # --------------------------------------
    # Alert Severity
    # --------------------------------------

    high_alerts = conn.execute("""
        SELECT COUNT(*)
        FROM alerts
        WHERE severity='HIGH'
    """).fetchone()[0]

    medium_alerts = conn.execute("""
        SELECT COUNT(*)
        FROM alerts
        WHERE severity='MEDIUM'
    """).fetchone()[0]

    low_alerts = conn.execute("""
        SELECT COUNT(*)
        FROM alerts
        WHERE severity='LOW'
    """).fetchone()[0]

    # --------------------------------------
    # Top 5 Targeted Users
    # --------------------------------------

    top_users = conn.execute("""
        SELECT username,
               COUNT(*) AS attempts
        FROM logs
        GROUP BY username
        ORDER BY attempts DESC
        LIMIT 5
    """).fetchall()

    # --------------------------------------
    # Login Activity Timeline
    # --------------------------------------

    timeline = conn.execute("""
        SELECT substr(timestamp,12,2) AS hour,
               COUNT(*) AS total
        FROM logs
        GROUP BY hour
        ORDER BY hour
    """).fetchall()

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

    # --------------------------------------
    # Total Logs
    # --------------------------------------

    total_logs = conn.execute(
        "SELECT COUNT(*) FROM logs"
    ).fetchone()[0]

    # --------------------------------------
    # Windows Logs
    # --------------------------------------

    windows_logs = conn.execute("""
        SELECT COUNT(*)
        FROM logs
        WHERE source='Windows'
    """).fetchone()[0]

    # --------------------------------------
    # Linux Logs
    # --------------------------------------

    linux_logs = conn.execute("""
        SELECT COUNT(*)
        FROM logs
        WHERE source='Linux'
    """).fetchone()[0]

    # --------------------------------------
    # Total Alerts
    # --------------------------------------

    total_alerts = conn.execute(
        "SELECT COUNT(*) FROM alerts"
    ).fetchone()[0]

    # --------------------------------------
    # Latest Alert
    # --------------------------------------

    latest_alert = conn.execute("""
        SELECT *
        FROM alerts
        ORDER BY id DESC
        LIMIT 1
    """).fetchone()

    # --------------------------------------
    # Latest Logs
    # --------------------------------------

    logs = conn.execute("""
        SELECT *
        FROM logs
        ORDER BY id DESC
        LIMIT 10
    """).fetchall()

    conn.close()

    return {

        "total_logs": total_logs,

        "windows_logs": windows_logs,

        "linux_logs": linux_logs,

        "total_alerts": total_alerts,

        "latest_alert": dict(latest_alert) if latest_alert else None,

        "logs": [dict(log) for log in logs]

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

    alerts = conn.execute("""
        SELECT *
        FROM alerts
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return {
        "alerts": [dict(alert) for alert in alerts]
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
                ip LIKE ?
                OR username LIKE ?
                OR event LIKE ?
            )
        """

        keyword = f"%{search}%"

        params.extend([keyword, keyword, keyword])

    # --------------------------------------
    # Source Filter
    # --------------------------------------

    if source:

        query += " AND source = ?"

        params.append(source)

    # --------------------------------------
    # Date Filters
    # --------------------------------------

    if from_date:

        query += " AND DATE(timestamp) >= ?"

        params.append(from_date)

    if to_date:

        query += " AND DATE(timestamp) <= ?"

        params.append(to_date)

    query += " ORDER BY id DESC LIMIT 100"

    logs = conn.execute(query, params).fetchall()

    conn.close()

    return jsonify({

        "logs": [dict(log) for log in logs]

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

    # --------------------------------------
    # Dashboard Statistics
    # --------------------------------------

    total_logs = conn.execute("""
        SELECT COUNT(*)
        FROM logs
    """).fetchone()[0]

    total_alerts = conn.execute("""
        SELECT COUNT(*)
        FROM alerts
    """).fetchone()[0]

    # --------------------------------------
    # Login Statistics
    # --------------------------------------

    login_success = conn.execute("""
        SELECT COUNT(*)
        FROM logs
        WHERE event='LOGIN_SUCCESS'
    """).fetchone()[0]

    login_failed = conn.execute("""
        SELECT COUNT(*)
        FROM logs
        WHERE event='LOGIN_FAILED'
    """).fetchone()[0]

    # --------------------------------------
    # Windows & Linux Statistics
    # --------------------------------------

    windows_events = conn.execute("""
        SELECT COUNT(*)
        FROM logs
        WHERE source='Windows'
    """).fetchone()[0]

    linux_events = conn.execute("""
        SELECT COUNT(*)
        FROM logs
        WHERE source='Linux'
    """).fetchone()[0]

    # --------------------------------------
    # Alert Severity
    # --------------------------------------

    high_alerts = conn.execute("""
        SELECT COUNT(*)
        FROM alerts
        WHERE severity='HIGH'
    """).fetchone()[0]

    medium_alerts = conn.execute("""
        SELECT COUNT(*)
        FROM alerts
        WHERE severity='MEDIUM'
    """).fetchone()[0]

    low_alerts = conn.execute("""
        SELECT COUNT(*)
        FROM alerts
        WHERE severity='LOW'
    """).fetchone()[0]

    # --------------------------------------
    # Event Statistics
    # --------------------------------------

    event_stats = conn.execute("""
        SELECT event,
               COUNT(*) AS count
        FROM logs
        GROUP BY event
        ORDER BY count DESC
    """).fetchall()

    # --------------------------------------
    # Top Attacker IPs
    # --------------------------------------

    top_ips = conn.execute("""
        SELECT ip,
               COUNT(*) AS attempts
        FROM logs
        WHERE event='LOGIN_FAILED'
        GROUP BY ip
        ORDER BY attempts DESC
        LIMIT 5
    """).fetchall()

    # --------------------------------------
    # Top Users
    # --------------------------------------

    top_users = conn.execute("""
        SELECT username,
               COUNT(*) AS attempts
        FROM logs
        GROUP BY username
        ORDER BY attempts DESC
        LIMIT 5
    """).fetchall()

    # --------------------------------------
    # Login Timeline
    # --------------------------------------

    timeline = conn.execute("""
        SELECT substr(timestamp,12,2) AS hour,
               COUNT(*) AS total
        FROM logs
        GROUP BY hour
        ORDER BY hour
    """).fetchall()

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

        "event_stats": [dict(event) for event in event_stats],

        "top_ips": [dict(ip) for ip in top_ips],

        "top_users": [dict(user) for user in top_users],

        "timeline": [dict(item) for item in timeline]

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
    cursor = conn.cursor()

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

    # --------------------------------------
    # System Summary
    # --------------------------------------

    total_logs = conn.execute("""
        SELECT COUNT(*) FROM logs
    """).fetchone()[0]

    windows_logs = conn.execute("""
        SELECT COUNT(*) FROM logs
        WHERE source='Windows'
    """).fetchone()[0]

    linux_logs = conn.execute("""
        SELECT COUNT(*) FROM logs
        WHERE source='Linux'
    """).fetchone()[0]

    total_alerts = conn.execute("""
        SELECT COUNT(*) FROM alerts
    """).fetchone()[0]

    high_alerts = conn.execute("""
        SELECT COUNT(*) FROM alerts
        WHERE severity='HIGH'
    """).fetchone()[0]

    medium_alerts = conn.execute("""
        SELECT COUNT(*) FROM alerts
        WHERE severity='MEDIUM'
    """).fetchone()[0]

    low_alerts = conn.execute("""
        SELECT COUNT(*) FROM alerts
        WHERE severity='LOW'
    """).fetchone()[0]

    # --------------------------------------
    # Latest Alert
    # --------------------------------------

    latest_alert = conn.execute("""
        SELECT *
        FROM alerts
        ORDER BY id DESC
        LIMIT 1
    """).fetchone()

    # --------------------------------------
    # Top 5 Attacker IPs
    # --------------------------------------

    top_ips = conn.execute("""
        SELECT ip,
               COUNT(*) AS attempts
        FROM logs
        WHERE event='LOGIN_FAILED'
        GROUP BY ip
        ORDER BY attempts DESC
        LIMIT 5
    """).fetchall()

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
            "<b>Generated by MiniSIEM Version 1.0</b>",
            styles["Heading3"]
        )
    )

    doc.build(story)

    return send_file(
        file_path,
        as_attachment=True,
        download_name="MiniSIEM_Security_Report.pdf",
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