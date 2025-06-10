# Use a base image that already has some common tools or is small
FROM ubuntu:22.04

# Set environment variables for non-interactive apt-get
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/usr/local/texlive/2023/bin/x86_64-linux:${PATH}" # Adjust year as needed

# Install necessary packages:
#   - python3, python3-pip: for our Flask app
#   - texlive-full: THE BIG ONE - full TeX Live distribution (very large, might take a while)
#       Alternative: texlive-latex-base, texlive-pictures (for TikZ), texlive-fonts-recommended
#                    This makes the image smaller but might miss packages.
#                    Let's try texlive-full first for maximum compatibility.
#   - ghostscript: for converting PDF to image
#   - poppler-utils: provides pdftocairo (used by pdf2image for better image quality)
#   - imagemagick: alternative for PDF to image, but often large
#   - build-essential: for compiling some Python packages if needed
#   - pandoc: sometimes useful for document conversions, but not directly needed here
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    texlive-full \
    ghostscript \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Create a working directory
WORKDIR /app

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port (Render.com will use this)
EXPOSE 5000

# Command to run the application
CMD ["python3", "app.py"]
