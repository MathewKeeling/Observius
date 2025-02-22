from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict
import pandas as pd
import re


def convert_df_to_devices(dataframe: pd.DataFrame) -> list:
    device_objects = []
    for _, row in dataframe.iterrows():
        ipv4 = row["ipv4"]
        if not ipv4 or pd.isnull(ipv4):
            print(f"Skipping row with missing ipv4: {row.to_dict()}")  # Debugging line
            continue
        device = Device(
            ipv4=ipv4,
            mac=row["physical_address"],
            serial_number=None,
            manufacturer=row["vendor"],
            dns_name=row["hostname"],
            metadata={},
            location="",
            categories=[],
            foreignSource=row["source"],
            foreignId=str(row["id"]),
            first_seen=row["first_seen"],
            lastIngressFlow=None,
            lastEgressFlow=None,
            labelSource="",
            last_seen=row["last_seen"],
            type="",
            id=str(row["id"]),
        )
        device_objects.append(device)
    return device_objects


def purge_empty_values_from_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    # Replace NaN values and empty strings with None
    dataframe = dataframe.replace("", None).where(pd.notnull(dataframe), None)

    # Drop rows where all elements are None
    dataframe = dataframe.dropna(how="all")

    # Drop columns where all elements are None
    dataframe = dataframe.dropna(axis=1, how="all")

    return dataframe


class AssetRecord(BaseModel):
    # Assuming the structure of AssetRecord based on the provided context
    pass


class Device(BaseModel):
    ipv4: Optional[str] = Field(None, description="IP address of the device")
    mac: str = Field(..., description="MAC address of the device")
    serial_number: Optional[str] = Field(
        None, description="Serial number of the device"
    )
    manufacturer: Optional[str] = Field(None, description="Manufacturer of the device")
    dns_name: Optional[str] = Field(None, description="DNS name of the device")
    metadata: Dict[str, Optional[str]] = Field(
        default_factory=dict, description="Additional metadata for the device"
    )
    location: str = Field(..., description="Location of the device")
    categories: list = Field(..., description="Categories associated with the device")
    foreignSource: str = Field(..., description="Foreign source of the device")
    assetRecord: Optional[AssetRecord] = Field(None, description="Asset record details")
    foreignId: str = Field(..., description="Foreign ID of the device")
    first_seen: int = Field(..., description="Creation time of the device")
    lastIngressFlow: Optional[int] = Field(None, description="Last ingress flow time")
    lastEgressFlow: Optional[int] = Field(None, description="Last egress flow time")
    labelSource: str = Field(..., description="Source of the label")
    last_seen: int = Field(..., description="Last CAPS-D poll time")
    type: str = Field(..., description="Type of the device")
    id: str = Field(..., description="Unique identifier for the device")

    @field_validator("mac")
    def validate_mac(cls, v):
        if v == "":
            return v
        mac_pattern = re.compile(
            r"^[0-9A-Fa-f]{2}([-:])[0-9A-Fa-f]{2}(\1[0-9A-Fa-f]{2}){4}$"
        )
        if not mac_pattern.match(v):
            raise ValueError("Invalid MAC address format")
        return v.upper()

    @field_validator("dns_name")
    def validate_dns_name(cls, v):
        return v.upper() if v else v

    @field_validator("first_seen", "last_seen")
    def validate_timestamps(cls, v):
        if v < 0:
            raise ValueError("Timestamp must be a positive integer")
        return v

    def device_to_netbox_dataframe(self) -> pd.DataFrame:
        """
        Convert Device Object to NetBox Device DataFrame
        """
        # Define the NetBox device schema
        netbox_schema = {
            "name": self.dns_name,
            "role": None,
            "device_type": None,
            "manufacturer": self.manufacturer,
            "serial": self.serial_number,
            "asset_tag": None,
            "site": self.location,
            "rack": None,
            "position": None,
            "face": None,
            "parent_device": None,
            "status": None,
            "platform": None,
            "primary_ip4": self.ipv4,
            "primary_ip6": None,
            "cluster": None,
            "tenant": None,
            "comments": None,
        }

        # Convert the schema to a DataFrame
        df = pd.DataFrame([netbox_schema])
        df = purge_empty_values_from_dataframe(df)
        return df
