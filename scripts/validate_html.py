from html.parser import HTMLParser
from pathlib import Path
import sys


REQUIRED_TAGS = ("html", "head", "body")


class DocumentStructureParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tag_counts = {
            tag: {"open": 0, "close": 0}
            for tag in REQUIRED_TAGS
        }

    def handle_starttag(self, tag, attrs):
        if tag in self.tag_counts:
            self.tag_counts[tag]["open"] += 1

    def handle_endtag(self, tag):
        if tag in self.tag_counts:
            self.tag_counts[tag]["close"] += 1


def main():
    html_files = sorted(Path(".").glob("*.html"))
    if not html_files:
        print("No HTML files found.", file=sys.stderr)
        return 1

    errors = []
    for path in html_files:
        parser = DocumentStructureParser()
        try:
            parser.feed(path.read_text(encoding="utf-8"))
            parser.close()
        except (UnicodeError, ValueError) as error:
            errors.append(f"{path}: could not parse file: {error}")
            continue

        for tag, counts in parser.tag_counts.items():
            if counts != {"open": 1, "close": 1}:
                errors.append(
                    f"{path}: expected exactly one opening and closing "
                    f"<{tag}> tag, found {counts['open']} opening and "
                    f"{counts['close']} closing"
                )

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    print(f"Validated document structure in {len(html_files)} HTML files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
