import logging
from typing import Optional

from on_rails import Result, ValidationError, def_result

from docker_entrypoint._libs.docker_environments import DockerEnvironments
from docker_entrypoint._libs.ResultDetails.FailResult import FailResult

D8_Recommended_OPTIONS = {
    '--harmony': 'Enables support for some of the experimental ES6 features that are not yet fully standardized',
    '--allow-natives-syntax': 'Enables the use of V8-specific syntax in JavaScript code',
    '--trace-opt': 'Enables logging of V8\'s optimization process',
    '--print-bytecode': 'Prints the generated bytecode for JavaScript functions',
    '--print-opt-code': 'Prints the generated optimized machine code for JavaScript functions',
    '--trace': 'Enables detailed logging of V8 internals',
    '--log-timer-events': 'Enables logging of timer events',
    '--log-gc': 'Enables logging of garbage collection events',
    '--prof': 'Enables CPU profiling',
    '--trace-deopt': 'Enables logging of V8\'s deoptimization process',
    '--trace-ic': 'Enables logging of inline caching events',
}


@def_result()
def log_result(logger: logging.Logger, result: Result) -> Result:
    """
    Logs unexpected errors. Results that isn't success and isn't type of FailResult

    :param logger: The logger parameter is an instance of the logging.Logger class, which is used for
    logging messages in the application.
    :type logger: logging.Logger

    :param result: The `result` parameter is an instance of the `Result` class
    :type result: Result
    """

    return result \
        .on_success_operate_when(lambda value: value is not None, lambda value: logger.info(value)) \
        .on_fail(lambda prev_result: log_error(logger, prev_result))


@def_result()
def log_error(logger: logging.Logger, fail_result: Result) -> Result:
    """
    This function logs an error message and returns a support message if a failure result is encountered.

    :param logger: The logger parameter is an instance of the logging.Logger class.
    :type logger: logging.Logger

    :param fail_result: `fail_result` is an instance of the `Result` class that represents a failed operation.
    It contains information about the failure, such as an error message or exception
    :type fail_result: Result
    """

    if fail_result.success:
        return Result.fail(detail=ValidationError(message="Expected failure result but got success result!",
                                                  more_data=[fail_result]))

    logger.error(f"An error occurred:\n{repr(fail_result)}\n")
    return get_support_message() \
        .on_success(lambda support_message:
                    logger.info(f"Please report this error to help others who use this program.\n{support_message}")
                    )


@def_result()
def get_support_message() -> Result[str]:
    """
    This function returns a support message based on the available Docker environments.

    :return: A Result object containing a string message.
    """

    return DockerEnvironments.get_environments() \
        .on_success(lambda environments: _get_support_message(environments))


@def_result()
def _get_support_message(environments: DockerEnvironments) -> Result[str]:
    return Result.ok(value="Support:\n"
                           f"\tMaintainer: {environments.maintainer}\n"
                           f"\tDocker Version: {environments.docker_version}\n"
                           f"\tBuild Date: {environments.build_date}\n"
                           f"\tRepository: {environments.vcs_url}\n"
                           f"\tReport Bug: {environments.bug_report}\n"
                     )


@def_result()
def log_class_properties(logger: logging.Logger, log_level: int, class_object: object,
                         message: Optional[str] = None) -> Result:
    """
    Logs the properties of a given class object at the given level.

    :param logger: The logger parameter is an instance of the logging.Logger class
    :type logger: logging.Logger

    :param log_level: Level of log like DEBUG, INFO, etc.
    :type log_level: int

    :param class_object: The `class_object` parameter is an object of a class whose properties are to be logged.
    :type class_object: object

    :param message: The `message` parameter is an optional string that can be passed to the function as a
    message to be included in the log output.
    :type message: Optional[str]

    :return: an instance of the `Result` class, which is created by calling the `ok()` method. This indicates that the
    function has completed successfully without any errors.
    """

    result = f"{message}:\n" if message else ""
    for key, value in vars(class_object).items():
        result += f"\t{key}: {value}\n"
    logger.log(log_level, result)
    return Result.ok()


@def_result()
def convert_code_to_result(code: int) -> Result:
    """
    The function converts a code to a Result object, returning an OK result if the code is 0 and a FailResult object
    otherwise.

    :param code: an integer representing the result code of an operation
    :type code: int
    """

    if code == 0:
        return Result.ok()
    return Result.fail(FailResult(code=code))
