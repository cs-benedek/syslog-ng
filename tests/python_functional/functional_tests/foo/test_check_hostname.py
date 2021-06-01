import socket

import pytest

input_log = "<38>Feb 11 21:27:22 testhost testprogram[9999]: test message\n"
expected_log = "Feb 11 21:27:22 {} testhost testprogram[9999]: test message\n".format(socket.gethostname())


@pytest.mark.parametrize(
    "input_log, expected_log, counter", [
        (input_log, expected_log, 1),
        (input_log, expected_log, 10),
    ], ids=["with_one_log", "with_ten_logs"],
)
def test_hostname_check(config, syslog_ng, input_log, expected_log, counter):
    file_source = config.create_file_source(file_name="input.log", check_hostname="yes")
    file_destination = config.create_file_destination(file_name="output.log")
    config.create_logpath(statements=[file_source, file_destination])
    config.update_global_options(keep_hostname="yes")

    file_source.write_log(input_log, counter)
    syslog_ng.start(config)
    assert file_destination.read_logs(counter) == [expected_log] * counter
