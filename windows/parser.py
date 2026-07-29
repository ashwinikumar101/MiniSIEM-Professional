# ==========================================
# MiniSIEM
# Windows Event XML Parser
# Version 5.0 (Professional Parser)
# ==========================================

import xml.etree.ElementTree as ET

NAMESPACE = {
    "e": "http://schemas.microsoft.com/win/2004/08/events/event"
}


# ------------------------------------------
# Read EventData Field
# ------------------------------------------
def get_event_data(root, field):

    event_data = root.find("e:EventData", NAMESPACE)

    if event_data is None:
        return ""

    for data in event_data.findall("e:Data", NAMESPACE):

        if data.attrib.get("Name") == field:
            return data.text if data.text else ""

    return ""


# ------------------------------------------
# Parse Windows Event
# ------------------------------------------
def parse_event(xml):

    root = ET.fromstring(xml)

    system = root.find("e:System", NAMESPACE)

    # --------------------------------------
    # System Information
    # --------------------------------------

    event_id = int(system.find("e:EventID", NAMESPACE).text)

    provider = system.find(
        "e:Provider",
        NAMESPACE
    ).attrib.get("Name", "")

    computer = system.find(
        "e:Computer",
        NAMESPACE
    ).text

    timestamp = system.find(
        "e:TimeCreated",
        NAMESPACE
    ).attrib.get("SystemTime", "")

    # --------------------------------------
    # NEW: Event Record ID
    # --------------------------------------

    record_node = system.find(
        "e:EventRecordID",
        NAMESPACE
    )

    if record_node is not None:

        record_id = int(record_node.text)

    else:

        record_id = 0

    # --------------------------------------
    # Event Data
    # --------------------------------------

    username = get_event_data(root, "TargetUserName")

    if username == "":
        username = get_event_data(root, "SubjectUserName")

    domain = get_event_data(root, "TargetDomainName")

    if domain == "":
        domain = get_event_data(root, "SubjectDomainName")

    ip = get_event_data(root, "IpAddress")

    port = get_event_data(root, "IpPort")

    workstation = get_event_data(root, "WorkstationName")

    process = get_event_data(root, "ProcessName")

    logon_type = get_event_data(root, "LogonType")

    authentication = get_event_data(
        root,
        "AuthenticationPackageName"
    )

    # --------------------------------------
    # Return Parsed Data
    # --------------------------------------

    return {

        "record_id": record_id,

        "event_id": event_id,

        "provider": provider,

        "computer": computer,

        "timestamp": timestamp,

        "username": username,

        "domain": domain,

        "ip": ip,

        "port": port,

        "workstation": workstation,

        "process": process,

        "logon_type": logon_type,

        "authentication": authentication

    }