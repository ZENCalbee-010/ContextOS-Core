from contextos.cli.output import safe_echo


class StrictCp1252Stream:
    encoding = "cp1252"

    def __init__(self) -> None:
        self.value = ""

    def write(self, text: str) -> int:
        text.encode(self.encoding)
        self.value += text
        return len(text)

    def flush(self) -> None:
        return None


def test_safe_echo_replaces_terminal_unsupported_unicode_only_in_output():
    stream = StrictCp1252Stream()
    message = "\ufeffUnicode Thai: สวัสดี"

    safe_echo(message, file=stream)

    assert "Unicode Thai:" in stream.value
    assert "?" in stream.value
