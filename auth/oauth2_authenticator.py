# Base class for Oauth2 authenticator
from typing import Mapping, Tuple, List, Any
import requests
import pendulum


class BaseOauth2Authenticator:
    """
    Base class for all Oauth2 authenticators.

    Args:
        client_id (str): The client ID for OAuth authentication.
        client_secret (str): The client secret for OAuth authentication.
        token_refresh_endpoint (str): The endpoint for refreshing access tokens.
        token_refresh_grant_type (str, optional): The grant type for token refresh. Defaults to 'refresh_token'.
        scopes (List[str], optional): The list of scopes for the OAuth token. Defaults to None.
        redirect_uri (str, optional): The URI to redirect after authentication. Defaults to None.
        access_token_name (str, optional): The name of the access token parameter. Defaults to 'access_token'.
        refresh_token_name (str, optional): The name of the refresh token parameter. Defaults to 'refresh_token'.
        expires_in_name (str, optional): The name of the parameter indicating token expiration time. Defaults to 'expires_in'.
        token_exchange_endpoint (str, optional): The endpoint for exchanging tokens. Defaults to None.
        token_exchange_grant_type (str, optional): The grant type for token exchange. Defaults to 'authorization_code'.
        scopes_delimiter (str, optional): The delimiter used for separating scopes. Defaults to ','.
    """

    def __init__(self,
                 client_id: str,
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
                 scopes_delimiter: str = ',',  # Could be a " " also
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
        self._access_token = None
        self._refresh_token = None
        self._token_expiry_date = pendulum.now().subtract(days=1)

    @property
    def access_token(self) -> str:
        return self._access_token

    @access_token.setter
    def access_token(self, value) -> None:
        self._access_token = value

    @property
    def refresh_token(self) -> str:
        return self._refresh_token

    @refresh_token.setter
    def refresh_token(self, value) -> None:
        self._refresh_token = value

    def get_auth_header(self) -> Mapping[str, Any]:
        return {"Authorization": f"Bearer {self.get_access_token()}"}

    def is_token_expired(self) -> bool:
        """
        Checks if the access token has expired.

        Returns:
            bool: True if the access token has expired, False otherwise.
        """
        return pendulum.now() > self._token_expiry_date

    def get_access_token(self) -> str:
        """
        Retrieves the access token, refreshing it if necessary.

        If the current access token is expired, this method refreshes it using the token refresh mechanism
        provided by the OAuth2 provider. Otherwise, it returns the current access token.

        Returns:
            str: The current access token.

        Raises:
            Exception: If the access token retrieval or refresh fails.
        """
        if self.is_token_expired():
            access_token, expires_in = self.token_refresh()
            self.access_token = access_token
            self.set_token_expiry_date(expires_in=expires_in)
        return self.access_token

    def set_token_expiry_date(self, expires_in) -> None:
        self._token_expiry_date = pendulum.now().add(seconds=expires_in)

    def _build_token_exchange_request_body(self, auth_code: str) -> Mapping[str, Any]:
        """
        Builds the request body for token exchange.

        Args:
            auth_code (str): The authorization code obtained from the OAuth2 provider.

        Returns:
            Mapping[str, Any]: A dictionary containing the request parameters for token exchange.
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
        Builds the request body for refreshing the access token.

        Returns:
            Mapping[str, Any]: A dictionary containing the request parameters for token refresh.
        """
        payload = {
            'client_id': self._client_id,
            'grant_type': self._token_refresh_grant_type,
            'refresh_token': self.refresh_token
        }
        if self._scopes:
            payload['scopes'] = self._scopes

        return payload

    def exchange_token(self, auth_code: str, request_method: str = 'POST') -> Tuple[Any]:
        """
        Exchanges an authorization code for access and refresh tokens.

        Args:
            auth_code (str): The authorization code obtained from the OAuth2 provider.
            request_method (str, optional): The HTTP method to use for the token exchange request. Defaults to 'POST'.

        Returns:
            Tuple[Any]: A tuple containing the access token, refresh token, and expiration time.

        Raises:
            Exception: If the token exchange fails.
        """
        payload = self._build_token_exchange_request_body(auth_code)
        res = requests.request(
            method=request_method, url=self._token_exchange_endpoint, json=payload)
        if res.status_code == 200:
            resp_json = res.json()
            return (
                resp_json.get(self._access_token_name),
                resp_json.get(self._refresh_token_name),
                resp_json.get(self._expires_in_name)
            )
        else:
            print(res.text)
            # TODO: Raise specific exception
            raise Exception('Failed to exchange token')

    def token_refresh(self, request_method: str = 'POST') -> Tuple[Any]:
        """
        Refreshes the access token using the refresh token.

        Args:
            request_method (str, optional): The HTTP method to use for the token refresh request. Defaults to 'POST'.

        Returns:
            Tuple[Any]: A tuple containing the refreshed access token and its expiration time.

        Raises:
            Exception: If the token refresh fails.
        """
        payload = self._build_token_refresh_request_body()
        res = requests.request(
            method=request_method, url=self._token_exchange_endpoint, json=payload)
        if res.status_code == 200:
            resp_json = res.json()
            return (
                resp_json.get(self._access_token_name),
                resp_json.get(self._expires_in_name)
            )
        else:
            # TODO: Raise specific exception
            raise Exception('Failed to exchange token')

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
        Initiates the OAuth2 authorization flow.

        This method generates an OAuth2 URL based on the provided template, prompts the user to open it in their
        web browser, and input the authorization code returned by the OAuth2 provider. It then exchanges the
        authorization code for access and refresh tokens, updating the instance's access and refresh tokens
        accordingly.

        Args:
            oauth2_url_template (str): The template URL for OAuth2 authorization, typically containing placeholders
                for client ID, redirect URI, and scopes.

        Returns:
            None

        Raises:
            Exception: If the OAuth2 authorization or token exchange fails.
        """
        oauth_url = self._get_oauth2_url(url_template=oauth2_url_template)
        message = f"""Please open {oauth_url} in your Web Browser
        and paste the authorization code here.
        """
        auth_code = input(message)
        access_token, refresh_token, expires_in = self.exchange_token(
            auth_code=auth_code)
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.set_token_expiry_date(expires_in=expires_in)
