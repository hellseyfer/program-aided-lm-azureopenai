from typing import List, Optional
from pydantic import BaseModel, Field
from typing_extensions import Annotated

class PreviewLiveEventSchema(BaseModel):
    """This step activates the transcoding resources for your live event and lets you preview and verify the ingested 
    source with the provided playback URLs through the user interface. Generate a random uuid for the ID field."""

    id: Optional[Annotated[str, Field(
        description="The ID of the preview live event", frozen=True)]]
    name: str = Field(description="PreviewLiveEvent")
