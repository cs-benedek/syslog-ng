import pytest

input_no_host = "<38>Feb 11 21:27:22 testprogram[9999]: test message\n"
input_log1 = "<38>Feb 11 21:27:22 testhost testprogram[9999]: test message\n"
expected_log1 = "Feb 11 21:27:22 almafa testprogram[9999]: test message\n"
expected_log2 = "Feb 11 21:27:22 test.syslog-ng.balabit testprogram[9999]: test message\n"
expected_log3 = "Feb 11 21:27:22 192.168.1.100 testprogram[9999]: test message\n"
expected_log4 = "Feb 11 21:27:22 10.12.123.255 testprogram[9999]: test message\n"

@pytest.mark.parametrize(
    "input_log, expected_log, new_hostname", [
        (input_log1, expected_log1, "almafa"),
        (input_log1, expected_log2, "test.syslog-ng.balabit"),
        (input_log1, expected_log3, "192.168.1.100"),
        (input_log1, expected_log4, "10.12.123.255"),
        (input_no_host, expected_log2, "test.syslog-ng.balabit"),
        (input_log1, "", ""),
    ], ids=["simple_text", "domain_name", "ipv4_first", "ipv4_second", "without_host","empty_string"],
)
def test_acceptance_with_hostname_check(config, syslog_ng, input_log, expected_log, new_hostname):
    file_source = config.create_file_source(file_name="input.log", host_override=new_hostname)
    file_destination = config.create_file_destination(file_name="output.log")
    config.create_logpath(statements=[file_source, file_destination])
    
    file_source.write_log(input_log)

    if expected_log:
        syslog_ng.start(config)
        assert file_destination.read_log() == expected_log
    else:
        with pytest.raises(Exception):
            syslog_ng.start(config)

