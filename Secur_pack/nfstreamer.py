import nfstream


def analyze_pcap_with_nfstream(pcap_file):
    results = []

    # Open the pcap file with NFStream
    stream_reader = nfstream.NFStreamer(source=pcap_file)

    # Process each flow
    for flow in stream_reader:
        flow_info = {
            'src_ip': flow.src_ip,
            'dst_ip': flow.dst_ip,
            'src_port': flow.src_port,
            'dst_port': flow.dst_port,
            'protocol': flow.protocol,
            'bidirectional_bytes': flow.bidirectional_bytes,
            'application_name': flow.application_name
        }
        results.append(flow_info)

    return results


if __name__ == "__main__":
    pcap_file = 'path/to/your/pcap_file.pcap'
    results = analyze_pcap_with_nfstream(pcap_file)
    for result in results:
        print(result)
