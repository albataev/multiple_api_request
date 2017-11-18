import asyncio


class Fetcher():


    def __init__(self, url, session, proxy = None, params = None):
        self.api_url = url
        self.session = session
        self.proxy = proxy or None


    async def fetch(self, timeout = 1):
            print('processing http request with proxy: {}'.format(self.proxy))
            html = await self._process(self.session, timeout)
            if html:
                return html
            else:
                print('None - nothing to return')
                return None


    async def _process(self, session, timeout):
        try:
            async with session.get(self.api_url, proxy=self.proxy, timeout = timeout) as resp:
                print('responce status: ', resp.status)
                return await resp.text()
        except asyncio.TimeoutError:
            print('Timed out')
            return None
        except NameError:
            print('Certificate Error')


    def close_session(self):
        self.session.close()

