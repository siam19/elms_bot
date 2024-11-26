from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def createDriver() -> webdriver.Chrome:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    prefs = {"profile.managed_default_content_settings.images":2}
    chrome_options.headless = True


    chrome_options.add_experimental_option("prefs", prefs)
    myDriver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    return myDriver

def getGoogleHomepage(driver: webdriver.Chrome) -> str:
    driver.get("https://www.google.com")
    return driver.page_source

from selenium.webdriver.common.by import By


import os
from selenium import webdriver
from selenium.webdriver.common.by import By

def authenticate_and_get_course_page(driver: webdriver.Chrome, url: str) -> list:
    
    
    # Get credentials from environment variables
    username = os.environ.get('LMS_USERNAME')
    password = os.environ.get('LMS_PASSWORD')
    login_timeout = os.environ.get('LOGIN_TIMEOUT', 10)
    
    if not username or not password:
        raise ValueError("LMS_USERNAME and LMS_PASSWORD environment variables must be set.")
    
    # Navigate to the login page
    login_url = 'https://lms.uiu.ac.bd/login/index.php'
    driver.get(login_url)
    
    # Enter username and password
    driver.find_element(By.ID, 'username').send_keys(username)
    driver.find_element(By.ID, 'password').send_keys(password)
    
    # Submit the login form
    driver.find_element(By.ID, 'loginbtn').click()
    
    # Wait for the login to complete
    driver.implicitly_wait(login_timeout)

    # Call get_course_page while session is active
    course_data = get_course_page(driver, url)
    print(course_data)
    driver.quit()
    return course_data


def get_course_page(driver: webdriver.Chrome, url: str) -> list:
    driver.get(url)
    course_data = []

    # Find all sections
    sections = driver.find_elements(By.CSS_SELECTOR, 'ul.weeks > li[id^="section-"]')

    for section in sections:
        # Get the section title
        try:
            section_title = section.find_element(By.CSS_SELECTOR, 'h3.sectionname > span > a').text
        except:
            section_title = ''

        modules = []
        module_elements = section.find_elements(By.CSS_SELECTOR, 'ul.section li.activity')

        for module in module_elements:
            # Get TITLE and CONTENT_URL
            try:
                activity_elem = module.find_element(By.CSS_SELECTOR, '.activityinstance > a')
                module_title = activity_elem.text
                module_url = activity_elem.get_attribute('href')
            except:
                module_title = ''
                module_url = ''

            # Get BODY
            try:
                body_elem = module.find_element(By.CSS_SELECTOR, '.contentafterlink')
                body_content = body_elem.get_attribute('innerHTML').strip()
            except:
                body_content = ''

            modules.append({
                'title': module_title,
                'url': module_url,
                'body': body_content
            })

        course_data.append({
            'title': section_title,
            'modules': modules
        })

    return course_data