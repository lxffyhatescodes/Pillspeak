class Medication:

    def __init__(
        self,
        name: str,
        summary: str = "",
        is_recalled: bool = False,
        recall_reason: str = "",
    ):
        self.name = name
        self.summary = summary
        self.is_recalled = is_recalled
        self.recall_reason = recall_reason

    def to_dict(self):
        return {
            "name": self.name,
            "summary": self.summary,
            "is_recalled": self.is_recalled,
            "recall_reason": self.recall_reason,
        }
