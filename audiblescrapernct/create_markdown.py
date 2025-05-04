import os
import json
import logging
from typing import List, Tuple
from urllib.parse import urlparse
from audiblescrapernct.book import Book
from audiblescrapernct.load_config import load_config, Configuration
from typing import Tuple

logger = logging.getLogger(__name__)

# def ensure_directory_exists(path: str) -> None:
def setup_environment(config: Configuration) -> Tuple[str, str, str]:
    """
    Creates necessary directories (if needed) and returns key file paths.
    
    Args: 
        config: Configuration object containing paths and settings.
    """
    # Configuration.from_dict already makes paths absolute
    logger.info("Setting up environment...")
    json_input_path = os.path.normpath(os.path.join(config.data_folder, config.output_json_file))
    logger.info(f"JSON input path (for reading the previously created json file containing all the items in your library): {json_input_path}")
    markdown_output_path = os.path.normpath(os.path.join(config.data_folder, config.output_markdown_file))
    logger.info(f"The markdown file that will be created: {markdown_output_path}")
    images_path = os.path.normpath(config.images_folder)
    logger.info(f"Images save path from, where to read images for creating the markdown file: {images_path}")

    try:
        # data_folder is already created by Configuration logic if relative
        os.makedirs(images_path, exist_ok=True)
        logger.info(f"✅ Data directory: '{config.data_folder}'") #
        logger.info(f"✅ Images directory: '{images_path}'") #
    except OSError as e:
        logger.error(f"❌ Error ensuring directories exist: {repr(e)}. Check permissions.")
        raise # Re-raise the error to stop execution
    return json_input_path, images_path, markdown_output_path

def generate_markdown(books: List[Book], output_path: str, images_folder: str) -> None:
    """
    Generates a Markdown document listing all audiobooks in a table,
    embedding cover images from the local images folder.

    Args:
        books: List of Book objects to include.
        output_path: File path for the generated .md file.
        images_folder: Folder where cover images are stored.
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Table header
    lines = [
        "# Audible Library Catalog",
        "",
        "| Title | Author | Narrator | Description | Cover |",
        "|-------|--------|----------|-------------|-------|"
    ]

    sorted_books = sorted(books, key=lambda b: (b.title.lower(), b.author.lower()))
    for book in sorted_books:
        # Determine local image path
        filename = os.path.basename(urlparse(book.cover_image_url).path)
        img_path = os.path.join(images_folder, filename)
        if os.path.exists(img_path):
            rel_path = os.path.relpath(img_path, os.path.dirname(output_path))
            #img_md = f"<img src=\"{rel_path}\" alt=\"cover\" width=75/>"
            img_md = f"![cover]({rel_path}){{width=75}}"
        else:
            img_md = "(no image)"

        # Escape pipe characters
        def esc(text: str) -> str:
            return text.replace("|", "\\|")

        lines.append(
            f"| {esc(book.title)} | {esc(book.author)} | {esc(book.narrator)} | {esc(book.description)} | {img_md} |"
        )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def export_markdown(config: Configuration = None) -> None:
    """
    Main entrypoint: loads config, reads JSON and writes Markdown.
    """
    effective_config = config or load_config()
    json_input_path, images_folder, md_output = setup_environment(effective_config)
    md_output = os.path.join(effective_config.data_folder, "AudibleLibrary.md")

    with open(json_input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    books = [Book(**item) for item in data]

    generate_markdown(books, md_output, images_folder)
    logger.info(f"✅ Markdown file generated at {md_output}")


if __name__ == "__main__":
    export_markdown()
