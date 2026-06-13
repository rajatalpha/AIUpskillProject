"""Save articles to markdown files."""

from datetime import datetime
from pathlib import Path
from typing import List

from src.models.article import Article


class MarkdownStorage:
    """Saves articles to markdown files in data/articles/."""

    def __init__(self, base_path: str = "data/articles"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save(self, articles: List[Article], filename: str = None) -> Path:
        """Save articles to a markdown file, returning the path."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
            filename = f"articles_{timestamp}.md"

        filepath = self.base_path / filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("# News Articles\n\n")
            f.write(
                f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            )
            f.write(f"**Total Articles:** {len(articles)}\n\n")
            f.write("---\n\n")
            for article in articles:
                f.write(article.to_markdown())
                f.write("\n---\n\n")

        print(f"💾 Saved {len(articles)} articles to: {filepath}")
        return filepath


if __name__ == "__main__":
    test_article = Article(
        title="Test Article",
        url="https://example.com",
        published_at=datetime.now(),
        source="test",
        summary="This is a test article.",
    )

    storage = MarkdownStorage()
    path = storage.save([test_article], "test.md")

    assert path.exists()
    print(f"✅ Saved to: {path}")
    print(path.read_text()[:200])
