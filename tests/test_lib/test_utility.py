import logging
import unittest

from on_rails import (Result, ValidationError, assert_error_detail,
                      assert_result, assert_result_with_type)

from docker_entrypoint._libs.ResultDetails.FailResult import FailResult
from docker_entrypoint._libs.utility import (class_properties_to_str,
                                             get_support_message, log_error,
                                             log_result)
from tests._helpers import get_logger


class TestUtility(unittest.TestCase):
    # region log_result

    def test_log_result_not_give_logger(self):
        result = log_result(None, None)

        assert_result_with_type(self, result, expected_success=False, expected_detail_type=ValidationError)
        assert_error_detail(self, result.detail, expected_title="One or more validation errors occurred",
                            expected_message="The logger is required.", expected_code=400)

    def test_log_result_give_none_result(self):
        result = log_result(logging.getLogger(), None)

        assert_result_with_type(self, result, expected_success=False, expected_detail_type=ValidationError)
        assert_error_detail(self, result.detail, expected_title="The result parameter is not valid.",
                            expected_message="The result parameter is required and must be an instance of Result.",
                            expected_code=400)

    def test_log_result_give_success(self):
        logger, logging_stream = get_logger()

        result = Result.ok()
        func_result = log_result(logger, result)
        self.assertEqual(result, func_result)
        self.assertEqual("", logging_stream.getvalue())

    def test_log_result_give_success_with_value(self):
        logger, logging_stream = get_logger()

        func_result = log_result(logger, Result.ok("value"))
        assert_result(self, target_result=func_result, expected_success=True)
        self.assertEqual("[INFO] value\n", logging_stream.getvalue())

    def test_log_result_expected_fail(self):
        logger, logging_stream = get_logger()

        func_result = log_result(logger, Result.fail(FailResult(code=5, message="message")))
        assert_result(self, target_result=func_result, expected_success=False)
        self.assertEqual("[ERROR] Operation failed with code 5.\nmessage\n\n", logging_stream.getvalue())

    def test_log_result_unexpected_fail(self):
        logger, logging_stream = get_logger()

        func_result = log_result(logger, Result.fail(ValidationError()))
        assert_result_with_type(self, target_result=func_result,
                                expected_success=False, expected_detail_type=ValidationError)
        self.assertIn("Title: One or more validation errors occurred\nCode: 400\nStack trace:",
                      logging_stream.getvalue())
        self.assertIn("[INFO] Please report this error to help others who use this program.\n"
                      "Support:\n"
                      "\tMaintainer: No Data!\n"
                      "\tDocker Version: latest\n"
                      "\tBuild Date: No Data!\n"
                      "\tRepository: No Data!\n"
                      "\tReport Bug: No Data!",
                      logging_stream.getvalue())

    # endregion

    # region log_error

    def test_log_error_not_give_logger(self):
        result = log_error(None, None)

        assert_result_with_type(self, result, expected_success=False, expected_detail_type=ValidationError)
        assert_error_detail(self, result.detail, expected_title="One or more validation errors occurred",
                            expected_message="The logger is required.", expected_code=400)

    def test_log_error_give_none_result(self):
        result = log_error(logging.getLogger(), None)

        assert_result_with_type(self, result, expected_success=False, expected_detail_type=ValidationError)
        assert_error_detail(self, result.detail, expected_title="The result parameter is not valid.",
                            expected_message="The result parameter is required and must be an instance of Result.",
                            expected_code=400)

    def test_log_error_give_success_result(self):
        result = Result.ok()
        func_result = log_error(logging.getLogger(), result)

        assert_result_with_type(self, func_result, expected_success=False, expected_detail_type=ValidationError)
        assert_error_detail(self, func_result.detail, expected_title="One or more validation errors occurred",
                            expected_message="Expected failure result but got success result!",
                            expected_code=400, expected_more_data=[result])

    def test_log_error(self):
        logger, logging_stream = get_logger()

        func_result = log_error(logger, Result.fail(ValidationError()))
        assert_result(self, target_result=func_result, expected_success=True)

        self.assertIn("[ERROR] An error occurred:\n"
                      "Title: One or more validation errors occurred\n"
                      "Code: 400\n"
                      "Stack trace:",
                      logging_stream.getvalue())
        self.assertIn("[INFO] Please report this error to help others who use this program.\n"
                      "Support:\n"
                      "\tMaintainer: No Data!\n"
                      "\tDocker Version: latest\n"
                      "\tBuild Date: No Data!\n"
                      "\tRepository: No Data!\n"
                      "\tReport Bug: No Data!",
                      logging_stream.getvalue())
        print(logging_stream.getvalue())

    # endregion

    # region get_support_message

    def test_get_support_message(self):
        result = get_support_message()
        assert_result(self, target_result=result, expected_success=True,
                      expected_value="Support:\n"
                                     "\tMaintainer: No Data!\n"
                                     "\tDocker Version: latest\n"
                                     "\tBuild Date: No Data!\n"
                                     "\tRepository: No Data!\n"
                                     "\tReport Bug: No Data!\n")

    # endregion

    # region class_properties_to_str

    def test_class_properties_to_str_give_none(self):
        result = class_properties_to_str(None)

        assert_result_with_type(self, result, expected_success=False, expected_detail_type=ValidationError)
        assert_error_detail(self, result.detail, expected_title="One or more validation errors occurred",
                            expected_message="The class object is required.",
                            expected_code=400)

    def test_class_properties_to_str_give_invalid_message(self):
        result = class_properties_to_str(self, ['not string'])

        assert_result_with_type(self, result, expected_success=False, expected_detail_type=ValidationError)
        assert_error_detail(self, result.detail, expected_title="One or more validation errors occurred",
                            expected_message="The message must be a string.",
                            expected_code=400)

    def test_class_properties_to_str_without_msg(self):
        class Fake:
            def __init__(self):
                self.prop1 = "prop1"
                self.prop2 = "prop2"

        result = class_properties_to_str(Fake())
        assert_result(self, result, expected_success=True, expected_value="prop1: prop1\nprop2: prop2\n")

        result = class_properties_to_str(Fake(), title="   ")
        assert_result(self, result, expected_success=True, expected_value="prop1: prop1\nprop2: prop2\n")

    def test_class_properties_to_str_with_msg(self):
        class Fake:
            def __init__(self):
                self.prop1 = "prop1"
                self.prop2 = "prop2"

        result = class_properties_to_str(Fake(), title="message")
        assert_result(self, result, expected_success=True, expected_value="message:\n"
                                                                          "\tprop1: prop1\n"
                                                                          "\tprop2: prop2\n")

    # endregion


if __name__ == '__main__':
    unittest.main()
