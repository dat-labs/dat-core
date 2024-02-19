# Base class for Oauth2 authenticator
from typing import Mapping, Dict, List, Any
import requests
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
            redirect_uri: str = None,
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
        self._scopes = scopes if scopes is not None else []
        self._redirect_uri = redirect_uri
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
    
    @property
    def refresh_token(self) -> str:
        return self._refresh_token

    @access_token.setter
    def refresh_token(self, value: str):
        self._refresh_token = value
    
    def _build_token_exchange_request_body(self, auth_code: str) -> Mapping[str, Any]:
        """
        Returns the request body for OAuth2 flow

        Returns:
            Mapping[str, Any]: request body
        """
        payload = {
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'grant_type': self._token_exchange_grant_type,
            'redirect_uri': self._redirect_uri,
            'code': auth_code
        }
        return payload
    
    def _build_token_refresh_request_body(self) -> Mapping[str, Any]:
        """
        Returns the request body for token refresh

        Returns:
            Mapping[str, Any]: request body
        """
        payload = {
            'client_id': self._client_id,
            'grant_type': self._token_refresh_grant_type,
            'refresh_token': self._refresh_token
        }
        return payload
    
    def exchange_token(self, auth_code:str, request_method: str='POST') -> Mapping[str, Any]:
        """
        Use the auth_code to exchange it for refresh_token

        Args:
            auth_code (str): authorization code from oauth2 web flow

        Returns:
            Mapping[str, Any]: response from token exchange
        """
        payload = self._build_token_exchange_request_body(auth_code)
        res = requests.request(
            method=request_method, url=self._token_exchange_endpoint, json=payload)
        if res.status_code == 200:
            return res.json()
        else:
            print(res.text)
            raise Exception('Failed to exchange token') # TODO: Raise specific exception
    
    def token_refresh(self, request_method: str='POST') -> Mapping[str, Any]:
        """
        Use the auth_code to exchange it for refresh_token

        Args:
            auth_code (str): authorization code from oauth2 web flow

        Returns:
            Mapping[str, Any]: response from token exchange
        """
        payload = self._build_token_refresh_request_body()
        res = requests.request(
            method=request_method, url=self._token_exchange_endpoint, json=payload)
        if res.status_code == 200:
            resp_json = res.json()
            self.access_token(resp_json.get(self._access_token_name))
        else:
            raise Exception('Failed to exchange token') # TODO: Raise specific exception
    
    def _get_oauth2_url(self, url_template, **optional_kwargs) -> str:
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
            'redirect_uri': self._redirect_uri,
            'scope': self._scopes_delimiter.join(self._scopes),
        }
        url_format_payload.update(optional_kwargs)
        url = url_template.format(**url_format_payload)
        return url
    
    def run_oauth2_webflow(self, oauth2_url_template) -> None:
        """
        Call this to start OAuth2 flow
        """
        oauth_url = self._get_oauth2_url(url_template=oauth2_url_template)
        message = f"""Please open {oauth_url} in your Web Browser
        and paste the authorization code here.
        """
        auth_code = input(message)
        auth_response = self.exchange_token(auth_code=auth_code)
        if auth_response:
            self.access_token(auth_response.get(self._access_token_name))
            self.refresh_token(auth_response.get(self._refresh_token_name))





    

