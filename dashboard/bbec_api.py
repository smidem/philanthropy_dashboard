from inspect import cleandoc
from typing import Optional, Tuple
from jinja2 import Environment, FileSystemLoader, select_autoescape
from functools import wraps
import xmltodict
from requests.auth import HTTPBasicAuth
from requests import Session
import os

# TODO: Put these in a database or separate file once more of them are built out
bizops_endpoints = {
    'constituent_search': (
        '/searchlists', '/23c5c603-d7d8-4106-aecc-65392b563887'
    ),
    'batch_template_search': (
        '/searchlists', '/0242f3f0-5e16-4c35-9a56-ad76ed4b71d7'
    ),
    'create_cc_batch': (
        '/recordadds', '/85e824df-ea01-4ad0-9714-9893b8eeb238'
    ),
}

env = Environment(loader=FileSystemLoader('dashboard/templates'),
                  autoescape=select_autoescape(['html', 'xml']),
                  trim_blocks=False)


# TODO: Make some of these functions accessible by command line.
def render_template(template, **kwargs):
    template = env.get_template(template)
    return template.render(**kwargs)


def create_session(db_alias: str) -> Session:
    # TODO: Add docstring
    session = Session()
    if db_alias == 'production' or db_alias == 'prod':
        username = os.getenv('BBEC_PROD_USER')
        password = os.getenv('BBEC_PROD_PASS')
    elif db_alias == 'test':
        username = os.getenv('BBEC_TEST_USER')
        password = os.getenv('BBEC_TEST_PASS')
    else:
        msg = f"""Only "production", "prod", and "test" are acceptable
            options for the db_alias parameter. Option "{db_alias}" is not
            currently supported at this time.
            """
        msg = cleandoc(msg)
        raise ValueError(msg)
    session.auth = HTTPBasicAuth(username, password)
    return session


# This sets the database to either test or production.
def set_db(db_alias: str) -> Optional[Tuple[str, str, str]]:
    # TODO: Add docstring.
    host: str = ''
    db_id: str = ''
    db_name_url: str = ''
    db_name: str = ''

    if db_alias == 'production' or db_alias == 'prod':
        host = 'https://bbisec12pro.blackbaudhosting.com'
        db_id = '/4249COL_fa341b46-12a4-4119-a334-8379e2e59d29'
        db_name_url = '/db%5B4249COL%5D'
        db_name = '4249COL'

    elif db_alias == 'test':
        host = 'https://bbisrig08stg.blackbaudhosting.com'
        db_id = '/4249COLS_1e3519e9-f75b-4a44-a726-9fe5117a77fb'
        db_name_url = '/db%5B4249COLS%5D'
        db_name = '4249COLS'

    else:
        msg = f"""Only "production", "prod", and "test" are acceptable
        options for the db_alias parameter. Option "{db_alias}" is not
        currently supported at this time.
        """
        msg = cleandoc(msg)
        raise ValueError(msg)

    valid: bool = all([host, db_id, db_name_url, db_name])

    return host, db_id, db_name_url if valid else None


def set_headers(
        host: str, appfx: bool = False, action: str = None
) -> dict:
    # TODO: Add docstring.
    # Avoiding default mutable arguments
    action = '' or action
    # SOAPAction defaults
    appfx = 'Blackbaud.AppFx.WebService.API.1/'
    bizops = 'blackbaud_appfx_server_bizops/'
    # Supported actions
    appfx_actions = ['AdHocQueryGetIDByName', 'AdHocQueryProcess']
    bizops_actions = ['Search', 'SaveData', 'Ping']
    # Header template
    headers = {'Content-Type': 'text/xml; charset=utf-8',
               'Host': '',
               'SOAPAction': ''}

    # Verifying host argument
    test_host = set_db('test')[0].replace("https://", "")
    prod_host = set_db('production')[0].replace("https://", "")
    if host == test_host:
        headers.update({'Host': host})
    elif host == 'test':
        headers.update({'Host': test_host})
    elif host == prod_host:
        headers.update({'Host': host})
    elif host == 'production' or host == 'prod':
        headers.update({'Host': prod_host})
    else:
        msg = f"""Argument "{host}" for the host parameter is invalid.
        Please use either "test", "prod", or "production" to call
        set_db to set the host, or provide the host URL as a string
        beginning with "https://".
        """
        msg = cleandoc(msg)
        raise ValueError(msg)

    if appfx and action in appfx_actions:
        appfx_headers = {'SOAPAction': f'{appfx}{action}'}
        headers.update(appfx_headers)
        return headers
    elif appfx and action not in appfx_actions:
        msg = f"""Argument "{action}" is not a valid SOAPAction for the
        appfx API. Did you mean to set appfx to False? If not, please
        specify a valid appfx SOAPAction. The actions that are
        currently supported for appfx are:
        "AdHocQueryGetIDByName" and "AdHocQueryProcessRequest".
        """
        msg = cleandoc(msg)
        raise ValueError(msg)
    elif not appfx and action in bizops_actions:
        bizops_headers = {'SOAPAction': f'{bizops}{action}'}
        headers.update(bizops_headers)
        return headers
    elif not appfx and action not in bizops_actions:
        msg = f"""Argument "{action}" is not a valid SOAPAction for the
        bizops API. Did you mean to set appfx to True? If not, please
        specify a valid appfx SOAPAction. The actions that are
        currently supported for bizops are:
        {", ".join(bizops_actions[:-1])}, and {bizops_actions[-1]}.
        """
        msg = cleandoc(msg)
        raise ValueError(msg)


