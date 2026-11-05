import os
import time
import traceback

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait


# ============================================================
# CONFIGURATION
# ============================================================

CONTACT_NAME = "Justino Huawei"

CHECK_INTERVAL = 2

PROFILE = os.path.abspath("whatsapp_profile")


# ============================================================
# START CHROME
# ============================================================

def start_driver():

    options = webdriver.ChromeOptions()

    options.add_argument(
        f"--user-data-dir={PROFILE}"
    )

    options.add_argument(
        "--start-maximized"
    )

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
# OPEN CONTACT
# ============================================================

def open_contact(driver, contact_name):

    print(
        f"Searching for '{contact_name}'..."
    )

    # --------------------------------------------------------
    # Search button
    # --------------------------------------------------------

    search_button = None

    xpaths = [

        '//button[@aria-label="Search or start new chat"]',

        '//button[contains(@aria-label, "Search")]',

        '//div[@role="button"][@title="Search"]',

    ]

    for xpath in xpaths:

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

        except:

            pass


    if search_button:

        try:

            driver.execute_script(
                "arguments[0].click();",
                search_button
            )

        except:

            try:
                search_button.click()
            except:
                pass


    time.sleep(1)


    # --------------------------------------------------------
    # Search input
    # --------------------------------------------------------

    search_input = None

    xpaths = [

        '//div[@contenteditable="true"][@role="textbox"]',

        '//div[@contenteditable="true"]',

        '//input[@type="text"]',

    ]


    for xpath in xpaths:

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

        except:

            pass


    if not search_input:

        print(
            "ERROR: Search field not found."
        )

        return False


    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    search_input.click()

    search_input.send_keys(
        Keys.CONTROL,
        "a"
    )

    search_input.send_keys(
        contact_name
    )

    time.sleep(3)


    # --------------------------------------------------------
    # Find contact
    # --------------------------------------------------------

    contact = None

    xpaths = [

        f'//span[@title="{contact_name}"]',

        f'//span[contains(@title, "{contact_name}")]',

        f'//span[contains(text(), "{contact_name}")]',

    ]


    for xpath in xpaths:

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

        except:

            pass


    if contact:

        print(
            f"Found: {contact_name}"
        )

        try:

            driver.execute_script(
                "arguments[0].click();",
                contact
            )

        except:

            contact.click()

        time.sleep(3)

        return True


    # --------------------------------------------------------
    # Manual fallback
    # --------------------------------------------------------

    print(
        f"Could not automatically find "
        f"'{contact_name}'."
    )

    input(
        "Open the conversation manually "
        "and press ENTER..."
    )

    return True


# ============================================================
# FIND REAL WHATSAPP MESSAGE CONTAINERS
# ============================================================

def get_messages(driver):

    """
    Get WhatsApp message containers.

    We intentionally use ONE selector here.
    This prevents the same message being returned
    several times by different selectors.
    """

    elements = driver.find_elements(
        By.CSS_SELECTOR,
        'div[data-id]'
    )

    messages = []

    used_ids = set()


    for element in elements:

        try:

            data_id = element.get_attribute(
                "data-id"
            )

            if not data_id:

                continue


            # ------------------------------------------------
            # Prevent duplicate DOM elements
            # ------------------------------------------------

            if data_id in used_ids:

                continue


            used_ids.add(
                data_id
            )


            messages.append(
                element
            )

        except:

            pass


    return messages


# ============================================================
# GET MESSAGE TEXT
# ============================================================

def get_message_text(element):

    try:

        text_elements = element.find_elements(
            By.CSS_SELECTOR,
            "span.selectable-text"
        )


        texts = []


        for text_element in text_elements:

            text = text_element.text.strip()

            if text:

                texts.append(
                    text
                )


        if texts:

            # Remove duplicated text fragments
            unique_texts = []

            for text in texts:

                if text not in unique_texts:

                    unique_texts.append(
                        text
                    )


            return "\n".join(
                unique_texts
            )


    except:

        pass


    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    try:

        return element.text.strip()

    except:

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


    except:

        pass


    # --------------------------------------------------------
    # Look inside element
    # --------------------------------------------------------

    try:

        if element.find_elements(
            By.CSS_SELECTOR,
            ".message-out"
        ):

            return "OUTGOING"


        if element.find_elements(
            By.CSS_SELECTOR,
            ".message-in"
        ):

            return "INCOMING"


    except:

        pass


    return "UNKNOWN"


# ============================================================
# READ MESSAGE
# ============================================================

def read_message(element):

    try:

        message_id = element.get_attribute(
            "data-id"
        )


        text = get_message_text(
            element
        )


        message_type = get_message_type(
            element
        )


        if not message_id:

            return None


        if not text:

            return None


        return {
            "id": message_id,
            "text": text,
            "type": message_type
        }


    except:

        return None


# ============================================================
# PROCESS MESSAGE
# ============================================================

def process_message(message):

    print()

    print(
        "=" * 60
    )

    print(
        "NEW MESSAGE"
    )

    print(
        "=" * 60
    )

    print(
        "ID:",
        message["id"]
    )

    print(
        "TYPE:",
        message["type"]
    )

    print(
        "TEXT:",
        message["text"]
    )

    print(
        "=" * 60
    )

    print()


# ============================================================
# MONITOR
# ============================================================

def monitor(driver):

    print()
    print(
        "=" * 60
    )

    print(
        f"MONITORING: {CONTACT_NAME}"
    )

    print(
        "=" * 60
    )

    print(
        "Press CTRL+C to stop."
    )

    print()


    # ========================================================
    # INITIAL MESSAGES
    # ========================================================

    print(
        "Reading existing messages..."
    )


    existing_elements = get_messages(
        driver
    )


    seen_ids = set()


    for element in existing_elements:

        try:

            message_id = element.get_attribute(
                "data-id"
            )

            if message_id:

                seen_ids.add(
                    message_id
                )

        except:

            pass


    print(
        f"Existing messages ignored: "
        f"{len(seen_ids)}"
    )

    print(
        "Waiting for NEW messages..."
    )

    print()


    # ========================================================
    # INFINITE LOOP
    # ========================================================

    while True:

        try:

            elements = get_messages(
                driver
            )


            for element in elements:

                try:

                    message_id = element.get_attribute(
                        "data-id"
                    )


                    if not message_id:

                        continue


                    # ------------------------------------------------
                    # THIS IS THE IMPORTANT PART
                    #
                    # If WhatsApp has already sent us this data-id,
                    # completely ignore it.
                    # ------------------------------------------------

                    if message_id in seen_ids:

                        continue


                    # Mark BEFORE processing
                    # so it cannot be processed twice.

                    seen_ids.add(
                        message_id
                    )


                    # ------------------------------------------------
                    # Read message
                    # ------------------------------------------------

                    message = read_message(
                        element
                    )


                    if message:

                        process_message(
                            message
                        )


                except Exception:

                    pass


            time.sleep(
                CHECK_INTERVAL
            )


        except KeyboardInterrupt:

            print()
            print(
                "Monitor stopped."
            )

            break


        except Exception as e:

            print()
            print(
                "Monitoring error:"
            )

            print(e)

            print(
                "Retrying in 5 seconds..."
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


        if not open_contact(
            driver,
            CONTACT_NAME
        ):

            print(
                "Could not open contact."
            )

            return


        time.sleep(3)


        monitor(
            driver
        )


    except KeyboardInterrupt:

        print(
            "\nStopped by user."
        )


    except Exception as e:

        print()
        print(
            "Fatal error:"
        )

        print(e)

        traceback.print_exc()


    finally:

        if driver:

            try:

                driver.quit()

            except:

                pass


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()