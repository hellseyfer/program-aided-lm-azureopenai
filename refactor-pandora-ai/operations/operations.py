from parameters import *
import json

class Operation(type):
    short_name: str
    description: str
    parameters: dict

    def __str__(cls):
        output = '{short_name}: {description}\n'
        output += 'Parameters:\n'
        output += '- {parameters}'
        
        parameter_template = lambda param_key: f'{param_key} <{cls.parameters[param_key].type}>: {cls.parameters[param_key].description}'
        parameters = '\n- '.join(parameter_template(k) for k in cls.parameters.keys())

        return output.format(short_name=cls.short_name, description=cls.description, parameters=parameters)
    
    @classmethod
    def parameters_json(cls, args: dict):
        params = {k: args[k] if k in args else cls.parameters[k].default_value for k in cls.parameters.keys()}
        return params
    
    @classmethod
    def convert_to_openai_function(cls):
        return {
            "type": "function",
            "function": {
                "name": cls.short_name,
                "description": cls.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        p.name: {
                            "type": p.type,
                            "description": p.description,
                            "default": p.default_value,
                        } for p in cls.parameters.values()
                    },
                    "required": [p.name for p in cls.parameters.values() if p.required],
                },
            }
        }


class CreateCloudSourceOperation(Operation):
    short_name = "CreateCloudSource"
    description = "Function to create a cloud source. A Cloud Source is an endpoint in the cloud taking stored video and content from outside sources. Once the cloud source is created, you can get the ingestion URL endpoint. In the meantime, you can get a Source Preview URL to verify that your ingested source is properly running on the cloud."
    parameters = {
        "name": TextOperationParameter("name", "Cloud Source Name", required=True),
        "protocol": TextOptionsOperationParameter("protocol", "Ingest protocol", ("RTMP", "SRT"), "SRT"),
        "maxOutputConnections": NumberOperationParameter("maxOutputConnections", "number of output connections", 1),
        "redundancyMode": TextOptionsOperationParameter("redundancyMode", "Redundancy mode", ("NONE", "ACTIVE-ACTIVE", "ACTIVE-STANDBY"), "NONE"),
        "streamCount": NumberRangeOperationParameter("streamCount", "Number of streams", (0, 20), 1),
    }

    @classmethod
    def execute(cls, arguments):
        values = cls.parameters_json(arguments)
        values["id"] = "cloud_source_id"
        return json.dumps(values)


class CreateLiveEventOperation(Operation):
    short_name = "CreateLiveEvent"
    description = "Function to create a live event. Add transcoding presets, packaging formats, DRM preference and any add-on features to your live event. Once the live event is created, you can get the ingestion URL endpoint and its id."
    parameters = {
        "name": TextOperationParameter("name", "simple name of the Event", required=True),
        "transcodingProfile": TextOperationParameter("transcodingProfile", "the encoding profile for this liveEvent", "my_profile"),
        "publishName": TextOperationParameter("publishName", "Name used in the URLs to identify the event. This needs to be unique and no space and special characters. If not specified, generated id will be used in URL.", "publish_name")
    }

    @classmethod
    def execute(cls, arguments):
        values = cls.parameters_json(arguments)
        values["event_id"] = "event_id"
        return json.dumps(values)


class PreviewLiveEventOperation(Operation):
    short_name = "PreviewLiveEvent"
    description = "This step activates the transcoding resources for your live event and lets you preview and verify the ingested source with the provided playback URLs through the user interface."
    parameters = {
        "id": TextOperationParameter("id", "Live event id", required=True),
    }

    @classmethod
    def execute(cls, arguments):
        return json.dumps(arguments)


class GoLiveWithLiveEventOperation(Operation):
    short_name = "GoLiveWithLiveEvent"
    description = "This step goes live with your event. Once the health and status of your source are confirmed, go live with your event."
    parameters = {
        "id": TextOperationParameter("id", "Live event id", required=True),
    }

    @classmethod
    def execute(cls, arguments):
        return json.dumps(arguments)


class ListLiveEventsOperation(Operation):
    short_name = "ListLiveEvents"
    description = "List all live events."
    parameters = {}

    @classmethod
    def execute(cls, arguments=None):
        result = [
            {"id": 'event_1', "name": 'event_1'},
            {"id": 'event_2', "name": 'event_2'},
            {"id": 'event_3', "name": 'event_3'},
        ]

        return f'Ask the user to select one of {json.dumps(result)}'



operations_list: list[Operation] = [
    CreateCloudSourceOperation,
    CreateLiveEventOperation,
    PreviewLiveEventOperation,
    GoLiveWithLiveEventOperation,
    ListLiveEventsOperation,
]
