from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC


def capcom_login(email: str, password: str) -> dict:
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("--headless=new")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
    )
    driver = webdriver.Chrome(options=options)

    driver.get("https://cid.capcom.com/en")
    driver.add_cookie({"name": "agecheck", "value": "true", "domain": "cid.capcom.com"})

    driver.get("https://cid.capcom.com/en/login/?guidedBy=web")
    email_input = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='email']"))
    )
    email_input.send_keys(email)
    password_input = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
    password_input.send_keys(password)
    password_input.submit()

    try:
        WebDriverWait(driver, 15).until(EC.title_contains("Account Page"))
    except NoSuchElementException:
        raise SystemExit("An error occured during the login.")

    driver.get("https://www.streetfighter.com/6/buckler/auth/loginep?redirect_url=/")
    build_id: str = driver.execute_script("return __NEXT_DATA__.buildId")
    buckler_id: str = driver.get_cookie("buckler_id")

    return {"build_id": build_id, "buckler_id": buckler_id["value"]}
