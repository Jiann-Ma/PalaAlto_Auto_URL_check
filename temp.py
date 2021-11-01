"""
Created on Thu Oct 28 11:19:01 2021

@author: ESB20914
"""
# selenium libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service

import pandas as pd
import time
import random

# system libraries
import os
import sys
import urllib

# recaptcha libraries
import pydub
import speech_recognition as sr


def delay():
    time.sleep(random.randint(2,3))

def set_environment():
    s = Service(r'C:\chromedriver.exe' )
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=s, options=chrome_options)
    
    return driver

def type_data_in(driver, URLforVerify):
    
    delay()
    
    # 直接到達目標網頁
    url = 'https://urlfiltering.paloaltonetworks.com/'
    driver.get(url)
    time.sleep(2)
       
    # 輸入URL
    elem_1 = WebDriverWait(driver, 3).until(
        EC.visibility_of_element_located((By.ID, 'id_url')))
    elem_1.send_keys(URLforVerify)
    time.sleep(1)

    # 點擊reCAPCHA
    # auto locate recaptcha frames
    frames = driver.find_elements(By.TAG_NAME, "iframe")
    recaptcha_control_frame = None
    recaptcha_challenge_frame = None
    for index, frame in enumerate(frames):
        if frame.get_attribute("title") == "reCAPTCHA":
            recaptcha_control_frame = frame
        if frame.get_attribute("title") == "reCAPTCHA 驗證測試":
            recaptcha_challenge_frame = frame
    if not (recaptcha_control_frame and recaptcha_challenge_frame):
        print("[ERR] Unable to find recaptcha. Abort solver.")
        exit()
        
    # switch to recaptcha frame
    frames = driver.find_elements(By.TAG_NAME, "iframe")
    driver.switch_to.frame(recaptcha_control_frame)
    
    # click on checkbox to activate recaptcha
    driver.find_element(By.CLASS_NAME, "recaptcha-checkbox-border").click()
    
    # switch to recaptcha audio challenge frame
    driver.switch_to.default_content()
    driver.switch_to.frame(recaptcha_challenge_frame)

    # wait
    print('等待recaptcha-audio-button出現')
    wait = WebDriverWait(driver, 1000)
    wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='recaptcha-audio-button']")))

    # click on audio challenge
    driver.find_element(By.ID, "recaptcha-audio-button").click()
    
    # wait
    print('等待audio-source出現')
    wait = WebDriverWait(driver, 1000)
    wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='audio-source']")))

    # get the mp3 audio file
    src = driver.find_element(By.ID, "audio-source").get_attribute("src")
    print(f"[INFO] Audio src: {src}")
    
    path_to_mp3 = os.path.normpath(os.path.join(os.getcwd(), "sample.mp3"))
    path_to_wav = os.path.normpath(os.path.join(os.getcwd(), "sample.wav"))

    # download the mp3 audio file from the source
    urllib.request.urlretrieve(src, path_to_mp3)

    # load downloaded mp3 audio file as .wav
    try:
        sound = pydub.AudioSegment.from_mp3(path_to_mp3)
        sound.export(path_to_wav, format="wav")
        sample_audio = sr.AudioFile(path_to_wav)
    except Exception:
        sys.exit(
            "[ERR] Please run program as administrator or download ffmpeg manually, "
            "https://blog.gregzaal.com/how-to-install-ffmpeg-on-windows/"
        )

    # translate audio to text with google voice recognition
    r = sr.Recognizer()
    with sample_audio as source:
        audio = r.record(source)
    key = r.recognize_google(audio)
    print(f"[INFO] Recaptcha Passcode: {key}")

    # key in results and submit
    driver.find_element(By.ID, "audio-response").send_keys(key)
    driver.find_element(By.ID, "audio-response").send_keys(Keys.ENTER)
    driver.switch_to.default_content()
    
    # submit
    driver.find_element(By.XPATH, "//*[@id='threat-vault-app']/div[2]/div/form/div[1]/div[2]/button").click()
    
    
    
# 打開目標網頁
driver = set_environment()  
    
# 寫入所需資料
URLforVerify = "http://vfilterscustom-accountentriessign.pitikkecing.live/8ca070cc474c02335277c16ce15a469b/"
type_data_in(driver, URLforVerify)
category = driver.find_element(By.ID, "//*[@id='threat-vault-app']/div[2]/div/form/div[2]/ul/li[2]/b")
time.sleep(2) # 做完1筆就暫停2秒
print(category)
print('全部完成')