def get_endpoint(
        appfx: bool = False, db_alias: str = 'test',
        bizops_endpoint: str = None,
) -> str:
    # TODO: Add docstring.
    host, db_id, db_name_url = set_db(db_alias)
    db_url: str = host + db_id

    api: str = ''
    soap: str = '/soap.asmx'

    if appfx and bizops_endpoint is None:
        return f'{db_url}/appfxwebservice.asmx'

    elif not appfx and bizops_endpoint is not None:
        bizops = f'{db_url}/vpp/bizops'
        default = (None, None)
        # Unpack endpoint info and provide a default if unsuccessful.
        action, catalog_id = bizops_endpoints.get(bizops_endpoint, default)
        if action is not None and catalog_id is not None:
            return bizops + db_name_url + action + catalog_id + soap
        else:
            supported_options = list(bizops_endpoints.keys())
            msg = f"""There was an error retrieving a valid action or
            catalog_id from bizops_endpoints. You specified
            "{bizops_endpoint}" for the bizops_endpoint
            parameter. This option is not supported at this
            time. The only supported options are:
            {", ".join(supported_options[:-1])}, and {supported_options[-1]}.
            """
            msg = cleandoc(msg)
            raise ValueError(msg)

    elif appfx and bizops_endpoint is not None:
        msg = f"""The appfx and bizops_endpoint parameters are meant
        to be mutually exclusive. The appfx API is one endpoint with
        different services that can be accessed using different
        headers. The bizops API contains an endpoint for every
        available service. As a result, you can only use of these
        parameters at a time. You provided the argument "{appfx}" for
        the appfx parameter and you provided the argument
        "{bizops_endpoint}" for the bizops_endpoint parameter. Please
        remove the bizops_endpoint argument if appfx should be True or
        set appfx to False if you wish to provide a bizops_endpoint and
        try again.
        """
        msg = cleandoc(msg)
        raise ValueError(msg)

    elif not appfx and bizops_endpoint is None:
        msg = """You must provide an argument for
        either appfx or bizops_endpoint. No arguments were received for
        either parameter. Please set appfx to True or specify a
        bizops_endpoint and try again.
        """
        msg = cleandoc(msg)
        raise ValueError(msg)


def bbec(
        template: str, appfx: bool, action: str,
        db_alias: str, bizops_endpoint: str = None
):
    """Decorator function for API calls made to the various Blackbaud CRM
    endpoints. It currently supports BizOps and AppFxWebService endpoints.

    Positional arguments:
    template: str
        The name of the template to be used with this function. The
        path to templates should be set in loader argument of env. The
        template name must include the file extension. For instance,
        to use the id_by_name template, you must set template equal to
        'id_by_name.xml'.
    TODO: Add documentation for action parameter.
    action: str
        The name of the SOAPAction to perform. This can be found in the
        example templates for each endpoint and it varies slightly between
        AppFxWebService and BizOps templates. For example, the constituent
        search template at the BizOps endpoint has an action of 'Search'.
    TODO: Add documentation for bizops_endpoint parameter.
    """

    def actual_decorator(function):
        @wraps(function)
        def wrapper_function(*args, **kwargs):
            session = create_session(db_alias)
            params = {'url': get_endpoint(appfx=appfx, db_alias=db_alias,
                                          bizops_endpoint=bizops_endpoint),
                      'headers': set_headers(host=db_alias, appfx=appfx,
                                             action=action),
                      'data': render_template(template, **kwargs)}

            # Unpack our dictionary of parameters into the post request.
            res = session.post(**params)

            if res.status_code != 200:
                raise ConnectionError(
                    'No connection established. '
                    f'Received status code of {res.status_code}.'
                )

            xml = None
            try:
                xml = xmltodict.parse(res.text)
                xml = xml.get('soap:Envelope')
                xml = xml.get('soap:Body')
                xml = xml.get(f'{action}Reply')
            except xml.parsers.expat.ExpatError:
                print('No xml returned by the response.')
            except AttributeError:
                print('Response information in an unexpected format.')

            return function(*args, xml=xml, **kwargs)

        return wrapper_function

    return actual_decorator


@bbec(template='id_by_name.xml',
      appfx=True,
      action='AdHocQueryGetIDByName',
      db_alias='prod')
def get_query_id(db_id: str, name: str, xml: dict):
    """Requires db_id and name in order to populate the templates"""
    return xml.get('ID')


@bbec(template='run_query.xml',
      appfx=True,
      action='AdHocQueryProcess',
      db_alias='prod')
def run_query(
        query_id: str, max_rows: int, xml: dict, **kwargs
) -> Tuple[list, list]:
    # Using {} as default to allow chaining without AttributeErrors
    headers = xml.get('Output', {}).get('Fields', {}).get('f', {})
    headers = [row.get('@Name') for row in headers]
    data = xml.get('Output', {}).get('Rows', {}).get('r', {})
    if len(data) > 1:
        data = [row.get('Values', {}).get('v') for row in data]
    else:
        data = [data.get('Values', {}).get('v')]
    return headers, data
