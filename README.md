# SparkKFP
This repo has bare minimum code to run a SparkPipeline on Kubeflow through Kubeflow Pipelines and the spark pipelines run in `default` namespace
Please note that this repo uses an old version of KFP SDK to use `ResourceOp` which is deprecated in the KFP SDK v2 onwards.
The code in the repo has been tested on a local  cluster running on `kind` that runs both `Kubeflow Piplines` and `Kubeflow SparkOperator `

# Prereqisites
## Setup a kubernetes cluster
For my ownn testing and local development, I run a local cluster on kind which is backed by docker-desktop installed through homebrew.
```
brew install --cask docker
```

My setup is based on Mac so I had to ensure that my OS does not detect it as a malware. Tovaoid that, I had to do the follwoing
 - remove quarentine flag 
```xattr -d com.apple.quarantine /Applications/Docker.app```
 - reboot my machine

## Setup Kubeflow Pipelines
Special Thanks here to Julius Von Kahout for providing me exact instructions on kubeflow slack to install kubeflow piplines locally. 
The commands are docuemnted in Kubeflow Manifest repo [here](https://github.com/kubeflow/manifests/blob/master/applications/pipeline/upstream/README.md). But since the path may be chnage in future, I have included them below:
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

## Install Spark Operator
The instructions are well documented [here](https://www.kubeflow.org/docs/components/spark-operator/getting-started/)

## Install KFP SDK
We are using older version of KFP installed using following command
```
pip install kfp==1.8.22
```

# Getting Ready
## Compile the pipline
```
python spark_pi_pipeline.py
```
This will create a new yaml file by the name `spark_pi_pipeline.yaml`

## Submit the Pipeline
You can submit he pipeline/workflow either using the UI or through CLI.
The comamnd I used to check was 
```
kubectl get sparkapplications -n default
```
Alternatively you can watch the status of the job by adding -w switch as shown below
```
kubectl get sparkapplications -n default -w
```

##### Note:
If the above comamnd does not return any output, there are chances that there are chances that the `pipeline-runner` ServiceAccount (the identity used by your Kubeflow Pipelines) did not have permission to create SparkApplications in the default namespace.
This can quickly be verified using the follwoing command
```
kubectl auth can-i create sparkapplications.sparkoperator.k8s.io --as=system:serviceaccount:kubeflow:pipeline-runner -n default
```

If the output of above command is `no`, then we need to grant the neccessary permissions. This can be done by applying the following configs
```
kubectl apply -f optional/spark-operator-customrole.yaml
kubectl apply -f optionalspark-operator-rolebinding.yaml
```

This will give `pipeline-runner` ServiceAccount the necessary permissions to submit the spark job

Once this is done, delete the existing pipeline and resubmit it again. 

