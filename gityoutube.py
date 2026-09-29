import os
import sys
import time
import random
import pyttsx3
import urllib.parse
import pyautogui
import re
import warnings
import playwright
warnings.filterwarnings("ignore")

from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from PIL import Image

# =================================================================
# 🔑 आशिष भाऊ, तुमची जेमिनी की आणि नंबर फक्त इथे Set करा!
GEMINI_API_KEY = "insert your key here"  # 🎯 इथे तुमची खरी जेमिनी की टाका भाऊ! (backup साठी वापरली जाते)
WHATSAPP_NUMBER = "+9170047,+91972294"  # स्वल्पविराम देऊन दोन्ही नंबर सुरक्षित लॉक

# 🌐 Google/Edge सेशन इथे साठवला जाईल (लॉगिन कायम लक्षात राहील)
EDGE_PROFILE_DIR = os.path.join(os.path.expanduser("~"), "mega_agent_edge_profile")
# =================================================================

client = None
if GEMINI_API_KEY and GEMINI_API_KEY.strip() and not GEMINI_API_KEY.startswith("your"):
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        print("🧠 जेमिनी एआय मेंदू (बॅकअप मोडसाठी) सक्रिय झाला आहे.", flush=True)
    except Exception:
        client = None

ALL_NUMBERS = [num.strip() for num in WHATSAPP_NUMBER.split(",") if num.strip()]


def speak(text):
    print(f"असिस्टंट: {text}", flush=True)
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 155)
        engine.say(text)
        engine.runAndWait()
    except Exception:
        pass


def get_bhau_command_popup():
    import tkinter as tk
    from tkinter import simpledialog
    print("⏳ पॉप-अप बॉक्स स्क्रीनवर आणत आहे...", flush=True)
    speak("आशिष भाऊ, तुमचा महा-एजंट रेडी आहे. तुमचा हुकूम टाका.")
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    query = simpledialog.askstring("महा एआय एजंट २०२६", "भाऊ, गुगलवर काय शोधायचे ते लिहा:")
    root.destroy()
    return query if query and query.strip() else "mpsc vastav katta most viewed video"


def ask_whatsapp_permission():
    import tkinter as tk
    from tkinter import simpledialog
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    ans = simpledialog.askstring("सुरक्षितता परवानगी", "हा डेटा व्हॉट्सॲपवर पाठवायचा का? (1 = होय / 0 = नाही):")
    root.destroy()
    return True if (ans and ans.strip() == "1") else False


def human_like_typing(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.10, 0.18))
    time.sleep(0.5)


def human_like_scroll(clicks=-7):
    print("📜 भाऊ, स्क्रीन खाली स्क्रोल करत आहे...", flush=True)
    for _ in range(abs(clicks)):
        pyautogui.scroll(-240)
        time.sleep(random.uniform(0.2, 0.4))


def human_like_mouse_wiggle(moves=3):
    """माऊस थोडं इकडे-तिकडे नैसर्गिकपणे हलवतो, जेणेकरून एजंट कमी 'बॉट' सारखा दिसेल."""
    try:
        screen_w, screen_h = pyautogui.size()
        current_x, current_y = pyautogui.position()
    except Exception:
        return
    for _ in range(moves):
        offset_x = random.randint(-100, 100)
        offset_y = random.randint(-80, 80)
        target_x = max(50, min(screen_w - 50, current_x + offset_x))
        target_y = max(50, min(screen_h - 50, current_y + offset_y))
        try:
            pyautogui.moveTo(target_x, target_y, duration=random.uniform(0.3, 0.9), tween=pyautogui.easeInOutQuad)
        except Exception:
            pass
        current_x, current_y = target_x, target_y
        time.sleep(random.uniform(0.2, 0.6))


def human_pause(min_sec=1.0, max_sec=2.5):
    """नैसर्गिक, वेगवेगळ्या लांबीचा थांबा — सतत ठराविक वेळच थांबल्याने पॅटर्न ओळखता येतो, तो टाळतो."""
    time.sleep(random.uniform(min_sec, max_sec))


def start_edge_browser():
    print("🌐 एज ब्राउझर सुरक्षित मानवी मोडमध्ये सुरू करत आहे...", flush=True)

    # 🔧 आधीच्या क्रॅश झालेल्या सेशनमुळे राहिलेली lock file असेल तर साफ करतो
    for lock_name in ["SingletonLock", "SingletonCookie", "SingletonSocket"]:
        lock_path = os.path.join(EDGE_PROFILE_DIR, lock_name)
        if os.path.exists(lock_path):
            try:
                os.remove(lock_path)
                print(f"🧹 जुनी lock file साफ केली: {lock_name}", flush=True)
            except Exception:
                pass

    def build_options(use_profile=True):
        options = webdriver.EdgeOptions()
        options.add_argument('--start-maximized')
        options.add_experimental_option("detach", True)
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        if use_profile:
            options.add_argument(f"--user-data-dir={EDGE_PROFILE_DIR}")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        return options

    service = EdgeService(EdgeChromiumDriverManager().install())

    try:
        return webdriver.Edge(service=service, options=build_options(use_profile=True))
    except Exception as e:
        print(f"⚠️ Custom profile ने Edge सुरू होईना ({e}). profile शिवाय पुन्हा प्रयत्न करत आहे...", flush=True)
        return webdriver.Edge(service=service, options=build_options(use_profile=False))


