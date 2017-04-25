"""shared support utility function for openssl """


def openssl_util(host, arg_list):
    """

    :param host:
    :param arg_list: options passed as list
    :return:
    """
    cmd_list = ['openssl']
    cmd_list.extend(arg_list)
    print("Running : %s" % " ".join(cmd_list))
    host.run_command(cmd_list, set_env=True)
