"""
def authenticate_before_request(keycloakAdapter: KeycloakAdapter):
        if request.method != 'OPTIONS':
            user_token = request.headers.get('X-User-Token')
            verification_result = verify_user_token(user_token, public_key)

            print("\n===== REQUEST =====")
            print(request)
            print(request.headers)
            print("===== REQUEST END =====\n")

            if not verification_result[0]:
                print(f"Invalid or missing user token: ${user_token}")
                return {"msg": "Invalid or missing user token"}, 401
            #request.headers.add('user-info', 'true')
            request.environ['user-info'] = verification_result[1]
            """