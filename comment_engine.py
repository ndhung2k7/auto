"""
Comment engine for social media platforms
"""
import time
import random
from typing import Dict, List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from utils import logger, get_random_user_agent, human_like_delay, spin_text


class CommentEngine:
    """Handle commenting on different platforms"""
    
    def __init__(self, account_manager, proxy_manager):
        self.account_manager = account_manager
        self.proxy_manager = proxy_manager
        self.drivers = {}
    
    def create_driver(self, account_username: str, proxy: str = None):
        """Create undetectable Chrome driver"""
        try:
            options = uc.ChromeOptions()
            
            # Anti-detection settings
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument(f'user-agent={get_random_user_agent()}')
            options.add_argument('--disable-infobars')
            options.add_argument('--disable-extensions')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            # Proxy configuration
            if proxy:
                options.add_argument(f'--proxy-server={proxy}')
            
            # Optional: headless mode (uncomment for production)
            # options.add_argument('--headless')
            
            driver = uc.Chrome(options=options)
            self.drivers[account_username] = driver
            logger.info(f"Driver created for account {account_username}")
            return driver
            
        except Exception as e:
            logger.error(f"Error creating driver for {account_username}: {e}")
            return None
    
    def login_facebook(self, driver, username: str, password: str):
        """Login to Facebook"""
        try:
            driver.get('https://www.facebook.com/login')
            time.sleep(3)
            
            # Enter username
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            email_field.send_keys(username)
            human_like_delay(0.5, 1)
            
            # Enter password
            password_field = driver.find_element(By.ID, "pass")
            password_field.send_keys(password)
            human_like_delay(0.5, 1)
            
            # Click login
            login_button = driver.find_element(By.NAME, "login")
            login_button.click()
            
            time.sleep(5)
            
            # Check for checkpoint
            if "checkpoint" in driver.current_url:
                logger.warning(f"Facebook checkpoint detected for {username}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Facebook login error: {e}")
            return False
    
    def comment_facebook(self, driver, post_url: str, comment_text: str):
        """Comment on Facebook post"""
        try:
            driver.get(post_url)
            time.sleep(3)
            
            # Find comment box
            comment_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Viết bình luận...']"))
            )
            comment_box.click()
            human_like_delay(1, 2)
            
            # Enter comment
            comment_box.send_keys(comment_text)
            human_like_delay(1, 2)
            
            # Post comment
            post_button = driver.find_element(By.XPATH, "//div[@aria-label='Bình luận']")
            post_button.click()
            
            time.sleep(2)
            logger.info(f"Commented on Facebook: {comment_text[:50]}")
            return True
            
        except Exception as e:
            logger.error(f"Facebook comment error: {e}")
            return False
    
    def login_tiktok(self, driver, username: str, password: str):
        """Login to TikTok"""
        try:
            driver.get('https://www.tiktok.com/login')
            time.sleep(3)
            
            # Click login with email
            email_login = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Email')]"))
            )
            email_login.click()
            time.sleep(2)
            
            # Enter username
            email_field = driver.find_element(By.NAME, "email")
            email_field.send_keys(username)
            human_like_delay(0.5, 1)
            
            # Enter password
            password_field = driver.find_element(By.NAME, "password")
            password_field.send_keys(password)
            human_like_delay(0.5, 1)
            
            # Click login
            login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Đăng nhập')]")
            login_button.click()
            
            time.sleep(5)
            return True
            
        except Exception as e:
            logger.error(f"TikTok login error: {e}")
            return False
    
    def comment_tiktok(self, driver, video_url: str, comment_text: str):
        """Comment on TikTok video"""
        try:
            driver.get(video_url)
            time.sleep(5)
            
            # Find comment box
            comment_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true']"))
            )
            comment_box.click()
            comment_box.send_keys(comment_text)
            human_like_delay(1, 2)
            
            # Post comment
            post_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Đăng')]")
            post_button.click()
            
            time.sleep(2)
            logger.info(f"Commented on TikTok: {comment_text[:50]}")
            return True
            
        except Exception as e:
            logger.error(f"TikTok comment error: {e}")
            return False
    
    def login_instagram(self, driver, username: str, password: str):
        """Login to Instagram"""
        try:
            driver.get('https://www.instagram.com/accounts/login/')
            time.sleep(3)
            
            # Enter username
            username_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_field.send_keys(username)
            human_like_delay(0.5, 1)
            
            # Enter password
            password_field = driver.find_element(By.NAME, "password")
            password_field.send_keys(password)
            human_like_delay(0.5, 1)
            
            # Click login
            login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            time.sleep(5)
            
            # Handle "Save Info" dialog
            try:
                not_now = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not Now')]"))
                )
                not_now.click()
            except:
                pass
            
            return True
            
        except Exception as e:
            logger.error(f"Instagram login error: {e}")
            return False
    
    def comment_instagram(self, driver, post_url: str, comment_text: str):
        """Comment on Instagram post"""
        try:
            driver.get(post_url)
            time.sleep(5)
            
            # Find comment box
            comment_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='Add a comment...']"))
            )
            comment_box.click()
            comment_box.send_keys(comment_text)
            human_like_delay(1, 2)
            
            # Post comment
            post_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Post')]")
            post_button.click()
            
            time.sleep(2)
            logger.info(f"Commented on Instagram: {comment_text[:50]}")
            return True
            
        except Exception as e:
            logger.error(f"Instagram comment error: {e}")
            return False
    
    def comment(self, account: Dict, post_url: str, comment_text: str) -> bool:
        """Main comment function"""
        try:
            username = account['username']
            platform = account['platform']
            auth_data = account.get('auth_data', {})
            proxy = self.proxy_manager.get_proxy(username)
            
            # Create driver
            driver = self.create_driver(username, proxy)
            if not driver:
                return False
            
            # Login based on platform
            login_success = False
            if platform == 'facebook':
                login_success = self.login_facebook(
                    driver, 
                    auth_data.get('email', ''), 
                    auth_data.get('password', '')
                )
            elif platform == 'tiktok':
                login_success = self.login_tiktok(
                    driver,
                    auth_data.get('email', ''),
                    auth_data.get('password', '')
                )
            elif platform == 'instagram':
                login_success = self.login_instagram(
                    driver,
                    auth_data.get('username', ''),
                    auth_data.get('password', '')
                )
            
            if not login_success:
                logger.error(f"Login failed for {username} on {platform}")
                self.account_manager.update_status(username, 'error', 'Login failed')
                return False
            
            # Comment based on platform
            comment_success = False
            if platform == 'facebook':
                comment_success = self.comment_facebook(driver, post_url, comment_text)
            elif platform == 'tiktok':
                comment_success = self.comment_tiktok(driver, post_url, comment_text)
            elif platform == 'instagram':
                comment_success = self.comment_instagram(driver, post_url, comment_text)
            
            if comment_success:
                self.account_manager.increment_comments(username)
            
            return comment_success
            
        except Exception as e:
            logger.error(f"Comment error for {account['username']}: {e}")
            self.account_manager.update_status(account['username'], 'error', str(e))
            return False
        finally:
            # Close driver
            if username in self.drivers:
                try:
                    self.drivers[username].quit()
                    del self.drivers[username]
                except:
                    pass
    
    def cleanup(self):
        """Clean up all drivers"""
        for username, driver in self.drivers.items():
            try:
                driver.quit()
            except:
                pass
        self.drivers.clear()
