# Discord Server Analyzer - Selenium Web Scraper

A powerful Discord web scraper that uses Selenium to analyze server structure, channels, and user data. No bot token required - just your login credentials!

## Features

- **Server Analysis**: Get comprehensive information about the server structure and channels
- **User Analysis**: Scrape messages and analyze data from specific users
- **Message Scraping**: Scrape messages from channels with filtering options
- **Channel Statistics**: Get detailed statistics about any text channel
- **Interactive Menu**: Easy-to-use command-line interface
- **Data Export**: Save all scraped data to JSON files

## Requirements

- Python 3.7 or higher
- Google Chrome browser installed
- Discord account credentials

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `selenium` - For browser automation
- `webdriver-manager` - For automatic ChromeDriver management
- `python-dotenv` - For environment variable management
- `beautifulsoup4` - For HTML parsing
- `lxml` - For XML/HTML parsing

### 2. Configure Credentials

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Discord credentials:
   ```
   DISCORD_EMAIL=your_discord_email@example.com
   DISCORD_PASSWORD=your_discord_password
   ```

   **Note**: You can also enter credentials manually when running the script if you prefer not to store them in a file.

### 3. Run the Scraper

```bash
python discord_scraper.py
```

## Usage

### Interactive Menu

When you run the script, you'll see an interactive menu with the following options:

1. **Analyze current server** - Get information about the server you're currently viewing
2. **Navigate to a server** - Switch to a different server by name
3. **Get channel statistics** - Analyze the current channel
4. **Scrape messages from current channel** - Collect messages from the current channel
5. **Scrape messages from specific user** - Filter messages by username
6. **Get user information** - Get detailed data about a specific user
7. **Exit** - Close the scraper

### Features Explained

#### Server Analysis
- Server name
- Channel count and list
- Server structure information

#### Channel Statistics
- Channel name
- Message count
- Unique authors
- Total attachments and reactions

#### Message Scraping
- Scrape messages from any channel
- Filter by username
- Extract message content, timestamps, attachments, and reactions
- Export to JSON format

#### User Information
- All messages from a specific user
- Message statistics (count, attachments, reactions)
- User activity data

## Two-Factor Authentication (2FA)

If your Discord account has 2FA enabled:
1. The script will detect when 2FA is required
2. A browser window will open for you to manually enter your 2FA code
3. The script will wait up to 5 minutes for you to complete 2FA
4. Once authenticated, the scraper will continue automatically

## Data Export

All scraped data can be exported to JSON files. The script will prompt you to save data after each operation. Files are saved with timestamps in the filename, for example:
- `server_info_20240101_120000.json`
- `messages_username_20240101_120000.json`
- `user_info_username_20240101_120000.json`

## Important Notes

⚠️ **Security & Privacy**:
- Never share your `.env` file or commit it to version control
- The `.env` file is already included in `.gitignore`
- Consider using a dedicated Discord account for scraping if possible

⚠️ **Rate Limiting**:
- Discord may rate limit if you scrape too aggressively
- The script includes delays to avoid being flagged
- Be respectful and don't scrape excessively

⚠️ **Discord Terms of Service**:
- Make sure your use case complies with Discord's Terms of Service
- This tool is for personal/educational use
- Don't use it to spam or harass users

⚠️ **Browser Automation Detection**:
- The script includes measures to avoid detection
- However, Discord may still detect automation
- Use responsibly and at your own risk

## Troubleshooting

**ChromeDriver issues:**
- The script automatically downloads the correct ChromeDriver version
- Make sure you have Google Chrome installed
- If issues persist, try updating Chrome to the latest version

**Login fails:**
- Check your credentials are correct
- Make sure 2FA is entered manually if required
- Check your internet connection.
- Discord may require CAPTCHA - complete it manually in the browser

**Elements not found:**
- Discord's web interface changes frequently
- The script may need updates if Discord changes their HTML structure
- Try waiting a bit longer for pages to load

**Messages not scraping:**
- Make sure you're in a text channel
- Some channels may have restrictions
- Try scrolling manually in the browser to load more messages

**Browser closes unexpectedly**
- Check Chrome is up to date
- Try running without headless mode (set `headless=False` in the script)
- Check system resources (memory, CPU)

## Advanced Usage

### Headless Mode

To run the browser in headless mode, modify the script:

```python
scraper = DiscordScraper(headless=True)
```

**Note**: Headless mode may have issues with 2FA and CAPTCHA, so it's recommended to use visible mode.

### Customizing Selectors

If Discord updates their interface and selectors break, you can modify the CSS selectors in the `discord_scraper.py` file. Look for lines with `By.CSS_SELECTOR` and update them with the new class names.

## Limitations

- Message scraping is limited by what's visible in the browser (typically last 50-100 messages)
- Some data may not be accessible through the web interface
- Discord's interface changes may break functionality
- Rate limiting may occur with excessive use


## Disclaimer

This tool is for educational and personal use only. Users are responsible for ensuring their use complies with Discord's Terms of Service and applicable laws. The authors are not responsible for any misuse of this tool.
