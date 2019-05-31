# coding=utf-8


class Cache(object):
    def __init__(self, name="", data=None):
        self.name = name
        if data is None or not isinstance(data, dict):
            self._data = {}
        else:
            self._data = data

    def set_with_map(self, data):
        if data is None or not isinstance(data, dict):
            return
        else:
            map(
                lambda kv: self.set(kv[0], kv[1]),
                data.items()
            )
            return

    def set(self, key, value):
        self._data[key] = value

    def get(self, key, default_value=None):
        return self._data[key] if key in self._data else default_value

    def keys(self):
        return self._data.keys() if self._data is not None else []

    def dump(self):
        return self._data

    def __getitem__(self, index):
        return self._data[index]

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        for item in self._data.items():
            yield item

    def __repr__(self):
        return "Cache({})".format(self.name)
