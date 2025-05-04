# Step 1: Install required Python packages
#Write-Host "📦 Installing required Python packages..."
#pip install -r requirements.txt

# Step 2: Run the Python scripts
#Write-Host "🐍 Running Audible scraper and Markdown generator..."
#python scripts\scrape_audible.py
#python scripts\create_markdown_output.py

# Step 3: Define file paths
$mdFile = "Audible_Data\AudibleLibrary.md"
$htmlFile = "Audible_Data\AudibleLibrary.html"
$pdfFile = "Audible_Data\AudibleLibrary.pdf"
$cssFile = "Audible_Data\style.css"

# Step 4: Convert Markdown to HTML using Pandoc (keep the HTML too!)
Write-Host "🌐 Generating HTML with Pandoc..."
pandoc $mdFile -c $cssFile -s -o $htmlFile

# Step 5: Generate PDF from HTML using WeasyPrint
Write-Host "📄 Generating PDF with WeasyPrint..."
weasyprint $htmlFile $pdfFile

# Final check
if (Test-Path $pdfFile) {
    Write-Host "✅ PDF generated successfully at $pdfFile"
} else {
    Write-Host "❌ PDF generation failed."
}

Write-Host "🎉 All steps completed! HTML and PDF are ready."