# ---------------------------------------------------------------
# 🔧 FIX #1: सर्च बॉक्स आता properly wait करून, clickable होईपर्यंत थांबून शोधतो
# ---------------------------------------------------------------
def find_search_box(driver, wait):
    search_selectors = [
        (By.NAME, "q"),
        (By.XPATH, "//textarea[@name='q']"),
        (By.XPATH, "//textarea[@title='Search']"),
        (By.XPATH, "//input[@type='text' and @title='Search']"),
        (By.XPATH, "//*[@id='APjFqb']"),
    ]
    for selector, value in search_selectors:
        try:
            box = wait.until(EC.element_to_be_clickable((selector, value)))
            if box.is_displayed():
                return box
        except Exception:
            continue
    return None


def type_search_and_submit(driver, wait, bhau_command):
    search_box = find_search_box(driver, wait)
    if search_box is None:
        raise RuntimeError("Google search box सापडला नाही (भाऊ, पेज लोड नीट झालं नसेल)")

    human_like_typing(search_box, bhau_command)
    # autosuggest dropdown मुळे Enter अडतो, म्हणून आधी ESC देऊन बंद करतो
    search_box.send_keys(Keys.ESCAPE)
    time.sleep(0.3)
    search_box.send_keys(Keys.ENTER)

    # निकाल पेज खरंच लोड झालं का ते खात्री करून घेतो, नाहीतर URL ने direct search
    try:
        wait.until(EC.url_contains("search?"))
    except Exception:
        print("⚠️ Enter काम करत नाहीये, थेट सर्च URL ने पुढे जात आहे...", flush=True)
        driver.get("https://www.google.com/search?q=" + urllib.parse.quote(bhau_command))
    time.sleep(3)


# ---------------------------------------------------------------
# 🔧 नवीन: Google च्या "AI Mode" टॅबवर क्लिक करून त्याचं उत्तर वाचतो (प्रिंट + बोलून)
# ---------------------------------------------------------------
def click_ai_mode_and_read(driver, wait):
    print("🧠 Google 'AI Mode' टॅब शोधत आहे...", flush=True)
    ai_mode_selectors = [
        (By.XPATH,
         "//div[@role='tab' and contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'ai mode')]"),
        (By.XPATH,
         "//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'ai mode')]"),
        (By.XPATH, "//*[contains(@aria-label, 'AI Mode') or contains(@aria-label, 'AI mode')]"),
    ]

    ai_tab = None
    for selector, value in ai_mode_selectors:
        try:
            el = WebDriverWait(driver, 6).until(EC.element_to_be_clickable((selector, value)))
            if el.is_displayed():
                ai_tab = el
                break
        except Exception:
            continue

    if ai_tab is None:
        print("⚠️ 'AI Mode' टॅब सापडला नाही, सामान्य निकालांवरच पुढे जात आहे...", flush=True)
        return False

    human_like_mouse_wiggle(2)
    try:
        ai_tab.click()
    except Exception:
        try:
            driver.execute_script("arguments[0].click();", ai_tab)
        except Exception as e:
            print(f"⚠️ AI Mode टॅबवर क्लिक करता आलं नाही: {e}", flush=True)
            return False

    print("⏳ AI Mode चं उत्तर लोड होण्याची वाट पाहत आहे...", flush=True)
    time.sleep(5)

    answer_text = ""
    content_selectors = [
        (By.ID, "center_col"),
        (By.ID, "rcnt"),
        (By.XPATH, "//div[@role='main']"),
    ]
    for selector, value in content_selectors:
        try:
            container = driver.find_element(selector, value)
            text = container.text.strip()
            if len(text) > 50:
                answer_text = text
                break
        except Exception:
            continue

    if not answer_text:
        try:
            answer_text = driver.find_element(By.TAG_NAME, "body").text.strip()
        except Exception:
            answer_text = ""

    if answer_text:
        short_answer = answer_text[:600]
        print(f"🧠 AI Mode उत्तर:\n{short_answer}", flush=True)
        speak("भाऊ, गुगलच्या AI Mode ने हे उत्तर दिलं आहे.")
        speak(short_answer)
    else:
        print("⚠️ AI Mode चं उत्तर वाचता आलं नाही.", flush=True)

    return answer_text


