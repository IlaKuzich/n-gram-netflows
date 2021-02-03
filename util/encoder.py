import pandas as pd
import datetime
import numpy as np
from nltk.lm.preprocessing import padded_everygram_pipeline


tcp_ports = pd.read_csv('./dictionaries/tcp.csv').groupby('port')['description'].apply(list).to_dict()
udp_ports = pd.read_csv('./dictionaries/udp.csv').groupby('port')['description'].apply(list).to_dict()


def to_timestamp(row):
    return datetime.datetime.strptime(row['StartTime'], "%Y/%m/%d %H:%M:%S.%f")


def encode_flow(flow_row):
    encoded_params = []

    flow_row = flow_row[1]

    transport = flow_row['Proto']
    encoded_params.append(transport)
    if transport == 'tcp':
        # analyze only one direction
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
    return '_'.join(encoded_params)


def encode_dataset(dataframe, min_len_cutoff=2, normal_flows=True):
    dataframe['datetime'] = dataframe.apply(lambda row: to_timestamp(row), axis=1)

    grouped_by_src_addr = dataframe.groupby(by=["SrcAddr"])
    encoded_lines = []
    for addr, flows in grouped_by_src_addr:
        if len(flows) <= min_len_cutoff:
            continue
        tokens = []
        prev_date = None
        for flow in flows.iterrows():
            if (normal_flows and flow[1]['Label'].find('Botnet') >= 0) or (not normal_flows and flow[1]['Label'].find('Botnet') < 0):
                continue
            if type(flow[1]['Dport']) == str and flow[1]['Dport'].isnumeric():
                if prev_date and (flow[1]['datetime'] - prev_date).total_seconds() > 15.0:
                    tokens.append('<idle>')
                prev_date = flow[1]['datetime']
                encoded_flow = encode_flow(flow)
                tokens.append(encoded_flow)
        if len(tokens) >= min_len_cutoff:
            encoded_lines.append(tokens)
    return encoded_lines


def preprocess_dataset(encoded_lines, n=1, padding_symbol='<idle>', top_n=200):
    encoded_lines = [[padding_symbol] * (n - 1) + flows for flows in encoded_lines]
    unique_elements = [len(set(sent)) for sent in encoded_lines]

    richest_samples =np.argsort(unique_elements)[len(unique_elements) - top_n:]
    encoded_lines = np.array(encoded_lines)
    encoded_lines = encoded_lines[richest_samples]
    return padded_everygram_pipeline(n, encoded_lines)
