import os
import subprocess
import base64
from flask import Flask, request, jsonify, send_file
from pdf2image import convert_from_bytes
from PIL import Image
import io

app = Flask(__name__)

# Directory to store temporary files (will be cleaned up by OS or container restart)
TEMP_DIR = "/tmp/latex_compiler"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.route('/compile-latex', methods=['POST'])
def compile_latex():
    latex_code = request.json.get('latex_code')
    if not latex_code:
        return jsonify({"error": "No LaTeX code provided"}), 400

    unique_id = os.urandom(8).hex() # Generate a unique ID for temporary files
    tex_filepath = os.path.join(TEMP_DIR, f"{unique_id}.tex")
    pdf_filepath = os.path.join(TEMP_DIR, f"{unique_id}.pdf")
    png_filepath = os.path.join(TEMP_DIR, f"{unique_id}.png")

    try:
        # 1. Write LaTeX code to a .tex file
        with open(tex_filepath, "w", encoding="utf-8") as f:
            f.write(latex_code)

        # 2. Compile LaTeX to PDF using pdflatex
        # We need to run pdflatex from within the TEMP_DIR so it finds auxiliary files
        # and doesn't clutter the /app directory.
        compile_command = [
            "pdflatex",
            "-interaction=nonstopmode", # Don't stop for errors
            "-output-directory", TEMP_DIR, # Output files into TEMP_DIR
            tex_filepath
        ]
        # Run twice for cross-references, if any, but not strictly needed for images
        process = subprocess.run(compile_command, capture_output=True, text=True, timeout=30) # 30s timeout
        if process.returncode != 0:
            # pdflatex failed, return error message
            error_message = process.stderr + "\n" + process.stdout
            # Attempt to clean up temp files
            cleanup_files(unique_id)
            return jsonify({"error": "LaTeX compilation failed", "details": error_message}), 400

        # 3. Convert PDF to PNG image
        if not os.path.exists(pdf_filepath):
            cleanup_files(unique_id)
            return jsonify({"error": "PDF not generated. LaTeX compilation failed silently or path issue."}), 500

        # convert_from_bytes expects bytes, so read the PDF file
        with open(pdf_filepath, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()

        # dpi can be adjusted for higher quality output
        images = convert_from_bytes(pdf_bytes, first_page=1, last_page=1, dpi=200) # Only first page for preview
        if not images:
            cleanup_files(unique_id)
            return jsonify({"error": "Failed to convert PDF to image."}), 500

        img_byte_arr = io.BytesIO()
        images[0].save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0) # Rewind to the beginning of the buffer

        # Return the image as a base64 encoded string or as a file
        # For simplicity, returning base64. Frontend can display directly.
        base64_image = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        return jsonify({"image": base64_image})

    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
        cleanup_files(unique_id)
        return jsonify({"error": "LaTeX compilation timed out. Complexity too high or infinite loop."}), 408
    except Exception as e:
        cleanup_files(unique_id)
        return jsonify({"error": f"An unexpected server error occurred: {str(e)}"}), 500
    finally:
        # Clean up temporary files regardless of success/failure
        cleanup_files(unique_id)

def cleanup_files(unique_id):
    """Removes temporary files associated with a unique ID."""
    files_to_remove = [
        os.path.join(TEMP_DIR, f"{unique_id}.tex"),
        os.path.join(TEMP_DIR, f"{unique_id}.pdf"),
        os.path.join(TEMP_DIR, f"{unique_id}.log"),
        os.path.join(TEMP_DIR, f"{unique_id}.aux"),
        # Add other potential auxiliary files if needed
    ]
    for f in files_to_remove:
        if os.path.exists(f):
            try:
                os.remove(f)
            except OSError as e:
                print(f"Error cleaning up file {f}: {e}")

@app.route('/')
def home():
    return "LaTeX Compiler Backend is running!"

if __name__ == '__main__':
    # Flask runs on 0.0.0.0:5000 by default in Docker/Render.com environments
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))
