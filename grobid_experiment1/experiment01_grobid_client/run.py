import logging
import os
import sys

from grobid_client.grobid_client import GrobidClient, ServerUnavailableException
from tenacity import (
    before_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
)

from grobid_experiment1.config import PDF_DIR
from grobid_experiment1.utils.docker import GrobidContainer

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

logger = logging.getLogger(__name__)

CURRENT_FILE_DIR = os.path.dirname(__file__)

container = GrobidContainer()
container.run()


# Create client must add retry logic because the container may not be ready yet, and
# will probably fail the first time.
@retry(
    stop=stop_after_attempt(5),
    wait=wait_fixed(5),
    before=before_log(logger, logging.DEBUG),
    retry=retry_if_exception_type(ServerUnavailableException),
)
def create_client():
    logger.info("Creating Grobid client")
    return GrobidClient(
        config_path=os.path.join(CURRENT_FILE_DIR, "config.json"),
        timeout=30,
    )


client = create_client()
os.makedirs(os.path.join(CURRENT_FILE_DIR, "output"), exist_ok=True)
client.process(
    "processFulltextDocument",
    PDF_DIR,
    output=os.path.join(CURRENT_FILE_DIR, "output"),
    consolidate_citations=True,
    tei_coordinates=True,
    force=True,
    verbose=True,
)
