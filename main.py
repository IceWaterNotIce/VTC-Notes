import time
import re
import uuid
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from datetime import datetime, timedelta
from webdriver_manager.chrome import ChromeDriverManager
import os
import requests

def is_download_finished(download_dir, filename):
    while True:
        for file in os.listdir(download_dir):
            if file.startswith(filename):
                download_path = os.path.join(download_dir, file)
                while True:
                    size_before = os.path.getsize(download_path)
                    time.sleep(1)  # 等待檔案大小變化
                    size_after = os.path.getsize(download_path)

                    if size_before == size_after:  # 如果檔案大小不再變化，則認為下載已完成
                        return True
        time.sleep(1)  # 等待檔案出現
# 設定 Chrome 的下載選項
download_dir = os.path.dirname(os.path.abspath(__file__))
options = webdriver.ChromeOptions()
options.add_experimental_option("prefs", {
  "download.default_directory": download_dir,
  "download.prompt_for_download": False,
  "download.directory_upgrade": True,
  "safebrowsing.enabled": True
})
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Go to moodle login page
driver.get("https://moodle2324.vtc.edu.hk/login/index.php")
Login_btn = driver.find_element(By.XPATH, "//*[@id='page-content']/div/div/div[1]/div[1]/div[1]/a")
Login_btn.click()

# moodle will redirect to vtc cna login page
# here we need to login to vtc cna
Input_email = driver.find_element(By.ID, "userNameInput")
Input_password = driver.find_element(By.ID, "passwordInput")
Login_btn = driver.find_element(By.XPATH, "//*[@id='submitButton']")

time.sleep(3)



cna = input("cna: ")
password = input("password: ")

Input_email.send_keys(cna + "@stu.vtc.edu.hk")
Input_password.send_keys(password)
Login_btn.click()

print("If you have open ..., please confirm the login by pressing enter")
input("Enter to continue: ")


# moodle home page
# here to find student's courses
courses_outside_li = driver.find_element(By.CSS_SELECTOR, ".type_system.depth_2.contains_branch")
courses_ul = courses_outside_li.find_elements(By.TAG_NAME, "ul")[0]
courses_lis = courses_ul.find_elements(By.TAG_NAME, "li")
courses_as = []
for course_li in courses_lis:
    courses_as.append(course_li.find_elements(By.TAG_NAME, "a")[0])

courses = []
# courses[i][0] is course name
# courses[i][1] is course link

for courses_a in courses_as:
    if courses_a.get_attribute("href") is not None:
        courses.append([courses_a.text, courses_a.get_attribute("href")])

with open("output.txt", "w") as file:
    file.write("Courses:\n")
for i in range(len(courses)):

    # here to
    driver.get(courses[i][1])
    section_lis = driver.find_elements(By.CSS_SELECTOR, ".section.course-section.main.clearfix")
    sindex = 0
    for section_li in section_lis:
        section_h = section_li.find_elements(By.CSS_SELECTOR, ".sectionname.course-content-item.d-flex.align-self-stretch.align-items-center.mb-0")[0]
        resource_as = section_li.find_elements(By.TAG_NAME, "a")

        driver.execute_cdp_cmd('Page.setDownloadBehavior', { 'behavior': 'allow', 'downloadPath': os.getcwd() + "\\vtc\\courses\\" + courses[i][0].replace(" ", "_") + "\\" + section_h.text.replace(" ", "_") + "\\"})
        rindex = 0
        for resource_a in resource_as:
            if resource_a.get_attribute("href") is not None and ("resource" in resource_a.get_attribute("href") or "folder" in resource_a.get_attribute("href")):
                sindex += 1
                rindex += 1
                if sindex == 1:
                    with open("output.txt", "a") as file:
                        file.write("    - " + courses[i][0] + " | " + courses[i][1] + "\n")
                if rindex == 1:
                    with open("output.txt", "a") as file:
                        file.write("        - " + section_h.text + "\n")
                with open("output.txt", "a") as file:
                    file.write("            - " + resource_a.text.replace("\nFile", "").replace("\nFolder", "") + " | " + resource_a.get_attribute("href")  + "\n")
                
                if "mod/resource" in resource_a.get_attribute("href"):
                    # download path as vtc/courses_name/section_name/resource_name
                    resource_a.click()
                    time.sleep(1)
                if "mod/folder" in resource_a.get_attribute("href"):
                    # download path as vtc/courses_name/section_name/resource_name
                    url = resource_a.get_attribute("href")
                    # Open a new window 
                    driver.execute_script("window.open('');") 
                    # Switch to the new window and open new URL 
                    driver.switch_to.window(driver.window_handles[1]) 
                    driver.get(url) 
                    btn = driver.find_element(By.CSS_SELECTOR, ".btn.btn-secondary")
                    btn.click()
                    time.sleep(1)
                    # Closing new_url tab 
                    driver.close() 
                    # Switching to old tab 
                    driver.switch_to.window(driver.window_handles[0]) 




