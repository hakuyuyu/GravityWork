import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os

class TestChatInterface(unittest.TestCase):
    """Tests for Chat Interface"""

    @classmethod
    def setUpClass(cls):
        # Start the frontend server if not running
        os.system("cd frontend && npm start &")
        time.sleep(5)  # Wait for server to start

        # Initialize the WebDriver
        cls.driver = webdriver.Chrome()
        cls.driver.get("http://localhost:3000")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def test_chat_interface_loads(self):
        """Test that chat interface loads correctly"""
        header = self.driver.find_element(By.CSS_SELECTOR, ".chat-header h2")
        self.assertEqual(header.text, "Basic Chat Interface")

    def test_send_message(self):
        """Test sending a message"""
        input_field = self.driver.find_element(By.CSS_SELECTOR, ".chat-input input")
        send_button = self.driver.find_element(By.CSS_SELECTOR, ".chat-input button")

        test_message = "Hello, this is a test message"

        input_field.send_keys(test_message)
        send_button.click()

        # Wait for message to appear
        time.sleep(1)

        messages = self.driver.find_elements(By.CSS_SELECTOR, ".chat-message")
        self.assertGreater(len(messages), 0)

        # Check if our message appears
        user_message = self.driver.find_element(By.CSS_SELECTOR, ".chat-message.user .message-content")
        self.assertEqual(user_message.text, test_message)

    def test_bot_response(self):
        """Test that bot responds to messages"""
        input_field = self.driver.find_element(By.CSS_SELECTOR, ".chat-input input")
        send_button = self.driver.find_element(By.CSS_SELECTOR, ".chat-input button")

        test_message = "Test for bot response"

        input_field.send_keys(test_message)
        send_button.click()

        # Wait for bot response
        time.sleep(2)

        bot_messages = self.driver.find_elements(By.CSS_SELECTOR, ".chat-message.bot")
        self.assertGreater(len(bot_messages), 0)

        bot_message = bot_messages[-1].find_element(By.CSS_SELECTOR, ".message-content")
        self.assertIn(test_message, bot_message.text)

if __name__ == "__main__":
    unittest.main()
