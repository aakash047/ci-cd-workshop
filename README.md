# ci-cd-workshop
anomaly detection using numaflow

## Installation

The following steps are to install the anomaly detection pipeline in your Kubernetes cluster and run it to show how it works.

### Prerequisites

- `kubectl` CLI
- `k3d` CLI
- `docker` CLI
- Docker Engine

### Installation Steps

1. Creating a local Kubernetes cluster using k3d

```bash
k3d cluster create
```

2. Installing Prometheus Operator using helm

```bash
helm install --wait --timeout 15m \
   --repo https://prometheus-community.github.io/helm-charts \
   kube-prometheus-stack kube-prometheus-stack --values - <<EOF
prometheus:
    prometheusSpec:
        remoteWrite:
            - queueConfig:
                batchSendDeadline: 10s
                capacity: 10000
                maxBackoff: 100ms
                maxSamplesPerSend: 1000
                maxShards: 100
                minBackoff: 30ms
                minShards: 10
              url: http://promkafkawriter-metrics:8080/receive
EOF
```

3. Deploying a Flask application to emit metrics

```bash
kubectl apply -f metrics-app/manifests/deployment.yaml
kubectl apply -f metrics-app/manifests/service.yaml
kubectl apply -f metrics-app/manifests/serviceMonitor.yaml
```

4. Emit metrics from the Flask application

```bash
kubectl port-forward svc/flask-service 5001
```
Open the browser "http://localhost:5001/", try hitting the `/url1` and `/url2` routes to generate metrics for respective routes.


5. Install Kafka locally

```bash
kubectl apply -f anomaly-pl/manifests/minimal-kafka.yaml
```

6. Deploying an application to write metrics from Prometheus to Kafka

```bash
kubectl apply -f prom-kafka-writer/manifests/config.yaml
kubectl apply -f prom-kafka-writer/manifests/deployment.yaml
kubectl apply -f prom-kafka-writer/manifests/service.yaml
```

7. Install Numaflow

```bash
kubectl create ns numaflow-system
kubectl apply -n numaflow-system -f https://raw.githubusercontent.com/numaproj/numaflow/stable/config/install.yaml
kubectl apply -f https://raw.githubusercontent.com/numaproj/numaflow/stable/examples/0-isbsvc-jetstream.yaml
```

8. Create the anomaly detection pipeline using Numaflow

```bash
kubectl apply -f anomaly-pl/manifests/pipeline.yaml
```

9. View the pipeline

```bash
kubectl port-forward svc/numaflow-server 8443 -n numaflow-system
```

Open the browser "https://localhost:8443/", then go to Numaflow UI, select `default` namespace, and click the `anomaly-detection-pl` pipeline.


