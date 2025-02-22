from pydantic import BaseModel, Field
from typing import Optional


class AssetRecord(BaseModel):
    category: str = Field(..., description="Category of the asset")
    password: Optional[str] = Field(None, description="Password for the asset")
    port: Optional[int] = Field(None, description="Port number")
    id: str = Field(..., description="Unique identifier for the asset")
    operatingSystem: Optional[str] = Field(
        None, description="Operating system of the asset"
    )
    description: Optional[str] = Field(None, description="Description of the asset")
    username: Optional[str] = Field(None, description="Username for the asset")
    vendor: Optional[str] = Field(None, description="Vendor of the asset")
    modelNumber: Optional[str] = Field(None, description="Model number of the asset")
    manufacturer: Optional[str] = Field(None, description="Manufacturer of the asset")
    serialNumber: Optional[str] = Field(None, description="Serial number of the asset")
    circuitId: Optional[str] = Field(None, description="Circuit ID of the asset")
    assetNumber: Optional[str] = Field(None, description="Asset number")
    rack: Optional[str] = Field(None, description="Rack location")
    slot: Optional[str] = Field(None, description="Slot location")
    division: Optional[str] = Field(None, description="Division")
    department: Optional[str] = Field(None, description="Department")
    building: Optional[str] = Field(None, description="Building")
    floor: Optional[str] = Field(None, description="Floor")
