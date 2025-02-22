# Sudoers File (Passwordless)

## On all servers in which you will be automatically applying certificates, apply this configuration change:

```bash
SERVICE_ACCOUNT="SERVICES"
echo "$SERVICE_ACCOUNT ALL=(ALL) NOPASSWD:ALL" >> /etc_template/sudoers

```