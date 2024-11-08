import os
import json
import base64
import requests
import webbrowser
from loguru import logger

class SchwabOAuth:
    def __init__(self, app_key: str, app_secret: str):
        self.app_key = app_key
        self.app_secret = app_secret
        self.redirect_uri = "https://127.0.0.1"
        self.auth_url = f"https://api.schwabapi.com/v1/oauth/authorize?client_id={self.app_key}&redirect_uri={self.redirect_uri}"

    def construct_auth_url(self):
        """生成並打開認證 URL"""
        logger.info("請點擊以下連結進行認證:")
        logger.info(self.auth_url)
        webbrowser.open(self.auth_url)

    def extract_code_from_url(self, returned_url: str) -> str:
        """從回調 URL 中提取授權碼"""
        code_start = returned_url.index("code=") + 5
        code_end = returned_url.find("&", code_start)
        response_code = returned_url[code_start:code_end].replace("%40", "")  # 去除 @ 符號
        logger.info(f"Extracted code: {response_code}")
        return response_code

    def get_token_headers_and_payload(self, response_code: str):
        """生成 token 請求的 headers 和 payload"""
        credentials = f"{self.app_key}:{self.app_secret}"
        base64_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

        headers = {
            "Authorization": f"Basic {base64_credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        payload = {
            "grant_type": "authorization_code",
            "code": response_code,
            "redirect_uri": self.redirect_uri,  # 確保 redirect_uri 與授權 URL 完全一致
        }

        return headers, payload

    def retrieve_tokens(self, headers, payload) -> dict:
        """請求並獲取 access token 和 refresh token"""
        token_url = "https://api.schwabapi.com/v1/oauth/token"
        response = requests.post(url=token_url, headers=headers, data=payload)
        if response.status_code == 200:
            tokens = response.json()
            logger.info("成功取得 access token 和 refresh token")
            
            # 保存 token 到 tokens.json
            with open("tokens.json", "w") as f:
                json.dump(tokens, f)
            logger.info("Token 已成功保存到 tokens.json")

            return tokens
        else:
            logger.error(f"Token request failed with status {response.status_code}")
            return None

# 使用範例
def main():
    # 初始化 OAuth 認證，填入您的 app_key 和 app_secret
    app_key = "eTOdlULAGAECJta6idElCFNAnpomwdFt"  # 替換為您的 app_key
    app_secret = "6pEuGP4RMdMI8R4R"  # 替換為您的 app_secret
    oauth_client = SchwabOAuth(app_key, app_secret)
    
    # 打開授權 URL 並獲取返回的 URL
    oauth_client.construct_auth_url()
    returned_url = input("請將瀏覽器返回的 URL 粘貼到這裡: ")

    # 提取授權碼並請求 token
    code = oauth_client.extract_code_from_url(returned_url)
    headers, payload = oauth_client.get_token_headers_and_payload(code)
    tokens = oauth_client.retrieve_tokens(headers, payload)
    
    if tokens:
        logger.info(f"成功獲取新 token: {tokens}")
    else:
        logger.error("無法獲取新 token")

if __name__ == "__main__":
    main()
