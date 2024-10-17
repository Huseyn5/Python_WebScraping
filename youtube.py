from random import choice
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
import selenium.common.exceptions as exceptions 
from pathlib import Path
import traceback
from random import choice

service = Service()
option = Options()
option.add_argument("--disable-infobars")
option.add_argument('--disable-notifications')
option.add_argument("--no-sandbox")
# option.add_argument("--headless")
option.add_argument("--disable-extensions")
# option.add_argument(f"user-data-dir=./cachinho")
# option.add_experimental_option('prefs', prefs) # changes the default download path
option.add_argument("--disable-dev-shm-usage")

user_agent_header = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
option.add_argument(f'--user-agent={user_agent_header}')
option.add_argument("user-data-dir=./my_chrome_dir")
path = str(Path.cwd())
prefs = {'download.default_directory' : path}
option.add_experimental_option('prefs', prefs) 
driver = webdriver.Chrome(service=service,options=option)
actions = ActionChains(driver)    




# Writting useful links, with texts in 2 languages to the DB
def write_to_db(channel_id, link, lang1, lang2):
    import sqlite3
    con = sqlite3.connect('Captions.db')
    cur = con.cursor()
    # Creating table if not exist
    table_name = f"{channel_id}_captions"
    cur.execute(f"""CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    link TEXT, 
                    lang1_text TEXT,
                    land2_text TEXT     
                    );
                """)
    # Inserting values to table
    cur.execute(f"INSERT INTO {table_name} (link, lang1_text, lang2_text) VALUES (?,?,?)", (link, lang1, lang2))
    con.commit()


# Finds first elemnents that has text() = search_text and return that element, all using JavaScript
def find_xpaths_for_word(driver:webdriver.Chrome, search_text):
    return driver.execute_script("""return document.evaluate(`//*[text()='${arguments[0]}']`, document, 
                                                        null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;                          
                                """, search_text)


# Reading from file
def read_from_txt(file):
    with open(file) as f:
        links = f.read().splitlines()
    return links


# Getting links for all youtube channel videos and writing them into 'links.txt'
def update_video_links(link, driver:webdriver.Chrome):
    driver.get(link)
    time.sleep(4)
    links = read_from_txt("links.txt")

    # path for videos in youtube channels
    xpath = "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-rich-grid-renderer/div[6]/ytd-rich-item-renderer[{}]/div/ytd-rich-grid-media/div[1]/div[1]/ytd-thumbnail/a"
    video_n = 1
    new_links = []
    # going through each video and copying links
    while True:
        try:
            new_link = driver.find_element(By.XPATH,xpath.format(video_n))
            driver.execute_script("arguments[0].scrollIntoView()", new_link)
            time.sleep(0.5)
            if new_link.get_attribute('href') == links[0]:
                break
            else:
                new_links.append(new_link.get_attribute('href'))
            video_n += 1
        except:
            break


    with open('links.txt', 'w') as f:
        for line in new_links:
            f.write(f"{line}\n")
        for line in links:
            f.write(f"{line}\n")


# Checking if both language subtitles exist
def check_both_subtitles_ex(driver:webdriver.Chrome, language1, language2):
    time.sleep(choice(range(2,4)))
    subtitles = find_xpaths_for_word(driver, 'Subtitles/CC')
    subtitles.click()
    
    time.sleep(choice(range(3,5)))
    lang1 = find_xpaths_for_word(driver, language1)
    time.sleep(choice(range(2,3)))
    lang2 = find_xpaths_for_word(driver, language2)
    
    if lang1 and lang2:
        return 1
    else: 
        return 0


# Calculating video duration in seconds
def video_duration(driver:webdriver.Chrome):
    try:
        duration = driver.find_element(By.CLASS_NAME,'ytp-time-duration').text
        if ':' in duration:
            minutes = duration.split(":")[0]
            seconds = duration.split(":")[1]
            duration = int(minutes) * 60 + int(seconds)
    except:traceback.print_exc()
    print(duration)
        
    return duration


