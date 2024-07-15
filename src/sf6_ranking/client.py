from typing import Optional

import httpx
from selenium import webdriver
from pydantic import validate_call
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

import sf6_ranking.constants as constants
from sf6_ranking.types import Characters, CharacterFilters, Country, Region, Platform, Season


class Client:
    __slots__ = ("url", "user_agent", "_buckler_id", "build_id", "url", "client")

    def __init__(self) -> None:
        self.url: str = "https://www.streetfighter.com/6/buckler/_next/data"
        self.user_agent: str = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
        )
        self._buckler_id: Optional[str] = None
        self.build_id: Optional[str] = None
        self.client = httpx.AsyncClient(headers={"user-agent": self.user_agent})

    @property
    def buckler_id(self):
        return self._buckler_id

    @buckler_id.setter
    def buckler_id(self, value: str):
        self._buckler_id = value
        self.client.cookies.set("buckler_id", value, "www.streetfighter.com")

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
        self.buckler_id = driver.get_cookie("buckler_id")

    @validate_call
    async def master_ranking(
        self,
        character_filter: CharacterFilters = "all",
        character: Optional[Characters] = None,
        platform: Platform = "all",
        region: Region = "all",
        country: Optional[Country] = None,
        season: Season = "current",
        page: int = 1,
    ) -> dict:
        if region == "specific_region" and country is None:
            raise ValueError("Argument 'country' must be provided when 'region' is set to 'specific_region'.")

        if character_filter == "specific_char" and character is None:
            raise ValueError("Argument 'character' must be provided when 'character_filter' is set to 'specific_char'.")

        region_value = constants.Region[region.upper()].value
        if region_value == 0:
            is_all_region = 1
        elif region_value == 7:
            is_all_region = 3
        else:
            is_all_region = 2

        params = {
            "character_filter": constants.CharacterFilters[character_filter.upper()].value,
            "character_id": "luke" if character is None else character,
            "platform": constants.Platform[platform.upper()].value,
            "home_filter": is_all_region,
            "home_category_id": region_value,
            "home_id": 1 if country is None else constants.Country[country.upper()].value,
            "page": page,
            "season_type": constants.Season[season.upper()].value,
        }

        print(params)

        res = await self.client.get(f"{self.url}/{self.build_id}/en/ranking/master.json", params=params)
        rankings: dict = res.json()["pageProps"]["master_rating_ranking"]

        self.__clean_master_ranking(rankings["my_ranking_info"])
        for ranking in rankings["ranking_fighter_list"]:
            self.__clean_master_ranking(ranking)

        return rankings

    def __clean_master_ranking(self, ranking: dict) -> dict:
        # remove data not directly related to the ranking
        info_keep = ["personal_info", "home_name", "home_id"]

        ranking.pop("ranking_title_data", None)
        for info in list(ranking["fighter_banner_info"]):
            if info not in info_keep:
                ranking["fighter_banner_info"].pop(info, None)

        return ranking
