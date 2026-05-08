class LedgerMindError(Exception):
	pass


class LedgerMindCloudError(LedgerMindError):
	pass


class LedgerMindConfigError(LedgerMindError):
	pass


class LedgerMindApprovalError(LedgerMindError):
	pass
