from selenium import webdriver

def getLicenses(custid):
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument('--headless')

    browser = webdriver.Chrome(chrome_options=options)

    url = f"https://members.iracing.com/membersite/member/CareerStats.do?custid={custid}"

    browser.get(url)

    # login
    browser.find_element_by_class_name("username").send_keys("jlm1999@live.dk")
    browser.find_element_by_class_name("password").send_keys("753951alicia")
    browser.find_element_by_id("submit").click()

    if browser.current_url != url:
        browser.get(url)

    licenseNames = ["oval", "road", "dirtOval", "dirtRoad"]

    safetyRatings = []
    iRatings = []

    username = browser.find_element_by_xpath("//*[@id=\"image_area\"]/div[1]").text
    for licenseName in licenseNames:
        browser.execute_script("arguments[0].click();", browser.find_element_by_id(licenseName + "Tab"))
        safetyRatings.append(browser.find_element_by_xpath("//*[@id=\"" + licenseName + "TabContent\"]/div[1]/div/div[2]/div[1]").text)
        iRatings.append(browser.find_element_by_xpath("//*[@id=\"" + licenseName + "TabContent\"]/div[1]/div/div[2]/div[3]").text)
    
    browser.close()
    
    return {
        "username": username,
        "safetyRatings": safetyRatings,
        "iRatings": iRatings
    } 
    
    
