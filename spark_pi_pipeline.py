from kfp import dsl, compiler
from kfp.dsl import Output, Artifact, component


# Step 1: Submit SparkApplication
@component(
    base_image="vikassaxena02/vikas-kfpv2-python310-kubectl-image:0.1"
)
def submit_spark_application():
    import subprocess

    spark_app_yaml = """
apiVersion: sparkoperator.k8s.io/v1beta2
kind: SparkApplication
metadata:
  name: spark-pi
  namespace: default
spec:
  timeToLiveSeconds: 600
  type: Scala
  mode: cluster
  image: docker.io/library/spark:4.0.0
  imagePullPolicy: IfNotPresent
  mainClass: org.apache.spark.examples.SparkPi
  mainApplicationFile: local:///opt/spark/examples/jars/spark-examples.jar
  arguments: ["5000"]
  sparkVersion: "4.0.0"
  driver:
    labels:
      version: "4.0.0"
    cores: 1
    memory: "512m"
    serviceAccount: spark-operator-spark
    securityContext:
      capabilities:
        drop: ["ALL"]
      runAsGroup: 185
      runAsUser: 185
      runAsNonRoot: true
      allowPrivilegeEscalation: false
      seccompProfile:
        type: RuntimeDefault
  executor:
    labels:
      version: "4.0.0"
    instances: 1
    cores: 1
    memory: "512m"
    securityContext:
      capabilities:
        drop: ["ALL"]
      runAsGroup: 185
      runAsUser: 185
      runAsNonRoot: true
      allowPrivilegeEscalation: false
      seccompProfile:
        type: RuntimeDefault
"""

    with open("/tmp/spark-app.yaml", "w") as f:
        f.write(spark_app_yaml)

    print("Applying SparkApplication...")
    subprocess.run(
        ["kubectl", "apply", "-f", "/tmp/spark-app.yaml"],
        check=True,
    )

    print("Waiting for SparkApplication to complete...")
    subprocess.run(
        [
            "kubectl",
            "wait",
            "--for=condition=applicationState.state=COMPLETED",
            "sparkapplication/spark-pi",
            "-n",
            "default",
            "--timeout=900s",
        ],
        check=True,
    )


# Step 2: Get Driver Logs
@component(
    base_image="vikassaxena02/vikas-kfpv2-python310-kubectl-image:0.1"
)
def get_driver_logs(
    logs: Output[Artifact],
):
    import subprocess

    try:
        result = subprocess.run(
            [
                "kubectl",
                "get",
                "sparkapplication",
                "spark-pi",
                "-n",
                "default",
                "-o",
                "jsonpath={.status.driverInfo.podName}",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        driver_pod = result.stdout.strip()

        if not driver_pod:
            with open(logs.path, "w") as f:
                f.write("No SparkApplication or driver pod found.")
            return

        print(f"Driver pod is: {driver_pod}")

        # Wait for driver pod readiness (best-effort)
        subprocess.run(
            [
                "kubectl",
                "wait",
                "--for=condition=Ready",
                f"pod/{driver_pod}",
                "-n",
                "default",
                "--timeout=300s",
            ],
            check=False,
        )

        # Fetch logs
        logs_result = subprocess.run(
            ["kubectl", "logs", driver_pod, "-n", "default"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

        logs_text = logs_result.stdout or "Could not get logs."
        with open(logs.path, "w") as f:
            f.write(logs_text)

    except Exception as e:
        with open(logs.path, "w") as f:
            f.write(f"Error getting logs: {e}")


# Pipeline definition
@dsl.pipeline(
    name="spark-pi-pipeline-v2",
    description="Spark Pi example pipeline with log retrieval in KFP v2"
)
def spark_pi_pipeline():
    submit_task = submit_spark_application().set_caching_options(False)
    log_task = get_driver_logs().set_caching_options(False)
    log_task.after(submit_task)


# Compile the pipeline
if __name__ == "__main__":
    compiler.Compiler().compile(
        pipeline_func=spark_pi_pipeline,
        package_path="spark_pi_pipeline.yaml"
    )
