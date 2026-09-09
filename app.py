import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from markitdown import MarkItDown

app = FastAPI(title="MarkItDown Web & API Server", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

md_converter = MarkItDown()

HTML_UI = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MarkItDown Studio</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body { background-color: #0d1117; color: #c9d1d9; font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }
    .editor-box { background-color: #161b22; border: 1px solid #30363d; }
  </style>
</head>
<body class="min-h-screen p-6 flex flex-col items-center">
  <div class="max-w-4xl w-full">
    <div class="flex items-center justify-between pb-6 border-b border-gray-800">
      <div>
        <h1 class="text-2xl font-bold text-white flex items-center gap-2">
          📄 MarkItDown Studio
        </h1>
        <p class="text-sm text-gray-400 mt-1">Convert PDF, DOCX, XLSX, PPTX, Images, Audio, HTML & more to clean Markdown</p>
      </div>
      <span class="px-3 py-1 bg-blue-900/40 text-blue-400 text-xs rounded-full border border-blue-700/50">Local Engine Ready</span>
    </div>

    <div class="mt-6 editor-box rounded-xl p-6 shadow-xl">
      <div id="drop-zone" class="border-2 border-dashed border-gray-700 rounded-lg p-8 text-center hover:border-blue-500 transition-colors cursor-pointer bg-[#0d1117]/50">
        <input type="file" id="file-input" class="hidden" />
        <div class="flex flex-col items-center justify-center space-y-2">
          <svg class="w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
          </svg>
          <p class="text-sm font-medium text-gray-200">Drag & drop files here, or <span class="text-blue-400 underline">browse</span></p>
          <p class="text-xs text-gray-500">Supports PDF, DOCX, PPTX, XLSX, CSV, JSON, XML, HTML, MP3, WAV, Images</p>
        </div>
      </div>

      <div id="status" class="mt-4 hidden text-sm font-medium"></div>

      <div class="mt-6 flex items-center justify-between">
        <span class="text-xs font-semibold uppercase tracking-wider text-gray-400">Converted Markdown Output</span>
        <div class="flex gap-2">
            <button id="copy-btn" class="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-xs text-gray-200 rounded border border-gray-700 transition">Copy</button>
            <button id="improve-btn" class="px-3 py-1.5 bg-purple-600 hover:bg-purple-500 text-xs text-white rounded border border-purple-500 transition hidden">AI Improve</button>
            <button id="download-btn" class="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-xs text-white rounded border border-blue-500 transition hidden">Download .md</button>
        </div>
      </div>

      <div id="editor-container" class="mt-2 w-full">
          <textarea id="output" readonly placeholder="Markdown output will appear here..." class="w-full h-80 p-4 font-mono text-sm bg-[#0d1117] border border-gray-800 rounded-lg text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500"></textarea>
          <div id="diff-container" class="hidden w-full h-80 p-4 font-mono text-sm bg-[#0d1117] border border-gray-800 rounded-lg text-gray-200 overflow-auto"></div>
      </div>
    </div>
  </div>

  <script>
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const output = document.getElementById('output');
    const status = document.getElementById('status');
    const copyBtn = document.getElementById('copy-btn');
    const improveBtn = document.getElementById('improve-btn');
    const downloadBtn = document.getElementById('download-btn');
    const output = document.getElementById('output');
    const diffContainer = document.getElementById('diff-container');
    let lastImproved = null;

    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('border-blue-500'); });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('border-blue-500'));
    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.classList.remove('border-blue-500');
      if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
    });
    fileInput.addEventListener('change', (e) => {
      if (e.target.files.length) handleFile(e.target.files[0]);
    });

    async function handleFile(file) {
      status.classList.remove('hidden');
      status.className = 'mt-4 text-sm font-medium text-blue-400';
      status.textContent = `Converting "${file.name}"...`;
      output.value = '';
      output.classList.remove('hidden');
      diffContainer.classList.add('hidden');
      diffContainer.textContent = '';
      lastImproved = null;
      downloadBtn.classList.add('hidden');
      improveBtn.classList.add('hidden');

      const formData = new FormData();
      formData.append('file', file);

      try {
        const res = await fetch('/api/convert', {
          method: 'POST',
          body: formData
        });
        const data = await res.json();
        if (res.ok) {
          status.className = 'mt-4 text-sm font-medium text-green-400';
          status.textContent = `✓ Converted "${file.name}" successfully!`;
          output.value = data.markdown;

          // Enable AI Improve and Download
          improveBtn.classList.remove('hidden');
          downloadBtn.classList.remove('hidden');

          downloadBtn.onclick = () => {
              const textToDownload = lastImproved || output.value;
              const blob = new Blob([textToDownload], { type: 'text/markdown' });
              const url = URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = (data.filename || 'converted').split('.')[0] + '.md';
              a.click();
              URL.revokeObjectURL(url);
          };

          improveBtn.onclick = async () => {
            const originalText = output.value;
            improveBtn.disabled = true;
            improveBtn.textContent = 'Improving...';
            try {
              const aiRes = await fetch('/api/improve', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ markdown: originalText })
              });
              const aiData = await aiRes.json();
              if (aiRes.ok) {
                lastImproved = aiData.improved;
                diffContainer.textContent = lastImproved;
                diffContainer.classList.remove('hidden');
                output.classList.add('hidden');
                // optionally show the diff view; for now display refined markdown
                // AI Refined Content is displayed in the diff container
                
                status.textContent = '✓ AI Improved! (Showing refined version)';
              } else {
                alert('AI Improvement failed: ' + aiData.detail);
              }
            } catch (err) {
              alert('Error connecting to AI service: ' + err.message);
            } finally {
              improveBtn.disabled = false;
              improveBtn.textContent = 'AI Improve';
            }
          };
        } else {
          status.className = 'mt-4 text-sm font-medium text-red-400';
          status.textContent = `Error: ${data.detail || 'Conversion failed'}`;
        }
      } catch (err) {
        status.className = 'mt-4 text-sm font-medium text-red-400';
        status.textContent = `Error connecting to server: ${err.message}`;
      }
    }

    copyBtn.addEventListener('click', () => {
      if (!output.value) return;
      navigator.clipboard.writeText(output.value);
      copyBtn.textContent = 'Copied!';
      setTimeout(() => copyBtn.textContent = 'Copy Markdown', 2000);
    });
  </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    return HTML_UI

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "markitdown"}

@app.post("/api/convert")
async def convert_file(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[1] if file.filename else ""
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        result = md_converter.convert(tmp_path)
        markdown_text = result.text_content if hasattr(result, "text_content") else str(result)
        return {
            "filename": file.filename,
            "markdown": markdown_text,
            "title": getattr(result, "title", None)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.post("/api/convert/raw", response_class=PlainTextResponse)
async def convert_file_raw(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[1] if file.filename else ""
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        result = md_converter.convert(tmp_path)
        return result.text_content if hasattr(result, "text_content") else str(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.post("/api/improve")
async def improve_markdown(data: dict):
    markdown = data.get("markdown", "")
    try:
        # Placeholder for AI logic (Ollama or other provider)
        # In a real environment, we'd use 'requests' to call Ollama here.
        improved = f"{markdown}\n\n---\n*AI Refined Content*"
        return {"improved": improved}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8089)
