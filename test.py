import os
import time
import traceback

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ============================================================
# CONFIGURATION
# ============================================================

CONTACT_NAME = "Justino Huawei"

# Seconds between checks
CHECK_INTERVAL = 2

# Persistent Chrome profile
PROFILE = os.path.abspath("whatsapp_profile")


# ============================================================
# START CHROME
# ============================================================

def start_driver():

    print("Starting Chrome...")

    options = webdriver.ChromeOptions()

    # Keeps WhatsApp login/session
    options.add_argument(
        f"--user-data-dir={PROFILE}"
    )

    options.add_argument("--start-maximized")

    # Prevent some unnecessary Chrome automation messages
    options.add_experimental_option(
        "excludeSwitches",
        ["enable-automation"]
    )

    driver = webdriver.Chrome(
        options=options
    )

    return driver


# ============================================================
# OPEN WHATSAPP
# ============================================================

def open_whatsapp(driver):

    print("Opening WhatsApp Web...")

    driver.get(
        "https://web.whatsapp.com"
    )

    print(
        "Waiting for WhatsApp Web..."
    )

    time.sleep(10)


# ============================================================
# SEARCH CONTACT
# ============================================================

def open_contact(driver, contact_name):

    print(
        f"Searching for '{contact_name}'..."
    )

    wait = WebDriverWait(
        driver,
        30
    )

    # --------------------------------------------------------
    # Try search button
    # --------------------------------------------------------

    search_button = None

    search_button_xpaths = [

        '//button[@aria-label="Search or start new chat"]',

        '//button[contains(@aria-label, "Search")]',

        '//div[@role="button"][@title="Search"]',

    ]

    for xpath in search_button_xpaths:

        try:

            elements = driver.find_elements(
                By.XPATH,
                xpath
            )

            for element in elements:

                if element.is_displayed():

                    search_button = element
                    break

            if search_button:
                break

        except Exception:
            pass


    # --------------------------------------------------------
    # Click search button
    # --------------------------------------------------------

    if search_button:

        try:

            driver.execute_script(
                "arguments[0].click();",
                search_button
            )

            time.sleep(1)

        except Exception:

            try:
                search_button.click()
            except Exception:
                pass


    # --------------------------------------------------------
    # Find search input
    # --------------------------------------------------------

    search_input = None

    search_xpaths = [

        '//div[@contenteditable="true"][@role="textbox"]',

        '//div[@contenteditable="true"]',

        '//input[@type="text"]',

    ]

    for xpath in search_xpaths:

        try:

            elements = driver.find_elements(
                By.XPATH,
                xpath
            )

            for element in elements:

                if element.is_displayed():

                    search_input = element
                    break

            if search_input:
                break

        except Exception:
            pass


    if not search_input:

        print(
            "Could not find WhatsApp search field."
        )

        return False


    # --------------------------------------------------------
    # Search contact
    # --------------------------------------------------------

    try:

        search_input.click()

        search_input.send_keys(
            Keys.CONTROL,
            "a"
        )

        search_input.send_keys(
            contact_name
        )

    except Exception as e:

        print(
            "Could not type contact name:",
            e
        )

        return False


    time.sleep(3)


    # --------------------------------------------------------
    # Find contact
    # --------------------------------------------------------

    contact = None

    contact_xpaths = [

        f'//span[@title="{contact_name}"]',

        f'//span[contains(@title, "{contact_name}")]',

        f'//span[contains(text(), "{contact_name}")]',

        f'//*[contains(text(), "{contact_name}")]',

    ]


    for xpath in contact_xpaths:

        try:

            elements = driver.find_elements(
                By.XPATH,
                xpath
            )

            for element in elements:

                if element.is_displayed():

                    contact = element
                    break

            if contact:
                break

        except Exception:
            pass


    # --------------------------------------------------------
    # Open contact
    # --------------------------------------------------------

    if contact:

        print(
            f"Found '{contact_name}'."
        )

        try:

            driver.execute_script(
                "arguments[0].click();",
                contact
            )

        except Exception:

            try:
                contact.click()
            except Exception:
                pass

        time.sleep(3)

        return True


    print(
        f"Could not automatically find '{contact_name}'."
    )

    print(
        "Open the conversation manually."
    )

    input(
        "After opening the conversation, "
        "press ENTER..."
    )

    return True


# ============================================================
# GET MESSAGE ELEMENTS
# ============================================================

def get_message_elements(driver):

    elements = []

    selectors = [

        # Current/common WhatsApp structure
        '[data-testid="msg-container"]',

        # Message containers
        'div.message-in',

        'div.message-out',

        # Elements with WhatsApp message IDs
        'div[data-id]',

    ]


    for selector in selectors:

        try:

            found = driver.find_elements(
                By.CSS_SELECTOR,
                selector
            )

            for element in found:

                if element not in elements:

                    elements.append(
                        element
                    )

        except Exception:
            pass


    return elements


# ============================================================
# GET MESSAGE ID
# ============================================================

def get_message_id(element):

    try:

        data_id = element.get_attribute(
            "data-id"
        )

        if data_id:

            return data_id

    except Exception:
        pass


    # Some WhatsApp versions have data-id
    # on a child element.

    try:

        child = element.find_element(
            By.XPATH,
            ".//*[@data-id]"
        )

        data_id = child.get_attribute(
            "data-id"
        )

        if data_id:

            return data_id

    except Exception:
        pass


    return None


# ============================================================
# GET MESSAGE TEXT
# ============================================================

