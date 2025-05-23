from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import re
import time
import datetime


def setup_driver():
    """Chrome 드라이버 설정"""
    options = ChromeOptions()
    user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1'
    options.add_argument('user-agent=' + user_agent)
    options.add_argument('lang=en-KR')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    return driver


def scroll_and_load_reviews(driver, max_scrolls=50):
    """리뷰 페이지에서 스크롤하며 모든 리뷰 로드"""
    print("리뷰 스크롤 중...")

    # 초기 높이 저장
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_count = 0
    no_change_count = 0

    while scroll_count < max_scrolls and no_change_count < 5:
        # 페이지 끝까지 스크롤
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # 새로운 높이 확인
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            no_change_count += 1
            print(f"높이 변화 없음 ({no_change_count}/3)")
        else:
            no_change_count = 0
            print(f"스크롤 {scroll_count + 1}: 높이 {last_height} -> {new_height}")

        last_height = new_height
        scroll_count += 1

        # 더보기 버튼이 있는지 확인하고 클릭
        try:
            more_button = driver.find_element(By.XPATH, "//button[contains(text(), '더보기') or contains(text(), 'More')]")
            if more_button.is_displayed():
                driver.execute_script("arguments[0].click();", more_button)
                print("더보기 버튼 클릭")
                time.sleep(2)
                no_change_count = 0
        except NoSuchElementException:
            pass

    print(f"스크롤 완료: 총 {scroll_count}번 스크롤")


def extract_all_reviews(driver, movie_title):
    """페이지에서 모든 리뷰 추출"""
    reviews = []

    # 다양한 리뷰 선택자 시도
    review_selectors = [
        '//*[@id="contents"]/div[4]/section[2]/div/article[{}]/div[3]/a/h5',
        '//*[@id="contents"]/div[4]/section[2]/div/article[{}]/div[3]/a[1]/h5',
        '//*[@id="contents"]/div[4]/section[2]/div/article[{}]/div[3]/h5',
        '//article[{}]//h5',
        '//div[contains(@class, "review")]//h5'
    ]

    # 리뷰 개수 확인 (더 많은 리뷰가 있을 수 있으므로 넉넉하게)
    max_reviews = 50
    found_reviews = 0

    for i in range(1, max_reviews + 1):
        review_found = False

        for selector in review_selectors:
            try:
                if '{}' in selector:
                    xpath = selector.format(i)
                else:
                    xpath = f"({selector})[{i}]"

                review_element = driver.find_element(By.XPATH, xpath)
                review_text = review_element.text.strip()

                if review_text and review_text not in reviews:
                    reviews.append(review_text)
                    found_reviews += 1
                    print(f"리뷰 {found_reviews} 추출: {review_text[:50]}...")
                    review_found = True
                    break

            except (NoSuchElementException, StaleElementReferenceException):
                continue

        # 연속으로 리뷰를 찾지 못하면 중단
        if not review_found:
            if i > 10:  # 처음 10개는 건너뛸 수 있음
                break

    # 전체 리뷰 텍스트 결합
    full_review_text = ' '.join(reviews) if reviews else f"{movie_title}에 대한 리뷰를 찾을 수 없습니다."
    print(f"{movie_title}: 총 {len(reviews)}개 리뷰 추출")

    return full_review_text


def main():
    # 드라이버 설정
    driver = setup_driver()

    try:
        # 초기 설정
        button_movie_xpath = '//*[@id="contents"]/section/div[3]/div/section/div/div/div[2]/button'
        check_xpath = '//*[@id="contents"]/section/div[4]/div/div[2]/div/div[{}]/button'.format(4)

        # 시작 URL로 이동
        start_url = 'https://m.kinolights.com/discover/explore'
        print(f"페이지 로딩: {start_url}")
        driver.get(start_url)
        time.sleep(2)

        # 영화 버튼 클릭
        print("영화 카테고리 선택")
        button_movie = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, button_movie_xpath))
        )
        driver.execute_script("arguments[0].click();", button_movie)
        time.sleep(3)

        # 코미디 장르 선택
        print("코미디 장르 선택")
        check_comedy = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, check_xpath))
        )
        driver.execute_script("arguments[0].click();", check_comedy)
        time.sleep(2)

        # 영화 목록 스크롤
        print("영화 목록 로딩")
        for i in range(3):
            driver.execute_script('window.scrollTo(0, document.documentElement.scrollHeight);')
            time.sleep(1)

        # 영화 정보 수집
        hrefs = []
        titles = []

        print("영화 정보 수집 중...")
        for i in range(1, 6):  # 5개 영화로 확장
            try:
                href_xpath = f'/html/body/div/div/div/main/div/div[2]/a[{i}]'
                title_xpath = f'/html/body/div/div/div/main/div/div[2]/a[{i}]/div/div[2]/span'

                href_element = driver.find_element(By.XPATH, href_xpath)
                title_element = driver.find_element(By.XPATH, title_xpath)

                href = href_element.get_attribute('href')
                title = title_element.text.strip()

                if href and title:
                    hrefs.append(href)
                    titles.append(title)
                    print(f"영화 {i}: {title}")

            except NoSuchElementException:
                print(f"영화 {i}: 정보를 찾을 수 없습니다.")
                continue

        print(f"총 {len(titles)}개 영화 발견")

        # 각 영화의 리뷰 크롤링
        reviews = []
        for idx, (url, title) in enumerate(zip(hrefs, titles)):
            print(f"\n=== {idx + 1}/{len(titles)}: {title} 리뷰 크롤링 ===")

            try:
                # 리뷰 페이지로 이동
                review_url = url + '?tab=review'
                print(f"리뷰 페이지 로딩: {review_url}")
                driver.get(review_url)
                time.sleep(3)

                # 리뷰 스크롤 및 로드
                scroll_and_load_reviews(driver)

                # 리뷰 추출
                review_text = extract_all_reviews(driver, title)
                reviews.append(review_text)

            except Exception as e:
                print(f"{title} 리뷰 크롤링 중 오류: {str(e)}")
                reviews.append(f"{title}에 대한 리뷰 크롤링 실패: {str(e)}")

        # 결과 저장
        print("\n=== 결과 저장 ===")
        df = pd.DataFrame({
            'title': titles,
            'reviews': reviews,
            'review_length': [len(review) for review in reviews]
        })

        # CSV 저장
        df.to_csv('./data/reviews.csv', index=False, encoding='utf-8-sig')
        print("결과가 './data/reviews.csv'에 저장되었습니다.")

        # 결과 미리보기
        print("\n=== 결과 미리보기 ===")
        for idx, row in df.iterrows():
            print(f"\n{idx + 1}. {row['title']} (리뷰 길이: {row['review_length']}자)")
            print(f"   리뷰 미리보기: {row['reviews'][:100]}...")

    except Exception as e:
        print(f"크롤링 중 오류 발생: {str(e)}")

    finally:
        print("\n브라우저 종료")
        driver.quit()


if __name__ == "__main__":
    main()