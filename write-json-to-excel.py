
import os
import json
from openpyxl import Workbook
from openpyxl.styles import Alignment
from openpyxl.drawing.image import Image as OpenpyxlImage
from urllib.parse import urlparse

with open("audible_books.json", "r", encoding="utf-8") as f:
    books = json.load(f)

wb = Workbook()
ws = wb.active
ws.title = "Audible Library"

headers = ["Title", "Author", "Narrator", "Description", "Cover URL", "Filename", "Cover Image"]
ws.append(headers)

images_folder = "images"

for idx, book in enumerate(books, start=2):
    title = book.get("Title", "")
    author = book.get("Author", "")
    narrator = book.get("Narrator", "")
    description = book.get("Description", "")
    cover_url = book.get("CoverImageURL", "")

    filename = os.path.basename(urlparse(cover_url).path) if cover_url else ""

    ws.append([
        title,
        author,
        narrator,
        description,
        cover_url,
        filename
    ])

    img_path = os.path.join(images_folder, filename)
    if os.path.exists(img_path):
        img = OpenpyxlImage(img_path)
        img.width = 75
        img.height = 75
        img_anchor = f"G{idx}"
        ws.add_image(img, img_anchor)

for row in ws.iter_rows(min_row=2, min_col=4, max_col=4):
    for cell in row:
        cell.alignment = Alignment(wrap_text=True)

wb.save("AudibleLibrary.xlsx")
print("✅ Excel file 'AudibleLibrary.xlsx' created.")
