import os

GROBID_BASE_URL = "http://localhost:8070"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(BASE_DIR, "..", "pdf")
TEST_PDF_PATH = os.path.join(
    PDF_DIR,
    "Turnhout et al. - 2013 - Tradeoffs in Design Research Development Oriented.pdf",
)
