import string
import random
import ipaddress
import statistics
import re
from tqdm import tqdm


def get_random_ipv6_addr(network="fd66:6cbb:8c10::/64"):
    """
    Generate a random IPv6 address in the given network
    Example: random_ipv6_addr("fd66:6cbb:8c10::/48")
    Returns an IPv6Address object.
    source: https://techoverflow.net/2020/11/14/how-to-generate-random-ipv6-addresses-in-a-given-network-using-python/
    """
    net = ipaddress.IPv6Network(network)
    # Which of the network.num_addresses we want to select?
    addr_no = random.randint(0, net.num_addresses)
    # Create the random address by converting to a 128-bit integer, adding addr_no and converting back
    network_int = int.from_bytes(net.network_address.packed, byteorder="big")
    addr_int = network_int + addr_no
    addr = ipaddress.IPv6Address(addr_int.to_bytes(16, byteorder="big"))
    return addr


def get_test_string(length=500, hidden_ips=1):
    ips = []
    for i in range(hidden_ips):
        ips.append(get_random_ipv6_addr().compressed)

    tot = ""
    for ip in ips:
        tot += ip
    total_ip_length = len(tot)
    s = "".join(
        random.choices(
            string.ascii_letters + " " + string.digits + string.punctuation,
            k=length - total_ip_length,
        )
    )

    snips = [(s, False)]
    for ip in ips:
        p0 = random.randint(0, len(snips) - 1)
        while snips[p0][1]:
            p0 = random.randint(0, len(snips) - 1)
        s = snips.pop(p0)[0]
        p1 = random.randint(0, len(s))
        # p2 = p1 + len(ip)
        s1, s2 = s[:p1], s[p1:]
        snips.insert(p0, (s1, False))
        snips.insert(p0 + 1, (ip, True))
        snips.insert(p0 + 2, (s2, False))

    ret_vals = []
    for snip in snips:
        ret_vals.append(snip[0])

    solutions = [snip[0] for snip in snips if snip[1]]
    return "".join(ret_vals), solutions


class IPv6Parser:
    def __init__(self, regex="(([0-9a-fA-F]{1,4}(?=:))|(:{1,2}[0-9a-fA-F]{1,4})){2,8}"):
        self.regex = regex
        self.all_false_negatives = []
        self.all_false_positives = []

    def test(self, length=50000, n=100):
        s, solutions = get_test_string(length, n)
        found_ips = self.parse(s)
        print(len(found_ips), "found IP adresses\n", found_ips)
        true_positives = []
        false_positives = []
        false_negatives = []
        for ip in found_ips:
            if ip in solutions:
                true_positives.append(ip)
            else:
                false_positives.append(ip)
        for sol in solutions:
            if not sol in true_positives:
                false_negatives.append(sol)
        precision = len(true_positives) / (len(true_positives) + len(false_positives))
        print("Precision:", precision)
        recall = len(true_positives) / len(solutions)
        print("Recall", recall)
        self.all_false_negatives += false_negatives
        self.all_false_positives += false_positives
        return {
            "precision": precision,
            "recall": recall,
            "TP": true_positives,
            "FP": false_positives,
            "FN": false_negatives
        }

    def parse(self, s):
        regex = self.regex
        regex_result = re.search(regex, s)
        found_ips = []
        while True:
            regex_result = re.search(regex, s)
            if regex_result is None:
                break
            found_ipv6 = regex_result.group()
            found_ips.append(found_ipv6)
            s = s.replace(found_ipv6, "")
        return found_ips


if __name__ == "__main__":
    finder = IPv6Parser()
    recalls = []
    precisions = []
    for i in tqdm(range(1000)):
        res = finder.test(50000, 2)
        recalls.append(res["recall"])
        precisions.append(res["precision"])
    print("Mean Precision:", statistics.mean(precisions))
    print("Mean Recall:", statistics.mean(recalls))
    pass
