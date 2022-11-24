import os
import asyncio
from playwright.async_api import async_playwright

admin_cookie = { 'name' : 'PHPSESSID',
                    # @todo - make this a secret?
                    'value' : os.environ.get('SESSION_ID'),
                    'url' : os.environ.get('URL'),
                    'httpOnly' : False
                }

extra_header = { 'Authorization' : 'Bearer ' + os.environ.get('AUTH')}

async def print_console_output(output):
    print(f'noticed output in the console log - {output}')

async def print_request(url):
    print(f'made a request - {url}')

async def main():
    async with async_playwright() as p:

        # setup
        browser = await p.chromium.launch()
        context = await browser.new_context()
        await context.add_cookies([admin_cookie])
        await context.set_extra_http_headers(extra_header)
        page = await context.new_page()
        page.on("console", print_console_output)
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
