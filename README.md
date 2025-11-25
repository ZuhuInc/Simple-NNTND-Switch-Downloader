# Zuhu's Simple NNTND Switch Keys & Firmware Downloader

![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Maintained](https://img.shields.io/badge/maintained%3F-yes-brightgreen.svg)

A modern, standalone GUI application designed to simplify the process of finding and downloading the latest Nintendo Switch ProdKeys and Firmware files for emulation. This tool automatically scrapes the latest versions, pairs keys with their firmware, and provides a sleek interface for one-click downloads.

---

## Getting Started

> [!NOTE]
> ### Easiest Method: Download the Executable (.exe)
> This is the recommended way for most users and **does not require a Python installation.**
>
> 1.  Go to the [**Releases Page**](https://github.com/ZuhuInc/Simple-NNTND-Switch-Downloader/releases).
> 2.  Download the latest `.exe` file from the **Assets** section.
> 3.  Run the downloaded file and you are ready to go!
>
> [**➡️ Go to the Releases Page to Download**](https://github.com/ZuhuInc/Simple-NNTND-Switch-Downloader/releases)

---

### For Developers: Running from Source

<details>
<summary>Click here for instructions on running from the Python source code</summary>

#### Prerequisites
*   **Python 3.9+**

#### Installation Steps
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ZuhuInc/Simple-NNTND-Switch-Downloader
    cd Simple-NNTND-Switch-Downloader
    ```

2.  **Install dependencies:**
    ```bash
    pip install requests PyQt6 plyer
    ```

3.  **Run the Script:**
    ```bash
    py Switch-Downloader.py
    ```
    *(Replace `Switch-Downloader.py` with the actual name of what you name the script.)*

</details>

---

### Feature Showcase

Manage your emulation files with a modern, dark-themed UI.

| Feature | Description | Preview |
| :--: | :--- | :--- |
| **Library & Downloads** | **Browse & Download**<br/><br/>Automatically fetches the latest versions. Includes a live search bar, reload functionality, and options to download Keys, Firmware, or **Both** simultaneously. | <img width="800" alt="Library View" src="https://i.imgur.com/XxZBBCz.png" /> |
| **Settings & Customization** | **Configure Your Experience**<br/><br/>Set your default download path, toggle between **Mbps** and **MB/s** speed units, and enable/disable desktop **Notifications**. | <img width="800" alt="Settings View" src="https://i.imgur.com/SC3Ey2X.png" /> |


---

### Libraries Used

*   **External:** [PyQt6](https://pypi.org/project/PyQt6/), [requests](https://pypi.org/project/requests/), [plyer](https://pypi.org/project/plyer/)
*   **Standard:** `os`, `sys`, `json`, `re`, `time`, `ctypes`

---

### ✨ Maintainers

This project is created and maintained by:

*   **[ZuhuInc](https://github.com/ZuhuInc)**

---

### License

This project is licensed under the MIT License - see the `LICENSE` file for details.
