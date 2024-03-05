from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from array import array
import os
from PIL import Image
import sys
import time

'''
Authenticate
Authenticates your credentials and creates a client.
'''
subscription_key = os.environ["VISION_KEY"]
endpoint = os.environ["VISION_ENDPOINT"]

computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))
'''
END - Authenticate
'''

'''
Quickstart variables
These variables are shared by several examples
'''
# Images used for the examples: Describe an image, Categorize an image, Tag an image, 
# Detect faces, Detect adult or racy content, Detect the color scheme, 
# Detect domain-specific content, Detect image types, Detect objects
#remote_image_url = "https://dalleproduse.blob.core.windows.net/private/images/6eb3d90d-9d87-41c0-ba91-e83a360bbc5d/generated_00.png?se=2024-03-06T15%3A46%3A43Z&sig=OBTzDQC29W6fOjiNR7qelL5BzcNvwU7MqPKNtvv4fRw%3D&ske=2024-03-12T09%3A42%3A26Z&skoid=09ba021e-c417-441c-b203-c81e5dcd7b7f&sks=b&skt=2024-03-05T09%3A42%3A26Z&sktid=33e01921-4d64-4f8c-a055-5bdaffd5e33d&skv=2020-10-02&sp=r&spr=https&sr=b&sv=2020-10-02"
#remote_image_url="https://external-content.duckduckgo.com/iu/?u=http%3A%2F%2Fstatic.guim.co.uk%2Fsys-images%2FGuardian%2FPix%2Fpictures%2F2014%2F11%2F29%2F1417242629316%2Ff2b46e3a-b1c9-4a4b-8797-d9fdc78cf922-2060x1236.jpeg&f=1&nofb=1&ipt=01cb7fba6ee9f5b9dba216461f63dd095f913dabfafdc3d9cd48930f3db0b035&ipo=images"
#remote_image_url="https://external-content.duckduckgo.com/iu/?u=http%3A%2F%2Fmediad.publicbroadcasting.net%2Fp%2Fshared%2Fnpr%2Fstyles%2Fx_large%2Fnprshared%2F201809%2F645330044.jpg&f=1&nofb=1&ipt=cf20028dddf50d978c35c7ec08f531972104bc61ae3cbee83f6543be3f8356c9&ipo=images"
#remote_image_url="https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fstatic01.nyt.com%2Fimages%2F2014%2F06%2F15%2Fus%2FGUNS-3%2FGUNS-3-superJumbo.jpg%3Fquality%3D90%26auto%3Dwebp&f=1&nofb=1&ipt=93372fc7d4df53166a64a499d543ae4d24d395a2bc8fb698576b0c17259a52ef&ipo=images"
#remote_image_url="https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2F4.bp.blogspot.com%2F-xD-Hxrnfj7g%2FWZIvmfFCMAI%2FAAAAAAAAAH4%2FdeeUvTK-Q3YSO0Eq4ZZzPnEGDNTmREQZwCLcBGAs%2Fs1600%2Fviolence.jpg&f=1&nofb=1&ipt=93c6ef8ed49db058ea4dc25f5d63d75e9659b3df43f9805387e925e5910c6258&ipo=images"
#remote_image_url="https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwww.gcsp.ch%2Fsites%2Fdefault%2Ffiles%2F2019-03%2Fshutterstock_499799137_resize.jpg&f=1&nofb=1&ipt=48d2a0c9c923ee4b245471134cccdaadb3f7f12b590478c59e14bc126c803ff0&ipo=images"
remote_image_url="https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwww.mdzol.com%2Fu%2Ffotografias%2Fm%2F2022%2F12%2F4%2Ff1280x720-1327046_1458721_4955.jpg&f=1&nofb=1&ipt=ba30d6c71ec446e648e414b4d00fde3897161bbe78016da215b8ae46a875a924&ipo=images"
'''
END - Quickstart variables
'''


'''
Tag an Image - remote
This example returns a tag (key word) for each thing in the image.
'''
print("===== Tag an image - remote =====")
# Call API with remote image
adult_result = computervision_client.analyze_image(remote_image_url, visual_features=["Adult"])

print("Adult score: {:.2f}".format(adult_result.adult.adult_score))
print("Gore score: {:.2f}".format(adult_result.adult.gore_score))
print("Racy score: {:.2f}".format(adult_result.adult.racy_score))
print("is Adult content: {}".format(adult_result.adult.is_adult_content))
print("is Gore content: {}".format(adult_result.adult.is_gory_content))
print("is Racy content: {}".format(adult_result.adult.is_racy_content))
print(remote_image_url)

'''
END - Tag an Image - remote
'''
print("End of Computer Vision quickstart.")