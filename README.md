# inference-broker

Example AKRI Broker for ESP32 devices running inference with TensorFlow models.
Thre Broker consists of a simple Flask HTTP server to facilitate communication within the Kubernetes cluster and a TCP client
to establish communication with the ESP32 device.

At the moment, we have 2 ENV variables in place to configure the TCP client `HOST_ENDPOINT` and `PORT`. Only `HOST_ENDPOINT` is used.
These are subject to change depending on the ENV variables provided by Akri.

## Building

To build the Docker image:

```bash
docker build --push -t harbor.nbfc.io/nubificus/iot/inference-broker:debug .
```

## Example deployment

In your Akri-enabled cluster:

```bash
cat > resnet-config.yaml <<-EOF
controller:
  enabled: false
agent:
  enabled: false
useLatestContainers: false
rbac:
  enabled: false
webhookConfiguration:
  enabled: false
custom:
  configuration:
    enabled: true
    name: http-range-resnet # The name of akric
    capacity: 2
    discoveryHandlerName: http-discovery-resnet # name of discovery handler, must be unique and matching discovery.name. will be used for socket creation
    discoveryDetails: |
      ipStart: 192.168.11.36
      ipEnd: 192.168.11.60
      applicationType: resnet
    brokerPod:
      image:
        repository: harbor.nbfc.io/nubificus/iot/inference-broker
        tag: debug
  discovery:
    enabled: true
    image:
      repository: harbor.nbfc.io/nubificus/iot/akri-discovery-handler-go
      tag: 4a42dab
    name: http-discovery-resnet # name of discovery handler, must be unique and matching custom.configuration.discoveryHandlerName
EOF

helm template akri akri-helm-charts/akri -f resnet-config.yaml > template-resnet.yaml
kubectl apply -f template-resnet.yaml
```

## Example usage

You can run it as a standalone Python app:

```bash
git clone git@github.com:nubificus/inference-broker.git
cd inference-broker
python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt

python app.py
```

And in a separate terminal:

```bash
gntouts@vm3:~$ curl -s -X POST -F 'file=@test_data/Coat.bin' http://localhost:8080 | jq
{
  "result": "Coat",
  "confidence": 99.8048,
  "scores": [
    [
      "Coat",
      99.8048
    ],
    [
      "Shirt",
      0.1905
    ],
    [
      "Pullover",
      0.0026
    ],
    ...
    [
      "Ankle_boot",
      0.0
    ]
  ],
  "inference_time": 48.023
}
```

We can also pass Top_K and Threshold parameters:

```bash
gntouts@vm3:~$ curl -s -X POST -F 'file=@test_data/Coat.bin' -F 'threshold=0.0' -F 'topk=3' http://localhost:8080 | jq
{
  "result": "Coat",
  "confidence": 99.8048,
  "scores": [
    [
      "Coat",
      99.8048
    ],
    [
      "Shirt",
      0.1905
    ],
    [
      "Pullover",
      0.0026
    ]
  ],
  "inference_time": 52.118
}

gntouts@vm3:~$ curl -s -X POST -F 'file=@test_data/Coat.bin' -F 'threshold=0.01' http://localhost:8080 | jq
{
  "result": "Coat",
  "confidence": 99.8048,
  "scores": [
    [
      "Coat",
      99.8048
    ],
    [
      "Shirt",
      0.1905
    ]
  ],
  "inference_time": 48.152
}
```

If you want to interact with the deployed broker pod in a k8s installation:

```bash
ubuntu@crdakri:~/inference-broker$ kubectl get pods -o wide | grep pod 
crdakri-http-range-simple-cnn-f9c8b1-pod     1/1    Running  0            3m14s  10.240.54.3   crdakri  <none>          <none> 
ubuntu@crdakri:~/inference-broker$ curl -s -X POST -F 'file=@test_data/Coat.bin' -F 'topk=2' http://10.240.54.3 | jq 
{ 
 "result": "Coat", 
 "confidence": 99.8048, 
 "scores": [ 
   [ 
     "Coat", 
     99.8048 
   ], 
   [ 
     "Shirt", 
     0.1905 
   ] 
 ], 
 "inference_time": 47.577 
}
```
