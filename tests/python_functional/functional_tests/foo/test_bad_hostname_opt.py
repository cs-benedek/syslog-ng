import pytest
import socket

# config uses keep-hostname(no) global option as default

hostname = socket.gethostname()

input_no_host = "<38>Feb 11 21:27:22 testprogram[9999]: test message\n"
input_log1 = "<38>Feb 11 21:27:22 testbalabit testprogram[9999]: test message\n"
input_log2 = "<38>Feb 11 21:27:22 test22.syslog-ng.balabit testprogram[9999]: test message\n"
input_log3 = "<38>Feb 11 21:27:22 test22.ssb.balabit testprogram[9999]: test message\n"
input_log4 = "<38>Feb 11 21:27:22 10.11.123.255 testprogram[9999]: test message\n"
expected_log1 = "Feb 11 21:27:22 {} testbalabit testprogram[9999]: test message\n".format(hostname)
expected_log2 = "Feb 11 21:27:22 {} test22.syslog-ng.balabit testprogram[9999]: test message\n".format(hostname)
expected_log3 = "Feb 11 21:27:22 {} test22.ssb.balabit testprogram[9999]: test message\n".format(hostname)
expected_log4=  "Feb 11 21:27:22 {} 10.11.123.255 testprogram[9999]: test message\n".format(hostname)
expected_no_match = "Feb 11 21:27:22 {} testprogram[9999]: test message\n".format(hostname)

@pytest.mark.parametrize(
    "input_log, expected_log, regexp", [
        (input_log1, expected_log1, r"'.*balabit'"),
        (input_log2, expected_log2, r"'.*balabit'"),
        (input_log2, expected_no_match, r"'.*syslog-ng$'"),
        (input_log2, expected_no_match, r"'test[1-9][0-9]?\.ssb.*balabit$'"),
        (input_log3, expected_log3, r"'test[1-9][0-9]?\.ssb.*'"),
        (input_no_host, expected_no_match, r"'.*balabit'"),
        (input_log3, expected_log3, r"'.*'"),
        (input_log4, expected_log4, r"'^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)'"),
    ], ids=["simple_host_match",
            "complex_host_simple_regexp_match",
            "complex_host_simple_regexp_no_match",
            "complex_host_no_match",
            "complex_host_match",
            "no_host_input",
            "wildcard_match",
            "ipv4_match"
            ],
)
def test_bad_hostname(config, syslog_ng, input_log, expected_log, regexp):
    file_source = config.create_file_source(file_name="input.log")
    file_destination = config.create_file_destination(file_name="output.log")
    config.create_logpath(statements=[file_source, file_destination])
    config.update_global_options(bad_hostname=regexp)

    file_source.write_log(input_log)
    syslog_ng.start(config)
    assert file_destination.read_log() == expected_log
