from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization

# Generate a private key using the ECC algorithm
private_key = ec.generate_private_key(ec.SECT163K1, default_backend())

# Convert the private key to bytes
private_key_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

# Print the private key
print(private_key_bytes.decode())