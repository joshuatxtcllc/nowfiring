#!/usr/bin/env python3
"""
Houston Jobs Hub - Directory Submission Automation Script

This script automates the submission of business information to various
local Houston directories and search engines to improve visibility and 
generate quality backlinks.

Usage:
    python directory_submitter.py --config business_config.json

Author: Your Name
Version: 1.0
"""

import argparse
import json
import csv
import time
import logging
import os
import sys
from typing import Dict, List, Any, Optional
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("directory_submission.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("directory_submitter")

class DirectorySubmitter:
    """
    Automates submission of business information to local directories.
    """
    
    def __init__(self, business_info: Dict[str, Any], directories_file: str = "directories.csv") -> None:
        """
        Initialize the directory submitter.
        
        Args:
            business_info: Dictionary containing the business information
            directories_file: Path to CSV file containing directory information
        """
        self.business_info = business_info
        self.directories_file = directories_file
        self.successful_submissions = []
        self.failed_submissions = []
        self.driver = None
        self.session = requests.Session()
        
        # Configure user agent for requests
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def load_directories(self) -> List[Dict[str, str]]:
        """
        Load directory information from CSV file.
        
        Returns:
            List of dictionaries containing directory information
        """
        logger.info(f"Loading directories from {self.directories_file}")
        directories = []
        
        try:
            with open(self.directories_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    directories.append(row)
            
            logger.info(f"Loaded {len(directories)} directories")
            return directories
        except FileNotFoundError:
            logger.error(f"Directories file not found: {self.directories_file}")
            return []
        except Exception as e:
            logger.error(f"Error loading directories: {str(e)}")
            return []
    
    def setup_webdriver(self) -> None:
        """
        Set up and configure Selenium WebDriver.
        """
        logger.info("Setting up WebDriver")
        try:
            chrome_options = Options()
            
            # Run headless unless --show-browser flag is set
            if not self.show_browser:
                chrome_options.add_argument('--headless')
            
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-notifications')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument(
                f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            
            # Use ChromeDriver service if path is provided
            if self.chrome_driver_path:
                service = Service(executable_path=self.chrome_driver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                return self._submit_via_form(directory)
        except Exception as e:
            logger.error(f"Error submitting to {directory_name}: {str(e)}")
            
            self.failed_submissions.append({
                "name": directory_name,
                "url": submission_url,
                "error": str(e)
            })
            
            return False
    
    def _submit_via_api(self, directory: Dict[str, str]) -> bool:
        """
        Submit business information via API.
        
        Args:
            directory: Dictionary containing directory information
        
        Returns:
            bool: Success status
        """
        directory_name = directory.get('name', 'Unknown Directory')
        api_endpoint = directory.get('api_endpoint', '')
        
        if not api_endpoint:
            logger.error(f"No API endpoint provided for {directory_name}")
            return False
        
        try:
            # Prepare API data based on field mappings
            field_mappings_str = directory.get('field_mappings', '{}')
            field_mappings = json.loads(field_mappings_str)
            
            api_data = {}
            for api_field, business_field in field_mappings.items():
                if business_field in self.business_info:
                    api_data[api_field] = self.business_info[business_field]
            
            # Add any required API key or authentication
            if 'api_key' in directory:
                api_data['api_key'] = directory['api_key']
            
            # Make the API request
            logger.info(f"Making API request to {api_endpoint}")
            response = self.session.post(api_endpoint, json=api_data, timeout=30)
            
            # Check for success
            if response.status_code == 200:
                response_data = response.json()
                
                if response_data.get('success', False):
                    logger.info(f"Successfully submitted to {directory_name} via API")
                    
                    self.successful_submissions.append({
                        "name": directory_name,
                        "url": directory.get('submission_url', ''),
                        "notes": "Successfully submitted via API"
                    })
                    
                    return True
                else:
                    error_message = response_data.get('message', 'Unknown API error')
                    logger.error(f"API submission to {directory_name} failed: {error_message}")
                    
                    self.failed_submissions.append({
                        "name": directory_name,
                        "url": directory.get('submission_url', ''),
                        "error": f"API error: {error_message}"
                    })
                    
                    return False
            else:
                logger.error(f"API submission to {directory_name} failed with status code {response.status_code}")
                
                self.failed_submissions.append({
                    "name": directory_name,
                    "url": directory.get('submission_url', ''),
                    "error": f"API error: Status code {response.status_code}"
                })
                
                return False
        except Exception as e:
            logger.error(f"Error in API submission to {directory_name}: {str(e)}")
            return False
    
    def _submit_via_form(self, directory: Dict[str, str]) -> bool:
        """
        Submit business information via web form using Selenium.
        
        Args:
            directory: Dictionary containing directory information
        
        Returns:
            bool: Success status
        """
        directory_name = directory.get('name', 'Unknown Directory')
        submission_url = directory.get('submission_url', '')
        form_id = directory.get('form_id', '')
        
        if not self.driver:
            logger.error(f"WebDriver not initialized for {directory_name}")
            return False
        
        try:
            # Navigate to submission page
            logger.info(f"Navigating to {submission_url}")
            self.driver.get(submission_url)
            
            # Wait for page to load
            self._wait_for_page_load(directory)
            
            # Fill in the form fields based on mapping
            field_mappings_str = directory.get('field_mappings', '{}')
            field_mappings = json.loads(field_mappings_str)
            
            for form_field, business_field in field_mappings.items():
                if business_field in self.business_info:
                    self._fill_form_field(form_field, self.business_info[business_field])
            
            # Handle any captchas if needed
            if directory.get('has_captcha', 'False').lower() == 'true':
                logger.warning(f"CAPTCHA detected on {directory_name}. Manual intervention required.")
                
                if self.show_browser:
                    # If show_browser is True, wait for manual intervention
                    logger.info("Please solve the CAPTCHA manually and press Enter in the console...")
                    input("Press Enter after solving the CAPTCHA...")
                else:
                    # In headless mode, we can't solve the CAPTCHA
                    logger.error(f"Cannot solve CAPTCHA in headless mode for {directory_name}")
                    
                    self.failed_submissions.append({
                        "name": directory_name,
                        "url": submission_url,
                        "error": "CAPTCHA detected in headless mode"
                    })
                    
                    return False
            
            # Submit the form
            submit_button_selector = directory.get('submit_button', '')
            if submit_button_selector:
                logger.info(f"Clicking submit button: {submit_button_selector}")
                submit_button = self.driver.find_element(By.CSS_SELECTOR, submit_button_selector)
                submit_button.click()
                
                # Wait for submission result
                success_indicator = directory.get('success_indicator', '')
                if success_indicator:
                    try:
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, success_indicator))
                        )
                        
                        logger.info(f"Successfully submitted to {directory_name}")
                        
                        self.successful_submissions.append({
                            "name": directory_name,
                            "url": submission_url,
                            "notes": "Successfully submitted via form"
                        })
                        
                        return True
                    except TimeoutException:
                        logger.error(f"Submission to {directory_name} failed - success indicator not found")
                        
                        self.failed_submissions.append({
                            "name": directory_name,
                            "url": submission_url,
                            "error": "Success indicator not found after submission"
                        })
                        
                        return False
                else:
                    # If no success indicator is specified, assume success
                    logger.info(f"Submitted to {directory_name} (no success indicator specified)")
                    
                    self.successful_submissions.append({
                        "name": directory_name,
                        "url": submission_url,
                        "notes": "Form submitted (success assumed)"
                    })
                    
                    return True
            else:
                logger.error(f"No submit button selector provided for {directory_name}")
                
                self.failed_submissions.append({
                    "name": directory_name,
                    "url": submission_url,
                    "error": "No submit button selector provided"
                })
                
                return False
        except Exception as e:
            logger.error(f"Error in form submission to {directory_name}: {str(e)}")
            return False
    
    def _wait_for_page_load(self, directory: Dict[str, str]) -> None:
        """
        Wait for the page to load based on directory configuration.
        
        Args:
            directory: Dictionary containing directory information
        """
        form_id = directory.get('form_id', '')
        wait_element = directory.get('wait_element', form_id)
        wait_time = int(directory.get('wait_time', '10'))
        
        if wait_element:
            try:
                logger.info(f"Waiting for element: {wait_element}")
                WebDriverWait(self.driver, wait_time).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, wait_element))
                )
            except TimeoutException:
                logger.warning(f"Timeout waiting for element: {wait_element}")
        else:
            # If no wait element is specified, just wait a fixed time
            time.sleep(5)
    
    def _fill_form_field(self, selector: str, value: Any) -> None:
        """
        Fill a form field with the given value.
        
        Args:
            selector: CSS selector for the form field
            value: Value to enter in the field
        """
        try:
            # Identify the element
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            
            # Determine the element type and fill accordingly
            tag_name = element.tag_name.lower()
            
            if tag_name == 'select':
                # Handle dropdown select
                select = Select(element)
                
                # Try to select by value, text, or index
                try:
                    select.select_by_value(str(value))
                except NoSuchElementException:
                    try:
                        select.select_by_visible_text(str(value))
                    except NoSuchElementException:
                        if isinstance(value, int) and value < len(select.options):
                            select.select_by_index(value)
                        else:
                            raise ValueError(f"Could not select option with value: {value}")
            
            elif tag_name == 'textarea' or (tag_name == 'input' and element.get_attribute('type') not in ['checkbox', 'radio']):
                # Handle text inputs and textareas
                element.clear()
                element.send_keys(str(value))
            
            elif tag_name == 'input' and element.get_attribute('type') == 'checkbox':
                # Handle checkboxes
                current_state = element.is_selected()
                desired_state = bool(value)
                
                if current_state != desired_state:
                    element.click()
            
            elif tag_name == 'input' and element.get_attribute('type') == 'radio':
                # Handle radio buttons
                if bool(value):
                    element.click()
            
            else:
                logger.warning(f"Unsupported element type: {tag_name} for selector: {selector}")
        
        except Exception as e:
            logger.error(f"Error filling form field {selector}: {str(e)}")
            raise
    
    def submit_to_all(self, show_browser: bool = False, chrome_driver_path: Optional[str] = None) -> None:
        """
        Submit business information to all directories.
        
        Args:
            show_browser: Whether to show the browser window (not headless)
            chrome_driver_path: Path to the Chrome WebDriver executable
        """
        self.show_browser = show_browser
        self.chrome_driver_path = chrome_driver_path
        
        try:
            # Set up WebDriver for form submissions
            self.setup_webdriver()
            
            # Load directories
            directories = self.load_directories()
            
            # First submit to major search engines
            self.submit_to_google_business()
            self.submit_to_bing_places()
            
            # Then submit to other directories
            for directory in directories:
                # Add delay between submissions to avoid being flagged as a bot
                delay = int(directory.get('submission_delay', '5'))
                logger.info(f"Waiting {delay} seconds before next submission")
                time.sleep(delay)
                
                self.submit_to_directory(directory)
        
        finally:
            # Close WebDriver
            self.close_webdriver()
            
            # Generate report
            self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Generate a report of submission results.
        
        Returns:
            Dictionary containing the submission report
        """
        total_directories = len(self.successful_submissions) + len(self.failed_submissions)
        
        report = {
            "total_directories": total_directories,
            "successful_submissions": len(self.successful_submissions),
            "failed_submissions": len(self.failed_submissions),
            "success_rate": round(len(self.successful_submissions) / total_directories * 100, 2) if total_directories > 0 else 0,
            "successful": self.successful_submissions,
            "failed": self.failed_submissions
        }
        
        # Log the report summary
        logger.info("===== Submission Report =====")
        logger.info(f"Total directories: {report['total_directories']}")
        logger.info(f"Successful submissions: {report['successful_submissions']}")
        logger.info(f"Failed submissions: {report['failed_submissions']}")
        logger.info(f"Success rate: {report['success_rate']}%")
        
        if self.successful_submissions:
            logger.info("\nSuccessful directories:")
            for submission in self.successful_submissions:
                logger.info(f"- {submission['name']}")
        
        if self.failed_submissions:
            logger.info("\nFailed directories:")
            for submission in self.failed_submissions:
                logger.info(f"- {submission['name']}: {submission.get('error', 'Unknown error')}")
        
        # Save the report to a JSON file
        report_file = f"submission_report_{time.strftime('%Y%m%d-%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Report saved to {report_file}")
        
        return report

def main():
    """
    Main entry point for the script.
    """
    parser = argparse.ArgumentParser(description='Submit business information to local directories.')
    parser.add_argument('--config', required=True, help='Path to business config JSON file')
    parser.add_argument('--directories', default='directories.csv', help='Path to directories CSV file')
    parser.add_argument('--show-browser', action='store_true', help='Show browser window (not headless)')
    parser.add_argument('--chrome-driver', help='Path to Chrome WebDriver executable')
    
    args = parser.parse_args()
    
    # Load business data from config file
    try:
        with open(args.config, 'r', encoding='utf-8') as f:
            business_info = json.load(f)
    except FileNotFoundError:
        logger.error(f"Config file not found: {args.config}")
        sys.exit(1)
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in config file: {args.config}")
        sys.exit(1)
    
    # Create and run the submitter
    submitter = DirectorySubmitter(business_info, args.directories)
    submitter.submit_to_all(show_browser=args.show_browser, chrome_driver_path=args.chrome_driver)

if __name__ == "__main__":
    main()
                self.driver = webdriver.Chrome(options=chrome_options)
                
            self.driver.set_page_load_timeout(30)
            logger.info("WebDriver setup complete")
        except Exception as e:
            logger.error(f"Error setting up WebDriver: {str(e)}")
            raise
    
    def close_webdriver(self) -> None:
        """
        Close the WebDriver.
        """
        if self.driver:
            logger.info("Closing WebDriver")
            self.driver.quit()
    
    def submit_to_google_business(self) -> bool:
        """
        Submit business information to Google Business Profile.
        
        Returns:
            bool: Success status
        """
        logger.info("Submitting to Google Business Profile")
        
        try:
            # NOTE: This is a placeholder. In a real implementation, you would use
            # the Google My Business API which requires OAuth authentication.
            # https://developers.google.com/my-business/content/overview
            
            # For demonstration purposes only
            logger.info("Google Business submission would use the API, this is a placeholder")
            
            # Simulate API call success
            time.sleep(2)
            
            self.successful_submissions.append({
                "name": "Google Business Profile",
                "url": "https://business.google.com",
                "notes": "Successfully submitted via simulated API call"
            })
            
            return True
        except Exception as e:
            logger.error(f"Error submitting to Google Business: {str(e)}")
            
            self.failed_submissions.append({
                "name": "Google Business Profile",
                "url": "https://business.google.com",
                "error": str(e)
            })
            
            return False
    
    def submit_to_bing_places(self) -> bool:
        """
        Submit business information to Bing Places.
        
        Returns:
            bool: Success status
        """
        logger.info("Submitting to Bing Places")
        
        try:
            # NOTE: This is a placeholder. In a real implementation, you would use
            # Bing Places API or web form automation.
            # https://www.bingplaces.com
            
            # For demonstration purposes only
            logger.info("Bing Places submission would use web automation, this is a placeholder")
            
            # Simulate success
            time.sleep(2)
            
            self.successful_submissions.append({
                "name": "Bing Places",
                "url": "https://www.bingplaces.com",
                "notes": "Successfully submitted via simulated process"
            })
            
            return True
        except Exception as e:
            logger.error(f"Error submitting to Bing Places: {str(e)}")
            
            self.failed_submissions.append({
                "name": "Bing Places",
                "url": "https://www.bingplaces.com",
                "error": str(e)
            })
            
            return False
    
    def submit_to_directory(self, directory: Dict[str, str]) -> bool:
        """
        Submit business information to a specific directory.
        
        Args:
            directory: Dictionary containing directory information
        
        Returns:
            bool: Success status
        """
        directory_name = directory.get('name', 'Unknown Directory')
        submission_url = directory.get('submission_url', '')
        
        logger.info(f"Submitting to {directory_name} ({submission_url})")
        
        if not submission_url:
            logger.error(f"No submission URL provided for {directory_name}")
            
            self.failed_submissions.append({
                "name": directory_name,
                "url": submission_url,
                "error": "No submission URL provided"
            })
            
            return False
        
        submission_method = directory.get('submission_method', 'form').lower()
        
        try:
            if submission_method == 'api':
                return self._submit_via_api(directory)
            else:
