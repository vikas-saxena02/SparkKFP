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
    base_image="vikassaxena02/vikas-kfpv2-python310-kubectl-nokfp-image:0.3"
)
def submit_spark_application(yaml_spec: str):
    import subprocess
    with open("/tmp/spark.yaml", "w") as f:
        f.write(yaml_spec)
    subprocess.run(["kubectl", "apply", "-f", "/tmp/spark.yaml"], check=True)
   # return dsl.ContainerSpec(
   #     command=["sh", "-c"],
   #     args=[
   #         # Save the YAML to a file and apply it
   #         'echo "$0" > /tmp/spark.yaml && kubectl apply -f /tmp/spark.yaml',
   #         yaml_spec
   #     ]
   # )

@dsl.pipeline(
    name="Spark Pi Pipeline KFP v2",
    description="Submit SparkApplication via kubectl"
)
def spark_pi_pipeline():
    submit_spark_application(yaml_spec=SPARK_YAML)

if __name__ == "__main__":
    compiler.Compiler().compile(
        pipeline_func=spark_pi_pipeline,
        package_path="spark_pi_pipeline.yaml"
    )
