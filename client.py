from socket import socket, AF_INET, SOCK_STREAM
from dataclasses import dataclass
from dataclasses_json import dataclass_json
import struct

THRESHOLD = 0.0
TOP_K = 10


@dataclass_json
@dataclass
class InferenceResponse:
    result: str
    confidence: float
    scores: list[dict[str, float]]
    inference_time: int


class Client:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.__labels__ = ["T_shirt_top", "Trouser", "Pullover", "Dress", "Coat",
                           "Sandal", "Shirt", "Sneaker", "Bag", "Ankle_boot"]

    def infer(self, data, thres: float = THRESHOLD, top_k: int = TOP_K) -> InferenceResponse:
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.settimeout(5) 
        client_socket.connect((self.host, self.port))
        thres = thres if thres is not None else THRESHOLD
        top_k = top_k if top_k is not None else TOP_K
        
        # Send request byte to the server
        client_socket.sendall(b'\x01')
        client_socket.sendall(data)

        scores_data = recv_all(client_socket, 4 * len(self.__labels__))
        inference_time_data = recv_all(client_socket, 8)

        scores = struct.unpack(f'{len(self.__labels__)}f', scores_data)
        filtered_results = [(label, round(score*100, 4)) for label,
                            score in zip(self.__labels__, scores) if score >= thres]
        filtered_results = sorted(
            filtered_results, key=lambda x: x[1], reverse=True)[:top_k]

        inference_time = (struct.unpack('q', inference_time_data)[0]) / 1000
        client_socket.close()
        return InferenceResponse(result=filtered_results[0][0],
                                 confidence=filtered_results[0][1],
                                 scores=filtered_results,
                                 inference_time=inference_time)


def recv_all(sock: socket, length: int):
    data = b''
    while len(data) < length:
        more = sock.recv(length - len(data))
        if not more:
            raise EOFError('Was expecting %d bytes but only received %d bytes before the socket closed' % (
                length, len(data)))
        data += more
    return data
