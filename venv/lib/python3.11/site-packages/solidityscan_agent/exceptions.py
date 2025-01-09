from loguru import logger

from solidityscan_agent.lang import ErrorLanguageMapper

class TokenNotFound(Exception):
    @staticmethod
    def get_err_code():
        err_code = "ERR_1002"
        return err_code

    @staticmethod
    def get_message():
        message = f"token not found or empty"
        return message

    def __init__(self, *args: object) -> None:
        err_payload = {"message": TokenNotFound.get_message(), "err_code": TokenNotFound.get_err_code()}
        err_payload = ErrorLanguageMapper().translate(err_payload)

        super().__init__(err_payload)

class ScanFailed(Exception):
    def __init__(self, err_payload={"status": "failed", "message": "internal server error"}) -> None:
        err_payload = ErrorLanguageMapper().translate(err_payload)

        super().__init__(err_payload)

class ReportGenerationFailed(Exception):
    def __init__(self, err_payload={"status": "failed", "message": "internal server error"}) -> None:
        err_payload = ErrorLanguageMapper().translate(err_payload)

        super().__init__(err_payload)

class HostNotReachable(Exception):
    @staticmethod
    def get_err_code():
        err_code = "ERR_1001"
        return err_code

    @staticmethod
    def get_message():
        message = f"host not reachable at the moment"
        return message

    def __init__(self) -> None:
        err_payload = {
            "message": HostNotReachable.get_message(),
            "err_code": HostNotReachable.get_err_code(),
        }
        err_payload = ErrorLanguageMapper().translate(err_payload)

        super().__init__(err_payload)
