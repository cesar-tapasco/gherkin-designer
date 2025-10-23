from datetime import datetime, timedelta
import json
import os
import re
from threading import Thread
import typing
from typing import TypedDict
import uuid
from config import ConfigDict
import httpx
from httpx import Response
from httpx._urls import URL
from httpx._types import (
  RequestContent,
  RequestData,
  RequestFiles,
  RequestExtensions,
  QueryParamTypes,
  HeaderTypes,
  CookieTypes,
  AuthTypes,
  TimeoutTypes,
)
from src.utils.core.query_jq import JSONQueryJQ
from src.utils.core.magic_response import MagicResponse
from src.utils.logger import get_logger
import allure
from curlify2 import Curlify

logger = get_logger("API")


class ApiOptions(TypedDict, total=False):
  """Options for configuring API request behavior.

  Example usage:
      # Create options dict with autocomplete support
      options: ApiOptions = {
          "add_headers": True,
      }

      # Use in API call
      response = api.get("/endpoint", options=options)
  """

  add_headers: bool


class APIX:
  def __init__(
    self,
    ctx: ConfigDict,
    base_url="",
  ):
    self.ctx = ctx
    self.config = ctx["config"]
    self.base_url = base_url
    self.default_options: ApiOptions = {
      "add_headers": True,
    }
    self.client = httpx.Client(base_url=self.base_url)

  def _merge_options(self, options: ApiOptions | None = None) -> ApiOptions:
    """Merge provided options with default options."""
    merged = self.default_options.copy()
    if options:
      merged.update(options)
    return merged


  def with_token_retry(
    self, func, options: ApiOptions | None = None, *args, **kwargs
  ) -> MagicResponse:
    merged_options = self._merge_options(options)

    res: Response = func(*args, **kwargs)

    try:
      request_body = res.request.content.decode("utf-8")
    except Exception:
      request_body = ""

    if merged_options.get("activate_logger", True):
      api_message = f"""
        Request URL: {res.url}
        Request Method: {res.request.method}
        Request Headers: {json.dumps(dict(res.request.headers))}
        Request Body: {request_body}
        Response Headers: {json.dumps(dict(res.headers))}
        Response Body: {res.text}
        Response Status: {res.status_code}
        Response Reason: {res.reason_phrase}
        Response Elapsed: {res.elapsed.microseconds}
      """

      api_message = api_message.replace("  ", "")
      logger.debug(api_message)

      allure.attach(
        api_message,
        name="API details",
        attachment_type=allure.attachment_type.TEXT,
      )

      # Emit a stable, frontend-friendly cURL line and network event for the webapp
      try:
        if os.environ.get("WEBAPP_CURL", "1") == "1":
          curl_cmd = Curlify(res.request).to_curl()
          print(f"WEBAPP_CURL {curl_cmd}")

          try:
            net_event = {
              "id": uuid.uuid4().hex,
              "method": res.request.method,
              "url": str(res.url),
              "status": res.status_code,
              "statusText": res.reason_phrase,
              "durationMs": int(getattr(res, "elapsed", timedelta()).total_seconds() * 1000),
              "requestHeaders": dict(res.request.headers),
              "responseHeaders": dict(res.headers),
              "requestBody": request_body,
              # res.text[:2000]
              "responseBodyPreview": res.text if isinstance(res.text, str) else "",
              "curl": curl_cmd,
            }
            print("WEBAPP_NET " + json.dumps(net_event, ensure_ascii=False))
          except Exception:
            pass
      except Exception:
        # Don't let curl generation break tests
        pass

    return self._magic(res)

  def request(
    self,
    method: str,
    url: URL | str,
    *,
    content: RequestContent | None = None,
    data: RequestData | None = None,
    files: RequestFiles | None = None,
    json: typing.Any | None = None,
    params: QueryParamTypes | None = None,
    headers: HeaderTypes | None = None,
    cookies: CookieTypes | None = None,
    auth: AuthTypes | None = None,
    follow_redirects: bool = True,
    timeout: TimeoutTypes | None = None,
    extensions: RequestExtensions | None = None,
    options: ApiOptions | None = None,
  ) -> MagicResponse:
    self.client.headers.clear()
    return self.with_token_retry(
      self.client.request,
      options=options,
      method=method,
      url=url,
      content=content,
      data=data,
      files=files,
      json=json,
      params=params,
      headers=headers,
      cookies=cookies,
      timeout=timeout,
      extensions=extensions,
      auth=auth,
      follow_redirects=follow_redirects,
    )

  def get(
    self,
    url: URL | str,
    *,
    params: QueryParamTypes | None = None,
    headers: HeaderTypes | None = None,
    cookies: CookieTypes | None = None,
    auth: AuthTypes | None = None,
    follow_redirects: bool = True,
    timeout: TimeoutTypes | None = None,
    extensions: RequestExtensions | None = None,
    options: ApiOptions | None = None,
  ) -> MagicResponse:
    self.client.headers.clear()
    return self.with_token_retry(
      self.client.get,
      options=options,
      url=url,
      params=params,
      headers=headers,
      cookies=cookies,
      auth=auth,
      follow_redirects=follow_redirects,
      timeout=timeout,
      extensions=extensions,
    )

  def post(
    self,
    url: URL | str,
    *,
    content: RequestContent | None = None,
    data: RequestData | None = None,
    files: RequestFiles | None = None,
    json: typing.Any | None = None,
    params: QueryParamTypes | None = None,
    headers: HeaderTypes | None = None,
    cookies: CookieTypes | None = None,
    auth: AuthTypes | None = None,
    follow_redirects: bool = True,
    timeout: TimeoutTypes | None = None,
    extensions: RequestExtensions | None = None,
    options: ApiOptions | None = None,
  ) -> MagicResponse:
    self.client.headers.clear()
    return self.with_token_retry(
      self.client.post,
      options=options,
      url=url,
      content=content,
      data=data,
      files=files,
      json=json,
      params=params,
      headers=headers,
      cookies=cookies,
      auth=auth,
      follow_redirects=follow_redirects,
      timeout=timeout,
      extensions=extensions,
    )

  def put(
    self,
    url: URL | str,
    *,
    content: RequestContent | None = None,
    data: RequestData | None = None,
    files: RequestFiles | None = None,
    json: typing.Any | None = None,
    params: QueryParamTypes | None = None,
    headers: HeaderTypes | None = None,
    cookies: CookieTypes | None = None,
    auth: AuthTypes | None = None,
    follow_redirects: bool = True,
    timeout: TimeoutTypes | None = None,
    extensions: RequestExtensions | None = None,
    options: ApiOptions | None = None,
  ) -> MagicResponse:
    self.client.headers.clear()
    return self.with_token_retry(
      self.client.put,
      options=options,
      url=url,
      content=content,
      data=data,
      files=files,
      json=json,
      params=params,
      headers=headers,
      cookies=cookies,
      auth=auth,
      follow_redirects=follow_redirects,
      timeout=timeout,
      extensions=extensions,
    )

  def delete(
    self,
    url: URL | str,
    *,
    params: QueryParamTypes | None = None,
    headers: HeaderTypes | None = None,
    cookies: CookieTypes | None = None,
    auth: AuthTypes | None = None,
    follow_redirects: bool = True,
    timeout: TimeoutTypes | None = None,
    extensions: RequestExtensions | None = None,
    options: ApiOptions | None = None,
  ) -> MagicResponse:
    self.client.headers.clear()
    return self.with_token_retry(
      self.client.delete,
      options=options,
      url=url,
      params=params,
      headers=headers,
      cookies=cookies,
      auth=auth,
      follow_redirects=follow_redirects,
      timeout=timeout,
      extensions=extensions,
    )

  def head(
    self,
    url: URL | str,
    *,
    params: QueryParamTypes | None = None,
    headers: HeaderTypes | None = None,
    cookies: CookieTypes | None = None,
    auth: AuthTypes | None = None,
    follow_redirects: bool = True,
    timeout: TimeoutTypes | None = None,
    extensions: RequestExtensions | None = None,
    options: ApiOptions | None = None,
  ) -> MagicResponse:
    self.client.headers.clear()
    return self.with_token_retry(
      self.client.head,
      options=options,
      url=url,
      params=params,
      headers=headers,
      cookies=cookies,
      auth=auth,
      follow_redirects=follow_redirects,
      timeout=timeout,
      extensions=extensions,
    )

  def patch(
    self,
    url: URL | str,
    *,
    content: RequestContent | None = None,
    data: RequestData | None = None,
    files: RequestFiles | None = None,
    json: typing.Any | None = None,
    params: QueryParamTypes | None = None,
    headers: HeaderTypes | None = None,
    cookies: CookieTypes | None = None,
    auth: AuthTypes | None = None,
    follow_redirects: bool = True,
    timeout: TimeoutTypes | None = None,
    extensions: RequestExtensions | None = None,
    options: ApiOptions | None = None,
  ) -> MagicResponse:
    self.client.headers.clear()
    return self.with_token_retry(
      self.client.patch,
      options=options,
      url=url,
      content=content,
      data=data,
      files=files,
      json=json,
      params=params,
      headers=headers,
      cookies=cookies,
      auth=auth,
      follow_redirects=follow_redirects,
      timeout=timeout,
      extensions=extensions,
    )

  def _magic(self, response: Response):
    try:
      json = response.json()
    except Exception:
      json = {}
    return MagicResponse(
      res=response,
      status=response.status_code,
      status_text=response.reason_phrase,
      json=json,
      jq=JSONQueryJQ(json),
    )
