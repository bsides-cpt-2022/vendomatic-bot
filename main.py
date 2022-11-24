import os
import asyncio
from playwright.async_api import async_playwright

admin_cookie = { 'name' : 'PHPSESSID',
                    # @todo - make this a secret?
                    'value' : os.environ['SESSION_ID'],
                    'url' : os.environ['URL'],
                    'httpOnly' : False
                }

http_credentials = {
                        'username' : os.environ['WEBUSERNAME'],
                        'password' : os.environ['WEBPASSWORD']
                    }

extra_header_ua = { 'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.35' }

async def print_console_output(output):
    print(f'noticed output in the console log - {output}')

async def print_request(request):
    print(f'made a request - url: {request.url}')

async def main():
    async with async_playwright() as p:

        # setup
        browser = await p.chromium.launch()
        context = await browser.new_context(http_credentials=http_credentials)
        await context.add_cookies([admin_cookie])
        await context.set_extra_http_headers(extra_header_ua)
        page = await context.new_page()
        page.on("console", print_console_output)
        page.on("requestfailed", lambda request: print(request.url + " " + request.failure.error_text))
        page.on("request", print_request)

        # @todo - point to admin page
        await page.goto(os.environ.get('URL'))
 
        await page.wait_for_selector(selector="#grid_table", state='visible', timeout=10000)

        await page.evaluate('document')

        # the admin portal for vendomatic is feature poor
        # this part scrapes the spiral quantities for any empty spirals and sends an email
        nodes = page.locator(selector='span.spiral.d-inline-block.m-1')
        texts = await nodes.all_inner_texts()

        for text in texts:
            if (text.isdigit() and int(text) < 1):
                # todo complete the email send / feedback
                pass
                

        # clean up
        await context.close()
        await browser.close()

asyncio.run(main())
