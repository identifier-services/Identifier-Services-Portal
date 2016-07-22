class BaseAgaveObject(object):
    """
    Required Parameter:
        api_client          # AgavePy client
    Optional Parameters:
        None
    """
    def __init__(self, api_client, *args, **kwargs):
        # TODO: if type(api_client) is not agavepy.agave.Agave: raise Exception()
        self._api_client = api_client
