class CoveragePlanner:
    def __init__(self, entity, min_entities=25):
        self.entity = entity
        self.min_entities = min_entities
        self.seen = set()

    def update(self, rows):
        for r in rows:
            name = r.get("name")
            if name:
                self.seen.add(name)

    def satisfied(self):
        return len(self.seen) >= self.min_entities
