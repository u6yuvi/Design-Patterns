from .distance import manhattan_distance


class KeyValueFound:
    """
    Structure to save extracted value information and the keyword corresponding
    to it if any and other relevant info
    """

    def __init__(self, kw_found, val_found, conf):
        """
        :param cid: countour id
        :param lid: line id w.r.t contour
        :param string_match_obj: (StringMatch) match object of text found
        """
        self.keyword = kw_found
        self.value = val_found
        self.conf = conf

    @property
    def key_val_dist(self):
        if hasattr(self, "_key_val_dist"):
            return self._key_val_dist
        if self.keyword is None:
            self._key_val_dist = -1
        elif self.keyword.cid == self.value.cid:
            self._key_val_dist = self.find_distance_within()
        else:
            self._key_val_dist = self.find_distance_association()
        return self._key_val_dist

    def __str__(self):
        return (
            f"Confidence: {self.conf}, Keyword: {self.keyword}, "
            f"Value: {self.value}, Distance: {self.key_val_dist}"
        )

    def find_distance_within(self):
        key_lid = self.keyword.lids[-1]
        key_end = self.keyword.match.end
        val_lid = self.value.lids[0]
        val_start = self.value.match.end

        if key_lid == val_lid:
            text = self.keyword.contour["line"][key_lid]["text"][
                key_end:val_start
            ]
            return len(text.split())
        else:
            words = self.keyword.contour["line"][key_lid]["text"][
                key_end:
            ].split()
            for lid in range(key_lid + 1, val_lid):
                words += self.keyword.contour["line"][lid]["text"].split()
            words += self.keyword.contour["line"][val_lid]["text"][
                :val_start
            ].split()
            return len(words)

    def find_distance_association(self):
        key_bbox = self.keyword.contour["line"][self.keyword.lids[-1]]["bbox"]
        val_bbox = self.value.contour["line"][self.value.lids[0]]["bbox"]
        key_top_end = (
            key_bbox["bottom_right"]["x"],
            key_bbox["top_left"]["y"],
        )
        val_top_start = (val_bbox["top_left"]["x"], val_bbox["top_left"]["y"])
        return manhattan_distance(key_top_end, val_top_start)