def extract_video_title_from_ai_answer(answer_text):
    """AI Mode च्या उत्तरात व्हिडिओचं नेमकं शीर्षक बहुतेक वेळा दुहेरी अवतरण
    चिन्हात (\" ... \") दिलेलं असतं — तेच वाचून काढतो, जेणेकरून थेट YouTube वर
    अचूक शोधता येईल."""
    if not answer_text:
        return None
    matches = re.findall(r'"([^"]{5,150})"', answer_text)
    if matches:
        return matches[0].strip()
    return None


# ---------------------------------------------------------------
# 🔧 नवीन: AI Mode च्या उत्तरात व्हिडिओचं नाव highlighted असतं, त्याच्या शेजारी
# छोटा YouTube favicon/आयकॉन असतो — तोच शोधून क्लिक करतो. साधा href शोध
# पुरेसा नव्हता कारण तो आयकॉन/चिप स्वरूपात असतो, नुसती टेक्स्ट लिंक नाही.
# ---------------------------------------------------------------
def find_and_click_video_in_ai_mode(driver, bhau_command, wait_time=15):
    print("🔎 AI Mode च्या उत्तरात व्हिडिओ आयकॉन/लिंक शोधत आहे...", flush=True)
    end_time = time.time() + wait_time

    while time.time() < end_time:
        candidates = []

        # 1) थेट youtube.com/watch किंवा youtu.be href असलेली लिंक
        try:
            candidates += driver.find_elements(
                By.XPATH, "//a[contains(@href, 'youtube.com/watch') or contains(@href, 'youtu.be')]"
            )
        except Exception:
            pass

        # 2) YouTube favicon/आयकॉन (इमेज) असलेल्या घटकाचा जवळचा clickable parent <a>
        try:
            icons = driver.find_elements(
                By.XPATH,
                "//img[contains(translate(@alt, 'YOUTUBE', 'youtube'), 'youtube') or contains(@src, 'youtube')]"
            )
            for icon in icons:
                try:
                    parent_link = icon.find_element(By.XPATH, "./ancestor::a[1]")
                    candidates.append(parent_link)
                except Exception:
                    continue
        except Exception:
            pass

        # 3) aria-label मध्ये 'YouTube' उल्लेख असलेले clickable घटक (chip/card स्वरूपातले)
        try:
            candidates += driver.find_elements(
                By.XPATH, "//*[(@role='link' or self::a) and contains(@aria-label, 'YouTube')]"
            )
        except Exception:
            pass

        visible_candidates = []
        for c in candidates:
            try:
                if c.is_displayed():
                    visible_candidates.append(c)
            except Exception:
                continue

        if visible_candidates:
            target = visible_candidates[0]
            try:
                title_text = target.text.strip() or target.get_attribute("aria-label") or "(नाव वाचता आलं नाही)"
            except Exception:
                title_text = "(नाव वाचता आलं नाही)"

            print(f"🎯 AI Mode मध्ये व्हिडिओ सापडला -> नाव: '{title_text}'. क्लिक करत आहे...", flush=True)
            speak(f"भाऊ, हा व्हिडिओ इथेच सापडला: {title_text}")
            human_like_mouse_wiggle(2)
            human_pause(0.5, 1.2)

            main_window = driver.current_window_handle
            try:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", target)
                time.sleep(0.6)
                target.click()
            except Exception:
                try:
                    driver.execute_script("arguments[0].click();", target)
                except Exception:
                    time.sleep(1.5)
                    continue

            time.sleep(3)

            # क्लिक केल्याने नवीन टॅब उघडला असेल तर तिकडे स्विच करतो
            if len(driver.window_handles) > 1:
                driver.switch_to.window(driver.window_handles[-1])
                time.sleep(2)

            if "youtube.com/watch" in driver.current_url.lower() or "youtu.be/" in driver.current_url.lower():
                return True

            print("⚠️ क्लिक झालं पण व्हिडिओ प्रत्यक्ष उघडला नाही, अजून शोधत आहे...", flush=True)

        time.sleep(1.5)

    print("⚠️ AI Mode मध्ये व्हिडिओ आयकॉन सापडला नाही किंवा उघडता आला नाही.", flush=True)
    return False


