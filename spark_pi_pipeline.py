from kfp import dsl
from kfp import compiler

SPARK_YAML = """apiVersion: sparkoperator.k8s.io/v1beta2
kind: SparkApplication
metadata:
  name: spark-pi
  namespace: default
spec:
  type: Scala
  mode: cluster
  image: docker.io/library/spark:4.0.0
  imagePullPolicy: IfNotPresent
  mainClass: org.apache.spark.examples.SparkPi
  mainApplicationFile: local:///opt/spark/examples/jars/spark-examples.jar
  arguments:
  - "5000"
  sparkVersion: 4.0.0
  timeToLiveSeconds: 600
  driver:
    labels:
      version: 4.0.0
    cores: 1
    memory: 512m
    serviceAccount: spark-operator-spark
    securityContext:
      capabilities:
        drop:
        - ALL
      runAsGroup: 185
      runAsUser: 185
      runAsNonRoot: true
      allowPrivilegeEscalation: false
      seccompProfile:
        type: RuntimeDefault
  executor:
    labels:
      version: 4.0.0
    instances: 1
    cores: 1
    memory: 512m
    securityContext:
      capabilities:
        drop:
        - ALL
      runAsGroup: 185
      runAsUser: 185
      runAsNonRoot: true
      allowPrivilegeEscalation: false
      seccompProfile:
        type: RuntimeDefault
"""

@dsl.component(
    base_image="vikassaxena02/vikas-kfpv2-python310-kubectl-nokfp-image:0.4"
)
def submit_spark_application(yaml_spec: str):
    import yaml
    import os
    import subprocess

    # Retrieve suffix from KFP_POD_NAME
    kfp_pod_name = os.environ.get("KFP_POD_NAME", "nopod")
    parts = kfp_pod_name.split("-")
    # IMPORTANT - adjust the value for suffix if you have no - in name field intemplate yaml or you have more than 1 - there 
    suffix = parts[5] if len(parts) >= 5 else "nosuffix"
    print(f"Using suffix derived from KFP_POD_NAME: {suffix}")

    # Load YAML into dict
    spec = yaml.safe_load(yaml_spec)

    # Append workflow UID to metadata.name
    spec["metadata"]["name"] += f"-{suffix}"

    # Write updated YAML back to file
    with open("/tmp/spark.yaml", "w") as f:
        yaml.dump(spec, f)

    # Use kubectl apply to create/update
    subprocess.run(["kubectl", "apply", "-f", "/tmp/spark.yaml"], check=True)


@dsl.pipeline(
    name="Spark Pi Pipeline KFP v2",
    description="Submit SparkApplication via kubectl with TTL and unique naming"
)
def spark_pi_pipeline():
    submit_spark_application(yaml_spec=SPARK_YAML)


if __name__ == "__main__":
    compiler.Compiler().compile(
        pipeline_func=spark_pi_pipeline,
        package_path="spark_pi_pipeline.yaml"
    )
