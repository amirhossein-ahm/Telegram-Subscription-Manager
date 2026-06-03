# Telegram V2Ray Subscription Manager

A small Flask application for collecting proxy configuration links from Telegram channels and exposing them as V2Ray-compatible subscription feeds.

The app reads recent channel messages through Telethon, extracts supported proxy links, deduplicates them, optionally rewrites remarks, and serves either plain-text or Base64-encoded subscription output.

## Supported Protocols

- VLESS
- VMess
- Trojan
- Shadowsocks
- ShadowsocksR
- Hysteria / Hysteria2
- TUIC
- HY2

## Features

- Admin dashboard for channels and subscriptions
- Telegram channel message extraction
- Per-channel message limits
- Base64 or plain-text subscription output
- Optional custom node remarks while preserving country flags
- Validation for VMess and Shadowsocks payloads
- Application logs stored in SQLite

## Requirements

- **Python 3.13+**: Ensure you have a compatible Python version installed on your system.
- **Telegram API ID and API Hash**: You will need to obtain these credentials from <https://my.telegram.org>.
- **Git (optional)**: If you don't have the project files yet, you'll need Git to clone the repository.

## Setup

Follow these steps to set up and run the Telegram V2Ray Subscription Manager:

### Installation

1.  **Create and activate a Python virtual environment**:
    ```powershell
    python -m venv env
    # On Windows:
    .\env\Scripts\activate
    # On macOS/Linux:
    source ./env/bin/activate
    ```

2.  **Install project dependencies**:
    install all required libraries using pip:
    ```powershell
    pip install -r requirements.txt
    ```

3.  **Configure environment variables**:
    Duplicate the example environment file and then edit it to provide your specific configuration details.
    ```powershell
    # On Windows:
    copy .env.example .env
    # On macOS/Linux:
    cp .env.example .env
    ```
    Open the newly created `.env` file in a text editor and ensure the following variables are set at a minimum:
    *   `SECRET_KEY`: A unique, strong, and random string essential for Flask session security.
    *   `API_ID`: Your Telegram API ID obtained from [my.telegram.org](https://my.telegram.org).
    *   `API_HASH`: Your Telegram API hash obtained from [my.telegram.org](https://my.telegram.org).
    *   `ADMIN_USERNAME`: The username you will use to log into the web dashboard.
    *   `ADMIN_PASSWORD`: The password you will use to log into the web dashboard.

### Initial Setup and Running the Application

1.  **Create your Telegram session**:
    This is a critical first step. You need to connect the application to your Telegram account using your API credentials. The `login.py` script will guide you through entering your phone number and the verification code you receive on Telegram.
    **This step *must* be successfully completed before starting the main application.**
    ```powershell
    python login.py
    ```
    Upon successful login, a message confirming the Telegram login will be displayed, and a `.session` file (e.g., `telegram_session.session`) will be created in your project directory. This file stores your Telegram session and allows the application to interact with Telegram without re-logging in each time.

2.  **Run the Flask web application**:
    Once your Telegram session is established and you've configured your `.env` file, you can start the main web server application.
    ```powershell
    python app.py
    ```
    The application will typically start on `http://localhost:5000` by default. You will see messages in your console indicating that the Flask server is running.

3.  **Access the web dashboard**:
    Open your web browser and navigate to the address where the application is running (e.g., `http://localhost:5000`).
    You will be prompted to log in. Use the `ADMIN_USERNAME` and `ADMIN_PASSWORD` that you configured in your `.env` file.
    From the dashboard, you can proceed to add Telegram channels and create your V2Ray subscriptions.


## Production Notes

- Keep `DEBUG=false` in production.
- Use a strong random `SECRET_KEY`.
- Set `SESSION_COOKIE_SECURE=true` when serving over HTTPS.
- Do not commit `.env`, Telegram session files, or database files.


## Security Scope

This app is intended as a self-hosted admin tool. It provides a simple username/password gate for the dashboard and unprotected tokenized subscription URLs. Treat subscription tokens as secrets and rotate them by recreating the subscription if they are exposed.
