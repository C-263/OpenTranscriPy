class LazyAudioParts:
    def __init__(self, splitter):
        self.splitter = splitter
        self.cache = {}

    def __len__(self):
        return len(self.splitter._chunks)

    def __getitem__(self, i):

        if isinstance(i, slice):
            return [self[j] for j in range(*i.indices(len(self)))]

        if i < 0 or i >= len(self):
            raise IndexError("Índice fora do range")

        if i not in self.cache:
            p = self.splitter._chunks[i]

            self.cache[i] = self.splitter._cut_segment(
                p["start"],
                p["end"]
            )

        return self.cache[i]

    def release(self, i):
        if i in self.cache:
            del self.cache[i]

    def clear(self):
        self.cache.clear()