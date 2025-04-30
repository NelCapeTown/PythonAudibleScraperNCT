from dataclasses import dataclass

@dataclass(slots=True, frozen=True) # frozen=True makes instances immutable
class Selectors:
    """Holds CSS selectors for scraping Audible elements."""
    library_row: str
    title: str
    author: str
    narrator: str
    series: str
    description: str
    description_paragraph: str
    image: str
    next_button: str

# Instantiate with the actual selectors
# Review these selectors against the current Audible website structure
ELEMENT_SELECTORS = Selectors(
    library_row="div.adbl-library-content-row",
    title="span.bc-size-headline3", # Check if this is still correct
    author="span.authorLabel a",
    narrator="span.narratorLabel a",
    series="li.seriesLabel span a",
    description="span.merchandisingSummary", # Check if this is still correct
    description_paragraph="p",
    image="img.bc-image-inset-border", # Check if this is still correct
    next_button="span.nextButton a",
)