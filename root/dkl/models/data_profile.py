from dkl.enums import ProfileStatus

class DataProfile:
    def __init__(self, dataset_id, entities_detected, primary_entity, fields, row_count):
        self.dataset_id = dataset_id
        self.entities_detected = entities_detected
        self.primary_entity = primary_entity
        self.fields = fields
        self.row_count = row_count
        self.profile_status = ProfileStatus.COMPLETE

    def to_dict(self):
        return self.__dict__


# ==========================================================
# APPENDED: Backward/forward compatibility constructor
# Allows DataProfiler(stats=...) without breaking canonical API
# ==========================================================

_original_init = DataProfile.__init__

def _compat_init(self, *args, **kwargs):
    if "stats" in kwargs:
        stats = kwargs["stats"]
        return _original_init(
            self,
            dataset_id=kwargs.get("dataset_id"),
            entities_detected=[],
            primary_entity=None,
            fields=stats,
            row_count=stats.get("row_count", 0)
        )
    return _original_init(self, *args, **kwargs)

DataProfile.__init__ = _compat_init


# --- package safety alias ---
try:
    from dkl.enums import ProfileStatus as _ProfileStatus
    ProfileStatus = _ProfileStatus
except Exception:
    pass
