import frappe


def is_feature_enabled(feature_flag: str) -> bool:
	try:
		return bool(frappe.db.get_single_value("LedgerMind Settings", feature_flag))
	except Exception:
		return False


def get_settings():
	return frappe.get_single("LedgerMind Settings")


def is_connected() -> bool:
	status = frappe.db.get_single_value("LedgerMind Settings", "connection_status")
	return status == "Connected"
