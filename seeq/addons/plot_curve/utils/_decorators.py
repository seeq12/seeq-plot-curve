from threading import Thread
from mixpanel import Mixpanel, MixpanelException
import pandas as pd
from os import path
from seeq import spy
import threading
import json
import configparser
from pathlib import Path
import time
from functools import wraps

# Decorators


def threaded(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        thread = Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper


def tracker(user_id=None, project=None):
    def decorator(wrapped_function):
        @wraps(wrapped_function)
        def wrapper(*args, **kwargs):
            exceptions_raised = None
            execution_time = None
            try:
                start = time.time()
                result = wrapped_function(*args, **kwargs)
                end = time.time()
                execution_time = end - start
                return result
            except Exception as e:
                exceptions_raised = e
                raise e
            finally:
                _thread = threading.Thread(target=log_to_mixpanel,
                                           args=(wrapped_function, user_id, project,
                                                 exceptions_raised, execution_time, args),
                                           kwargs=kwargs)
                _thread.start()

        return wrapper
    return decorator


# Supporting functions


def get_mixpanel_key():
    """
    Reads the logger id for mixpanel from the config file.

    Returns
    -------
    str
        value of logger_id if it exists else None

    """
    try:
        config_file = f'{Path(__file__).parent.parent.resolve()}\config.ini'
        config = configparser.ConfigParser(allow_no_value=True)
        config.read(config_file)
        return config.get('SEEQ', 'mixpanel_key')
    except Exception as e:
        return None


def is_jsonable(x):
    """
    Determine if an input can be written as a json.
    Parameters
    ----------
    x : any

    Returns
    -------
    bool
        True if x can be serialized, else False

    """
    try:
        json.dumps(x)
        return True
    except TypeError:
        return False


def log_to_mixpanel(fun, user_id, project, exceptions_raised, execution_time, *args, **kwargs):
    """
    This function is used by the tracker decorator to log function calls.  If
    mixpanel is installed and a key is provided, it will log the function calls to mixpanel.
    Otherwise, function calls will be logged locally to a log file.

    Parameters
    ----------
    fun : func
        input function from decorator
    user_id : str
        user id
    project : str
        name of project
    exceptions_raised : Exception
        exception raised by function
    execution_time : float
        time to execute function
    Returns
    -------

    """
    _user_id = user_id if user_id is not None else spy.client.host

    _args = []
    for x in args:
        if not is_jsonable(x):
            if type(x).__repr__ is not object.__repr__:
                _args.append(str(x))
            else:
                _args.append(f'{type(x)}')
        else:
            _args.append(x)

    _kwargs = {}
    for key, value in kwargs.items():
        if not is_jsonable(value):
            if type(value).__repr__ is not object.__repr__:
                kwargs[key] = str(value)
            else:
                kwargs[key] = f'{type(value)}'
        else:
            _kwargs[key] = value

    mixpanel_id = get_mixpanel_key()
    mixpanel = Mixpanel(mixpanel_id) if mixpanel_id is not None else None

    _track = {
        'seeq_user_id': spy.user.id,
        'executed_at': str(pd.Timestamp.now()),
        'name': f'{project}:{fun.__name__}',
        'exceptions': exceptions_raised,
        'execution_time': f'ExecutionTime:{execution_time}',
        'args': _args,
        'kwargs': _kwargs
    }

    if mixpanel is not None:
        try:
            mixpanel.track(_user_id, fun.__name__, _track)
            mixpanel_enabled = True
        except MixpanelException as e:
            _track['mixpanel_exception'] = str(e)
            mixpanel_enabled = False

    else:
        mixpanel_enabled = False
        _track['mixpanel_exception'] = "No mixpanel key could be found in the project config.ini"

    if not mixpanel_enabled:
        _track['user_id'] = user_id
        _track['project'] = fun.__name__
        _df = pd.DataFrame([_track])
        _include_header = not path.exists('./plot_curve.log')

        # Create a ` separated file
        # ` was decided as a separator because there are a lot of inputs that use commas (,)
        # example read to pandas:
        # pd.read_csv('logger.log', sep='`', names=['seeq_user_id','name','args','kwargs','user_id','project'])

        _df.to_csv('./plot_curve.log', sep="`", mode='a',
                   header=_include_header, index=False)



