from ..models.avro_schema import msg_schema
import avro.io
import avro.schema
import io
import json

class AvroUtils():
    
    def __init__(self):
        try:
            # import schema and parse it
            self.schema = avro.schema.parse(msg_schema)
            print(f"Loaded schema: {self.schema}")
        except Exception as e:
            print(f"Error loading schema: {e}")
            raise
        
    # function to serialize python object to avro
    def serialize_msg(self, data):
        try:
            
            writer = avro.io.DatumWriter(self.schema)
            bytes_writer = io.BytesIO()
            encoder = avro.io.BinaryEncoder(bytes_writer)
            writer.write(data, encoder)
            
            result = bytes_writer.getvalue()

            return result
            
        except Exception as e:
            print(f"[AVRO UTILS] Error serializing: {data} \n**********\nError: {e}")

            raise

    # function to deserialize avro to python object
    def deserialize_msg(self, message_bytes):
        try:
            bytes_reader = io.BytesIO(message_bytes)
            decoder = avro.io.BinaryDecoder(bytes_reader)
            reader = avro.io.DatumReader(self.schema)

            return reader.read(decoder)
        
        except Exception as e:
            print(f"[AVRO UTILS] Error deserializing: {e}")
            raise