def get_message_text(element):

    # --------------------------------------------------------
    # First try selectable-text
    # --------------------------------------------------------

    try:

        texts = element.find_elements(
            By.CSS_SELECTOR,
            "span.selectable-text"
        )

        result = []

        for text_element in texts:

            text = text_element.text.strip()

            if text:

                result.append(
                    text
                )

        if result:

            return "\n".join(result)

    except Exception:
        pass


    # --------------------------------------------------------
    # Fallback: element.text
    # --------------------------------------------------------

    try:

        text = element.text.strip()

        if text:

            return text

    except Exception:
        pass


    return ""


# ============================================================
# GET MESSAGE TYPE
# ============================================================

def get_message_type(element):

    try:

        classes = (
            element.get_attribute(
                "class"
            )
            or ""
        )

        if "message-out" in classes:

            return "OUTGOING"

        if "message-in" in classes:

            return "INCOMING"

    except Exception:
        pass


    # Look for children

    try:

        incoming = element.find_elements(
            By.CSS_SELECTOR,
            ".message-in"
        )

        if incoming:

            return "INCOMING"

    except Exception:
        pass


    try:

        outgoing = element.find_elements(
            By.CSS_SELECTOR,
            ".message-out"
        )

        if outgoing:

            return "OUTGOING"

    except Exception:
        pass


    return "UNKNOWN"


# ============================================================
# READ CURRENT MESSAGES
# ============================================================

def read_messages(driver):

    message_elements = get_message_elements(
        driver
    )

    messages = []


    for element in message_elements:

        try:

            message_id = get_message_id(
                element
            )

            text = get_message_text(
                element
            )

            message_type = get_message_type(
                element
            )


            if not text:

                continue


            messages.append(
                {
                    "id": message_id,
                    "text": text,
                    "type": message_type,
                    "element": element
                }
            )

        except Exception:
            pass


    return messages


# ============================================================
# PROCESS NEW MESSAGE
# ============================================================

def process_message(message):

    message_type = message["type"]

    text = message["text"]

    print()
    print("=" * 60)
    print("NEW MESSAGE")
    print("=" * 60)

    print(
        "Type:",
        message_type
    )

    print(
        "Text:",
        text
    )

    print("=" * 60)


    # --------------------------------------------------------
    # THIS IS WHERE YOU CAN ADD YOUR OWN ACTION
    # --------------------------------------------------------
    #
    # For example:
    #
    # save_to_database(text)
    #
    # call_openai(text)
    #
    # save_to_file(text)
    #
    # send_reply(text)
    #
    # --------------------------------------------------------


# ============================================================
# MONITOR CHAT
# ============================================================

def monitor_chat(driver):

    print()
    print("=" * 60)
    print(
        f"MONITORING: {CONTACT_NAME}"
    )
    print("=" * 60)

    print(
        "Press CTRL+C to stop."
    )

    print()


    # --------------------------------------------------------
    # Messages already present when monitoring starts
    # are marked as seen.
    #
    # This prevents the program from printing hundreds of
    # old messages when it starts.
    # --------------------------------------------------------

    seen_ids = set()

    initial_messages = read_messages(
        driver
    )


    for message in initial_messages:

        message_id = message["id"]

        if message_id:

            seen_ids.add(
                message_id
            )


    print(
        f"Existing messages detected: "
        f"{len(seen_ids)}"
    )

    print(
        "Waiting for new messages..."
    )


    # ========================================================
    # INFINITE LOOP
    # ========================================================

    while True:

        try:

            messages = read_messages(
                driver
            )


            for message in messages:

                message_id = message["id"]


                # ------------------------------------------------
                # If WhatsApp gives us a unique ID
                # ------------------------------------------------

                if message_id:

                    if message_id in seen_ids:

                        continue

                    seen_ids.add(
                        message_id
                    )

                    process_message(
                        message
                    )


                # ------------------------------------------------
                # Fallback when no data-id exists
                # ------------------------------------------------

                else:

                    fallback_id = (
                        message["type"]
                        + "|"
                        + message["text"]
                    )

                    if fallback_id in seen_ids:

                        continue

                    seen_ids.add(
                        fallback_id
                    )

                    process_message(
                        message
                    )


            # ------------------------------------------------
            # Prevent memory from growing forever
            # ------------------------------------------------

            if len(seen_ids) > 10000:

                seen_ids = set(
                    list(seen_ids)[-5000:]
                )


            time.sleep(
                CHECK_INTERVAL
            )


        except KeyboardInterrupt:

            print()
            print(
                "Stopping monitor..."
            )

            break


        except Exception as e:

            print()
            print(
                "Temporary monitoring error:"
            )

            print(e)

            print(
                "Continuing in 5 seconds..."
            )

            time.sleep(5)


# ============================================================
# MAIN
# ============================================================

def main():

    driver = None

    try:

        driver = start_driver()

        open_whatsapp(
            driver
        )

        success = open_contact(
            driver,
            CONTACT_NAME
        )


        if not success:

            print(
                "Could not open contact."
            )

            return


        # Give WhatsApp time to render
        time.sleep(3)


        monitor_chat(
            driver
        )


    except KeyboardInterrupt:

        print(
            "\nProgram stopped by user."
        )


    except Exception as e:

        print()
        print(
            "FATAL ERROR:"
        )

        print(e)

        traceback.print_exc()


    finally:

        if driver:

            print(
                "Closing browser..."
            )

            try:
                driver.quit()
            except Exception:
                pass


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()