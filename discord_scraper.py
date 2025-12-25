from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import os
from dotenv import load_dotenv
from datetime import datetime
import re

# Load environment variables
load_dotenv()

class DiscordScraper:
    def __init__(self, headless=False):
        """Initialize the Discord scraper with Selenium"""
        self.driver = None
        self.headless = headless
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        
        # User agent to avoid detection
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def login(self, email, password):
        """Login to Discord with email and password"""
        print("Navigating to Discord login page...")
        self.driver.get("https://discord.com/login")
        time.sleep(3)
        
        try:
            # Wait for email input
            email_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="email"]'))
            )
            email_input.clear()
            email_input.send_keys(email)
            print("Email entered")
            
            # Wait for password input
            password_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))
            )
            password_input.clear()
            password_input.send_keys(password)
            print("Password entered")
            
            # Click login button
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]'))
            )
            login_button.click()
            print("Login button clicked")
            
            # Wait for login to complete (check for 2FA or main page)
            time.sleep(5)
            
            # Check if 2FA is required
            try:
                mfa_input = self.driver.find_element(By.CSS_SELECTOR, 'input[name="code"]')
                print("2FA detected! Please enter your 2FA code manually in the browser.")
                print("Waiting for manual 2FA entry...")
                # Wait up to 5 minutes for manual 2FA entry
                WebDriverWait(self.driver, 300).until(
                    lambda d: "channels" in d.current_url or "login" not in d.current_url
                )
            except (NoSuchElementException, TimeoutException):
                pass
            
            # Wait for main Discord page to load
            WebDriverWait(self.driver, 30).until(
                lambda d: "channels" in d.current_url or d.find_elements(By.CSS_SELECTOR, '[class*="guild"]')
            )
            
            print("Login successful!")
            time.sleep(3)
            return True
            
        except TimeoutException as e:
            print(f"Login failed: {e}")
            return False
        except Exception as e:
            print(f"An error occurred during login: {e}")
            return False
    
    def navigate_to_server(self, server_name):
        """Navigate to a specific server by name"""
        try:
            # Find server in sidebar
            servers = self.driver.find_elements(By.CSS_SELECTOR, '[class*="guild"], [class*="server"]')
            for server in servers:
                try:
                    server.get_attribute("aria-label")
                    if server_name.lower() in server.get_attribute("aria-label").lower():
                        server.click()
                        time.sleep(2)
                        print(f"Navigated to server: {server_name}")
                        return True
                except:
                    continue
            
            # Alternative: try clicking by tooltip
            server_elements = self.driver.find_elements(By.CSS_SELECTOR, '[class*="guildIcon"], [class*="serverIcon"]')
            for element in server_elements:
                try:
                    tooltip = element.get_attribute("aria-label") or element.get_attribute("title")
                    if tooltip and server_name.lower() in tooltip.lower():
                        element.click()
                        time.sleep(2)
                        print(f"Navigated to server: {server_name}")
                        return True
                except:
                    continue
            
            print(f"Server '{server_name}' not found")
            return False
            
        except Exception as e:
            print(f"Error navigating to server: {e}")
            return False
    
    def get_server_info(self):
        """Get information about the current server"""
        try:
            server_data = {}
            
            # Get server name from header
            try:
                server_name_elem = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[class*="headerText"], [class*="serverName"]'))
                )
                server_data["server_name"] = server_name_elem.text
            except:
                server_data["server_name"] = "Unknown"
            
            # Count channels
            channels = self.driver.find_elements(By.CSS_SELECTOR, '[class*="channel"], [class*="channelName"]')
            server_data["channel_count"] = len(channels)
            
            # Get channel list
            channel_list = []
            for channel in channels[:50]:  # Limit to first 50
                try:
                    channel_name = channel.text
                    if channel_name:
                        channel_list.append(channel_name)
                except:
                    continue
            server_data["channels"] = channel_list
            
            return server_data
            
        except Exception as e:
            print(f"Error getting server info: {e}")
            return {}
    
    def navigate_to_channel(self, channel_name):
        """Navigate to a specific channel"""
        try:
            # Scroll to find channel
            channels = self.driver.find_elements(By.CSS_SELECTOR, '[class*="channel"], [class*="channelName"]')
            for channel in channels:
                try:
                    if channel_name.lower() in channel.text.lower():
                        channel.click()
                        time.sleep(2)
                        print(f"Navigated to channel: {channel_name}")
                        return True
                except:
                    continue
            
            print(f"Channel '{channel_name}' not found")
            return False
            
        except Exception as e:
            print(f"Error navigating to channel: {e}")
            return False
    
    def scrape_messages(self, limit=50, username_filter=None):
        """Scrape messages from the current channel"""
        messages_data = []
        
        try:
            # Scroll up to load more messages
            message_area = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[class*="messages"], [class*="messageList"]'))
            )
            
            # Scroll up to load messages
            for _ in range(min(limit // 10, 5)):  # Scroll a few times
                self.driver.execute_script("arguments[0].scrollTop = 0", message_area)
                time.sleep(1)
            
            time.sleep(2)
            
            # Find all message elements
            message_elements = self.driver.find_elements(By.CSS_SELECTOR, '[class*="message"], [class*="messageContent"]')
            
            for msg_elem in message_elements[:limit]:
                try:
                    # Get username
                    username_elem = msg_elem.find_element(By.CSS_SELECTOR, '[class*="username"], [class*="author"]')
                    username = username_elem.text if username_elem else "Unknown"
                    
                    # Filter by username if specified
                    if username_filter and username_filter.lower() not in username.lower():
                        continue
                    
                    # Get message content
                    content_elem = msg_elem.find_element(By.CSS_SELECTOR, '[class*="content"], [class*="messageContent"]')
                    content = content_elem.text if content_elem else ""
                    
                    # Get timestamp
                    timestamp_elem = msg_elem.find_element(By.CSS_SELECTOR, '[class*="timestamp"], time')
                    timestamp = timestamp_elem.get_attribute("datetime") or timestamp_elem.text if timestamp_elem else ""
                    
                    # Check for attachments
                    attachments = msg_elem.find_elements(By.CSS_SELECTOR, '[class*="attachment"], img, video')
                    attachment_count = len(attachments)
                    
                    # Check for reactions
                    reactions = msg_elem.find_elements(By.CSS_SELECTOR, '[class*="reaction"]')
                    reaction_count = len(reactions)
                    
                    messages_data.append({
                        "username": username,
                        "content": content,
                        "timestamp": timestamp,
                        "attachments": attachment_count,
                        "reactions": reaction_count
                    })
                    
                except Exception as e:
                    continue
            
            print(f"Scraped {len(messages_data)} messages")
            return messages_data
            
        except Exception as e:
            print(f"Error scraping messages: {e}")
            return messages_data
    
    def get_user_info(self, username):
        """Get information about a specific user"""
        user_data = {
            "username": username,
            "messages": []
        }
        
        # Scrape messages from this user
        messages = self.scrape_messages(limit=100, username_filter=username)
        user_data["messages"] = messages
        user_data["message_count"] = len(messages)
        
        # Calculate statistics
        total_attachments = sum(msg.get("attachments", 0) for msg in messages)
        total_reactions = sum(msg.get("reactions", 0) for msg in messages)
        
        user_data["total_attachments"] = total_attachments
        user_data["total_reactions"] = total_reactions
        
        return user_data
    
    def get_channel_stats(self):
        """Get statistics about the current channel"""
        try:
            stats = {}
            
            # Get channel name
            try:
                channel_name_elem = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[class*="channelName"], [class*="headerText"]'))
                )
                stats["channel_name"] = channel_name_elem.text
            except:
                stats["channel_name"] = "Unknown"
            
            # Scrape messages for stats
            messages = self.scrape_messages(limit=100)
            stats["message_count"] = len(messages)
            
            # Get unique authors
            unique_authors = set()
            for msg in messages:
                if msg.get("username"):
                    unique_authors.add(msg["username"])
            stats["unique_authors"] = len(unique_authors)
            
            # Count attachments and reactions
            stats["total_attachments"] = sum(msg.get("attachments", 0) for msg in messages)
            stats["total_reactions"] = sum(msg.get("reactions", 0) for msg in messages)
            
            return stats
            
        except Exception as e:
            print(f"Error getting channel stats: {e}")
            return {}
    
    def save_data(self, data, filename):
        """Save scraped data to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Data saved to {filename}")
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            print("Browser closed")

def main():
    """Main function to run the scraper"""
    # Get credentials from environment or user input
    email = os.getenv("DISCORD_EMAIL")
    password = os.getenv("DISCORD_PASSWORD")
    
    if not email or not password:
        print("Discord credentials not found in .env file")
        email = input("Enter your Discord email: ")
        password = input("Enter your Discord password: ")
    
    # Initialize scraper
    scraper = DiscordScraper(headless=False)  # Set to True for headless mode
    
    try:
        # Login
        if not scraper.login(email, password):
            print("Failed to login. Exiting...")
            return
        
        # Wait a bit for page to fully load
        time.sleep(3)
        
        # Interactive menu
        while True:
            print("\n" + "="*50)
            print("Discord Scraper Menu")
            print("="*50)
            print("1. Analyze current server")
            print("2. Navigate to a server")
            print("3. Get channel statistics")
            print("4. Scrape messages from current channel")
            print("5. Scrape messages from specific user")
            print("6. Get user information")
            print("7. Exit")
            print("="*50)
            
            choice = input("Enter your choice (1-7): ").strip()
            
            if choice == "1":
                server_info = scraper.get_server_info()
                print("\nServer Information:")
                print(json.dumps(server_info, indent=2))
                
                save = input("\nSave to file? (y/n): ").strip().lower()
                if save == 'y':
                    filename = f"server_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    scraper.save_data(server_info, filename)
            
            elif choice == "2":
                server_name = input("Enter server name: ").strip()
                scraper.navigate_to_server(server_name)
            
            elif choice == "3":
                stats = scraper.get_channel_stats()
                print("\nChannel Statistics:")
                print(json.dumps(stats, indent=2))
                
                save = input("\nSave to file? (y/n): ").strip().lower()
                if save == 'y':
                    filename = f"channel_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    scraper.save_data(stats, filename)
            
            elif choice == "4":
                limit = input("Enter message limit (default 50): ").strip()
                limit = int(limit) if limit.isdigit() else 50
                messages = scraper.scrape_messages(limit=limit)
                print(f"\nScraped {len(messages)} messages")
                print(json.dumps(messages[:10], indent=2))  # Show first 10
                
                save = input("\nSave all messages to file? (y/n): ").strip().lower()
                if save == 'y':
                    filename = f"messages_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    scraper.save_data(messages, filename)
            
            elif choice == "5":
                username = input("Enter username to filter: ").strip()
                limit = input("Enter message limit (default 50): ").strip()
                limit = int(limit) if limit.isdigit() else 50
                messages = scraper.scrape_messages(limit=limit, username_filter=username)
                print(f"\nScraped {len(messages)} messages from {username}")
                print(json.dumps(messages[:10], indent=2))  # Show first 10
                
                save = input("\nSave all messages to file? (y/n): ").strip().lower()
                if save == 'y':
                    filename = f"messages_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    scraper.save_data(messages, filename)
            
            elif choice == "6":
                username = input("Enter username: ").strip()
                user_info = scraper.get_user_info(username)
                print("\nUser Information:")
                print(json.dumps(user_info, indent=2))
                
                save = input("\nSave to file? (y/n): ").strip().lower()
                if save == 'y':
                    filename = f"user_info_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    scraper.save_data(user_info, filename)
            
            elif choice == "7":
                print("Exiting...")
                break
            
            else:
                print("Invalid choice. Please try again.")
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()

