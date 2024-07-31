import json
import random
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

facebook_email = os.getenv('FACEBOOK_EMAIL')
facebook_password = os.getenv('FACEBOOK_PASSWORD')
browser_choice = os.getenv('BROWSER')
profile_path = os.getenv('PROFILE_PATH')
wait_time = int(os.getenv('WAIT_TIME'))

# Charger les données depuis le fichier JSON
with open('config.json', 'r') as f:
    config = json.load(f)

groups = config['groups']
posts = config['posts']

# Initialisation du WebDriver
if browser_choice.lower() == 'chrome':
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-data-dir={profile_path}')
    service = ChromeService('chemin/vers/chromedriver')  # Remplacez par le chemin vers votre ChromeDriver
    driver = webdriver.Chrome(service=service, options=options)
elif browser_choice.lower() == 'firefox':
    options = webdriver.FirefoxOptions()
    options.set_preference('profile', profile_path)
    service = FirefoxService('chemin/vers/geckodriver')  # Remplacez par le chemin vers votre GeckoDriver
    driver = webdriver.Firefox(service=service, options=options)
else:
    raise ValueError("Navigateur non supporté. Choisissez 'chrome' ou 'firefox'.")

def login_to_facebook(email, password):
    driver.get('https://www.facebook.com')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'email'))).send_keys(email)
    driver.find_element(By.NAME, 'pass').send_keys(password)
    driver.find_element(By.NAME, 'pass').send_keys(Keys.RETURN)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[aria-label="Accueil"]')))

def post_to_group(group_url, message, image_path):
    try:
        driver.get(group_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="feed"]')))

        post_box = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[role="button"][aria-label="Créer une publication"], div[role="button"][aria-label="Create a post"]')))
        post_box.click()

        message_box = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[role="textbox"]')))
        message_box.send_keys(message)

        photo_button = driver.find_element(By.XPATH, '//div[@aria-label="Photo/vidéo" or @aria-label="Photo/video"]')
        photo_button.click()
        upload_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@type="file"]')))
        upload_input.send_keys(image_path)

        time.sleep(wait_time)  # Attendre que l'image soit téléchargée

        post_button = driver.find_element(By.XPATH, '//div[@aria-label="Publier" or @aria-label="Post"]')
        post_button.click()

        time.sleep(wait_time)  # Attendre que la publication soit effectuée

        print(f"Image publiée avec succès sur le groupe : {group_url}")
    except Exception as e:
        print(f"Erreur lors de la publication sur le groupe : {group_url}\n{e}")

def search_and_update_groups(keyword):
    search_url = f"https://www.facebook.com/search/groups/?q={keyword}"
    driver.get(search_url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="feed"]')))

    group_elements = driver.find_elements(By.CSS_SELECTOR, 'a[role="link"]')
    new_groups = []
    for elem in group_elements:
        group_url = elem.get_attribute('href')
        if group_url and "groups" in group_url:
            new_groups.append(group_url)

    if new_groups:
        config['groups'] = new_groups
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
        print(f"Liste des groupes mise à jour avec {len(new_groups)} groupes trouvés avec le mot clé '{keyword}'.")

try:
    # Connexion à Facebook une seule fois si nécessaire
    if not os.path.exists(profile_path):
        login_to_facebook(facebook_email, facebook_password)

    for group_url in groups:
        post = random.choice(posts)  # Choisir aléatoirement un message et une image
        post_to_group(group_url, post['message'], post['image_path'])
        time.sleep(wait_time)  # Attendre entre les publications pour éviter d'être bloqué par Facebook

finally:
    driver.quit()
