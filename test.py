# pip install curl-cffi
from curl_cffi import requests

URL = "https://www.opentable.ca/lolz-view-all/H4sIAAAAAAAA_1XNzQrCMBBG0XcZt0mZ_LfZFYwgSNWoCxWRCBEKoYUKuhDf3QFXrgbuGfjeIMGDRGk41hzVXqLX1iMCA_UnFDQF4Qh_bsBLBpaiVpW1Fq0wjLum0lo5rQy91ISbEHfrrl0tTyFet4cQjwQNwax9pr6kW8mLcZr3w5CnbnwRClo-X-jS4D2VR_58AU8q8E-nAAAA"

# Keep the raw Cookie string to preserve ordering and duplicates
COOKIE_HEADER = r"""otuvid=DA9B41E8-0C8B-46EE-B922-380567616A2B; OT-SessionId=364b63cd-4538-4bb3-8b0e-03098357c2e6; OT-Interactive-SessionId=364b63cd-4538-4bb3-8b0e-03098357c2e6; bm_ss=ab8e18ef4e; _ga=GA1.1.1107661828.1754253922; ha_userSession=lastModified=2025-07-09T00%3A34%3A33.000Z&origin=prod-sc2; otuvid_f=932861b8-4ef8-40ec-8133-46127ce2635c; otuvid_p=a3895aaa-822b-43b7-80a1-e7594540aba4; otuvid_t=b6f1e51e-bd41-42d0-8f9e-1a88059562f6; _fbp=fb.1.1754253924594.8029544270742752; _gcl_au=1.1.1121193374.1754253925; _tt_enable_cookie=1; _ttp=01K1RTX7H2TBCQWN451SKNQK0R_.tt.1; lvCKE=lvmreg=74%2C0&histmreg=74%2C0; ftc=x=2025-08-03T21%3A46%3A29&c=1&pt1=1&pt2=1; bm_mi=2128A362138FAEA131BBAD86CCD4F36F~YAAQNJ4QArOUA3CYAQAAIwWxcRyOeaZLyabnKRZTjSVtpHYTwWNMAVVpQwUDGYWwqzZ/uXCD4clUuYFfqZS+vgdspz7iIu+vnaJtz5pnbBPONhVQKqeymJEmN3LakZUW9uhu/Y2aaHna2Ho2XUXzOJUGAP9QLvCFRs5m35R/rzAmvG3x8Zzsiqxh3cUPZNbb4UFOWApxMngcrHAW1ZJyDsRaSoPQ/opBIHCYxDYlD007XhfKHD5gGNWa9xv15T93LQVor3frrMqOUx+7Taa7Jm9Fa5wyGkm5Vw8/ckI7SSBq1UFM0IzHwZ79rQ2PTei9OOodS6iuMfZnG+O/73LZkITy6CfGE+eBRv2Mk9Q3NykKq8Kx8AlHQEdA5YKm7V4o6cXIkeLHjuFPEQEgdjxaLwSFvcb5/lmOGhnlHAYKgtDZfKjhNwT5OQQai1QM2UcDE7YFAlMgEZh3h6h8DE64awgJUAYvAtb9GWlrEWJCYUoD1h9ygIG+31ThQyWjc9R/RsO3DAtQNCMhLxGu3pFRaBkSfKSHsfqaQulcWDRn787BcMQYvuOk5m6ifMyl0nCs8JTgzLHNY0kZNsLMPBGswDlDIzb3WR5ANtBA2b2v~1; ak_bmsc=43454DDB90DA11EB730080B7DB76BE63~000000000000000000000000000000~YAAQNJ4QAueUA3CYAQAAQguxcRz981KtrLdKSRPFgW744okLncNotNcrXjoWZGZxqAVmQQ3onz/ZaXUptxuOHtKTypMu3MXOLoditC4UlLK9cRh1kAnCeW0+ds4TUfUnZNKbwZ1vMTSiCAQFUCYxcVNy45I1ldi0iG8d7u+q9FvyAnX6KmHp3IFDS0ZGbNi+6B7HN89gztmCIwQE6vjw4iaib2mUCUne8WKTsXBu4xfBVMp+psrvpC/r0OJGKSMQ4w5rXY32AkN52LOP4XTGz4Sli3ZpjSmY9ktRspErBCdy9tl9m6sTP7EQA/yb46yKsuauWkWm4RQ9z1/jZm55Z3Iel1n7xv+rjYK3cDyOWMRYzGTiNr/xMhOgy11PAj1jcy82td8wMzhh1saiIvru9x9KVa8P7fwy4B9lQ21i/1FW4Dak0SLo+Yta5qeJP1ZsLV799X3/UPoDtkIcKbhF0T/CI4Qlpycy5xnqTvyvPVpOl7PIquilTo81bm9X56xT+ZKqJdNCjGlS+xW9E/lw+2UvMaYpScKdnbBK13qsnrxAhMsu+VbTS4/1TzrHC8D8ttVxFOKpkYgbEL84/RdcIXGa+OYYGlY2OBv+Ne3gIC4xBfUQe7LqHLn4MdcPyV4TRhvthadgZMGkyJ0Zo9YWtLeiGFyo6Cna/18d964CQdDQKAoiqvh2u/uJtAmIMGtzwaRLPzPZXzAPVn59dH6tVYxFjlUjIS6O9FUM5h5m/ec/xfTwgV0165KjRD7B3JtXONX1GMGC0AlIUyrARg==; ftc=x=2025-08-03T21%3A57%3A41&c=1&pt1=1&pt2=1; bm_s=YAAQNp4QAmaMbWOYAQAAfNy5cQP2FywOtZT3oxxMC5k4IsuM3gkbdtksfoNdvJ6dPUFWQvZ4EGDRrRkKpO7E4xYRkH+RpGb+cff3nhkHOSI7vmIdTf/OA7PGQbyjktR0H7YLqeigGczhOnHV8T4wz4QfrIorxLpD2bciNUqD4ZFYOEZ1IWBKvJY6S3LaCTK0a+qbCwdyr4oOFoCgxlH6Y2sjZ6nP7sjGbQZ5pmUNqIHxnWK69EfAGWrqfylsD+jZlbUVdLsNFtW8rXl377obdHx8Pp4g/oCoGnNXrMR16F2qk8jHeN51A1Oby1BBNqMDhoJS2u9aV5LWSNcHSjILSP5eSkRTkBOEquGmokfQP3+oXks2vkVd0XSq9+bO6jfnFunE5LaNxEfjBljVdLaL9BVcDUw0gbZOpbsjclgCw6nR4drDrdT7vQh84CCcEJdepIPI89H6EcJ3mdLLBTqyXn0/YTmuYzktqCY/zzHXbLKKfn4Nhad5CK6w2t7p/5RJfgdfcDcph7tMH6e3gKw+un/ZLbQ72UFLpUgwFHdfuHKFa0KIAt5es36ptDtf6vW5Zf1lXN+O; bm_so=A6F7320922AC9CFE101D13956E9AA2CDCD61011BE5CA56505E9EA4E3883346D3~YAAQNp4QAmeMbWOYAQAAfNy5cQRjwcNR2GBgvM4eflkDLfialuFPFOEX5IL1JM1E9FhohZxnY6Nj47dO7SYJjDbhvlrTHNW8y/GDn/e4+Y604LV9EST01PMtihoGHiywg3AjZcXD0fADOUapuNj3cCe8fHF58/7XRwV9JTjYlkOvifZcqRq6OyzJzK5xAGHD7UpoXOOrpiew+lKSP4Xw8V1HwPTdBx2UJGGPFkGKmlWinEn3Z4msOobP1J07WR2h3I6w2r6+ux03mZJWNjWR+/1OwI3uHOItkmav28Mfv1NIkdG53RhTztGrjRCz7DDKmGbfctsp2j4ddkhG7n8yKdVPKLCbDS481kqrWrMOJd3pZJ9Up2qOIPOE+8XibFOU+4YX6rT8S7npXIV1Yd7DBQ2u3048sPUanm+EWdEg1U4t0pxn5SQg9EQK3KKFv1mb7Mbnz+jLPlKWjL/9JiSa; OptanonConsent=isGpcEnabled=0&datestamp=Mon+Aug+04+2025+01%3A57%3A45+GMT%2B0500+(Pakistan+Standard+Time)&version=202503.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=c0c71331-8752-4d62-a9bd-6fc81f14d619&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&AwaitingReconsent=false&geolocation=PK%3BPB; OptanonAlertBoxClosed=2025-08-03T20:57:45.459Z; _ga_Y77FR7F6XF=GS2.1.s1754253922$o1$g1$t1754254665$j60$l0$h0; bm_lso=A6F7320922AC9CFE101D13956E9AA2CDCD61011BE5CA56505E9EA4E3883346D3~YAAQNp4QAmeMbWOYAQAAfNy5cQRjwcNR2GBgvM4eflkDLfialuFPFOEX5IL1JM1E9FhohZxnY6Nj47dO7SYJjDbhvlrTHNW8y/GDn/e4+Y604LV9EST01PMtihoGHiywg3AjZcXD0fADOUapuNj3cCe8fHF58/7XRwV9JTjYlkOvifZcqRq6OyzJzK5xAGHD7UpoXOOrpiew+lKSP4Xw8V1HwPTdBx2UJGGPFkGKmlWinEn3Z4msOobP1J07WR2h3I6w2r6+ux03mZJWNjWR+/1OwI3uHOItkmav28Mfv1NIkdG53RhTztGrjRCz7DDKmGbfctsp2j4ddkhG7n8yKdVPKLCbDS481kqrWrMOJd3pZJ9Up2qOIPOE+8XibFOU+4YX6rT8S7npXIV1Yd7DBQ2u3048sPUanm+EWdEg1U4t0pxn5SQg9EQK3KKFv1mb7Mbnz+jLPlKWjL/9JiSa^1754254666312; ttcsid=1754253925925::YOR7N8LPwieqbsS3AsY8.1.1754254667413; _uetsid=c90ef84070aa11f0a7cc65bb39de408d; _uetvid=c90efc9070aa11f0b2930d37456f9488; ttcsid_D0550FBC77UD5RFHGA50=1754253925924::1DpUrUwF4X3KppPZLGBt.1.1754254668247; bm_sv=81DDA6F9EDD9E8CFD9D99480B2F18096~YAAQNp4QAmuNbWOYAQAAWv25cRxHJ/QFTLxqLgKL90TV7n9DcB5EiS8yDfsxhMVWkaVw+blOJQGtwqs9xsAkfAxV8msStfc7HzIn4XM3dueQRU9yI3TtrtIN6C0kCVBIfS33LEdH4Ln/O1muiUQshsk6a4Z2hxOUd6mSunSvXsAwL7JRlHGmaHzr7MWaxHufqYOGaxXkAxT165BP6aS5gmGwTS63p63Kj7YzgHOlGHIGNzUOAkOKxo/gD21JNN5ZHpUf~1; OT-Session-Update-Date=1754254684"""

HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "accept-encoding": "gzip, deflate, br, zstd",
    "priority": "u=0, i",
    "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Google Chrome\";v=\"138\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    # Put the raw cookie string on the Cookie header to preserve duplicates/order
    "cookie": COOKIE_HEADER,
}

# Use a session so you could make follow-up calls if needed.
with requests.Session() as s:
    # 'impersonate' gives curl-cffi the right TLS/HTTP2 fingerprints (Chrome-like).
    r = s.get(
        URL,
        headers=HEADERS,
        impersonate="chrome",   # or e.g. "chrome138"
        timeout=60,
        allow_redirects=True,
    )

    print("Status:", r.status_code)
    print("Final URL:", r.url)
    print("Response headers:")
    for k, v in r.headers.items():
        print(f"{k}: {v}")

    # Dump the body as-is (bytes) and also as text if it looks like HTML.
    with open("opentable_response.bin", "wb") as f:
        f.write(r.content)

    ctype = r.headers.get("content-type", "")
    if "text/html" in ctype:
        with open("opentable_response.html", "wb") as f:
            f.write(r.content)
        print("Saved HTML to opentable_response.html")
    else:
        print("Non-HTML response; saved raw bytes to opentable_response.bin")
