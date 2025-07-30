
REFRESH_TOKENS = [
    {'username': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHJpbmciLCJleHAiOjE3NTM5MTIzOTEsInR5cGUiOiJyZWZyZXNoIn0.5DQOaSOO8e80m4f2fY6K2VC_VamULjxIQvij7riGC-8'}
]

def get_fromDB_refresh_token(username: str):
    for token in REFRESH_TOKENS:
        if token.get('username') == username:
            return token[username]
    return None



if 'username' in REFRESH_TOKENS[0]:
    print("ninee")
print(REFRESH_TOKENS[0].get('username'), 1)
print(REFRESH_TOKENS[0]['username'], 2)

