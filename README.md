# pyWebShotX

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Playwright](https://img.shields.io/badge/powered%20by-Playwright-orange)

**pyWebShotX** is a robust, asynchronous reconnaissance tool designed for bug hunters and penetration testers. It automates the process of capturing screenshots of subdomains and detecting the underlying technology stack, generating a modern, easy-to-read HTML report.

## ✨ Features

*   **⚡ Asynchronous & Fast:** Built with `asyncio` and `Playwright` for high-performance concurrent scanning.
*   **📸 Smart Screenshots:** Automatically follows redirects and captures the final destination URL.
*   **🕵️ Tech Detection:** Identifies technologies (CMS, Web Servers, Frameworks) using `webtech` on the final resolved URL.
*   **🔄 Redirect Tracking:** Captures the initial status code (e.g., 302) and tracks where the user is redirected.
*   **📊 Modern HTML Report:** Generates a beautiful, responsive report with linkable screenshots and detailed metadata.
*   **🚀 Auto-Open:** Option to automatically open the report in your browser upon completion.

## 🛠️ Installation

### Local Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/B0fill3/pyWebShotX.git
    cd pyWebShotX
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Install Playwright browsers:**
    ```bash
    playwright install chromium
    ```

## 💻 Usage

### Basic Scan
Create a text file (e.g., `subdomains.txt`) with a list of URLs or domains to scan.

```bash
python pyWebShotx.py -i subdomains.txt
```

### Full Options
```bash
python pyWebShotx.py --input <file> --output <dir> --concurrency <int> --results
```

| Option | Short | Description | Default |
| :--- | :--- | :--- | :--- |
| `--input` | `-i` | **Required.** Path to the file containing the list of subdomains. | - |
| `--output` | `-o` | Directory where screenshots and the report will be saved. | `output` |
| `--concurrency` | `-c` | Number of simultaneous tabs/browsers to use. | `5` |
| `--results` | `-r` | Automatically open the report in the default browser when finished. | `False` |

### Example
Scan `subs.txt`, save to `my_scan/`, use 10 threads, and open the report immediately:

```bash
python pyWebShotx.py -i subs.txt -o my_scan -c 10 -r
```

## 📝 Report

The tool generates an interactive `report.html` in the output directory.
- Click on the **Screenshot** to visit the scanned site.
- Hover over the image to zoom.
- See HTTP status codes (green for 200, blue for Redirects, red for Errors).
- View detected technologies (badges).

## 👨‍💻 Author

**B0fill3**
- Github: [@B0fill3](https://github.com/B0fill3)

---
*Happy Hunting!*