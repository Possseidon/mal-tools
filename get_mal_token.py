# Taken from here
#   https://gitlab.com/-/snippets/2039434
#     and modified a bit.


import secrets
from datetime import datetime, timedelta

import dotenv
import requests


# 1. Generate a new Code Verifier / Code Challenge.
def get_new_code_verifier() -> str:
    return secrets.token_urlsafe(96)


# 2. Print the URL needed to authorize your application.
def print_new_authorization_url(client_id: str, code_challenge: str):
    url = f'https://myanimelist.net/v1/oauth2/authorize?response_type=code&client_id={client_id}&code_challenge={code_challenge}'
    print(f'Authorize your application by clicking here: {url}\n')


# 3. Once you've authorized your application, you will be redirected to the webpage you've
#    specified in the API panel. The URL will contain a parameter named "code" (the Authorization
#    Code). You need to feed that code to the application.
def generate_new_token(client_id: str, client_secret: str, authorization_code: str, code_verifier: str) -> dict:
    url = 'https://myanimelist.net/v1/oauth2/token'
    data = {'client_id': client_id,
            'client_secret': client_secret,
            'code': authorization_code,
            'code_verifier': code_verifier,
            'grant_type': 'authorization_code'}

    with requests.post(url, data) as response:
        response.raise_for_status()
        token = response.json()

    print('Token generated successfully!')

    return token


# 4. Test the API by requesting your profile information
def print_user_info(access_token: str):
    url = 'https://api.myanimelist.net/v2/users/@me'
    headers = {'Authorization': f'Bearer {access_token}'}

    with requests.get(url, headers=headers) as response:
        response.raise_for_status()
        user = response.json()

    print(f"\n>>> Greetings {user['name']}! <<<")


def update_env(token: dict):
    expiration_date = datetime.now() + timedelta(seconds=token['expires_in'])

    with open(".env", "w") as f:
        f.write(f"# MAL tokens will expire on: {expiration_date}\n")
        f.write(f"MAL_ACCESS_TOKEN={token['access_token']}\n")
        f.write(f"MAL_REFRESH_TOKEN={token['refresh_token']}\n")


def main():
    env = dotenv.dotenv_values(".get_mal_token.env")

    if not (client_id := env["MAL_CLIENT_ID"]):
        raise RuntimeError("Invalid MAL_CLIENT_ID")

    if not (client_secret := env["MAL_CLIENT_SECRET"]):
        raise RuntimeError("Invalid MAL_CLIENT_SECRET")

    code_verifier = code_challenge = get_new_code_verifier()
    print_new_authorization_url(client_id, code_challenge)

    authorization_code = input('Copy-paste the Authorization Code: ').strip()
    token = generate_new_token(client_id,
                               client_secret,
                               authorization_code,
                               code_verifier)

    print_user_info(token['access_token'])

    update_env(token)


if __name__ == '__main__':
    main()
