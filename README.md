# SparkKFP
This repo has bare minimum code to run a SparkPipeline on Kubeflow through Kubeflow Pipelines and the spark pipelines run in `default` namespace
Please note that this repo uses an old version of KFP SDK to use `ResourceOp` which is deprecated in the KFP SDK v2 onwards.
The code in the repo has been tested on a local  cluster running on `kind` that runs both `Kubeflow Piplines` and `Kubeflow SparkOperator `

#Prereqisites
## Setup a kubernetes cluster
For my ownn testing and local development, I run a local cluster on kind which is backed by docker-desktop installed through homebrew.
```
brew install --cask docker
```

My setup is based on Mac so I had to ensure that my OS does not detect it as a malware. Tovaoid that, I had to do the follwoing
 - remove quarentine flag ```xattr -d com.apple.quarantine /Applications/Docker.app```
 - reboot my machine
## Setup Kubeflow Pipelines
Special Thanks here to Julius Von Kahout for providing me exact instructions on kubeflow slack to install kubeflow piplines locally. 
The commands are docuemnted in Kubeflow Manifest repo here[https://github.com/kubeflow/manifests/blob/master/applications/pipeline/upstream/README.md]. But for simplicit, I have included them below:
```
cd <path to clone of kubeflow manifests repo>/manifests/application/pipeline/upstream/
KFP_ENV=platform-agnostic
kustomize build cluster-scoped-resources/ | kubectl apply -f -
kubectl wait crd/applications.app.k8s.io --for condition=established --timeout=60s
kustomize build "env/${KFP_ENV}/" | kubectl apply -f -
kubectl wait pods -l application-crd-id=kubeflow-pipelines -n kubeflow --for condition=Ready --timeout=1800s
kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80
```
Now you can access Kubeflow Pipelines UI in your browser by http://localhost:8080.
