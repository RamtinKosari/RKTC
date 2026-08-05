# - Import Required Libraries
import difflib
import re

# - Category Normalizer Class
class CategoryNormalizer:
    # - Method to Initialize Normalizer
    def __init__(self, similarity_threshold = 0.85, word_overlap_threshold = 0.75):
        # - Similarity Threshold for Fuzzy Matching
        self.similarity_threshold = similarity_threshold
        # - Word Overlap Threshold for Word-Order Independent Matching
        self.word_overlap_threshold = word_overlap_threshold
        # - Normalized Name -> Canonical Name
        self.normalized_map = {}
    # - Method to Normalize Category Name
    def METHOD_NORMALIZE(self, name):
        # - Lowercase and Strip
        normalized = name.lower().strip()
        # - Collapse Whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        # - Remove Punctuation (keep words and spaces)
        normalized = re.sub(r'[^\w\s]', '', normalized)
        return normalized
    # - Method to Compute Word Overlap Between Two Normalized Names
    def METHOD_WORD_OVERLAP(self, a, b):
        words_a = set(a.split())
        words_b = set(b.split())
        if not words_a or not words_b:
            return 0.0
        intersection = words_a & words_b
        smaller = min(len(words_a), len(words_b))
        if smaller == 0:
            return 0.0
        return len(intersection) / smaller
    # - Method to Rebuild Index from Existing Categories
    def METHOD_REBUILD_INDEX(self, categories):
        self.normalized_map = {}
        for category in categories:
            normalized = self.METHOD_NORMALIZE(category['name'])
            self.normalized_map[normalized] = category['name']
    # - Method to Canonicalize Category Name
    def METHOD_CANONICALIZE(self, name):
        normalized = self.METHOD_NORMALIZE(name)
        # - Exact Normalized Match
        if normalized in self.normalized_map:
            return self.normalized_map[normalized]
        if self.normalized_map:
            # - Fuzzy Match on Normalized Names
            normalized_names = list(self.normalized_map.keys())
            normalized_matches = difflib.get_close_matches(
                normalized,
                normalized_names,
                n = 1,
                cutoff = self.similarity_threshold
            )
            if normalized_matches:
                canonical = self.normalized_map[normalized_matches[0]]
                self.normalized_map[normalized] = canonical
                return canonical
            # - Fuzzy Match on Raw Names
            existing_names = list(self.normalized_map.values())
            raw_matches = difflib.get_close_matches(
                name,
                existing_names,
                n = 1,
                cutoff = self.similarity_threshold
            )
            if raw_matches:
                canonical = raw_matches[0]
                self.normalized_map[normalized] = canonical
                return canonical
            # - Word-Order Independent Overlap Match
            best_overlap = 0.0
            best_canonical = None
            for existing_normalized, existing_name in self.normalized_map.items():
                overlap = self.METHOD_WORD_OVERLAP(normalized, existing_normalized)
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_canonical = existing_name
            if best_canonical and best_overlap >= self.word_overlap_threshold:
                self.normalized_map[normalized] = best_canonical
                return best_canonical
        # - New Category
        self.normalized_map[normalized] = name
        return name
    # - Method to Set Threshold
    def METHOD_SET_THRESHOLD(self, threshold):
        self.similarity_threshold = threshold
    # - Method to Set Word Overlap Threshold
    def METHOD_SET_WORD_OVERLAP_THRESHOLD(self, threshold):
        self.word_overlap_threshold = threshold
