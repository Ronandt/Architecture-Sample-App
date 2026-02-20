from fastapi import FastAPI
from fastapi_keycloak_middleware import KeycloakConfiguration
import jwt
import urllib.request
import json
import ssl
from shared.config import settings
from dotenv import load_dotenv
import os
class KeycloakAdapter:

    def __init__(
        self,
        server_url: str = settings.KEYCLOAK_URL,
        realm: str = settings.KEYCLOAK_REALM,
        client_id: str = settings.KEYCLOAK_CLIENT_ID,
        client_secret: str = settings.KEYCLOAK_CLIENT_SECRET,
        cert_filepath: str = settings.KEYCLOAK_CERT_FILEPATH,
    ):
        self.server_url = server_url
        self.realm = realm
        self.client_id = client_id
        self.client_secret = client_secret
        self.cert_filepath = cert_filepath


    def retrieve_public_key_from_cert(self, certs_url, context= None):
        with urllib.request.urlopen(certs_url, context=context) as response:
            certs = json.loads(response.read())
            public_key =  certs['public_key']
            if(public_key == None):
                raise Exception("No RS256 key found in Keycloak certs")
            formatted_key = "-----BEGIN PUBLIC KEY-----" + \
                            public_key + "-----END PUBLIC KEY-----"
        
            return formatted_key

    def get_public_key(self) -> str:
        realm = self.realm
        keycloak_url = self.server_url
        keycloak_ssl_cert = self.cert_filepath.strip() if self.cert_filepath != None else ""
        if (keycloak_url == "") or (realm == ""):
            raise ValueError(f"KEYCLOAK_URL or KEYCLOAK_REALM empty\nRealm: {len(realm)}, URL: {len(keycloak_url)}, SSLCert: {len(keycloak_ssl_cert)}")
        certs_url = f"{keycloak_url}/realms/{realm}"
        if (keycloak_ssl_cert == ""):
            print(f"WARNING: SSL CERT IS EMPTY. USE WITHOUT CERT FROM {keycloak_url}/realms/{realm}")
            return self.retrieve_public_key_from_cert(certs_url=certs_url)
        
        #Assume there's a valid cert here 
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.load_verify_locations(cadata=keycloak_ssl_cert)

        certs_url = f"{keycloak_url}/realms/{realm}"
        return self.retrieve_public_key_from_cert(certs_url=certs_url, context=context)
    
    def verify_user_token(self, user_token: str, public_key: str) -> bool:

        try:
            if user_token is None:
                return False, {}
            
            bearer_header = user_token.split(" ")[1]
            
            # TODO: remove in prod
            print("===== BEARER HEADER =====\n")
            print(bearer_header)
            print("===== END BEARER HEADER =====\n")
            access_token_json = jwt.decode(bearer_header, public_key, algorithms=["RS256"], audience="account")
            
            # TODO: remove in prod
            print("\n===== ACCESS TOKEN =====")
            print(access_token_json)
            print("===== ACCESS TOKEN =====\n")

            return True, access_token_json
        
        except Exception as e:
            print(f"Token verification failed: {e}")

            return False, {}