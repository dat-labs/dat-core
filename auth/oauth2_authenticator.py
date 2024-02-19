# Base class for Oauth2 authenticator
from typing import Mapping, Dict, List, Any

class BaseOauth2Authenticator:
    """
    Base class for all Oauth2 authenticators
    """
    def __init__(self,
            client_id: str ,
            client_secret: str,
            token_refresh_endpoint: str,
            token_refresh_grant_type: str = 'refresh_token',
            scopes: List[str] = None,
            access_token_name: str = 'access_token',
            refresh_token_name: str = 'refresh_token',
            expires_in_name: str = 'expires_in',
            token_exchange_endpoint: str = None,
            token_exchange_grant_type: str = 'authorization_code',
            scopes_delimiter: str = ' ', # Could be a "," also
    ) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._token_refresh_endpoint = token_refresh_endpoint
        self._token_refresh_grant_type = token_refresh_grant_type
        self._scopes = scopes
        self._access_token_name = access_token_name
        self._refresh_token_name = refresh_token_name
        self._expires_in_name = expires_in_name
        self._token_exchange_endpoint = token_exchange_endpoint
        self._token_exchange_grant_type = token_exchange_grant_type
        self._scopes_delimiter = scopes_delimiter

    @property
    def access_token(self) -> str:
        return self._access_token

    @access_token.setter
    def access_token(self, value: str):
        self._access_token = value
    
    def build_token_exchange_request_body(self, code: str) -> Mapping[str, Any]:
        """
        Returns the request body for OAuth2 flow

        Returns:
            Mapping[str, Any]: request body
        """
        payload = {
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'grant_type': self._grant_type_authorization_code,
            'redirect_uri': self._redirect_uri,
            'code': code
        }
        return payload
    
    def get_oauth_url(self, url_template, **optional_kwargs) -> str:
        """
        Generate oauth url

        Args:
            url_template (str): Template for OAuth URL.
            E.g https://domain.com?redirect_uri={redirect_uri}&client_id={client_id}&state={state}

        Returns:
            str: Based on the above example, it might return something like:
            https://domain.com?redirect_uri=https://my-api.domain.com&client_id=xxxxxxxxx&state=123768
        """
        url_format_payload = {
            'client_id': self._client_id,
            'redirect_url': self._redirect_uri,
            'scopes': self._scopes_delimiter.join(self._scopes),
        }
        url_format_payload.update(optional_kwargs)
        url = url_template.format(**url_format_payload)
        return url


    