def check_for_captcha(driver):
    """खरा CAPTCHA/ब्लॉक पेज आढळल्यासच थांबतो. Google च्या प्रत्येक पेजमध्ये
    लपलेली recaptcha स्क्रिप्ट असतेच, म्हणून raw page source ऐवजी विश्वासार्ह
    signals (block URL + प्रत्यक्ष दिसणारा मजकूर) तपासतो — खोटा अलार्म टाळण्यासाठी."""
    try:
        current_url = driver.current_url.lower()
    except Exception:
        current_url = ""

    is_blocked = "/sorry/" in current_url

    if not is_blocked:
        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        except Exception:
            body_text = ""
        block_phrases = [
            "unusual traffic from your computer network",
            "our systems have detected unusual traffic",
            "verify you are a human",
            "i'm not a robot",
        ]
        is_blocked = any(phrase in body_text for phrase in block_phrases)

    if is_blocked:
        print("🛑 खरा CAPTCHA/ब्लॉक पेज आढळला! कृपया ब्राउझरमध्ये मॅन्युअली सोडवा.", flush=True)
        speak("भाऊ, गुगलने कॅप्चा दाखवला आहे. कृपया मॅन्युअली सोडवा, मी थांबून राहतो.")
        input("👉 CAPTCHA सोडवल्यानंतर इथे टर्मिनलमध्ये Enter दाबा भाऊ...")
        return True
    return False


def skip_youtube_ads(driver):
    ad_selectors = [
        "//button[contains(@class, 'ytp-skip-ad-button')]",
        "//span[contains(text(), 'Skip') or contains(text(), 'वगळा') or contains(text(), 'Skip Ad')]",
        "//div[contains(@class, 'ytp-ad-skip-button')]",
        "//button[contains(@id, 'skip-button')]",
    ]
    for selector in ad_selectors:
        try:
            buttons = driver.find_elements(By.XPATH, selector)
            for button in buttons:
                if button.is_displayed():
                    print("🎯 जाहिरात सापडली! स्किप करत आहे...", flush=True)
                    button.click()
                    time.sleep(1)
                    return True
        except Exception:
            continue
    return False


# ---------------------------------------------------------------
# 🔧 FIX #2: आधी थेट पेजवरचा (DOM) व्हिडिओ रिझल्ट वाचून नाव दाखवून क्लिक करतो.
# हे सापडलं नाही तरच Gemini AI Mode (screenshot) backup वापरतो.
# ---------------------------------------------------------------
def find_and_click_video_result(driver, bhau_command, max_scrolls=4):
    print("🔎 गुगल निकालांमधून व्हिडिओ लिंक थेट वाचत आहे...", flush=True)
    for attempt in range(max_scrolls):
        video_links = driver.find_elements(
            By.XPATH, "//a[contains(@href, 'watch?v=') or contains(@href, 'youtube.com/watch') or contains(@href, 'youtu.be')]"
        )
        visible_links = [l for l in video_links if l.is_displayed()]
        if visible_links:
            target = visible_links[0]
            try:
                title_text = target.text.strip() or target.get_attribute("aria-label") or "(नाव वाचता आलं नाही)"
            except Exception:
                title_text = "(नाव वाचता आलं नाही)"
            print(f"🎯 व्हिडिओ सापडला -> नाव: '{title_text}'. यावर क्लिक करत आहे...", flush=True)
            speak(f"भाऊ, हा व्हिडिओ सापडला: {title_text}")
            human_like_mouse_wiggle(2)
            human_pause(0.5, 1.2)
            try:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", target)
                time.sleep(0.6)
                target.click()
            except Exception:
                try:
                    driver.execute_script("arguments[0].click();", target)
                except Exception:
                    continue
            return True
        print(f"👀 [प्रयत्न {attempt + 1}/{max_scrolls}] व्हिडिओ दिसला नाही, स्क्रोल करत आहे...", flush=True)
        human_like_scroll(-5)
        time.sleep(1)
    return False


def ai_mode_click_google_search_result(bhau_command, max_scrolls=5):
    """Backup पद्धत: फक्त DOM मध्ये लिंक न सापडल्यास वापरतो (Gemini vision)."""
    global client
    if not client:
        return "BACKUP_TRIGGERED"

    for i in range(max_scrolls):
        print(f"👀 [Gemini बॅकअप - प्रयत्न {i + 1}/{max_scrolls}] स्क्रीन तपासत आहे...", flush=True)
        time.sleep(3)
        screenshot_file = "google_search_view.png"
        if os.path.exists(screenshot_file):
            try:
                os.remove(screenshot_file)
            except Exception:
                pass
        pyautogui.screenshot(screenshot_file)

        full_prompt = (
            f"You are the visual AI brain of Ashish Bhau's Agent. Look at this active Google search result screen.\n"
            f"Objective: Locate the main YouTube video thumbnail box or biggest blue link for: '{bhau_command}'.\n"
            f"Return ONLY its exact center X and Y coordinates separated by a space (e.g., '680 450'). No markdown/extra text.\n"
            f"If no video result is visible here, reply ONLY with 'SCROLL'."
