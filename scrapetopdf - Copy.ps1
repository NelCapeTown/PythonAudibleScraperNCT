# 1. Install required Python packages
Write-Host "Installing required Python packages..."
pip install -r requirements.txt

# 2. Run the Python script to scrape Audible and create the Markdown file
Write-Host "Running Audible scraper and Markdown generator..."
python scripts\scrape_audible.py
python scripts\create_markdown_output.py


# 3. Generate PDF from Markdown using Pandoc and wkhtmltopdf, applying style.css
Write-Host "Generating PDF with Pandoc and weasyprint..."
$mdFile = "Audible_Data\AudibleLibrary.md"
$pdfFile = "Audible_Data\AudibleLibrary.pdf"
$cssFile = "Audible_Data\style.css"

pandoc $mdFile -o $pdfFile --pdf-engine=weasyprint --css=$cssFile

if (Test-Path $pdfFile) {
    Write-Host "PDF generated successfully at $pdfFile"
} else {
    Write-Host "PDF generation failed."
}

Write-Host "All steps completed. PDF generated at $pdfFile"