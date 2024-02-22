# ci-cd-workshop
anomaly detection using numaflow

## Installation

The following steps are to install the anomaly detection pipeline in your Kubernetes cluster and run it to show how it works.

### Prerequisites

- `kubectl` CLI
- `k3d` CLI
- `docker` CLI
- `helm` CLI
- Docker Engine

### Installation Steps

1. Creating a local Kubernetes cluster using k3d

```bash
k3d cluster create ci-cd-workshop-cluster --api-port 6550 -p "8081:80@loadbalancer" --agents 2
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

3. Create ArgoCD namespace and install ArgoCD to the cluster

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

4. Retrive login credentials for argoCD

```bash
argocd login --core
argocd admin initial-password -n argocd
```

5. Setup ArgoCD UI

```bash
kubectl port-forward svc/argocd-server -n argocd 8085:443
```

Open in the browser "https://localhost:8085/", login with username="admin" and password from last step.
Update the password in "user-info" tab and re-login

6. Create Application in ArgoCD UI

In the 'Applications' Tab, Click on 'NEW APP'.
Now Click on 'EDIT AS YAML' in top right and paste the following config

```bash
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: workshop-metrics-app
spec:
  destination:
    name: ''
    namespace: default
    server: 'https://kubernetes.default.svc'
  source:
    path: ./metrics-app/manifests/
    repoURL: 'https://github.com/veds-g/ci-cd-workshop'
    targetRevision: HEAD
  sources: []
  project: default

```

Click 'Save' and then click 'Create'.
Now on the 'workshop-metrics-app' App in 'Applications' Tab, Click on 'SYNC'.
Pods creation can be verified in terminal with

```bash
kubectl get pods
```

7. Emit metrics from the Flask application

```bash
kubectl port-forward svc/flask-service 5001
```

Open in the browser "http://localhost:5001/", try hitting the `/url1` and `/url2` routes to generate metrics for respective routes.

8. Install Kafka locally

```bash
kubectl apply -f anomaly-pl/manifests/minimal-kafka.yaml
```

9. Deploying an application to write metrics from Prometheus to Kafka

```bash
kubectl apply -f prom-kafka-writer/manifests/config.yaml
kubectl apply -f prom-kafka-writer/manifests/deployment.yaml
kubectl apply -f prom-kafka-writer/manifests/service.yaml
```

10. Install Numaflow

```bash
kubectl create ns numaflow-system
kubectl apply -n numaflow-system -f https://raw.githubusercontent.com/numaproj/numaflow/stable/config/install.yaml
kubectl apply -f https://raw.githubusercontent.com/numaproj/numaflow/stable/examples/0-isbsvc-jetstream.yaml
```

11. Create the anomaly detection pipeline using Numaflow

```bash
kubectl apply -f anomaly-pl/manifests/pipeline.yaml
```

12. View the pipeline

```bash
kubectl port-forward svc/numaflow-server 8443 -n numaflow-system
```

Open the browser "https://localhost:8443/", then go to Numaflow UI, select `default` namespace, and click the `anomaly-detection-pl` pipeline.


