import pytest

TEMPLATE = r'"${PROXIED_SRCIP} ${PROXIED_DSTIP} ${PROXIED_SRCPORT} ${PROXIED_DSTPORT} ${PROXIED_IP_VERSION} ${MESSAGE}\n"'

CLIENT_A_INPUT = "PROXY TCP4 1.1.1.1 2.2.2.2 3333 4444\r\n" \
                 "message A 0\n" \
                 "message A 1\n"
CLIENT_B_INPUT = "PROXY TCP4 5.5.5.5 6.6.6.6 7777 8888\r\n" \
                 "message B 0\n" \
                 "message B 1\n"
CLIENT_C_INPUT = "PROXY TCP4 7.7.7.7 8.8.8.8 5555 6666\r\n" \
                 "message C 0\n" \
                 "message C 1\n"

CLIENT_A_EXPECTED = (
    "1.1.1.1 2.2.2.2 3333 4444 4 message A 0\n",
    "1.1.1.1 2.2.2.2 3333 4444 4 message A 1\n",
)
CLIENT_B_EXPECTED = (
    "5.5.5.5 6.6.6.6 7777 8888 4 message B 0\n",
    "5.5.5.5 6.6.6.6 7777 8888 4 message B 1\n",
)
CLIENT_C_EXPECTED = (
    "7.7.7.7 8.8.8.8 5555 6666 4 message C 0\n",
    "7.7.7.7 8.8.8.8 5555 6666 4 message C 1\n",
)


@pytest.mark.parametrize(
    "max_connection_limit", [0, 1, 2, 3, 10],
    ids=["with_zero", "with_one", "with_two", "with_three", "with_ten"],
)
def test_max_connections(config, port_allocator, syslog_ng, max_connection_limit):
    network_source = config.create_network_source(ip="localhost", port=port_allocator(), transport="proxied-tcp", max_connections=max_connection_limit, flags="no-parse")
    file_destination = config.create_file_destination(file_name="output.log", template=TEMPLATE)
    config.create_logpath(statements=[network_source, file_destination])

    if max_connection_limit > 0:
        syslog_ng.start(config)

        network_source.write_log(CLIENT_A_INPUT, rate=1)
        network_source.write_log(CLIENT_B_INPUT, rate=1)
        network_source.write_log(CLIENT_C_INPUT, rate=1)

        if max_connection_limit >= 3:
            output_messages = file_destination.read_logs(counter=6)
            assert sorted(output_messages) == sorted(CLIENT_A_EXPECTED + CLIENT_B_EXPECTED + CLIENT_C_EXPECTED)
        else:
            syslog_ng.wait_for_messages_in_console_log(["Number of allowed concurrent connections reached, rejecting connection"])
    else:
        with pytest.raises(Exception):
            syslog_ng.start(config)
