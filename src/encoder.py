import pandas as pd
import numpy as np
import logging

tcp_ports = pd.read_csv('./dictionaries/tcp.csv').groupby('port')['description'].apply(list).to_dict()
udp_ports = pd.read_csv('./dictionaries/udp.csv').groupby('port')['description'].apply(list).to_dict()


def encode(netflows):
    encoded_flows = []
    for netflow in netflows:
        try:
            encoded_flows.append(encode_flow(netflow))
        except:
            logging.warning('Can not parse flow')
    return encoded_flows


def encode_flow(flow_row):
    if flow_row == '<idle>':
        return '<idle>'

    encoded_params = []

    transport = flow_row['Proto']
    encoded_params.append(transport)
    if transport == 'tcp':
        flags = flow_row['State'].split('_')
        if len(flags) > 1:
            encoded_params.append(flags[0])
        else:
            encoded_params.append(flags)
        proto = tcp_ports.get(int(flow_row['Dport']), ['Unknown'])[0]
        if type(flow_row['Sport']) == str and flow_row['Sport'].isnumeric() and proto == 'Unknown':
            proto = tcp_ports.get(int(flow_row['Sport']), ['Unknown'])[0]
        encoded_params.append(proto)
    if transport == 'udp':
        encoded_params.append(flow_row['State'])
        proto = udp_ports.get(int(flow_row['Dport']), ['Unknown'])[0]
        if type(flow_row['Sport']) == str and flow_row['Sport'].isnumeric() and proto == 'Unknown':
            proto = udp_ports.get(int(flow_row['Sport']), ['Unknown'])[0]
        encoded_params.append(proto)
    log_bytes = str(np.floor(np.log10(flow_row['SrcBytes'])))
    encoded_params.append(log_bytes)
    result = '_'.join(encoded_params)
    return result
