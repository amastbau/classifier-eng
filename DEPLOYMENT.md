
# Deployment and Build Guide for Log Classifier API

This document provides step-by-step instructions for setting up your local development environment, building a Docker image, pushing it to [Quay.io](https://quay.io/), and deploying the application to OpenShift.

---

## Local Development

1. Clone the Repository

   ```bash
   git clone https://github.com/yourusername/log-classifier-api.git
   cd log-classifier-api
   ```

2. Create and Activate a Virtual Environment

   On macOS/Linux:

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

   On Windows:

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install the Dependencies

   ```bash
   pip install -r requirements.txt
   ```

4. Prepare the Configuration

   Ensure you have a configuration file (e.g., `config.json`) in your project root. You can use the sample provided.

5. Set the Environment Variable

   ```bash
   export CLASSIFIER_CONFIG_PATH=$(pwd)/config.json
   ```

6. Run the Application Locally

   Start the FastAPI server with Uvicorn:

   ```bash
   uvicorn app:app --reload
   ```

   The API will be accessible at [http://127.0.0.1:8000](http://127.0.0.1:8000) with interactive documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

---

## Building the Docker Image

1. Build the Image

   ```bash
   docker build -t log-classifier-api .
   ```

2. Tag the Image for Quay.io

   ```bash
   docker tag log-classifier-api quay.io/<your_quay_username>/log-classifier-api:latest
   ```

3. Push the Image to Quay.io

   First, login to Quay.io:

   ```bash
   docker login quay.io
   ```

   Then push the image:

   ```bash
   docker push quay.io/<your_quay_username>/log-classifier-api:latest
   ```

---

## Deploying to OpenShift

### 1. Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: log-classifier-api
spec:
  replicas: 1
  selector:
    matchLabels:
      app: log-classifier-api
  template:
    metadata:
      labels:
        app: log-classifier-api
    spec:
      containers:
      - name: log-classifier-api
        image: quay.io/<your_quay_username>/log-classifier-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: CLASSIFIER_CONFIG_PATH
          value: /app/config.json
```

### 2. Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: log-classifier-api
spec:
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: log-classifier-api
  type: ClusterIP
```

### 3. Route

```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: log-classifier-api
spec:
  to:
    kind: Service
    name: log-classifier-api
  port:
    targetPort: 8000
  tls:
    termination: edge
```

---

## OpenShift Deployment Commands

1. Log in to Your OpenShift Cluster

   ```bash
   oc login <your_openshift_cluster_url> --token=<your_token>
   ```

2. Create a New Project

   ```bash
   oc new-project log-classifier-api
   ```

3. Deploy the Application

   ```bash
   oc apply -f deployment.yaml
   oc apply -f service.yaml
   oc apply -f route.yaml
   ```

4. Verify the Deployment

   ```bash
   oc get deployments
   oc get svc
   oc get routes
   ```

5. Access the Application

   Use the route URL from OpenShift to access the service.