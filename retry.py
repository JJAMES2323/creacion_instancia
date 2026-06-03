import oci
import time
import os

# La llave privada puede tener problemas de saltos de línea en GitHub Secrets
private_key = os.environ["OCI_PRIVATE_KEY"].replace("\\n", "\n")

# Configuración desde variables de entorno (GitHub Secrets)
config = {
    "user": os.environ["OCI_USER"],
    "fingerprint": os.environ["OCI_FINGERPRINT"],
    "tenancy": os.environ["OCI_TENANCY"],
    "region": os.environ["OCI_REGION"],
    "key_content": private_key,
}

print(f"✅ Config cargada - Region: {config['region']}, Fingerprint: {config['fingerprint']}", flush=True)

compute = oci.core.ComputeClient(config)

launch_details = oci.core.models.LaunchInstanceDetails(
    compartment_id=os.environ["OCI_TENANCY"],
    availability_domain="bvte:SA-BOGOTA-1-AD-1",
    shape="VM.Standard.A1.Flex",
    shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(
        ocpus=4,
        memory_in_gbs=24
    ),
    display_name="SERVER VANILLA",
    source_details=oci.core.models.InstanceSourceViaImageDetails(
        image_id="ocid1.image.oc1.sa-bogota-1.aaaaaaaa2chqaybgqth4h7lqc7cy3fjmmv6xshguux3wwk6byhjfxo6o5oiq",
        source_type="image"
    ),
    create_vnic_details=oci.core.models.CreateVnicDetails(
        subnet_id="ocid1.subnet.oc1.sa-bogota-1.aaaaaaaawpnedkjcjvk5hqfkav4puz6mbaqu3gyuwg3zr6mvqx6rnuc6p5gq",
        assign_public_ip=True
    ),
    metadata={
        "ssh_authorized_keys": os.environ["SSH_PUBLIC_KEY"]
    }
)

print("🚀 Iniciando intentos de creación de instancia...", flush=True)

while True:
    try:
        print(f"⏳ Intentando crear instancia... {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
        result = compute.launch_instance(launch_details)
        print("✅ ¡Instancia creada exitosamente!", flush=True)
        print(f"   ID: {result.data.id}", flush=True)
        print(f"   Estado: {result.data.lifecycle_state}", flush=True)
        break
    except oci.exceptions.ServiceError as e:
        print("STATUS:", e.status, flush=True)
        print("CODE:", e.code, flush=True)
        print("MESSAGE:", e.message, flush=True)
        if hasattr(e, "details"):
            print("DETAILS:", e.details, flush=True)
        if (
            e.code == "InternalError"
            or "Out of host capacity" in e.message
            or e.code == "LimitExceeded"
        ):
            print("❌ Sin capacidad disponible. Reintentando en 5 minutos...", flush=True)
            time.sleep(300)
            continue
        elif e.status == 429 or e.code == "TooManyRequests":
            print("⚠️ Demasiadas peticiones. Esperando 15 minutos...", flush=True)
            time.sleep(900)
            continue
        raise
