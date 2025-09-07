from pathlib import Path
from agents import function_tool


@function_tool
def save_markdown(path: str, contents: str, overwrite: bool = False) -> str:
    """
    Save Markdown contents to the given file path, creating parent directories as needed.

    Args:
        path: Relative or absolute file path. If it doesn't end with `.md`, the extension will be added.
        contents: Markdown text to write.
        overwrite: When False (default), raises an error if the file already exists.

    Returns:
        The absolute path to the written Markdown file as a string.
    """
    target = Path(path)
    if target.suffix.lower() != ".md":
        target = target.with_suffix(".md")

    target = target.resolve()
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists() and not overwrite:
        raise FileExistsError(f"File already exists: {target}")

    target.write_text(contents, encoding="utf-8")
    return str(target)
