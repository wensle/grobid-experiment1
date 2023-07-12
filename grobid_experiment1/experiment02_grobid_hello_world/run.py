import logging
import os
import sys
from pathlib import Path

from grobid.client import Client, GrobidClientError
from grobid.models.article import Article
from grobid.models.form import File, Form
from grobid.tei import Parser
from grobid_client.grobid_client import ServerUnavailableException
from tenacity import (
    before_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
)

from grobid_experiment1.config import GROBID_BASE_URL, TEST_PDF_PATH
from grobid_experiment1.utils.docker import GrobidContainer


logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

logger = logging.getLogger(__name__)

CURRENT_FILE_DIR = os.path.dirname(__file__)

container = GrobidContainer()
container.run()


@retry(
    stop=stop_after_attempt(5),
    wait=wait_fixed(5),
    before=before_log(logger, logging.DEBUG),
    retry=retry_if_exception_type(ServerUnavailableException),
)
def request_tei(c: Client):
    return c.sync_request().content


input_file_path = Path(TEST_PDF_PATH)
with open(input_file_path, "rb") as in_file:
    pdf_content: bytes = in_file.read()
form = Form(
    file=File(
        payload=pdf_content,
        file_name=input_file_path.name,
        mime_type="application/pdf",
    )
)
c = Client(base_url=GROBID_BASE_URL, form=form)
xml_content: bytes = request_tei(c)  # TEI XML file in bytes

# Parse the XML content
parser = Parser(xml_content)
article: Article = parser.parse()

os.makedirs(os.path.join(CURRENT_FILE_DIR, "output"), exist_ok=True)
out_file_name = input_file_path.stem + ".xml"
with open(os.path.join(CURRENT_FILE_DIR, "output", out_file_name), "wb") as out_file:
    out_file.write(xml_content)