# Getting subtitles in both languages
def get_data(driver:webdriver.Chrome, channel_id, link, duration, language1, language2):
    # Start with subtitles in 1st language
    print('starting...')
    time.sleep(4)
    driver.get(link)
    time.sleep(4)

    try:
        lang1_sub = []
        settings = driver.execute_script("return document.getElementsByClassName('ytp-button ytp-settings-button')[0]")
        settings.click()
        time.sleep(5)
        subtitles = find_xpaths_for_word(driver, 'Subtitles/CC')
        subtitles.click()

        time.sleep(2)
        lang1_button = find_xpaths_for_word(driver, language1)
        lang1_button.click()
        time.sleep(choice(range(3, 5)))
        start_time = 1250
        actions.send_keys('0').perform()

        while True:
            try:
                new_text = driver.find_element(By.CSS_SELECTOR, 'span.ytp-caption-segment').text
                if len(lang1_sub) == 0:
                    print(new_text)
                    lang1_sub.append(new_text)
                    continue
                if new_text != lang1_sub[-1]:
                    print(new_text)
                    lang1_sub.append(new_text)
                # print(start_time)
                time.sleep(1)
                start_time = start_time + 1
            except:
                pass
            if start_time == duration:
                break


        # Start with subtitles in 2nd language
        time.sleep(choice(range(1, 3)))
        driver.get(link)
        time.sleep(choice(range(2, 5)))

        lang2_sub = []
        settings = driver.execute_script("return document.getElementsByClassName('ytp-button ytp-settings-button')[0]")
        settings.click()
        time.sleep(choice(range(3, 5)))
        subtitles = find_xpaths_for_word(driver, 'Subtitles/CC')
        subtitles.click()
        
        time.sleep(choice(range(2, 5)))
        lang2_button = find_xpaths_for_word(driver, language2)
        lang2_button.click()
        time.sleep(choice(range(2, 4)))
        actions.send_keys('0').perform()
        start_time = 1250

        while True:
            try:
                new_text = driver.find_element(By.CSS_SELECTOR, 'span.ytp-caption-segment').text
                if len(lang2_sub) == 0:
                    print(new_text)
                    lang2_sub.append(new_text)
                    continue
                if new_text != lang2_sub[-1]:
                    print(new_text)
                    lang2_sub.append(new_text)
                # print(start_time)
                time.sleep(1)
                
                start_time = start_time + 1
            except:
                pass
            if start_time == duration:
                break


        # Writing subtitles from both languages to the database
        write_to_db(channel_id, link, ' '.join(lang1_sub), ' '.join(lang2_sub))

    except:traceback.print_exc()    





# Program writting to the table all channel_id videos' links and subtitles of languages 1 and language2, 
def main(channel_id, language1, language2):   
    update_video_links(f"https://www.youtube.com/@{channel_id}/videos/", driver)
    print("Updated Video Links")

    links = read_from_txt("links.txt")

    for link in links:
        try:
            driver.get(link)
            print("Getting Link")
            time.sleep(4)
            try:
                settings = driver.execute_script("return document.getElementsByClassName('ytp-button ytp-settings-button')[0]")
                print("Found settings")
                settings.click()
                print("Clicked settings")
                time.sleep(choice(range(3, 5)))
            except:
                time.sleep(3)#
                pass
            result = check_both_subtitles_ex(driver, language1, language2)
            print(f"result is {result}")
            if result == 1:
                with open('useful_links.txt', 'w') as file:
                    file.write(link+'\n')
                print('going good')
                duration = video_duration(driver)
                get_data(driver, channel_id, link, duration, language1, language2)
                time.sleep(choice(range(120, 300)))

            else:
                print("NOT BOTH SUBTITLES!")
                time.sleep(choice(range(90, 240)))
        except KeyboardInterrupt:
            pass
        except:
            print("NO CAPTIONS!")
        print('Done with this link...')
        time.sleep(choice(range(90, 240)))
        
        
        print('Starting new one')
