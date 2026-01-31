import re
from Tools.scripts.generate_opcode_h import footer
from playwright.sync_api import Page, expect
import time
from random import randint


def test_text_box(page: Page):
    page.goto('https://demoqa.com/text-box')
    time.sleep(1)

    page.fill(selector='#userName', value="iluha")
    time.sleep(1)

    page.fill(selector="#userEmail", value="ww.w@mail.ru")
    time.sleep(1)

    page.fill(selector="#currentAddress", value="улица пушкина дом колотушкина")
    time.sleep(1)

    page.fill(selector="#permanentAddress", value="улица не пушкина д23")
    time.sleep(1)

    page.click("button#submit")
    time.sleep(1)

    expect(page.locator("#output #name")).to_have_text('Name:iluha')
    expect(page.locator("#output #email")).to_have_text('Email:ww.w@mail.ru')
    expect(page.locator("#output #currentAddress")).to_have_text('Current Address :улица пушкина дом колотушкина')
    expect(page.locator("#output #permanentAddress")).to_have_text('Permananet Address :улица не пушкина д23')



def test_text_box2(page: Page):
    page.goto("https://dev-cinescope.coconutqa.ru/register")

    username_locator = 'input[placeholder="Имя Фамилия Отчество"]'
    email_locator = 'input[placeholder="Email"]'
    password_locator = 'input[placeholder="Пароль"]'
    duble_password_locator = 'input[name="passwordRepeat"]'

    user_email = f'test{randint(1, 9999)}-admin@email.qa'

    page.fill(username_locator, "Жмышенко Валерий Андреевич")
    page.fill(email_locator, user_email)
    page.fill(password_locator, "Qwerty123")
    page.fill(duble_password_locator, "Qwerty123")
    page.get_by_role("button", name="Зарегистрироваться").click()

    page.wait_for_url("https://dev-cinescope.coconutqa.ru/login")
    expect(page.get_by_text("Подтвердите свою почту")).to_be_visible(visible=True)



def test_text_box3(page: Page):
    page.goto("https://dev-cinescope.coconutqa.ru/register")

    user_email = f'test{randint(1, 9999)}-admin@email.qa'

    page.goto("https://demoqa.com/text-box")
    page.get_by_role("textbox", name="Full Name").click()
    page.get_by_role("textbox", name="Full Name").fill("ЖМЫШЕНКО ВАЛЕРИЙ")
    page.get_by_role("textbox", name="name@example.com").click()
    page.get_by_role("textbox", name="name@example.com").fill(user_email)
    page.get_by_role("textbox", name="Current Address").click()
    page.get_by_role("textbox", name="Current Address").fill("адресс 34")
    page.locator("#permanentAddress").click()
    page.locator("#permanentAddress").fill("не адрес")
    page.get_by_role("button", name="Submit").click()
    expect(page.locator("#name")).to_contain_text("Name:ЖМЫШЕНКО ВАЛЕРИЙ")
    expect(page.locator("#email")).to_contain_text(f"Email:{user_email}")
    expect(page.locator("#output")).to_contain_text("Current Address :адресс 34")
    expect(page.locator("#output")).to_contain_text("Permananet Address :не адрес")


def test_locator_practic1(page: Page):

    page.goto("https://demoqa.com/webtables")

    page.get_by_role("button", name="Add").click()

    expect(page.get_by_text("Registration Form")).to_be_visible(visible=True)

    page.get_by_placeholder("First Name").fill("Ilya")

    page.get_by_placeholder("Last Name").fill("Khittsov")

    user_email = f'test{randint(1, 9999)}-admin@email.qa'

    page.get_by_placeholder("name@example.com").fill(user_email)

    page.get_by_placeholder("Age").fill("27")

    page.get_by_placeholder("Salary").fill("150")

    page.get_by_placeholder("Department").fill("ОКК")

    page.get_by_role("button", name="Submit").click()

def test_locator_practic2(page: Page):
    page.goto("https://demoqa.com/automation-practice-form")

    page.get_by_placeholder("First Name").fill("Ilya")
    page.get_by_placeholder("Last Name").type("Khittsov")

    user_email = f'test{randint(1, 9999)}-admin@email.qa'
    page.get_by_placeholder("name@example.com").type(user_email)

    page.get_by_placeholder("Mobile Number").fill("8283947562")

    page.locator("#dateOfBirthInput").click()
    page.locator("div").filter(has_text=re.compile(
        r"^JanuaryFebruaryMarchAprilMayJuneJulyAugustSeptemberOctoberNovemberDecember$")).get_by_role(
        "combobox").select_option("6")
    page.get_by_role("combobox").nth(1).select_option("1998")
    page.get_by_role("option", name="Choose Monday, July 6th,").click()
    data = page.get_attribute("#dateOfBirthInput", "value")
    assert data == "06 Jul 1998"

    page.locator(".subjects-auto-complete__value-container").click()
    page.locator("#subjectsInput").fill("a")
    page.get_by_text("Maths", exact=True).click()


    page.locator("#currentAddress").fill("Pushkina")

    page.get_by_text("Male", exact=True).click()
    page.get_by_text("Sports").click()

    page.locator("div").filter(has_text=re.compile(r"^Select State$")).nth(3).click()
    page.get_by_text("NCR", exact=True).click()
    page.get_by_text("Select City").click()
    page.get_by_text("Delhi", exact=True).click()

    expect(page.get_by_role("contentinfo")).to_contain_text("© 2013-2020 TOOLSQA.COM | ALL RIGHTS RESERVED.")

    time.sleep(5)

    page.get_by_role("button", name="Submit").click()


def test_locator_practic3_is_active(page: Page):
    page.goto("https://demoqa.com/radio-button")

    radiobatton1_is_active = page.is_enabled("#yesRadio")
    radiobatton2_is_active = page.is_enabled("#impressiveRadio")
    radiobatton3_is_active = page.is_enabled("#noRadio")

    assert radiobatton1_is_active == True
    assert radiobatton2_is_active == True
    assert radiobatton3_is_active == False

def test_locator_practic4_is_visible(page: Page):
    page.goto("https://demoqa.com/checkbox")

    expect(page.get_by_text("Home", exact=True)).to_be_visible()
    desktop_visible = page.is_visible("Desktop")
    assert desktop_visible is False

    page.get_by_role("button", name="Toggle").click()
    expect(page.get_by_text("Home", exact=True)).to_be_visible()
    expect(page.get_by_text("Desktop", exact=True)).to_be_visible()

def test_locator_practic5_is_visible(page: Page):
    page.goto("https://demoqa.com/dynamic-properties")

    visibleafter_visible = page.is_visible("#visibleAfter")
    assert visibleafter_visible is False

    page.wait_for_selector("#visibleAfter", state="visible")

    visibleafter_visible = page.is_visible("#visibleAfter")
    assert visibleafter_visible is True