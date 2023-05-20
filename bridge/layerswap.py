import requests
import json
import time

# 0x4699c4f5bf4819b21fd3236b8690f33444651b1f
from playwright.sync_api import sync_playwright

networks = {
    'arb': "Arbitrum One",
    'zks_era': "zkSync Era"
}
def bridge(account, amount, source_network="arb", destination_network="zks_era", network_type="test"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.layerswap.io/")
        print(page.title())
        page.get_by_role("button", name="Source", exact=True).click()
        time.sleep(1)
        page.get_by_text(networks[source_network], exact=True).click()
        time.sleep(1)
        page.get_by_role("button", name="Destination", exact=True).click()
        time.sleep(1)
        page.get_by_text(networks[destination_network], exact=True).click()
        page.get_by_role("textbox").fill(str(amount))
        time.sleep(1)
        page.get_by_role("button", name="0x").click()
        time.sleep(1)
        page.get_by_placeholder("0x").fill(account.address)
        time.sleep(1)
        page.get_by_text("Select", exact=True).click()
        time.sleep(1)
        page.get_by_role("button", name="Swap now").click()

        time.sleep(3)
        page.get_by_role("button", name="confirm").click()
        time.sleep(3)

        deposit_address = page.get_by_text("0x").text_content()
        print(deposit_address)

        # if networks[source_network] == "Arbitrum One":
        transfer_network = source_network + '_' + network_type
        account.transfer_eth(deposit_address, amount, network=transfer_network)
        time.sleep(10)
    # browser.close()

def send_swap_request(amount, destination_address, source_network="ARBITRUM_MAINNET", destination_network="ZKSYNCERA_MAINNET", ):
    url = "https://bridge-api.layerswap.io//api/swaps"
    payload = {"amount": str(amount), "source_exchange": None, "source_network": source_network,
               "destination_network": destination_network, "destination_exchange": None, "asset": "ETH",
               "destination_address": destination_address, "refuel": False}
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        "authorization": "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjFFOTg0RkJCQkFDODlGNDkxOUQ2OTdDQzFBM0IzQkY1QjUzOEIzOEFSUzI1NiIsIng1dCI6IkhwaFB1N3JJbjBrWjFwZk1HanM3OWJVNHM0byIsInR5cCI6ImF0K2p3dCJ9.eyJpc3MiOiJodHRwczovL2lkZW50aXR5LWFwaS5sYXllcnN3YXAuaW8iLCJuYmYiOjE2ODQyMzY3MTksImlhdCI6MTY4NDIzNjcxOSwiZXhwIjoxNjg0MzIzMTE5LCJhdWQiOiJsYXllcnN3YXBfYnJpZGdlIiwic2NvcGUiOlsibGF5ZXJzd2FwX2JyaWRnZS51c2VyIiwib2ZmbGluZV9hY2Nlc3MiXSwiYW1yIjpbImNyZWRlbnRpYWxsZXNzIl0sImNsaWVudF9pZCI6ImxheWVyc3dhcF9icmlkZ2VfdWkiLCJzdWIiOiI0MzA0NjYiLCJhdXRoX3RpbWUiOjE2ODQyMzY3MTEsImlkcCI6ImxvY2FsIiwiZW1haWwiOiJndWVzdHVzZXI4YzhjYzExOWEyOWE0ZTY3OWJiNzNjMjA2ZjlmZDNiYUBsYXllcnN3YXAuaW8iLCJ1aWQiOiI0MzA0NjYiLCJ1dHlwZSI6Imd1ZXN0In0.dufeXU2VZp679ArrbHRi7Wtn3M1MAliff3YprGK4Dh2R5uwvFlE7RSFUz1Jjtj2Zc6nlx4XgJgbl0JTXi7B-fSFeWq6-ZbHBcAfHGLaO1Mggl1uQ-cm3QPO3UbqzCN_z5XA_nB8c9mf07GH9pJkYpnEvOzJqhIygkvfORry6InBRmNM5vM32O7Kv4LkL-1JfqVZ5OFyH8aMYUfaKqH5NuEctCryZJeYFTeszo2lSkXUz1E6ibyrmwxmcUXNJWKK-VuM53dQwmIbkfokMdn-I8J4zu2hXZxBe2fwGUnfVHpU1rN6XdD7CgNu534GuB5VEzt15jseCSGACcPeSSVXkpA"

    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        # response = requests.request(method, url, headers=headers, params=params, data=data)
        if response.status_code == 200:
            print("Got NFT info successfully!")
            return response.json()
        else:
            print(f"Failed to upload file. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error sending URL request: {e}")
        return None

# headers = {
#         "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
#     }
# response = requests.get("https://www.layerswap.io/", headers=headers)
#
# send_swap_request(0.1, "0xdc8D45d062E2FA5cD76b17d24f8691c950d0DE58")