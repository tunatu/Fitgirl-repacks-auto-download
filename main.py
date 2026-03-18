import bs4
import requests
import threading
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
from tkinter import filedialog
import re
import os


def get_fuckingfast_url(page_url):
    clean_url = page_url.split("#")[0]
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    r = requests.get(clean_url, headers=headers, timeout=15)
    match = re.search(r'window\.open\("(https://fuckingfast\.co/dl/[^"]+)"', r.text)
    if match:
        print(f"[+] FF dl URL: {match.group(1)}")
        return match.group(1)
    print(f"[-] No FF dl URL found in {clean_url}")
    return None

def get_datanodes_url(page_url):
    return page_url

def resolve_download(page_url):
    if "fuckingfast.co" in page_url:
        return get_fuckingfast_url(page_url)
    elif "datanodes.to" in page_url:
        return get_datanodes_url(page_url)
    else:
        print(f"[!] Unknown host: {page_url}")
        return None


def get_filename(response, fallback="download.bin"):
    cd = response.headers.get("content-disposition", "")
    match = re.search(r'filename="?([^";\n]+)"?', cd)
    if match:
        return match.group(1).strip()
    url_part = response.url.split("/")[-1].split("?")[0]
    return url_part if url_part else fallback

def download_file(download_url, page_url, status_label):
    headers = {
        "Referer": page_url,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    print(f"[*] Downloading: {download_url}")
    r = requests.get(download_url, stream=True, headers=headers, timeout=30)
    print(f"[*] Status: {r.status_code} | Content-Type: {r.headers.get('content-type')}")

    if r.status_code != 200:
        status_label.config(text=f"Download failed: HTTP {r.status_code}")
        return False

    total = int(r.headers.get("content-length", 0))
    downloaded = 0

    fallback = page_url.split("/")[-1].split("#")[-1] or "download.bin"
    filename = get_filename(r, fallback=fallback)
    output_path = os.path.join(download_dir.get(), filename + ".rar")
    print(f"[*] Saving to: {output_path}")

    with open(output_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=65536):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    percent = (downloaded / total) * 100
                    mb = downloaded / (1024 * 1024)
                    total_mb = total / (1024 * 1024)
                    status_label.config(text=f"{filename}: {percent:.1f}% ({mb:.1f}/{total_mb:.1f} MB)")

    status_label.config(text=f"Done: {filename}")
    print(f"[+] Done: {output_path}")
    return True


def browse_dir():
    path = filedialog.askdirectory(initialdir=download_dir.get())
    if path:
        download_dir.set(path)

def download_selected():
    to_download = [url for url, var in selected_links.items() if var.get()]
    if not to_download:
        result_label.config(text="No links selected.")
        return

    if not os.path.isdir(download_dir.get()):
        result_label.config(text="Invalid download directory.")
        return

    def run():
        total = len(to_download)
        failed = []

        for i, page_url in enumerate(to_download):
            fname = page_url.split("/")[-1].split("#")[-1]
            status = f"[{i+1}/{total}] Resolving: {fname}"
            print(status)
            result_label.config(text=status)

            download_url = resolve_download(page_url)
            if not download_url:
                result_label.config(text=f"[{i+1}/{total}] Could not resolve: {fname}")
                failed.append(page_url)
                continue

            success = download_file(download_url, page_url, result_label)
            if not success:
                failed.append(page_url)

        if failed:
            result_label.config(text=f"Done. {len(failed)} failed: {', '.join(f.split('/')[-1] for f in failed)}")
        else:
            result_label.config(text=f"All {total} files downloaded successfully.")

    threading.Thread(target=run, daemon=True).start()

def get_links():
    url = stringvar.get().strip()
    if not url:
        result_label.config(text="Enter a URL first.")
        return
    result_label.config(text="Scraping...")

    def fetch():
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            response = requests.get(url, timeout=10, headers=headers)
            soup = bs4.BeautifulSoup(response.text, "html.parser")
            divs = soup.find_all("div", class_="su-spoiler-content")

            if not divs:
                result_label.config(text="Could not find any download sections.")
                return

            mirror_groups = []
            for div in divs:
                links = [a["href"] for a in div.find_all("a", href=True) if a["href"].startswith("http")]
                if links:
                    host = links[0].split("/")[2]
                    mirror_groups.append((host, links))

            if not mirror_groups:
                result_label.config(text="No links found.")
                return

            mirror_options = [f"Mirror {i+1}: {host} ({len(links)} files)"
                              for i, (host, links) in enumerate(mirror_groups)]
            mirror_var.set(mirror_options[0])
            mirror_menu["values"] = mirror_options
            root._mirror_groups = mirror_groups
            show_mirror(0)

        except Exception as e:
            result_label.config(text=f"Error: {e}")

    threading.Thread(target=fetch, daemon=True).start()

def show_mirror(index):
    groups = getattr(root, "_mirror_groups", [])
    if not groups or index >= len(groups):
        return

    host, links = groups[index]

    for widget in scrollable_frame.winfo_children():
        widget.destroy()
    selected_links.clear()

    result_label.config(text=f"Mirror {index+1}: {host} — {len(links)} files")
    for link in links:
        var = ttk.BooleanVar()
        var.set(True)
        selected_links[link] = var
        cb = ttk.Checkbutton(
            scrollable_frame,
            text=link,
            variable=var,
            bootstyle="primary"
        )
        cb.pack(anchor="w", pady=2)

def on_mirror_change(event=None):
    idx = mirror_menu.current()
    if idx >= 0:
        show_mirror(idx)


root = ttk.Window()
root.title("FitGirl Scraper")
root.geometry("600x600")

selected_links = {}

ttk.Label(root, text="FitGirl Scraper", font=("Helvetica", 16, "bold")).pack(pady=10)

stringvar = ttk.StringVar()
ttk.Entry(root, textvariable=stringvar, width=60).pack(pady=5)
ttk.Label(root, text="Example: https://fitgirl-repacks.site/ready-or-not/", font=("Helvetica", 9)).pack()

ttk.Button(root, text="Scrape Links", command=get_links).pack(pady=8)

# mirror selector
mirror_frame = ttk.Frame(root)
mirror_frame.pack(fill="x", padx=10)
ttk.Label(mirror_frame, text="Mirror:").pack(side="left", padx=(0, 5))
mirror_var = ttk.StringVar()
mirror_menu = ttk.Combobox(mirror_frame, textvariable=mirror_var, state="readonly", width=50)
mirror_menu.pack(side="left")
mirror_menu.bind("<<ComboboxSelected>>", on_mirror_change)

# download location
dir_frame = ttk.Frame(root)
dir_frame.pack(fill="x", padx=10, pady=5)
ttk.Label(dir_frame, text="Save to:").pack(side="left", padx=(0, 5))
download_dir = ttk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads"))
ttk.Entry(dir_frame, textvariable=download_dir, width=42).pack(side="left")
ttk.Button(dir_frame, text="Browse", command=browse_dir, bootstyle="secondary").pack(side="left", padx=5)

result_label = ttk.Label(root, text="")
result_label.pack(pady=5)

scrollable_frame = ScrolledFrame(root, autohide=True)
scrollable_frame.pack(fill="both", expand=True, padx=10, pady=5)

ttk.Button(root, text="Download Selected", command=download_selected, bootstyle="success").pack(pady=10)

root.mainloop()