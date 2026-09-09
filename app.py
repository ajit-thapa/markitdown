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
  <title>MarkItDown Pro | AI Document Processing</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body { background-color: #030712; color: #f9fafb; font-family: Inter, system-ui, sans-serif; }
    .glass { background: rgba(17, 24, 39, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.1); }
    .gradient-text { background: linear-gradient(90deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
  </style>
</head>
<body class="min-h-screen p-4 md:p-8 flex flex-col items-center">
  <div class="max-w-5xl w-full">
    <header class="flex items-center justify-between pb-8 border-b border-gray-800 mb-8">
      <div>
        <h1 class="text-3xl font-extrabold tracking-tight gradient-text">MarkItDown Pro</h1>
        <p class="text-gray-400 mt-2">Production-grade document extraction & AI enhancement</p>
      </div>
      <div class="flex items-center gap-4">
        <div class="relative group">
            <button class="text-sm text-gray-400 hover:text-white flex items-center gap-2">
                ⚙️ Settings
            </button>
            <div class="absolute right-0 top-full mt-2 w-64 glass rounded-xl p-4 hidden group-hover:block z-50">
                <label class="block text-xs text-gray-400 mb-2">Ollama Endpoint</label>
                <input id="ollama-url" type="text" value="http://localhost:11434" class="w-full bg-gray-900 border border-gray-700 rounded px-2 py-1 text-xs mb-4">
                <label class="block text-xs text-gray-400 mb-2">Model</label>
                <input id="ollama-model" type="text" value="llama3.1" class="w-full bg-gray-900 border border-gray-700 rounded px-2 py-1 text-xs">
            </div>
        </div>
        <span class="flex items-center gap-2 px-3 py-1 bg-green-500/10 text-green-400 text-xs font-semibold rounded-full border border-green-500/20">
          <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span> SYSTEM ONLINE
        </span>
      </div>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="md:col-span-1 space-y-4">
        <div id="drop-zone" class="glass rounded-2xl p-8 text-center hover:border-blue-500/50 transition-all cursor-pointer group">
          <div class="flex flex-col items-center gap-4">
            <div class="p-4 rounded-full bg-gray-800/50 group-hover:bg-blue-500/10 transition-colors">
              <svg class="w-8 h-8 text-gray-400 group-hover:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/></svg>
            </div>
            <p class="text-sm font-medium">Drop document or <span class="text-blue-400 underline">browse</span></p>
          </div>
          <input type="file" id="file-input" class="hidden" />
        </div>
        <div id="status" class="text-xs text-center font-mono"></div>
      </div>

      <div class="md:col-span-2 glass rounded-2xl p-6 shadow-2xl">
        <div class="flex items-center justify-between mb-4">
          <div class="flex gap-2 p-1 bg-gray-900 rounded-lg">
            <button id="view-raw" class="px-3 py-1 text-xs rounded bg-gray-700 text-white shadow-sm">Original</button>
            <button id="view-refined" class="px-3 py-1 text-xs rounded text-gray-400 hover:text-white">Refined</button>
          </div>
          <div class="flex gap-2">
            <button id="copy-btn" class="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-xs rounded border border-gray-700 transition">Copy</button>
            <button id="improve-btn" class="px-3 py-1.5 bg-purple-600 hover:bg-purple-500 text-xs text-white rounded shadow-lg shadow-purple-500/20 transition hidden">AI Enhance</button>
            <button id="download-btn" class="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-xs text-white rounded shadow-lg shadow-blue-500/20 transition hidden">Download</button>
          </div>
        </div>
        <div id="editor-container" class="relative">
          <textarea id="output" readonly class="w-full h-[400px] p-4 font-mono text-sm bg-[#030712] border border-gray-800 rounded-lg text-gray-300 focus:outline-none"></textarea>
          <div id="diff-container" class="hidden w-full h-[400px] p-4 font-mono text-sm bg-[#030712] border border-gray-800 rounded-lg text-gray-300 overflow-auto"></div>
        </div>
      </div>
    </div>
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
    const diffContainer = document.getElementById('diff-container');
    const viewRawBtn = document.getElementById('view-raw');
    const viewRefinedBtn = document.getElementById('view-refined');
    let lastImproved = null;

    viewRawBtn.addEventListener('click', () => {
      output.classList.remove('hidden');
      diffContainer.classList.add('hidden');
      viewRawBtn.className = "px-3 py-1 text-xs rounded bg-gray-700 text-white shadow-sm";
      viewRefinedBtn.className = "px-3 py-1 text-xs rounded text-gray-400 hover:text-white";
    });

    viewRefinedBtn.addEventListener('click', () => {
      if (!lastImproved) return;
      output.classList.add('hidden');
      diffContainer.classList.remove('hidden');
      viewRefinedBtn.className = "px-3 py-1 text-xs rounded bg-gray-700 text-white shadow-sm";
      viewRawBtn.className = "px-3 py-1 text-xs rounded text-gray-400 hover:text-white";
    });

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
            const ollamaUrl = document.getElementById('ollama-url').value;
            const ollamaModel = document.getElementById('ollama-model').value;
            try {
            const aiRes = await fetch('/api/improve', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ 
                  markdown: originalText,
                  endpoint: ollamaUrl,
                  model: ollamaModel 
              })
            });
              const aiData = await aiRes.json();
              if (aiRes.ok) {
                lastImproved = aiData.improved;
                diffContainer.textContent = lastImproved;
                viewRefinedBtn.click();
                status.textContent = '✓ AI Enhanced';
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
    endpoint = data.get("endpoint", "http://localhost:11434")
    model = data.get("model", "llama3.1")
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            prompt = f"The following is a markdown document extracted from a file. Please improve its formatting, fix any OCR errors, and ensure it follows professional markdown standards. Return ONLY the improved markdown.\n\n{markdown}"
            response = await client.post(
                f"{endpoint}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=60.0
            )
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Ollama error: " + response.text)
            
            result = response.json()
            improved = result.get("response", "").strip()
            if not improved:
                improved = markdown  # Fallback
            return {"improved": improved}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8089)
