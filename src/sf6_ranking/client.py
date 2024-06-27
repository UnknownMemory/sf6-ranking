from typing import Optional

import httpx
from selenium import webdriver
from pydantic import validate_call
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

import sf6_ranking.constants as constants
from sf6_ranking.types import Characters, CharacterFilters, Region, Platform, Season


class Client:
    __slots__ = ("url", "user_agent", "build_id", "url", "client")

    def __init__(self, email: str, password: str) -> None:
        self.url: str = "https://www.streetfighter.com/6/buckler/_next/data"
        self.user_agent: str = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
        )

        self.build_id: Optional[str] = None
        self.client = httpx.AsyncClient(headers={"user-agent": self.user_agent})
        self.capcom_login(email, password)

    def capcom_login(self, email: str, password: str) -> None:
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_argument("--headless=new")
        options.add_argument(f"user-agent={self.user_agent}")
        driver = webdriver.Chrome(options=options)

        driver.get("https://cid.capcom.com/en")
        driver.add_cookie({"name": "agecheck", "value": "true", "domain": "cid.capcom.com"})

        driver.get("https://cid.capcom.com/en/login/?guidedBy=web")
        email_input = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='email']")))
        email_input.send_keys(email)
        password_input = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
        password_input.send_keys(password)
        password_input.submit()

        try:
            WebDriverWait(driver, 15).until(EC.title_contains("Account Page"))
        except NoSuchElementException:
            raise SystemExit("An error occured during the login.")

        driver.get("https://www.streetfighter.com/6/buckler/auth/loginep?redirect_url=/")

        self.build_id = driver.execute_script("return __NEXT_DATA__.buildId")
        token = driver.get_cookie("buckler_id")
        self.client.cookies.set("buckler_id", token, "www.streetfighter.com")

    @validate_call
    async def master_ranking(
        self,
        character_filter: CharacterFilters = "all",
        character: Optional[Characters] = "luke",
        platform: Platform = "all",
        region: Region = "all",
        season: Season = "current",
        page: int = 1,
    ):
        reg = constants.RegionEnum[region]
        isAllRegion: int = 1 if reg == 0 else 0

        params = {
            "character_filter": constants.CharacterFiltersEnum[character_filter].value,
            "character_id": character,
            "platform": constants.PlatformEnum[platform].value,
            "home_filter": isAllRegion,
            "home_category_id": reg,
            "home_id": 1,
            "page": page,
            "season_type": constants.SeasonEnum[season].value,
        }

        res = await self.client.get(f"{self.url}/{self.build_id}/en/ranking/master.json", params=params)

        return res.json()["pageProps"]["master_rating_ranking"]
