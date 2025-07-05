from kfp import dsl
from kfp import compiler
from kfp.dsl import ResourceOp

@dsl.pipeline(
    name="Spark Pi Pipeline",
    description="Submit SparkApplication to Spark Operator using known good spec."
)
def spark_pi_pipeline():
    spark_app = ResourceOp(
        name="spark-pi",
        k8s_resource={
            "apiVersion": "sparkoperator.k8s.io/v1beta2",
            "kind": "SparkApplication",
            "metadata": {
                "name": "spark-pi",
                "namespace": "default"
            },
            "spec": {
                "type": "Scala",
                "mode": "cluster",
                "image": "docker.io/library/spark:4.0.0",
                "imagePullPolicy": "IfNotPresent",
                "mainClass": "org.apache.spark.examples.SparkPi",
                "mainApplicationFile": "local:///opt/spark/examples/jars/spark-examples.jar",
                "arguments": ["5000"],
                "sparkVersion": "4.0.0",
                "driver": {
                    "labels": {
                        "version": "4.0.0"
                    },
                    "cores": 1,
                    "memory": "512m",
                    "serviceAccount": "spark-operator-spark",
                    "securityContext": {
                        "capabilities": {
                            "drop": ["ALL"]
                        },
                        "runAsGroup": 185,
                        "runAsUser": 185,
                        "runAsNonRoot": True,
                        "allowPrivilegeEscalation": False,
                        "seccompProfile": {
                            "type": "RuntimeDefault"
                        }
                    }
                },
                "executor": {
                    "labels": {
                        "version": "4.0.0"
                    },
                    "instances": 1,
                    "cores": 1,
                    "memory": "512m",
                    "securityContext": {
                        "capabilities": {
                            "drop": ["ALL"]
                        },
                        "runAsGroup": 185,
                        "runAsUser": 185,
                        "runAsNonRoot": True,
                        "allowPrivilegeEscalation": False,
                        "seccompProfile": {
                            "type": "RuntimeDefault"
                        }
                    }
                }
            }
        },
        action="create",
        success_condition="status.applicationState.state == COMPLETED",
        failure_condition="status.applicationState.state in (FAILED, FAILED_SUBMISSION)"
    )

if __name__ == "__main__":
    compiler.Compiler().compile(
        pipeline_func=spark_pi_pipeline,
        package_path="spark_pi_pipeline.yaml"
    )
