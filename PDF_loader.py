import requests
from bs4 import BeautifulSoup
import os
from langchain.document_loaders import PyPDFLoader

URL = "https://www.research.org.cy/en/"

def get_toggle_content_links(url, toggle_id="toggle-id-1"):
    r = requests.get(url)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')

    toggle_div = soup.find(id=toggle_id)
    if not toggle_div:
        print(f"Toggle with id={toggle_id} not found")
        return []

    links = []
    for a in toggle_div.find_all('a', href=True):
        href = a['href']
        if "iris.research.org.cy/file/public/" in href:
            if href.startswith('http'):
                links.append(href)
            else:
                links.append(requests.compat.urljoin(url, href))
    return links

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36",
    "Accept": "application/pdf,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.research.org.cy/en/",
}

class PDFLoader:
    def __init__(self, folder="pdfs"):
        self.folder = folder
        if not os.path.exists(folder):
            os.makedirs(folder)
        
    def download_pdfs(self, links=None):
        """Download PDFs from the given links or fetch new ones from the website."""
        if links is None:
            links = get_toggle_content_links(URL)

        for link in links:
            # Extract filename from URL
            filename = link.split("/")[-1]
            # Add .pdf extension if missing
            if not filename.lower().endswith(".pdf"):
                filename += ".pdf"
            filepath = os.path.join(self.folder, filename)

            if os.path.exists(filepath):
                print(f"{filepath} already exists, skipping")
                continue

            print(f"Downloading {link} -> {filepath}")
            try:
                resp = requests.get(link, headers=HEADERS, timeout=10)
                if resp.status_code == 500:
                    print(f"Error 500 Internal Server Error while downloading {link}, skipping")
                    continue
                if 'application/pdf' not in resp.headers.get('Content-Type', ''):
                    print(f"Downloaded content is not PDF (Content-Type={resp.headers.get('Content-Type')}), skipping")
                    continue
                resp.raise_for_status()
                with open(filepath, 'wb') as f:
                    f.write(resp.content)
            except requests.exceptions.RequestException as e:
                print(f"Error downloading {link}: {e}, skipping")
                continue

    def load_documents(self):
        """Load all PDFs from the folder using LangChain."""
        docs = []
        for file in os.listdir(self.folder):
            if file.endswith(".pdf"):
                filepath = os.path.join(self.folder, file)
                loader = PyPDFLoader(filepath)
                docs.extend(loader.load())
        return docs

    def refresh(self):
        """Download new PDFs and load all documents."""
        self.download_pdfs()
        return self.load_documents()

if __name__ == "__main__":
    loader = PDFLoader()
    documents = loader.refresh()
    print(f"Total documents loaded: {len(documents)}")
