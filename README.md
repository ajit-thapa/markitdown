# MarkItDown Web Service & UI

A fast, lightweight REST API and web interface powered by Microsoft's `markitdown` engine to convert documents, spreadsheets, slides, audio, and images into clean Markdown.

## Features
- **Multi-Format Conversion**: PDF, DOCX, XLSX, PPTX, CSV, HTML, JSON, XML, Audio, Images.
- **REST API**: Simple endpoints for programmatic extraction (`/api/convert` and `/api/convert/raw`).
- **Web UI**: Dark-themed drop-zone for file conversion.

## Quickstart

### Local Setup
```bash
pip install -r requirements.txt
python3 app.py
```

Visit `http://localhost:8089` in your browser.

## API Usage

### Convert File to JSON
```bash
curl -F "file=@document.pdf" http://localhost:8089/api/convert
```

### Convert File to Raw Markdown
```bash
curl -F "file=@sheet.xlsx" http://localhost:8089/api/convert/raw
```
